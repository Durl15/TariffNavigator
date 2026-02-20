"""
Background job scheduler using APScheduler.
Manages periodic tasks like tariff change monitoring.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure job storage (persists to database)
# Note: APScheduler's SQLAlchemyJobStore requires synchronous DB URL
# Convert async URL to sync for job store
scheduler_db_url = str(settings.DATABASE_URL).replace('sqlite+aiosqlite', 'sqlite')
jobstores = {
    'default': SQLAlchemyJobStore(url=scheduler_db_url)
}

# Configure executors for async jobs
executors = {
    'default': AsyncIOExecutor()
}

# Create scheduler instance
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults={
        'coalesce': False,  # Run all missed executions
        'max_instances': 1,  # Only one instance of each job at a time
        'misfire_grace_time': 300  # 5 minutes grace period for misfires
    }
)


def register_jobs():
    """
    Register all scheduled jobs.
    Called during application startup.
    """
    # Import here to avoid circular dependencies
    from app.services.change_monitor import check_tariff_changes

    # Register tariff change monitoring job (runs every hour)
    scheduler.add_job(
        check_tariff_changes,
        'interval',
        hours=1,
        id='tariff_monitor',
        name='Monitor Tariff Changes',
        replace_existing=True,
        next_run_time=None  # Don't run immediately on startup
    )

    logger.info("Registered scheduled jobs: tariff_monitor (hourly)")


def start_scheduler():
    """Start the scheduler. Called during application startup."""
    if not scheduler.running:
        register_jobs()
        scheduler.start()
        logger.info("APScheduler started successfully")
    else:
        logger.warning("Scheduler is already running")


def shutdown_scheduler():
    """Shutdown the scheduler. Called during application shutdown."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("APScheduler shut down successfully")
