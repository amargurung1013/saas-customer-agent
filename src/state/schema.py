from typing import List, Optional, Literal, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class SupportState(TypedDict):
    """Extended state for customer support agent using modern TypedDict approach"""
    
    # Messages management (using built-in reducer)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Customer information
    customer_id: str
    customer_email: str
    subscription_tier: Literal["free", "pro", "enterprise"]
    
    # Language support
    language_code: str  # ISO language code (en, es, fr, etc.)
    needs_translation: bool  # Whether response needs translation
    
    # Conversation management
    conversation_summary: Optional[str]
    message_count: int
    
    # Routing and intent
    intent: Optional[Literal["billing", "technical", "account", "feature", "human_escalation"]]
    confidence_score: float
    
    # Support ticket management
    ticket_id: Optional[str]
    resolved: bool
    escalation_needed: bool
    escalation_reason: Optional[str]