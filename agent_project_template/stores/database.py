"""
Database Core

Global SQLAlchemy engine, session, and base for PostgreSQL access.
"""
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import QueuePool
from ai_agents.core.config import settings
from ai_agents.core.exceptions import DatabaseException
from ai_agents.core.error_codes import DatabaseErrorCode
from contextlib import contextmanager
from typing import Generator
from ai_agents.utils.logger import get_logger
import time
import threading

logger = get_logger(__name__)

# Global SQLAlchemy base
Base = declarative_base()

# Enhanced engine configuration with core connection pool settings
engine = create_engine(
    settings.database__url,
    echo=settings.database__echo,
    future=True,
    pool_pre_ping=settings.database__pool_pre_ping,
    pool_size=settings.database__pool_size,
    max_overflow=settings.database__max_overflow,
    pool_timeout=settings.database__pool_timeout,
    pool_recycle=settings.database__pool_recycle,
    pool_reset_on_return=settings.database__pool_reset_on_return,
    poolclass=QueuePool,
    connect_args={
        "connect_timeout": settings.database__connect_timeout,
        "application_name": "ai_agents_app"
    }
)

SessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, future=True)

# Connection pool monitoring
_pool_stats_lock = threading.Lock()
_last_pool_log_time = 0


def log_pool_status():
    """Log connection pool status for monitoring"""
    global _last_pool_log_time
    current_time = time.time()

    # Log pool status every 30 seconds at most
    with _pool_stats_lock:
        if current_time - _last_pool_log_time < 30:
            return
        _last_pool_log_time = current_time

    pool = engine.pool
    logger.info(
        "Connection Pool Status - Size: %d, Checked out: %d, Overflow: %d",
        pool.size(),
        pool.checkedout(),
        pool.overflow()
    )

# Add pool event listeners for monitoring


@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Log new connections"""
    logger.debug("New database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout and monitor pool status"""
    log_pool_status()


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin"""
    logger.debug("Database connection returned to pool")


def get_db() -> Generator:
    """
    FastAPI dependency for database session.
    Yields a SQLAlchemy session and ensures proper close.
    Enhanced with better error handling and connection management.
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error("Database session error: %s", str(e))
        # Ensure rollback on any exception
        try:
            db.rollback()
        except Exception as rollback_error:
            logger.error("Failed to rollback session: %s", str(rollback_error))
        raise
    finally:
        try:
            db.close()
            logger.debug("Database session closed")
        except Exception as close_error:
            logger.error("Failed to close database session: %s",
                         str(close_error))


@contextmanager
def transaction_manager(db_session):
    """
    Enhanced transaction context manager for database operations.

    Provides atomic transaction support with automatic rollback on exceptions.
    Enhanced with better error handling and session state management.

    Args:
        db_session: SQLAlchemy database session

    Yields:
        Session: The database session within transaction context

    Raises:
        DatabaseException: If transaction operations fail
        DatabaseException: If session management fails

    Example:
        with transaction_manager(db) as tx:
            # Perform multiple database operations
            crud.create_without_commit(data1)
            crud.update_without_commit(data2)
            # Transaction commits automatically on successful exit
    """
    if db_session is None:
        raise DatabaseException(DatabaseErrorCode.DATABASE_SESSION_ERROR, "Database session is None")

    logger.debug("Starting database transaction")

    # Check if session is still valid
    try:
        db_session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Session validation failed: %s", str(e))
        raise DatabaseException(DatabaseErrorCode.DATABASE_SESSION_ERROR, f"Invalid database session: {e}") from e

    try:
        # Begin transaction (SQLAlchemy session is already in transaction mode by default)
        yield db_session

        # Commit transaction if no exceptions occurred
        db_session.commit()
        logger.debug("Transaction committed successfully")

    except Exception as e:
        logger.error("Transaction failed, rolling back: %s", str(e))
        try:
            db_session.rollback()
            logger.debug("Transaction rolled back successfully")
        except Exception as rollback_error:
            logger.error("Transaction rollback failed: %s",
                         str(rollback_error))
            # Mark session as invalid to prevent further use
            try:
                db_session.close()
            except:
                pass
            raise DatabaseException(
                DatabaseErrorCode.DATABASE_TRANSACTION_ROLLBACK_ERROR,
                f"Failed to rollback transaction: {rollback_error}") from rollback_error

        # Re-raise the original exception
        raise DatabaseException(DatabaseErrorCode.DATABASE_TRANSACTION_ERROR, f"Transaction failed: {e}") from e


@contextmanager
def get_db_session():
    """
    Context manager for creating and managing database sessions.

    Provides automatic session creation, error handling, and cleanup.
    Use this for operations that need their own session lifecycle.

    Yields:
        Session: SQLAlchemy database session

    Raises:
        DatabaseException: If session creation or management fails

    Example:
        with get_db_session() as db:
            # Use db session for operations
            result = db.query(Model).all()
    """
    db_session = None
    try:
        db_session = SessionLocal()
        logger.debug("New database session created")
        yield db_session
    except Exception as e:
        logger.error("Database session error: %s", str(e))
        if db_session:
            try:
                db_session.rollback()
            except Exception as rollback_error:
                logger.error("Failed to rollback session: %s",
                             str(rollback_error))
        raise DatabaseException(DatabaseErrorCode.DATABASE_SESSION_ERROR, f"Database session failed: {e}") from e
    finally:
        if db_session:
            try:
                db_session.close()
                logger.debug("Database session closed")
            except Exception as close_error:
                logger.error(
                    "Failed to close database session: %s", str(close_error))


# Optional: test connection utility for startup
def test_connection():
    """Test database connection and log pool status"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log_pool_status()
        logger.info("Database connection test successful")
    except OperationalError as e:
        logger.error("Database connection test failed: %s", str(e))
        raise DatabaseException(DatabaseErrorCode.DATABASE_CONNECTION_FAILED, f"Database connection failed: {e}")


def get_pool_status() -> dict:
    """
    Get current connection pool status for monitoring.

    Returns:
        dict: Pool status information
    """
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "pool_size_limit": engine.pool._pool.maxsize if hasattr(engine.pool, '_pool') else 'unknown',
        "max_overflow": engine.pool._max_overflow if hasattr(engine.pool, '_max_overflow') else 'unknown'
    }
