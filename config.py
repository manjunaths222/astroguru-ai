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
        
        # Analysis Price
        ANALYSIS_PRICE = float(os.getenv("ANALYSIS_PRICE", "10.00"))  # Default ₹10
        QUERY_PRICE = float(os.getenv("QUERY_PRICE", "5.00"))  # Default ₹5 (50% of analysis price)
        
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
    
    class DatabaseConfig:
        """Database configuration"""
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/astroguru_db")
    
    class AuthConfig:
        """Authentication configuration"""
        # Google OAuth
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
        GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
        # Default redirect URI - backend runs on port 8002
        # For React dev server (port 3000), the callback still goes to backend
        GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8002/api/v1/auth/google/callback")
        
        # JWT
        JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
        
        # Admin
        ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@astroguru.ai")
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")  # Should be hashed
    
    class CORSConfig:
        """CORS configuration"""
        # CORS origins - comma-separated list, or "*" for all origins (development only)
        CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS", "*") != "*" else ["*"]
        CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    
    class PaymentConfig:
        """Payment configuration"""
        RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
        RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
        RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

