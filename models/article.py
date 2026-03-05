"""Article/Blog model for Vedic Astrology content"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database import Base


class Article(Base):
    """Article model for storing blog posts and articles about Vedic Astrology"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    excerpt = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # e.g., "Basics", "Advanced", "Remedies"
    author = Column(String(255), nullable=False, default="AstroGuru Team")
    featured_image = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=True, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title}, slug={self.slug})>"
