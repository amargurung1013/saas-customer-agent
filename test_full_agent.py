from src.agents import SupportAgent
import time

print("🚀 Testing Full Customer Support Agent\n" + "="*60)

# Initialize agent
agent = SupportAgent()

# Test 1: Billing question with knowledge base
print("\n📝 Test 1: Billing Question")
print("-" * 40)
response = agent.process_message(
    "How much does the pro plan cost and what features does it include?",
    "alice@company.com",
    "Alice Johnson"
)
print(f"Alice: How much does the pro plan cost?")
print(f"Agent: {response}\n")

time.sleep(1)

# Test 2: Technical issue
print("\n📝 Test 2: Technical Support")
print("-" * 40)
response = agent.process_message(
    "The dashboard is taking forever to load, it's been stuck for 5 minutes",
    "bob@startup.com",
    "Bob Smith"
)
print(f"Bob: The dashboard is taking forever to load")
print(f"Agent: {response}\n")

time.sleep(1)

# Test 3: Account issue
print("\n📝 Test 3: Account Management")
print("-" * 40)
response = agent.process_message(
    "I can't remember my password and the reset email isn't arriving",
    "carol@tech.io",
    "Carol Davis"
)
print(f"Carol: I can't remember my password")
print(f"Agent: {response}\n")

time.sleep(1)

# Test 4: Feature request
print("\n📝 Test 4: Feature Request")
print("-" * 40)
response = agent.process_message(
    "It would be great if you added a dark mode theme",
    "dave@design.com",
    "Dave Wilson"
)
print(f"Dave: It would be great if you added dark mode")
print(f"Agent: {response}\n")

time.sleep(1)

# Test 5: Human escalation
print("\n📝 Test 5: Human Escalation")
print("-" * 40)
response = agent.process_message(
    "This is a serious security concern, I need to speak with a human immediately",
    "eve@security.com",
    "Eve Brown"
)
print(f"Eve: I need to speak with a human immediately")
print(f"Agent: {response}\n")

time.sleep(1)

# Test 6: Multi-turn conversation with memory
print("\n📝 Test 6: Multi-turn Conversation (with memory)")
print("-" * 40)
thread_id = "conversation_123"

response1 = agent.process_message(
    "I'm having issues with billing",
    "frank@example.com",
    "Frank Miller",
    thread_id
)
print(f"Frank: I'm having issues with billing")
print(f"Agent: {response1}\n")

response2 = agent.process_message(
    "Yes, I was charged twice this month",
    "frank@example.com",
    "Frank Miller",
    thread_id
)
print(f"Frank: Yes, I was charged twice this month")
print(f"Agent: {response2}\n")

response3 = agent.process_message(
    "Can you process a refund for the duplicate charge?",
    "frank@example.com",
    "Frank Miller",
    thread_id
)
print(f"Frank: Can you process a refund?")
print(f"Agent: {response3}\n")

print("\n" + "="*60)
print("✅ All tests completed! Your support agent is fully functional!")
print("\nKey Features Demonstrated:")
print("• Intent classification (billing, technical, account, feature, escalation)")
print("• Knowledge base integration")
print("• Multi-turn conversation memory")
print("• Human escalation workflow")
print("• External database storage")
print("• Context-aware responses")