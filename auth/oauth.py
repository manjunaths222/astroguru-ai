"""Google OAuth handlers"""

import httpx
from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select
from config import AstroConfig, logger
from models.user import User
from auth.jwt_handler import create_access_token


async def get_google_oauth_url() -> str:
    """Generate Google OAuth URL"""
    from urllib.parse import urlencode
    
    params = {
        "client_id": AstroConfig.AuthConfig.GOOGLE_CLIENT_ID,
        "redirect_uri": AstroConfig.AuthConfig.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return auth_url


async def handle_google_callback(code: str, db: Session) -> Dict:
    """Handle Google OAuth callback and create/update user"""
    try:
        # Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": AstroConfig.AuthConfig.GOOGLE_CLIENT_ID,
            "client_secret": AstroConfig.AuthConfig.GOOGLE_CLIENT_SECRET,
            "redirect_uri": AstroConfig.AuthConfig.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            access_token = tokens.get("access_token")
            
            # Get user info from Google
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = await client.get(user_info_url, headers=headers)
            user_response.raise_for_status()
            user_info = user_response.json()
        
        # Extract user information
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name", email.split("@")[0])
        picture_url = user_info.get("picture")
        
        if not email or not google_id:
            raise ValueError("Missing required user information from Google")
        
        # Check if user exists
        stmt = select(User).where(User.google_id == google_id)
        result = db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            # Update existing user
            user.email = email
            user.name = name
            user.picture_url = picture_url
            logger.info(f"Updated existing user: {email}")
        else:
            # Create new user
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                picture_url=picture_url
            )
            db.add(user)
            logger.info(f"Created new user: {email}")
        
        db.commit()
        db.refresh(user)
        
        # Create JWT token
        # JWT 'sub' claim must be a string
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "type": "user"
        }
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture_url": user.picture_url
            }
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during OAuth callback: {e}")
        raise ValueError(f"Failed to authenticate with Google: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Error handling Google OAuth callback: {e}", exc_info=True)
        raise ValueError(f"Failed to authenticate: {str(e)}")
