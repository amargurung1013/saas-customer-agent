"""
Multi-language support for the customer support agent
"""

from typing import Tuple, Optional
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import logging

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Initialize translator
translator = GoogleTranslator()

# Language codes mapping
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'nl': 'Dutch',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'pl': 'Polish',
    'uk': 'Ukrainian',
    'sv': 'Swedish',
    'da': 'Danish',
    'no': 'Norwegian',
    'fi': 'Finnish',
}

# Welcome messages in different languages
WELCOME_MESSAGES = {
    'en': "Hello! I'm your customer support assistant. How can I help you today?",
    'es': "¡Hola! Soy tu asistente de atención al cliente. ¿Cómo puedo ayudarte hoy?",
    'fr': "Bonjour ! Je suis votre assistant de support client. Comment puis-je vous aider aujourd'hui ?",
    'de': "Hallo! Ich bin Ihr Kundensupport-Assistent. Wie kann ich Ihnen heute helfen?",
    'it': "Ciao! Sono il tuo assistente di supporto clienti. Come posso aiutarti oggi?",
    'pt': "Olá! Sou seu assistente de suporte ao cliente. Como posso ajudá-lo hoje?",
    'nl': "Hallo! Ik ben uw klantenservice-assistent. Hoe kan ik u vandaag helpen?",
    'ru': "Здравствуйте! Я ваш помощник службы поддержки. Чем могу помочь сегодня?",
    'ja': "こんにちは！カスタマーサポートアシスタントです。どのようにお手伝いできますか？",
    'ko': "안녕하세요! 고객 지원 어시스턴트입니다. 오늘 어떻게 도와드릴까요?",
    'zh-cn': "您好！我是您的客户支持助手。今天我能帮您什么？",
    'ar': "مرحباً! أنا مساعد دعم العملاء الخاص بك. كيف يمكنني مساعدتك اليوم؟",
    'hi': "नमस्ते! मैं आपका ग्राहक सहायता सहायक हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?",
}

class LanguageManager:
    """Manages language detection and translation for multi-language support"""
    
    def __init__(self):
        """Initialize the language manager"""
        self.current_language = 'en'
        self.logger = logging.getLogger(__name__)
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of the given text
        Returns: (language_code, confidence)
        """
        try:
            # Get the language code
            lang_code = detect(text)
            # Map Chinese variants
            if lang_code == 'zh-cn' or lang_code == 'zh-tw':
                pass  # Keep as detected
            elif lang_code == 'zh':
                lang_code = 'zh-cn'
            
            # Simple confidence - could be enhanced with more sophisticated methods
            confidence = 0.9 if len(text) > 20 else 0.7
            
            return lang_code, confidence
        except Exception as e:
            self.logger.error(f"Language detection error: {e}")
            return 'en', 0.5
    
    def translate_to_english(self, text: str, source_lang: Optional[str] = None) -> str:
        """
        Translate text to English
        """
        if not text:
            return text
        
        try:
            if source_lang and source_lang == 'en':
                return text
            
            # Use deep-translator
            translated = GoogleTranslator(source='auto', target='en').translate(text)
            return translated
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return text
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Translate English text to target language
        """
        if not text or target_lang == 'en':
            return text
        
        try:
            # Use deep-translator
            translated = GoogleTranslator(source='en', target=target_lang).translate(text)
            return translated
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return text
    
    def get_welcome_message(self, lang_code: str) -> str:
        """
        Get welcome message in specified language
        """
        return WELCOME_MESSAGES.get(lang_code, WELCOME_MESSAGES['en'])
    
    def get_language_name(self, lang_code: str) -> str:
        """
        Get the full name of a language from its code
        """
        return LANGUAGES.get(lang_code, 'Unknown')
    
    def detect_and_set_language(self, text: str) -> str:
        """
        Detect language from text and set as current
        Returns the detected language code
        """
        lang_code, confidence = self.detect_language(text)
        if confidence > 0.6:
            self.current_language = lang_code
        return lang_code