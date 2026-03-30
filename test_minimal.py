from src.agents import SupportAgent

print("Initializing Support Agent...")
agent = SupportAgent()
print("✅ Agent initialized successfully!\n")

# Simple test
message = "I need help with billing"
email = "test@example.com"

print(f"User: {message}")
response = agent.process_message(message, email, thread_id="test_1")
print(f"Agent: {response}")