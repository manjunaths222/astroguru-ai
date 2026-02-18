"""Chat service for managing chat messages"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from config import logger
from models.chat_message import ChatMessage
from models.order import Order


class ChatService:
    """Service for managing chat messages"""
    
    @staticmethod
    def save_chat_message(
        db: Session,
        order_id: int,
        role: str,
        content: str,
        message_number: int
    ) -> Optional[ChatMessage]:
        """Save a chat message to the database"""
        try:
            message = ChatMessage(
                order_id=order_id,
                message_number=message_number,
                role=role,
                content=content
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            logger.info(f"Saved chat message {message.id} for order {order_id} (message_number: {message_number})")
            return message
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving chat message: {e}", exc_info=True)
            return None
    
    @staticmethod
    def can_send_message(db: Session, order_id: int, max_user_messages: int = 3) -> bool:
        """Check if user can send more messages (max 3 user messages total)"""
        try:
            # Count only user messages
            stmt = select(func.count(ChatMessage.id)).where(
                ChatMessage.order_id == order_id,
                ChatMessage.role == "user"
            )
            result = db.execute(stmt)
            user_message_count = result.scalar() or 0
            
            can_send = user_message_count < max_user_messages
            logger.debug(f"Order {order_id}: {user_message_count}/{max_user_messages} user messages, can_send: {can_send}")
            return can_send
        except Exception as e:
            logger.error(f"Error checking message limit: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_user_message_count(db: Session, order_id: int) -> int:
        """Get count of user messages for an order"""
        try:
            stmt = select(func.count(ChatMessage.id)).where(
                ChatMessage.order_id == order_id,
                ChatMessage.role == "user"
            )
            result = db.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error getting user message count: {e}", exc_info=True)
            return 0
    
    @staticmethod
    def get_chat_history(db: Session, order_id: int) -> list:
        """Get all chat messages for an order, ordered by message_number and created_at"""
        try:
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.order_id == order_id)
                .order_by(ChatMessage.message_number.asc(), ChatMessage.created_at.asc())
            )
            result = db.execute(stmt)
            messages = list(result.scalars().all())
            logger.debug(f"Retrieved {len(messages)} chat messages for order {order_id}")
            return messages
        except Exception as e:
            logger.error(f"Error getting chat history: {e}", exc_info=True)
            return []
    
    @staticmethod
    def get_next_message_number(db: Session, order_id: int) -> int:
        """Get the next message number for an order"""
        try:
            stmt = select(func.max(ChatMessage.message_number)).where(ChatMessage.order_id == order_id)
            result = db.execute(stmt)
            max_number = result.scalar()
            return (max_number or 0) + 1
        except Exception as e:
            logger.error(f"Error getting next message number: {e}", exc_info=True)
            return 1


# Global chat service instance
chat_service = ChatService()

