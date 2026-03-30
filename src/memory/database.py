import sqlite3
import uuid
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    """Manages database operations for the support agent"""
    
    def __init__(self, db_path: str = "data/support.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with schema"""
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        with self._get_connection() as conn:
            # Get the absolute path to schema.sql
            schema_path = os.path.join(os.path.dirname(__file__), "../../data/schema.sql")
            with open(schema_path, "r") as f:
                conn.executescript(f.read())
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    # Customer operations
    def get_or_create_customer(self, email: str, name: str = "") -> Dict[str, Any]:
        """Get existing customer or create new one"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM customers WHERE email = ?",
                (email,)
            )
            customer = cursor.fetchone()
            
            if customer:
                # Update last interaction
                conn.execute(
                    "UPDATE customers SET last_interaction = CURRENT_TIMESTAMP WHERE id = ?",
                    (customer["id"],)
                )
                return dict(customer)
            else:
                # Create new customer
                customer_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO customers (id, email, name, subscription_tier) VALUES (?, ?, ?, ?)",
                    (customer_id, email, name, "free")
                )
                return {
                    "id": customer_id,
                    "email": email,
                    "name": name,
                    "subscription_tier": "free"
                }
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM customers WHERE id = ?",
                (customer_id,)
            )
            result = cursor.fetchone()
            return dict(result) if result else None
    
    # Ticket operations
    def create_ticket(self, customer_id: str, intent: str) -> str:
        """Create a new support ticket"""
        ticket_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO tickets (id, customer_id, intent, status) VALUES (?, ?, ?, ?)",
                (ticket_id, customer_id, intent, "open")
            )
        return ticket_id
    
    def update_ticket_status(self, ticket_id: str, status: str):
        """Update ticket status"""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE tickets SET status = ? WHERE id = ?",
                (status, ticket_id)
            )
            if status == "resolved":
                conn.execute(
                    "UPDATE tickets SET resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (ticket_id,)
                )
    
    def get_ticket_history(self, ticket_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a ticket"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM conversations WHERE ticket_id = ? ORDER BY timestamp",
                (ticket_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # Conversation operations
    def add_message(self, ticket_id: str, role: str, content: str):
        """Add a message to conversation history"""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO conversations (ticket_id, message_role, message_content) VALUES (?, ?, ?)",
                (ticket_id, role, content)
            )
    
    # Knowledge base operations
    def search_knowledge_base(self, query: str) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant answers"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """SELECT * FROM knowledge_base 
                   WHERE question LIKE ? OR answer LIKE ? OR keywords LIKE ?
                   LIMIT 3""",
                (f"%{query}%", f"%{query}%", f"%{query}%")
            )
            return [dict(row) for row in cursor.fetchall()]