
# ===========================================
# utils/scheduler.py
# ===========================================
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database.operations import TokenOperations, TokenGeneratorCountOperations
from datetime import datetime

scheduler = AsyncIOScheduler()

async def cleanup_expired_tokens():
    """Delete expired tokens (runs daily)"""
    deleted = await TokenOperations.delete_expired_tokens()
    print(f"🗑️  Cleaned up {deleted} expired tokens at {datetime.now()}")

async def reset_token_generator_count():
    """Reset token generator count (runs at midnight)"""
    deleted = await TokenGeneratorCountOperations.clear_old_counts()
    print(f"🔄 Reset token generator count, removed {deleted} old records at {datetime.now()}")

def start_scheduler():
    """Start the background scheduler"""
    # Cleanup expired tokens daily at 3 AM
    scheduler.add_job(
        cleanup_expired_tokens,
        CronTrigger(hour=3, minute=0),
        id="cleanup_tokens",
        replace_existing=True
    )
    
    # Reset token generator count at midnight
    scheduler.add_job(
        reset_token_generator_count,
        CronTrigger(hour=0, minute=0),
        id="reset_token_count",
        replace_existing=True
    )
    
    scheduler.start()
    print("⏰ Scheduler started")

def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("⏰ Scheduler stopped")