import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
print("Testing imports...")
try:
    from langgraph.checkpoint.memory import MemorySaver
    print("✅ MemorySaver imported successfully")
except Exception as e:
    print(f"❌ MemorySaver import failed: {e}")

try:
    from src.agents import SupportAgent
    print("✅ SupportAgent imported successfully")
except Exception as e:
    print(f"❌ SupportAgent import failed: {e}")

print("\nAll imports successful!")