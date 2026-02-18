"""Order service for managing orders"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from datetime import datetime, date
from config import logger
from models.order import Order
from models.payment import Payment
from models.user import User


def serialize_datetime(obj: Any) -> Any:
    """Recursively convert datetime, date, and other non-serializable objects to JSON-compatible formats"""
    import json
    
    # Handle None
    if obj is None:
        return None
    
    # Handle datetime and date objects
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    # Handle basic JSON-serializable types
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    # Handle dict - recursively process values
    elif isinstance(obj, dict):
        return {k: serialize_datetime(v) for k, v in obj.items()}
    # Handle list - recursively process items
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    # Handle tuple - recursively process items
    elif isinstance(obj, tuple):
        return tuple(serialize_datetime(item) for item in obj)
    # Handle set - convert to list
    elif isinstance(obj, set):
        return [serialize_datetime(item) for item in obj]
    # Handle custom objects (like Ayanamsa) - try to convert to string or extract value
    else:
        # First, try to serialize with json.dumps to catch any remaining issues
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # If it can't be serialized, try various conversion methods
            try:
                # If object has a value attribute, use it
                if hasattr(obj, 'value'):
                    return serialize_datetime(obj.value)
                # If object has a __str__ method, use it
                elif hasattr(obj, '__str__'):
                    str_repr = str(obj)
                    # If string representation looks like a number, try to convert
                    try:
                        if '.' in str_repr:
                            return float(str_repr)
                        else:
                            return int(str_repr)
                    except (ValueError, TypeError):
                        return str_repr
                # Otherwise, try to serialize the object's dict
                elif hasattr(obj, '__dict__'):
                    return serialize_datetime(obj.__dict__)
                else:
                    return str(obj)
            except Exception as e:
                logger.warning(f"Error serializing object {type(obj)}: {e}, converting to string")
                return str(obj)


class OrderService:
    """Service for managing orders"""
    
    @staticmethod
    def create_order(
        db: Session,
        user_id: int,
        amount: float,
        birth_details: Optional[Dict] = None,
        order_type: str = "full_report"
    ) -> Order:
        """Create a new order with payment_pending status"""
        try:
            order = Order(
                user_id=user_id,
                status="payment_pending",
                type=order_type,
                amount=amount,
                birth_details=birth_details
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            logger.info(f"Created order {order.id} for user {user_id} (type: {order_type})")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating order: {e}", exc_info=True)
            raise
    
    @staticmethod
    def get_order(db: Session, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
        """Get order by ID, optionally filtered by user_id"""
        try:
            stmt = select(Order).where(Order.id == order_id)
            if user_id:
                stmt = stmt.where(Order.user_id == user_id)
            
            result = db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting order: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_order_status(
        db: Session,
        order_id: int,
        status: str,
        error_reason: Optional[str] = None,
        analysis_data: Optional[Dict] = None
    ) -> Optional[Order]:
        """Update order status"""
        try:
            order = OrderService.get_order(db, order_id)
            if not order:
                return None
            
            order.status = status
            if error_reason:
                order.error_reason = error_reason
            if analysis_data:
                # Serialize datetime objects to strings for JSON compatibility
                order.analysis_data = serialize_datetime(analysis_data)
            
            db.commit()
            db.refresh(order)
            logger.info(f"Updated order {order_id} status to {status}")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating order status: {e}", exc_info=True)
            return None
    
    @staticmethod
    def get_user_orders(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Order]:
        """Get orders for a user"""
        try:
            stmt = (
                select(Order)
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting user orders: {e}", exc_info=True)
            return []
    
    @staticmethod
    def get_all_orders(
        db: Session,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Order], int]:
        """Get all orders with filters and pagination"""
        try:
            # Build query
            conditions = []
            if status:
                conditions.append(Order.status == status)
            if user_id:
                conditions.append(Order.user_id == user_id)
            if start_date:
                conditions.append(Order.created_at >= start_date)
            if end_date:
                conditions.append(Order.created_at <= end_date)
            
            # Count total
            count_stmt = select(func.count(Order.id))
            if conditions:
                count_stmt = count_stmt.where(and_(*conditions))
            count_result = db.execute(count_stmt)
            total = count_result.scalar() or 0
            
            # Get orders
            stmt = (
                select(Order)
                .options(joinedload(Order.user))
                .options(joinedload(Order.payment))
            )
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            stmt = stmt.order_by(Order.created_at.desc()).limit(limit).offset(offset)
            result = db.execute(stmt)
            orders = list(result.scalars().all())
            
            return orders, total
        except Exception as e:
            logger.error(f"Error getting all orders: {e}", exc_info=True)
            return [], 0
    
    @staticmethod
    def process_order(db: Session, order_id: int) -> Optional[Order]:
        """Mark order as processing (called after payment success)"""
        return OrderService.update_order_status(db, order_id, "processing")
    
    @staticmethod
    def complete_order(
        db: Session,
        order_id: int,
        analysis_data: Dict
    ) -> Optional[Order]:
        """Mark order as completed with analysis data"""
        return OrderService.update_order_status(
            db, order_id, "completed", analysis_data=analysis_data
        )
    
    @staticmethod
    def fail_order(
        db: Session,
        order_id: int,
        error_reason: str
    ) -> Optional[Order]:
        """Mark order as failed with error reason"""
        return OrderService.update_order_status(
            db, order_id, "failed", error_reason=error_reason
        )
    
    @staticmethod
    def reset_order_for_retry(db: Session, order_id: int) -> Optional[Order]:
        """Reset order to processing status and clear error_reason for retry"""
        try:
            order = OrderService.get_order(db, order_id)
            if not order:
                return None
            
            order.status = "processing"
            order.error_reason = None
            order.analysis_data = None  # Clear previous analysis data
            
            db.commit()
            db.refresh(order)
            logger.info(f"Reset order {order_id} for retry")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error resetting order for retry: {e}", exc_info=True)
            return None
    
    @staticmethod
    def get_stale_processing_orders(db: Session, minutes_threshold: int = 30) -> List[Order]:
        """Get orders in processing status that are older than the threshold"""
        try:
            from datetime import timedelta
            
            threshold_time = datetime.utcnow() - timedelta(minutes=minutes_threshold)
            
            stmt = (
                select(Order)
                .where(Order.status == "processing")
                .where(Order.created_at < threshold_time)
            )
            
            result = db.execute(stmt)
            orders = list(result.scalars().all())
            
            return orders
        except Exception as e:
            logger.error(f"Error getting stale processing orders: {e}", exc_info=True)
            return []
    
    @staticmethod
    def get_order_chat_messages(db: Session, order_id: int) -> List:
        """Get all chat messages for an order"""
        try:
            from models.chat_message import ChatMessage
            
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.order_id == order_id)
                .order_by(ChatMessage.message_number.asc(), ChatMessage.created_at.asc())
            )
            result = db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting chat messages: {e}", exc_info=True)
            return []
    
    @staticmethod
    def get_message_count(db: Session, order_id: int) -> int:
        """Get the count of messages for an order"""
        try:
            from models.chat_message import ChatMessage
            
            stmt = select(func.count(ChatMessage.id)).where(ChatMessage.order_id == order_id)
            result = db.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error getting message count: {e}", exc_info=True)
            return 0


# Global order service instance
order_service = OrderService()
