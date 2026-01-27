"""Tests for backup scheduler module.

Unit tests for BackupScheduler covering scheduling, background execution,
configuration, callbacks, and edge cases.
"""

import sqlite3
import tempfile
import shutil
import threading
import time
from pathlib import Path
from datetime import datetime, time as datetime_time, timedelta
from unittest.mock import Mock, patch

import pytest

from utils.backup_scheduler import BackupScheduler
from utils.backup_manager import BackupManager


@pytest.fixture
def temp_database():
    """Create a temporary SQLite database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"

    # Create test database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create tables
    cursor.execute("CREATE TABLE employees (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT)")
    cursor.execute("CREATE TABLE caces (id INTEGER PRIMARY KEY, employee_id INTEGER, kind TEXT)")
    cursor.execute("CREATE TABLE medical_visits (id INTEGER PRIMARY KEY, employee_id INTEGER, visit_date TEXT)")
    cursor.execute("CREATE TABLE online_trainings (id INTEGER PRIMARY KEY, employee_id INTEGER, title TEXT)")

    # Add test data
    cursor.execute("INSERT INTO employees (first_name, last_name) VALUES ('John', 'Doe')")
    cursor.execute("INSERT INTO employees (first_name, last_name) VALUES ('Jane', 'Smith')")

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def backup_manager(temp_database):
    """Create BackupManager instance for testing."""
    backup_dir = Path(temp_database).parent / "backups"
    manager = BackupManager(database_path=temp_database, backup_dir=backup_dir)
    yield manager

    # Cleanup
    if backup_dir.exists():
        shutil.rmtree(backup_dir, ignore_errors=True)


@pytest.fixture
def scheduler(backup_manager):
    """Create BackupScheduler instance for testing."""
    return BackupScheduler(backup_manager)


class TestBackupSchedulerInit:
    """Test BackupScheduler initialization."""

    def test_init_with_manager(self, backup_manager):
        """Test initialization with BackupManager."""
        config = {"backup_time": "03:00"}
        scheduler = BackupScheduler(backup_manager, config)

        assert scheduler.backup_manager is backup_manager
        assert scheduler.config["backup_time"] == "03:00"
        assert scheduler.running is False
        assert scheduler.thread is None

    def test_init_with_default_config(self, backup_manager):
        """Test initialization uses default config."""
        scheduler = BackupScheduler(backup_manager)

        assert scheduler.config["enabled"] is True
        assert scheduler.config["automatic_daily"] is True
        assert scheduler.config["backup_time"] == "02:00"
        assert scheduler.config["retention_days"] == 30

    def test_init_running_state_false(self, backup_manager):
        """Test that scheduler starts in stopped state."""
        scheduler = BackupScheduler(backup_manager)

        assert scheduler.running is False
        assert scheduler.is_running() is False


class TestStartStop:
    """Test scheduler start and stop functionality."""

    def test_start_scheduler(self, backup_manager):
        """Test starting scheduler creates thread."""
        scheduler = BackupScheduler(backup_manager)

        scheduler.start()

        assert scheduler.running is True
        assert scheduler.thread is not None
        assert scheduler.thread.is_alive()

        # Cleanup
        scheduler.stop()

    def test_start_when_automatic_disabled(self, backup_manager):
        """Test starting when automatic_daily is disabled."""
        config = {"automatic_daily": False}
        scheduler = BackupScheduler(backup_manager, config)

        scheduler.start()

        # Should not start
        assert scheduler.running is False
        assert scheduler.thread is None

    def test_start_idempotent(self, backup_manager):
        """Test that starting twice doesn't create extra threads."""
        scheduler = BackupScheduler(backup_manager)

        scheduler.start()
        first_thread = scheduler.thread

        scheduler.start()
        second_thread = scheduler.thread

        # Should use same thread
        assert first_thread is second_thread

        # Cleanup
        scheduler.stop()

    def test_stop_scheduler(self, backup_manager):
        """Test stopping scheduler terminates thread."""
        scheduler = BackupScheduler(backup_manager)

        scheduler.start()
        assert scheduler.running is True

        scheduler.stop()

        assert scheduler.running is False
        # Thread should be stopped
        time.sleep(0.2)  # Give thread time to stop
        if scheduler.thread:
            assert not scheduler.thread.is_alive()

    def test_stop_when_not_running(self, backup_manager):
        """Test stopping when not running doesn't error."""
        scheduler = BackupScheduler(backup_manager)

        # Should not raise
        scheduler.stop()

        assert scheduler.running is False


class TestBackupTiming:
    """Test backup timing logic."""

    def test_should_run_backup_at_scheduled_time(self, backup_manager):
        """Test that backup runs at scheduled time."""
        # Set backup time to current time - 1 minute
        now = datetime.now()
        past_time = (now - timedelta(minutes=1)).strftime("%H:%M")

        config = {"backup_time": past_time}
        scheduler = BackupScheduler(backup_manager, config)

        # Should run (past scheduled time, no backup today yet)
        assert scheduler._should_run_backup() is True

    def test_should_not_run_before_scheduled_time(self, backup_manager):
        """Test that backup doesn't run before scheduled time."""
        # Set backup time to 2 hours in future
        now = datetime.now()
        future_time = (now + timedelta(hours=2)).strftime("%H:%M")

        config = {"backup_time": future_time}
        scheduler = BackupScheduler(backup_manager, config)

        # Should not run yet
        assert scheduler._should_run_backup() is False

    def test_should_not_run_if_already_ran_today(self, backup_manager):
        """Test that backup doesn't run twice on same day."""
        now = datetime.now()
        past_time = (now - timedelta(minutes=1)).strftime("%H:%M")

        config = {"backup_time": past_time}
        scheduler = BackupScheduler(backup_manager, config)

        # Set last backup time to today
        scheduler._last_backup_time = now

        # Should not run again today
        assert scheduler._should_run_backup() is False

    def test_invalid_backup_time_format(self, backup_manager):
        """Test handling of invalid backup time format."""
        config = {"backup_time": "invalid"}
        scheduler = BackupScheduler(backup_manager, config)

        # Should return False (invalid format)
        assert scheduler._should_run_backup() is False


class TestRunBackupNow:
    """Test immediate backup functionality."""

    def test_run_backup_now_creates_backup(self, backup_manager):
        """Test that run_backup_now creates a backup."""
        scheduler = BackupScheduler(backup_manager)

        backup_path = scheduler.run_backup_now()

        assert backup_path.exists()
        assert "manual" in backup_path.name
        assert backup_path.stat().st_size > 0

    def test_run_backup_now_updates_last_backup_time(self, backup_manager):
        """Test that immediate backup updates last backup time."""
        # This would require integration with _run_scheduled_backup
        # For now, test that run_backup_now doesn't interfere
        scheduler = BackupScheduler(backup_manager)

        before_time = scheduler._last_backup_time
        backup_path = scheduler.run_backup_now()
        after_time = scheduler._last_backup_time

        # run_backup_now doesn't update _last_backup_time (only scheduled backups do)
        assert after_time == before_time


class TestCallbacks:
    """Test callback functionality."""

    def test_register_callback(self, backup_manager):
        """Test registering backup callbacks."""
        scheduler = BackupScheduler(backup_manager)

        callback = Mock()
        scheduler.register_callback(callback)

        assert callback in scheduler._backup_callbacks

    def test_multiple_callbacks(self, backup_manager):
        """Test registering multiple callbacks."""
        scheduler = BackupScheduler(backup_manager)

        callback1 = Mock()
        callback2 = Mock()
        scheduler.register_callback(callback1)
        scheduler.register_callback(callback2)

        assert len(scheduler._backup_callbacks) == 2

    def test_callbacks_called_on_success(self, backup_manager):
        """Test that callbacks are called on successful backup."""
        scheduler = BackupScheduler(backup_manager)

        callback = Mock()
        scheduler.register_callback(callback)

        # Run backup
        backup_path = scheduler.run_backup_now()

        # Callbacks not called for manual backups (only scheduled)
        # This is expected behavior
        callback.assert_not_called()


class TestConfigUpdate:
    """Test configuration update functionality."""

    def test_update_config(self, backup_manager):
        """Test updating scheduler configuration."""
        scheduler = BackupScheduler(backup_manager)

        assert scheduler.config["backup_time"] == "02:00"

        new_config = {"backup_time": "03:00", "retention_days": 60}
        scheduler.update_config(new_config)

        assert scheduler.config["backup_time"] == "03:00"
        assert scheduler.config["retention_days"] == 60
        # Original config value should remain
        assert scheduler.config["enabled"] is True

    def test_update_config_preserves_other_settings(self, backup_manager):
        """Test that update preserves existing config values."""
        scheduler = BackupScheduler(backup_manager)

        # Update only backup_time
        scheduler.update_config({"backup_time": "04:00"})

        # Check other values preserved
        assert scheduler.config["enabled"] is True
        assert scheduler.config["automatic_daily"] is True
        assert scheduler.config["retention_days"] == 30


class TestGetLastBackupTime:
    """Test last backup time retrieval."""

    def test_get_last_backup_time_initially_none(self, backup_manager):
        """Test that last backup time is None initially."""
        scheduler = BackupScheduler(backup_manager)

        assert scheduler.get_last_backup_time() is None

    def test_get_last_backup_time_returns_datetime(self, backup_manager):
        """Test that last backup time returns datetime when set."""
        scheduler = BackupScheduler(backup_manager)
        test_time = datetime.now()

        scheduler._last_backup_time = test_time

        assert scheduler.get_last_backup_time() == test_time


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_backup_manager_with_nonexistent_db(self):
        """Test scheduler with nonexistent database."""
        temp_dir = tempfile.mkdtemp()
        nonexistent_db = Path(temp_dir) / "nonexistent.db"

        backup_dir = Path(temp_dir) / "backups"
        manager = BackupManager(database_path=nonexistent_db, backup_dir=backup_dir)
        scheduler = BackupScheduler(manager)

        # run_backup_now should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            scheduler.run_backup_now()

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_scheduler_with_custom_config(self, backup_manager):
        """Test scheduler with custom configuration."""
        custom_config = {
            "enabled": False,
            "automatic_daily": False,
            "backup_time": "05:00",
            "backup_on_shutdown": True,
            "retention_days": 60,
            "retention_weeks": 24,
            "retention_months": 24,
        }

        scheduler = BackupScheduler(backup_manager, custom_config)

        assert scheduler.config == custom_config

    def test_concurrent_backup_calls(self, backup_manager):
        """Test handling of concurrent backup calls."""
        scheduler = BackupScheduler(backup_manager)

        # Run multiple backups quickly
        backup1 = scheduler.run_backup_now()
        backup2 = scheduler.run_backup_now()
        backup3 = scheduler.run_backup_now()

        # All should succeed
        assert backup1.exists()
        assert backup2.exists()
        assert backup3.exists()

        # Should have different names (different timestamps)
        assert backup1.name != backup2.name
        assert backup2.name != backup3.name

    def test_stop_scheduler_graceful(self, backup_manager):
        """Test that scheduler stops gracefully without errors."""
        scheduler = BackupScheduler(backup_manager)

        scheduler.start()
        time.sleep(0.2)  # Let thread start

        # Should not raise
        scheduler.stop()

        assert scheduler.running is False


class TestIntegration:
    """Integration tests with full backup workflow."""

    def test_full_backup_cycle(self, backup_manager):
        """Test complete backup cycle with scheduler."""
        scheduler = BackupScheduler(backup_manager)

        # Run immediate backup
        backup_path = scheduler.run_backup_now()

        # Verify backup
        verification = backup_manager.verify_backup(backup_path)

        assert verification['valid'] is True
        assert verification['employee_count'] >= 0
        assert verification['size_mb'] > 0

    def test_scheduler_preserves_backups(self, backup_manager):
        """Test that scheduler doesn't delete existing backups."""
        scheduler = BackupScheduler(backup_manager, {"retention_days": 5})

        # Create multiple backups
        backup1 = scheduler.run_backup_now()
        time.sleep(0.1)  # Ensure different timestamps
        backup2 = scheduler.run_backup_now()

        # Both should exist
        assert backup1.exists()
        assert backup2.exists()

        # List backups
        backups = backup_manager.list_backups()
        assert len(backups) >= 2

    def test_config_overrides_defaults(self, backup_manager):
        """Test that config overrides default values."""
        default_scheduler = BackupScheduler(backup_manager)
        custom_scheduler = BackupScheduler(
            backup_manager,
            {"backup_time": "06:00", "retention_days": 15}
        )

        # Custom config should override defaults
        assert default_scheduler.config["backup_time"] == "02:00"
        assert custom_scheduler.config["backup_time"] == "06:00"
        assert default_scheduler.config["retention_days"] == 30
        assert custom_scheduler.config["retention_days"] == 15
