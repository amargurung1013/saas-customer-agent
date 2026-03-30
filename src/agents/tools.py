from typing import Dict, Any, List
from langchain_core.tools import tool
from src.memory import DatabaseManager

# Initialize database manager
db = DatabaseManager()

@tool
def search_knowledge_base(query: str) -> List[Dict[str, Any]]:
    """Search the knowledge base for answers to customer questions"""
    results = db.search_knowledge_base(query)
    return results

@tool
def get_customer_info(customer_id: str) -> Dict[str, Any]:
    """Get customer information by ID"""
    customer = db.get_customer_by_id(customer_id)
    if customer:
        return customer
    return {"error": "Customer not found"}

@tool
def create_support_ticket(customer_id: str, intent: str, issue: str) -> str:
    """Create a new support ticket"""
    ticket_id = db.create_ticket(customer_id, intent)
    db.add_message(ticket_id, "user", issue)
    return ticket_id

@tool
def update_ticket_status(ticket_id: str, status: str) -> str:
    """Update ticket status (open, in_progress, resolved, escalated)"""
    db.update_ticket_status(ticket_id, status)
    return f"Ticket {ticket_id} status updated to {status}"

@tool
def escalate_to_human(ticket_id: str, reason: str) -> str:
    """Escalate a ticket to human support"""
    db.update_ticket_status(ticket_id, "escalated")
    db.add_message(ticket_id, "system", f"Escalated to human support. Reason: {reason}")
    return f"Ticket {ticket_id} has been escalated to human support. Reason: {reason}"