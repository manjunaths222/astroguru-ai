"""Admin authentication"""

from passlib.context import CryptContext
from config import AstroConfig, logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def verify_admin_credentials(email: str, password: str) -> bool:
    """Verify admin credentials from environment"""
    admin_email = AstroConfig.AuthConfig.ADMIN_EMAIL
    admin_password = AstroConfig.AuthConfig.ADMIN_PASSWORD
    
    if not admin_email or not admin_password:
        logger.warning("Admin credentials not configured")
        return False
    
    # Check email
    if email.lower() != admin_email.lower():
        logger.warning(f"Admin login attempt with wrong email: {email}")
        return False
    
    # Check password
    # If password is already hashed, compare directly
    # Otherwise, hash and compare (for backward compatibility)
    if admin_password.startswith("$2b$") or admin_password.startswith("$2a$"):
        # Already hashed
        if not verify_password(password, admin_password):
            logger.warning(f"Admin login attempt with wrong password for: {email}")
            return False
    else:
        # Plain text (should be hashed in production)
        if password != admin_password:
            logger.warning(f"Admin login attempt with wrong password for: {email}")
            return False
        else:
            logger.warning("Admin password is stored in plain text! Please hash it.")
    
    logger.info(f"Admin login successful: {email}")
    return True

