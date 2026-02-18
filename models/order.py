"""Order model"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Order(Base):
    """Order model for storing analysis orders"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True, default="payment_pending")
    # Status values: payment_pending, processing, completed, failed
    type = Column(String(50), nullable=False, index=True, default="full_report")
    # Type values: full_report, query
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    amount = Column(Float, nullable=False)
    birth_details = Column(JSON, nullable=True)  # Store birth details as JSON
    analysis_data = Column(JSON, nullable=True)  # Store analysis results as JSON
    error_reason = Column(Text, nullable=True)  # Store error message if failed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="orders")
    payment = relationship("Payment", foreign_keys=[payment_id], backref="order")
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status})>"

