"""Database connection and session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from config import AstroConfig, logger

# Create base class for models
Base = declarative_base()

# Global engine and session maker
engine = None
SessionLocal = None


def init_database():
    """Initialize database connection"""
    global engine, SessionLocal
    
    database_url = AstroConfig.DatabaseConfig.DATABASE_URL
    # Convert async URL to sync URL if needed (for backward compatibility)
    if "postgresql+asyncpg://" in database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        logger.warning("Converted asyncpg URL to synchronous postgresql URL")
    
    logger.info(f"Initializing database connection: {database_url.split('@')[1] if '@' in database_url else 'configured'}")
    
    engine = create_engine(
        database_url,
        echo=AstroConfig.AppSettings.DEBUG,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20
    )
    
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    logger.info("Database connection initialized successfully")


def close_database():
    """Close database connection"""
    global engine
    if engine:
        engine.dispose()
        logger.info("Database connection closed")


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
