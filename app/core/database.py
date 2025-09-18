"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Convert to async URL for asyncpg
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Sync engine for migrations and data loading
engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("DATABASE_POOL_SIZE", "3")),
    max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "5")),
    pool_pre_ping=True,  # Verify connections before using
    echo=os.getenv("DEBUG", "False").lower() == "true"  # SQL logging in debug mode
)

# Async engine for API operations
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=int(os.getenv("DATABASE_POOL_SIZE", "3")),
    max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "5")),
    pool_pre_ping=True,
    echo=os.getenv("DEBUG", "False").lower() == "true"
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


def get_db() -> Session:
    """
    Dependency to get database session for sync operations
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """
    Dependency to get database session for async operations
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database (create tables if they don't exist)
    """
    from app.models.database import Base
    
    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully")


async def close_db():
    """
    Close database connections
    """
    await async_engine.dispose()
    print("Database connections closed")