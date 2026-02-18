"""FastAPI dependencies for authentication"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from auth.jwt_handler import get_current_user

security = HTTPBearer()


def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    user_data = get_current_user(token)
    return user_data


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Dependency to get current authenticated admin"""
    token = credentials.credentials
    user_data = get_current_user(token)
    
    if user_data.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user_data


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """Dependency to get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_data = get_current_user(token)
        return user_data
    except Exception:
        return None
