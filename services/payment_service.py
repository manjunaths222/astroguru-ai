"""Payment service for Razorpay integration"""

import razorpay
import hmac
import hashlib
from typing import Dict, Optional
from config import AstroConfig, logger


class PaymentService:
    """Service for handling Razorpay payments"""
    
    def __init__(self):
        self.client = razorpay.Client(
            auth=(AstroConfig.PaymentConfig.RAZORPAY_KEY_ID, AstroConfig.PaymentConfig.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount: float, order_id: int, currency: str = "INR") -> Dict:
        """Create Razorpay order"""
        try:
            # Convert amount to paise (Razorpay uses smallest currency unit)
            amount_paise = int(amount * 100)
            
            razorpay_order = self.client.order.create({
                "amount": amount_paise,
                "currency": currency,
                "receipt": f"order_{order_id}",
                "notes": {
                    "order_id": order_id
                }
            })
            
            logger.info(f"Created Razorpay order: {razorpay_order['id']} for order {order_id}")
            return razorpay_order
            
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {e}", exc_info=True)
            raise ValueError(f"Failed to create payment order: {str(e)}")
    
    def verify_payment(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """Verify Razorpay payment signature"""
        try:
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            generated_signature = hmac.new(
                AstroConfig.PaymentConfig.RAZORPAY_KEY_SECRET.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = hmac.compare_digest(generated_signature, razorpay_signature)
            
            if is_valid:
                logger.info(f"Payment signature verified for order: {razorpay_order_id}")
            else:
                logger.warning(f"Invalid payment signature for order: {razorpay_order_id}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying payment signature: {e}", exc_info=True)
            return False
    
    def get_payment_details(self, razorpay_payment_id: str) -> Optional[Dict]:
        """Get payment details from Razorpay"""
        try:
            payment = self.client.payment.fetch(razorpay_payment_id)
            return payment
        except Exception as e:
            logger.error(f"Error fetching payment details: {e}", exc_info=True)
            return None
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Razorpay webhook signature"""
        try:
            webhook_secret = AstroConfig.PaymentConfig.RAZORPAY_WEBHOOK_SECRET
            if not webhook_secret:
                logger.warning("Webhook secret not configured, skipping signature verification")
                return True  # Allow if not configured (for development)
            
            generated_signature = hmac.new(
                webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = hmac.compare_digest(generated_signature, signature)
            
            if not is_valid:
                logger.warning("Invalid webhook signature")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}", exc_info=True)
            return False
    
    def create_refund(self, razorpay_payment_id: str, amount: float) -> Dict:
        """Create a refund for a Razorpay payment"""
        try:
            # Convert amount to paise (Razorpay uses smallest currency unit)
            amount_paise = int(amount * 100)
            
            refund = self.client.payment.refund(razorpay_payment_id, {
                "amount": amount_paise
            })
            
            logger.info(f"Created refund {refund['id']} for payment {razorpay_payment_id}")
            return refund
            
        except Exception as e:
            logger.error(f"Error creating refund: {e}", exc_info=True)
            raise ValueError(f"Failed to create refund: {str(e)}")


# Global payment service instance
payment_service = PaymentService()

