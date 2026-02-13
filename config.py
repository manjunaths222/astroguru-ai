import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AstroConfig:
    """Configuration for AstroGuru AI application"""
    
    class AppSettings:
        """General application settings"""
        APP_NAME = "astroguru-ai-langgraph"
        APP_TITLE = "AstroGuru AI - Astrology Product (LangGraph)"
        APP_DESCRIPTION = "AI-powered astrology analysis using LangGraph and Gemini Models"
        VERSION = "2.0.0"
        PORT = int(os.getenv("PORT", "8002"))
        DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        ENV = os.getenv("ENV", "dev")
        
        # Gemini Model settings
        GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
        GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))
        
        # Google AI API Key (for Gemini API)
        GOOGLE_AI_API_KEY = os.getenv("GEMINI_API_KEY", "")

        # Resend API Key
        RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
        RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "astroguruai@resend.dev")
        RESEND_FROM_NAME = os.getenv("RESEND_FROM_NAME", "AstroGuru AI")
        
        @staticmethod
        def validate_google_credentials() -> bool:
            """Validate that Google AI API key is configured"""
            api_key = AstroConfig.AppSettings.GOOGLE_AI_API_KEY
            if not api_key or api_key.strip() == "":
                return False
            # Basic validation - check if it looks like a valid API key
            # Google API keys typically start with "AIza" and are 39 characters long
            if len(api_key) < 20:  # Minimum reasonable length
                return False
            return True

