import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration for the support agent"""
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-4o-mini"  # Using latest model
    TEMPERATURE = 0.7
    
    # Intent classification
    INTENTS = ["billing", "technical", "account", "feature", "human_escalation"]
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")