"""Backup Scheduler Module

Provides automated backup scheduling with configurable times:
- Daily automatic backups
- Background thread execution
- Configurable backup time
- Logging and error handling
"""

import logging
import threading
import time
from datetime import datetime, time as datetime_time
from pathlib import Path
from typing import Optional, Callable

from utils.backup_manager import BackupManager

logger = logging.getLogger(__name__)


class BackupScheduler:
    """
    Manages automated backup scheduling.

    Runs backups in a background thread at configurable times.
    Supports daily automatic backups with logging and error handling.

    Attributes:
        backup_manager: BackupManager instance
        config: Scheduler configuration dictionary
        running: Whether scheduler is running
        thread: Background scheduler thread
    """

    def __init__(self, backup_manager: BackupManager, config: Optional[dict] = None):
        """
        Initialize backup scheduler.

        Args:
            backup_manager: BackupManager instance for creating backups
            config: Configuration dictionary (defaults if None)
        """
        self.backup_manager = backup_manager
        self.config = config or self._default_config()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_backup_time: Optional[datetime] = None
        self._backup_callbacks: list[Callable] = []

    def _default_config(self) -> dict:
        """Get default configuration."""
        return {
            "enabled": True,
            "automatic_daily": True,
            "backup_time": "02:00",  # 2:00 AM
            "backup_on_shutdown": False,
            "retention_days": 30,
            "retention_weeks": 12,
            "retention_months": 12,
        }

    def start(self):
        """
        Start the backup scheduler.

        Creates background thread that checks for scheduled backups.
        Only starts if automatic_daily is enabled in config.
        """
        if not self.config.get("automatic_daily", True):
            logger.info("Automatic daily backups disabled in config")
            return

        if self.running:
            logger.warning("Backup scheduler already running")
            return

        self._stop_event.clear()
        self.running = True

        # Start background thread
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()

        logger.info(f"Backup scheduler started (daily backup at {self.config['backup_time']})")

    def stop(self):
        """
        Stop the backup scheduler.

        Signals background thread to stop and waits for it to terminate.
        """
        if not self.running:
            return

        logger.info("Stopping backup scheduler...")
        self.running = False
        self._stop_event.set()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)

        logger.info("Backup scheduler stopped")

    def _run_scheduler(self):
        """Background thread that runs scheduled backups."""
        logger.info("Backup scheduler thread started")

        while self.running:
            try:
                # Check if it's time to run backup
                if self._should_run_backup():
                    self._run_scheduled_backup()

                # Sleep for 1 minute before next check
                if self._stop_event.wait(timeout=60):
                    break

            except Exception as e:
                logger.error(f"Error in backup scheduler: {e}")
                # Sleep for 1 minute before retry
                if self._stop_event.wait(timeout=60):
                    break

        logger.info("Backup scheduler thread stopped")

    def _should_run_backup(self) -> bool:
        """
        Check if it's time to run a backup.

        Returns:
            True if scheduled time has been reached since last backup
        """
        backup_time_str = self.config.get("backup_time", "02:00")
        try:
            hour, minute = map(int, backup_time_str.split(":"))
            backup_time = datetime_time(hour, minute)
        except (ValueError, AttributeError) as e:
            logger.error(f"Invalid backup_time format: {backup_time_str}, {e}")
            return False

        now = datetime.now()
        current_time = now.time()

        # Check if we've passed the backup time today
        if current_time >= backup_time:
            # Check if we already ran backup today
            if self._last_backup_time is None:
                return True
            elif self._last_backup_time.date() < now.date():
                return True

        return False

    def _run_scheduled_backup(self):
        """Run a scheduled backup with logging and callbacks."""
        logger.info("Starting scheduled automatic backup")
        start_time = time.time()

        try:
            # Create backup
            backup_path = self.backup_manager.create_backup(
                description="automatic"
            )

            # Verify backup
            verification = self.backup_manager.verify_backup(backup_path)

            duration = time.time() - start_time

            if verification['valid']:
                self._last_backup_time = datetime.now()
                logger.info(
                    f"Scheduled backup completed: {backup_path.name} "
                    f"({verification['size_mb']} MB, {duration:.2f}s, "
                    f"{verification['employee_count']} employees)"
                )

                # Call success callbacks
                for callback in self._backup_callbacks:
                    try:
                        callback("success", backup_path, verification)
                    except Exception as e:
                        logger.error(f"Backup callback error: {e}")
            else:
                logger.error(f"Scheduled backup verification failed: {verification.get('error')}")
                # Call failure callbacks
                for callback in self._backup_callbacks:
                    try:
                        callback("failed", backup_path, verification)
                    except Exception as e:
                        logger.error(f"Backup callback error: {e}")

        except Exception as e:
            logger.error(f"Scheduled backup failed: {e}")
            # Call failure callbacks
            for callback in self._backup_callbacks:
                try:
                    callback("error", None, {"error": str(e)})
                except Exception as cb_error:
                    logger.error(f"Backup callback error: {cb_error}")

    def register_callback(self, callback: Callable):
        """
        Register a callback function to be called on backup events.

        Args:
            callback: Function with signature (status, backup_path, info)
                     - status: "success", "failed", or "error"
                     - backup_path: Path object or None
                     - info: dict with backup info
        """
        self._backup_callbacks.append(callback)

    def run_backup_now(self) -> Path:
        """
        Run an immediate backup (manual trigger).

        Returns:
            Path to created backup file

        Raises:
            IOError: If backup creation fails
        """
        logger.info("Running immediate manual backup")
        return self.backup_manager.create_backup(description="manual")

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self.running

    def get_last_backup_time(self) -> Optional[datetime]:
        """Get timestamp of last successful backup."""
        return self._last_backup_time

    def update_config(self, new_config: dict):
        """
        Update scheduler configuration.

        Args:
            new_config: New configuration dictionary
        """
        self.config.update(new_config)
        logger.info(f"Backup scheduler config updated: {new_config}")
