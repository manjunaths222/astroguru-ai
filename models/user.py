"""User model"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    picture_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

