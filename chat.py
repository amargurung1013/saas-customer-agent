#!/usr/bin/env python
"""
Interactive Customer Support Agent Chat Interface with Multi-Language Support
Run with: uv run python chat.py
"""

from src.agents import SupportAgent
import sys
import os
from datetime import datetime

class InteractiveChat:
    """Interactive chat interface for the support agent"""
    
    def __init__(self):
        """Initialize the chat interface"""
        print("\n" + "="*60)
        print("🤖 SaaS Customer Support Agent - Multi-Language Support")
        print("="*60)
        print("\nInitializing agent...")
        
        try:
            self.agent = SupportAgent()
            print("✅ Agent ready!")
            print("🌍 Supports: English, Spanish, French, German, Japanese, Arabic, and more!")
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            sys.exit(1)
        
        # Store customer info for the session
        self.customer_email = None
        self.customer_name = None
        self.thread_id = "user_session"
        self.conversation_count = 0
    
    def get_customer_info(self):
        """Get customer information at start of session"""
        print("\n📋 Please tell me a bit about yourself:")
        print("-" * 40)
        
        self.customer_email = input("Email address: ").strip()
        self.customer_name = input("Your name (optional): ").strip() or "Customer"
        
        print(f"\n✅ Welcome {self.customer_name}!")
        print("💡 You can type in ANY language - I'll auto-detect and respond!")
        print("💡 Type 'exit' to end the conversation")
        print("💡 Type 'clear' to start a new conversation")
        print("💡 Type 'lang' to see detected language")
        print("-" * 40)
    
    def print_message(self, role: str, content: str, timestamp: bool = True):
        """Print formatted messages"""
        if timestamp:
            time_str = datetime.now().strftime("%H:%M")
        else:
            time_str = ""
        
        if role == "user":
            print(f"\n👤 You [{time_str}]: {content}")
        elif role == "agent":
            print(f"\n🤖 Agent [{time_str}]: {content}")
        elif role == "system":
            print(f"\n⚙️ System: {content}")
    
    def process_message(self, message: str) -> str:
        """Process a single message through the agent"""
        try:
            response = self.agent.process_message(
                message=message,
                customer_email=self.customer_email,
                customer_name=self.customer_name,
                thread_id=self.thread_id
            )
            return response
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."
    
    def run(self):
        """Run the interactive chat loop"""
        self.get_customer_info()
        
        print("\n" + "="*60)
        print("Chat session started! Type your questions below.")
        print("Try asking in different languages: Spanish, French, German, etc!")
        print("="*60)
        
        while True:
            # Get user input
            try:
                user_input = input("\n💬 You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Goodbye! Have a great day!")
                break
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("\n👋 Thank you for contacting support! Have a great day!")
                break
            
            # Check for clear command
            if user_input.lower() == 'clear':
                self.thread_id = f"session_{self.conversation_count + 1}"
                self.conversation_count += 1
                print("\n✨ Starting new conversation thread!")
                continue
            
            # Check for language detection command
            if user_input.lower() == 'lang':
                print("\n🌍 I automatically detect your language and respond in it!")
                print("Just type your message in any language and I'll understand.")
                continue
            
            # Skip empty messages
            if not user_input:
                continue
            
            # Process message
            self.print_message("user", user_input)
            
            # Show typing indicator
            print("🤖 Agent is thinking", end="", flush=True)
            for _ in range(3):
                print(".", end="", flush=True)
                import time
                time.sleep(0.3)
            print()
            
            # Get response
            response = self.process_message(user_input)
            
            # Print response
            self.print_message("agent", response)
            
            # Show separator
            print("-" * 40)

class QuickTestMode:
    """Quick test mode with predefined questions in multiple languages"""
    
    def __init__(self):
        self.agent = SupportAgent()
        
    def run(self):
        """Run quick test with sample questions"""
        print("\n" + "="*60)
        print("🚀 Quick Test Mode - Try in Different Languages!")
        print("="*60)
        
        # Sample questions in different languages
        test_questions = [
            ("alice@example.com", "Alice", "English", "How much does the pro plan cost?"),
            ("carlos@example.com", "Carlos", "Spanish", "No puedo iniciar sesión en mi cuenta"),
            ("marie@example.com", "Marie", "French", "J'ai été facturé deux fois ce mois-ci"),
            ("hans@example.com", "Hans", "German", "Die Anwendung ist sehr langsam"),
            ("yuki@example.com", "Yuki", "Japanese", "Proプランにアップグレードしたい"),
            ("ahmed@example.com", "Ahmed", "Arabic", "لدي مشكلة في لوحة التحكم"),
        ]
        
        for email, name, lang, question in test_questions:
            print(f"\n👤 {name} ({lang}): {question}")
            print("-" * 40)
            
            response = self.agent.process_message(
                message=question,
                customer_email=email,
                customer_name=name
            )
            
            print(f"🤖 Agent: {response}")
            print("="*60)
            input("\nPress Enter for next question...")

def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     🤖 SaaS Customer Support Agent - LangGraph Demo      ║
    ║                    Multi-Language Support                ║
    ╚══════════════════════════════════════════════════════════╝
    
    Choose mode:
    1. Interactive Chat - Talk with the agent in real-time (any language!)
    2. Quick Test - Run through sample questions in different languages
    3. Exit
    
    """)
    
    while True:
        choice = input("Enter your choice (1/2/3): ").strip()
        
        if choice == '1':
            chat = InteractiveChat()
            chat.run()
            break
        elif choice == '2':
            test = QuickTestMode()
            test.run()
            break
        elif choice == '3':
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please try again.")