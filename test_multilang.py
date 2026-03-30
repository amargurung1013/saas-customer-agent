"""
Test multi-language support in the customer support agent
"""

from src.agents import SupportAgent

def test_multi_language():
    """Test the agent with different languages"""
    
    print("="*60)
    print("🌍 Testing Multi-Language Support")
    print("="*60)
    
    agent = SupportAgent()
    
    # Test cases in different languages
    test_cases = [
        {
            "language": "Spanish",
            "email": "carlos@example.com", 
            "name": "Carlos",
            "message": "Hola, no puedo iniciar sesión en mi cuenta. Necesito ayuda para restablecer mi contraseña."
        },
        {
            "language": "French",
            "email": "marie@example.com",
            "name": "Marie", 
            "message": "Bonjour, j'ai été facturé deux fois ce mois-ci. Pouvez-vous m'aider à obtenir un remboursement?"
        },
        {
            "language": "German",
            "email": "hans@example.com",
            "name": "Hans",
            "message": "Hallo, die Anwendung ist sehr langsam. Was kann ich tun, um die Leistung zu verbessern?"
        },
        {
            "language": "Japanese",
            "email": "yuki@example.com",
            "name": "Yuki",
            "message": "こんにちは、Proプランにアップグレードしたいのですが、料金はいくらですか？"
        },
        {
            "language": "Arabic",
            "email": "ahmed@example.com",
            "name": "Ahmed",
            "message": "مرحباً، لدي مشكلة تقنية في لوحة التحكم. لا يتم تحميل البيانات بشكل صحيح."
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test['language']}")
        print("-" * 40)
        print(f"👤 {test['name']}: {test['message']}")
        
        try:
            response = agent.process_message(
                message=test['message'],
                customer_email=test['email'],
                customer_name=test['name'],
                thread_id=f"multilang_test_{i}"
            )
            print(f"🤖 Agent: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("="*60)

def test_simple_english():
    """Simple English test to verify agent works"""
    
    print("\n\n" + "="*60)
    print("📝 Testing English (Baseline)")
    print("="*60)
    
    agent = SupportAgent()
    
    response = agent.process_message(
        message="I need help with billing, I was charged twice this month",
        customer_email="test@example.com",
        customer_name="Test User"
    )
    
    print(f"👤 User: I need help with billing, I was charged twice this month")
    print(f"🤖 Agent: {response}")

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     🌍 Multi-Language Customer Support Agent Test        ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # First test English to make sure everything works
    test_simple_english()
    
    # Then test multi-language
    test_multi_language()
    
    print("\n" + "="*60)
    print("✅ Multi-language tests completed!")