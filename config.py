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
        GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY", "")
        
        @classmethod
        def validate_google_credentials(cls) -> bool:
            """Validate that Google credentials are available"""
            if not cls.GOOGLE_AI_API_KEY:
                logger.error("GOOGLE_AI_API_KEY not configured")
                return False
            return True

