"""Payment model"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base


class Payment(Base):
    """Payment model for storing payment information"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    razorpay_order_id = Column(String(255), unique=True, index=True, nullable=True)
    razorpay_payment_id = Column(String(255), unique=True, index=True, nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, index=True, default="pending")
    # Status values: pending, success, failed
    payment_method = Column(String(50), nullable=True)  # UPI, card, netbanking, etc.
    razorpay_refund_id = Column(String(255), nullable=True, index=True)
    refund_amount = Column(Float, nullable=True)
    refund_status = Column(String(50), nullable=True)  # Values: pending, processed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, status={self.status})>"

