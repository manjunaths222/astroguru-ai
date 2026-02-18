"""JWT token handling"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import HTTPException, status
from config import AstroConfig, logger


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=AstroConfig.AuthConfig.JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        AstroConfig.AuthConfig.JWT_SECRET_KEY,
        algorithm=AstroConfig.AuthConfig.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            AstroConfig.AuthConfig.JWT_SECRET_KEY,
            algorithms=[AstroConfig.AuthConfig.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token: str) -> Dict:
    """Get current user from token"""
    payload = verify_token(token)
    sub = payload.get("sub")
    user_type: Optional[str] = payload.get("type", "user")  # "user" or "admin"
    
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convert sub (string) back to integer user_id
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": user_id,
        "user_type": user_type,
        "email": payload.get("email")
    }

