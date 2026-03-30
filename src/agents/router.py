from typing import Dict, Any, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.utils.config import Config
from src.state import SupportState

class IntentRouter:
    """Routes customer queries to appropriate intent categories"""
    
    def __init__(self):
        """Initialize the router with LLM"""
        Config.validate()
        self.llm = ChatOpenAI(
            model=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
    
    def classify_intent(self, message: str, customer_tier: str = "free") -> Dict[str, Any]:
        """Classify the intent of a customer message"""
        
        system_prompt = """You are a customer support intent classifier for a SaaS company.
        
        Classify the user's message into one of these categories:
        - billing: Questions about pricing, subscriptions, invoices, refunds, upgrades/downgrades
        - technical: Technical issues, bugs, performance problems, API issues
        - account: Account management, password reset, login issues, profile updates
        - feature: Feature requests, product suggestions, new feature inquiries
        - human_escalation: Complex issues, complaints, security concerns, or when user explicitly asks for a human
        
        Also provide:
        - confidence_score: How confident are you? (0.0 to 1.0)
        - reasoning: Brief explanation of why you chose this intent
        - needs_escalation: Whether this should immediately go to human (true/false)
        
        Return as a valid JSON object.
        """
        
        user_prompt = f"Customer tier: {customer_tier}\nMessage: {message}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Use structured output for better parsing
        response = self.llm.invoke(messages)
        
        # Parse the response (simplified - in production use proper JSON parsing)
        import json
        try:
            # Extract JSON from response
            content = response.content
            # Find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                result = json.loads(json_str)
            else:
                # Fallback
                result = {"intent": "human_escalation", "confidence_score": 0.5, "reasoning": "Failed to parse"}
        except:
            # Fallback for any parsing errors
            result = {
                "intent": "human_escalation",
                "confidence_score": 0.3,
                "reasoning": "Error parsing LLM response"
            }
        
        return result
    
    def route(self, state: SupportState) -> SupportState:
        """Route the current state based on intent classification"""
        
        # Get the latest message
        if not state.get("messages"):
            return state
        
        latest_message = state["messages"][-1]
        message_content = latest_message.content
        
        # Classify intent
        classification = self.classify_intent(
            message_content,
            state.get("subscription_tier", "free")
        )
        
        # Update state with classification
        state["intent"] = classification.get("intent", "human_escalation")
        state["confidence_score"] = classification.get("confidence_score", 0.5)
        
        # Determine if escalation is needed
        if classification.get("needs_escalation", False) or state["confidence_score"] < 0.6:
            state["escalation_needed"] = True
            state["escalation_reason"] = classification.get("reasoning", "Low confidence or explicit request")
        else:
            state["escalation_needed"] = False
        
        return state