"""Chat message model"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class ChatMessage(Base):
    """Chat message model for storing chat history"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    message_number = Column(Integer, nullable=False)  # 1, 2, 3 for tracking message count
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)  # Message content
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", backref="chat_messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, order_id={self.order_id}, message_number={self.message_number}, role={self.role})>"

