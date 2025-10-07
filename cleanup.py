import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from config import settings
from models import Base, OTP

# Set up logging with explicit handler control
logger = logging.getLogger(__name__)
# Remove any existing handlers to prevent duplicates
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
# Remove root logger handlers
for handler in logging.getLogger().handlers[:]:
    logging.getLogger().removeHandler(handler)

# Add single stream handler
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def wait_for_db(max_retries=5, retry_interval=5):
    """Wait for database to be available."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            db = SessionLocal()
            try:
                db.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                return True
            finally:
                db.close()
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"Database connection attempt {retry_count} failed: {e}")
                logger.info(f"Retrying in {retry_interval} seconds...")
                asyncio.sleep(retry_interval)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts: {e}")
                return False
    return False

def cleanup_expired_otps():
    """Delete expired OTPs from the database."""
    try:
        db = SessionLocal()
        try:
            # Use timezone-aware UTC for comparison to match models
            now = datetime.now(timezone.utc)
            logger.debug(f"Running cleanup check at {now}")
            
            result = db.query(OTP).filter(
                OTP.expires_at < now
            ).delete()
            db.commit()
            
            # Always log the check, even if no deletions
            if result > 0:
                logger.info(f"Deleted {result} expired OTPs")
            else:
                logger.debug("No expired OTPs found to delete")
                
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error cleaning up expired OTPs: {e}")

async def run_cleanup_loop():
    """Run the cleanup task periodically."""
    logger.info(f"Starting cleanup loop with interval: {settings.CLEANUP_INTERVAL_SECONDS} seconds")
    
    while True:
        logger.debug("Running cleanup cycle...")
        cleanup_expired_otps()
        logger.debug(f"Sleeping for {settings.CLEANUP_INTERVAL_SECONDS} seconds...")
        await asyncio.sleep(settings.CLEANUP_INTERVAL_SECONDS)

def main():
    # Only show startup banner once
    logger.info("Starting OTP cleanup service...")
    logger.info(f"Database URL: {settings.database_url.replace(settings.POSTGRES_PASSWORD, '****')}")
    logger.info(f"Cleanup interval: {settings.CLEANUP_INTERVAL_SECONDS} seconds")
    
    # Wait for database with retries
    if not wait_for_db():
        logger.error("Failed to connect to database after retries. Exiting.")
        return
        
    try:
        # Run the cleanup loop
        asyncio.run(run_cleanup_loop())
    except KeyboardInterrupt:
        logger.info("Shutting down OTP cleanup service...")
    except Exception as e:
        logger.error(f"Error in cleanup service: {e}")
        raise

if __name__ == "__main__":
    main()
