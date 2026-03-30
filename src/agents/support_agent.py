from typing import Literal, Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from src.state import SupportState
from src.utils.config import Config
from src.utils.language import LanguageManager
from .router import IntentRouter
from .tools import search_knowledge_base, create_support_ticket, update_ticket_status, escalate_to_human
from src.memory import DatabaseManager

class SupportAgent:
    """Main customer support agent using LangGraph with multi-language support"""
    
    def __init__(self):
        """Initialize the agent"""
        Config.validate()
        self.llm = ChatOpenAI(
            model=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        self.router = IntentRouter()
        self.db = DatabaseManager()
        self.lang_manager = LanguageManager()  # Add language manager
        
        # Bind tools to LLM
        self.tools = {
            "search_knowledge_base": search_knowledge_base,
            "create_support_ticket": create_support_ticket,
            "update_ticket_status": update_ticket_status,
            "escalate_to_human": escalate_to_human
        }
        self.llm_with_tools = self.llm.bind_tools(list(self.tools.values()))
        
        # Build the graph
        self.graph = self._build_graph()
        
        # Add memory
        self.memory = MemorySaver()
        self.app = self.graph.compile(checkpointer=self.memory)
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(SupportState)
        
        # Add nodes
        workflow.add_node("detect_language", self.detect_language_node)
        workflow.add_node("route_intent", self.route_intent_node)
        workflow.add_node("handle_query", self.handle_query)
        workflow.add_node("process_tools", self.process_tools)
        workflow.add_node("translate_response", self.translate_response_node)
        
        # Set entry point - first detect language
        workflow.set_entry_point("detect_language")
        
        # Language detection -> routing
        workflow.add_edge("detect_language", "route_intent")
        
        # Add conditional edges based on intent
        workflow.add_conditional_edges(
            "route_intent",
            self.determine_intent,
            {
                "continue": "handle_query",
                "escalate": "handle_query"
            }
        )
        
        # After handling query, check for tools
        workflow.add_conditional_edges(
            "handle_query",
            self.should_use_tools,
            {
                "tools": "process_tools",
                "translate": "translate_response",
                "end": END
            }
        )
        
        # After processing tools, go back to handle_query for final response
        workflow.add_edge("process_tools", "handle_query")
        
        # After translation, end
        workflow.add_edge("translate_response", END)
        
        return workflow
    
    def detect_language_node(self, state: SupportState) -> Dict[str, Any]:
        """Detect language from the user's message"""
        messages = state.get("messages", [])
        if messages:
            # Get the last user message
            user_message = messages[-1].content
            
            # Detect language
            lang_code, confidence = self.lang_manager.detect_language(user_message)
            
            # Translate to English for processing if needed
            needs_translation = lang_code != 'en'
            if needs_translation:
                translated_message = self.lang_manager.translate_to_english(user_message, lang_code)
                # Replace the original message with translated version for processing
                messages[-1].content = translated_message
            
            return {
                "language_code": lang_code,
                "needs_translation": needs_translation
            }
        
        return {"language_code": "en", "needs_translation": False}
    
    def route_intent_node(self, state: SupportState) -> Dict[str, Any]:
        """Route the intent based on user message"""
        return self.router.route(state)
    
    def determine_intent(self, state: SupportState) -> str:
        """Determine which path to use"""
        if state.get("escalation_needed", False):
            return "escalate"
        return "continue"
    
    def handle_query(self, state: SupportState) -> Dict[str, Any]:
        """Handle the customer query based on intent with language awareness"""
        messages = state["messages"]
        intent = state.get("intent", "general")
        lang_code = state.get("language_code", "en")
        
        # Customize system prompt based on intent and language
        system_prompts = {
            "billing": f"""You are a billing support specialist. Help customers with:
            - Pricing and plans
            - Upgrades and downgrades  
            - Invoices and payments
            - Refunds and cancellations
            
            Be helpful and concise. Use search_knowledge_base if you need specific pricing info.
            If you need to create a ticket for refunds, use create_support_ticket.
            
            The customer is speaking in {self.lang_manager.get_language_name(lang_code)}.
            Respond in a friendly, professional manner that will be translated back to their language.
            """,
            
            "technical": f"""You are a technical support specialist. Help customers with:
            - Technical issues and bugs
            - Performance problems
            - API integration
            - Troubleshooting steps
            
            Be systematic and helpful. Use search_knowledge_base for common issues.
            
            The customer is speaking in {self.lang_manager.get_language_name(lang_code)}.
            Provide clear, step-by-step instructions that will be translated to their language.
            """,
            
            "account": f"""You are an account management specialist. Help customers with:
            - Password resets
            - Account settings
            - Profile updates
            - Data export
            
            Be helpful but cautious about security. Never ask for passwords.
            
            The customer is speaking in {self.lang_manager.get_language_name(lang_code)}.
            Be polite and professional in your response.
            """,
            
            "feature": f"""You are a product specialist. Handle feature requests by:
            - Acknowledging the request
            - Checking if feature exists
            - Explaining how to submit formal feature requests
            - Providing alternatives if available
            
            The customer is speaking in {self.lang_manager.get_language_name(lang_code)}.
            Be enthusiastic about their feedback.
            """,
            
            "human_escalation": f"""You are handling an escalation. Create a ticket for the customer
            and let them know a human will help them soon. Be empathetic and reassuring.
            
            The customer is speaking in {self.lang_manager.get_language_name(lang_code)}.
            Show understanding and empathy in your response.
            """
        }
        
        system_prompt = system_prompts.get(intent, f"""You are a helpful customer support agent. 
        Assist the customer with their query professionally and politely.
        
        The customer is speaking in {self.lang_manager.get_language_name(lang_code)}.
        Provide a helpful, friendly response that will be translated to their language.
        """)
        
        # Add escalation context if needed
        if state.get("escalation_needed"):
            system_prompt += "\n\nThis issue may need escalation. Create a ticket if it's complex."
        
        # If this is a follow-up after tools, don't add system prompt again
        last_message = messages[-1] if messages else None
        if last_message and isinstance(last_message, ToolMessage):
            # Just continue the conversation
            response = self.llm.invoke(messages)
        else:
            # Initial query with system prompt
            response = self.llm_with_tools.invoke([
                SystemMessage(content=system_prompt),
                *messages
            ])
        
        return {"messages": [response], "message_count": state.get("message_count", 0) + 1}
    
    def should_use_tools(self, state: SupportState) -> str:
        """Check if the last message has tool calls"""
        messages = state["messages"]
        if messages and hasattr(messages[-1], 'tool_calls') and messages[-1].tool_calls:
            return "tools"
        return "translate"  # Always translate before ending
    
    def process_tools(self, state: SupportState) -> Dict[str, Any]:
        """Process any tool calls from the last message"""
        messages = state["messages"]
        
        if not messages:
            return {"messages": []}
            
        last_message = messages[-1]
        
        # Check if the last message has tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            # Process each tool call
            tool_messages = []
            for tool_call in last_message.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                print(f"🔧 Executing tool: {tool_name} with args: {tool_args}")
                
                # Execute the appropriate tool
                if tool_name in self.tools:
                    try:
                        result = self.tools[tool_name].invoke(tool_args)
                        tool_messages.append(
                            ToolMessage(
                                content=str(result),
                                tool_call_id=tool_call['id']
                            )
                        )
                        print(f"✅ Tool executed successfully")
                    except Exception as e:
                        print(f"❌ Tool error: {e}")
                        tool_messages.append(
                            ToolMessage(
                                content=f"Error: {str(e)}",
                                tool_call_id=tool_call['id']
                            )
                        )
            
            # Return tool messages to be added to state
            if tool_messages:
                return {"messages": tool_messages}
        
        return {"messages": []}
    
    def translate_response_node(self, state: SupportState) -> Dict[str, Any]:
        """Translate the final response back to the user's language if needed"""
        messages = state.get("messages", [])
        lang_code = state.get("language_code", "en")
        needs_translation = state.get("needs_translation", False)
        
        if messages and needs_translation and lang_code != 'en':
            # Get the last AI message
            last_message = messages[-1]
            if isinstance(last_message, AIMessage) and last_message.content:
                # Translate to user's language
                translated_content = self.lang_manager.translate_from_english(
                    last_message.content, 
                    lang_code
                )
                # Replace the message content with translation
                last_message.content = translated_content
                return {"messages": [last_message]}
        
        return {}
    
    def process_message(self, message: str, customer_email: str, customer_name: str = "", thread_id: str = "default") -> str:
        """Process a customer message and return response with language support"""
        
        # Get or create customer
        customer = self.db.get_or_create_customer(customer_email, customer_name)
        
        # Create initial state with language support
        initial_state = SupportState(
            messages=[HumanMessage(content=message)],
            customer_id=customer["id"],
            customer_email=customer_email,
            subscription_tier=customer["subscription_tier"],
            language_code="en",  # Will be detected
            needs_translation=False,
            conversation_summary=None,
            message_count=1,
            intent=None,
            confidence_score=0.0,
            ticket_id=None,
            resolved=False,
            escalation_needed=False,
            escalation_reason=None
        )
        
        # Process through graph
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            result = self.app.invoke(initial_state, config)
            
            # Get the last message
            if result and result.get("messages"):
                # Find the last AI message (not tool messages)
                last_ai_message = None
                for msg in reversed(result["messages"]):
                    if isinstance(msg, AIMessage):
                        last_ai_message = msg
                        break
                
                if last_ai_message:
                    # Save to database if we have a ticket
                    if result.get("ticket_id"):
                        self.db.add_message(result["ticket_id"], "assistant", last_ai_message.content)
                    
                    return last_ai_message.content
            
            return "I'm sorry, I encountered an issue processing your request."
                
        except Exception as e:
            print(f"Error processing message: {e}")
            return f"I'm sorry, I encountered an error. Please try again."