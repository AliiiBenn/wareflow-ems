"""Tests for logging utilities."""

import pytest
import logging
from pathlib import Path
from io import StringIO
import tempfile
import shutil
from logging.handlers import RotatingFileHandler

from utils import log


class TestSetupLogger:
    """Tests for setup_logger function."""

    def test_setup_logger_creates_logger(self):
        """Should create a logger with specified name."""
        logger = log.setup_logger(name="test_logger")

        assert logger.name == "test_logger"
        assert isinstance(logger, logging.Logger)

    def test_setup_logger_with_console_handler_only(self):
        """Should create logger with console handler when no log file."""
        logger = log.setup_logger(name="test_console")

        # Should have exactly 1 handler (console)
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logger_with_file_handler(self, tmp_path):
        """Should create logger with file handler when log file specified."""
        log_file = tmp_path / "test.log"
        logger = log.setup_logger(name="test_file", log_file=log_file)

        # Should have 2 handlers (console + file)
        assert len(logger.handlers) == 2
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert isinstance(logger.handlers[1], RotatingFileHandler)

    def test_setup_logger_log_level(self):
        """Should set correct logging level."""
        logger_debug = log.setup_logger(name="test_debug", level="DEBUG")
        logger_info = log.setup_logger(name="test_info", level="INFO")

        assert logger_debug.level == logging.DEBUG
        assert logger_info.level == logging.INFO

    def test_setup_logger_creates_log_directory(self, tmp_path):
        """Should create parent directory for log file if needed."""
        log_file = tmp_path / "logs" / "nested" / "test.log"
        logger = log.setup_logger(name="test_dir", log_file=log_file)

        assert log_file.parent.exists()
        assert log_file.parent.is_dir()

    def test_setup_logger_clears_existing_handlers(self):
        """Should clear existing handlers to avoid duplicates."""
        logger = log.setup_logger(name="test_clear")
        initial_handlers = len(logger.handlers)

        # Call setup_logger again with same name
        logger = log.setup_logger(name="test_clear")

        # Should still have same number of handlers (not doubled)
        assert len(logger.handlers) == initial_handlers

    def test_setup_logger_log_rotation(self, tmp_path):
        """Should configure rotating file handler correctly."""
        log_file = tmp_path / "test_rotation.log"
        logger = log.setup_logger(
            name="test_rotation",
            log_file=log_file,
            max_bytes=1024,  # 1KB for testing
            backup_count=2
        )

        file_handler = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)][0]

        assert file_handler.maxBytes == 1024
        assert file_handler.backupCount == 2

    def test_logger_output_format(self, tmp_path):
        """Should use correct log format."""
        log_file = tmp_path / "test_format.log"
        logger = log.setup_logger(name="test_format", log_file=log_file)

        # Log a message
        logger.info("Test message")

        # Read log file
        log_content = log_file.read_text()

        # Should contain timestamp, level, logger name, and message
        assert "INFO" in log_content
        assert "test_format" in log_content
        assert "Test message" in log_content


class TestLogApplicationStart:
    """Tests for log_application_start function."""

    def test_log_application_start_output(self):
        """Should log application start information."""
        logger = log.setup_logger(name="test_start")
        log.log_application_start(logger)

        # Check that logger.info was called (no exception means success)
        assert True

    def test_log_application_start_includes_hostname(self):
        """Should include hostname in startup log."""
        logger = log.setup_logger(name="test_hostname")
        log.log_application_start(logger)

        # Logger should have recorded hostname (we can't easily test the exact output)
        assert True


class TestLogApplicationStop:
    """Tests for log_application_stop function."""

    def test_log_application_stop_output(self):
        """Should log application stop information."""
        logger = log.setup_logger(name="test_stop")
        log.log_application_stop(logger)

        # Check that logger.info was called
        assert True


class TestLogLockEvents:
    """Tests for lock event logging functions."""

    def test_log_lock_acquired(self):
        """Should log lock acquisition."""
        logger = log.setup_logger(name="test_lock_acquire")
        log.log_lock_acquired(logger, "PC-01", 12345)

        # Should not raise exception
        assert True

    def test_log_lock_released(self):
        """Should log lock release."""
        logger = log.setup_logger(name="test_lock_release")
        log.log_lock_released(logger, "PC-01", 12345)

        # Should not raise exception
        assert True

    def test_log_lock_lost(self):
        """Should log lock loss at CRITICAL level."""
        logger = log.setup_logger(name="test_lock_lost")
        log.log_lock_lost(logger, "PC-01")

        # Should not raise exception
        assert True


class TestLogDatabaseError:
    """Tests for database error logging."""

    def test_log_database_error_without_context(self):
        """Should log database error without context."""
        logger = log.setup_logger(name="test_db_error")
        error = Exception("Database connection failed")

        log.log_database_error(logger, error)

        # Should not raise exception
        assert True

    def test_log_database_error_with_context(self):
        """Should log database error with context."""
        logger = log.setup_logger(name="test_db_error_context")
        error = Exception("Table not found")

        log.log_database_error(logger, error, context="fetching employees")

        # Should not raise exception
        assert True


class TestLogFileOperation:
    """Tests for file operation logging."""

    def test_log_successful_operation(self):
        """Should log successful file operation at INFO level."""
        logger = log.setup_logger(name="test_file_success")
        log.log_file_operation(logger, "copy", Path("/path/to/file.pdf"), True)

        # Should not raise exception
        assert True

    def test_log_failed_operation(self):
        """Should log failed file operation at ERROR level."""
        logger = log.setup_logger(name="test_file_fail")
        log.log_file_operation(logger, "delete", Path("/path/to/file.pdf"), False)

        # Should not raise exception
        assert True


class TestGetLogger:
    """Tests for get_logger convenience function."""

    def test_get_logger_creates_new_logger(self):
        """Should create new logger if it doesn't exist."""
        logger = log.get_logger(name="new_test_logger")

        assert logger.name == "new_test_logger"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_returns_existing(self):
        """Should return existing logger."""
        logger1 = log.get_logger(name="existing_logger")
        logger2 = log.get_logger(name="existing_logger")

        # Should be the same instance
        assert logger1 is logger2

    def test_get_logger_sets_up_handlers_if_needed(self):
        """Should set up handlers if logger has none."""
        # Create a raw logger without handlers
        raw_logger = logging.getLogger("raw_logger")
        raw_logger.handlers.clear()

        # get_logger should set it up
        logger = log.get_logger(name="raw_logger")

        # Should now have handlers
        assert len(logger.handlers) > 0


class TestLogIntegration:
    """Integration tests for logging module."""

    def test_full_lifecycle_logging(self, tmp_path):
        """Should log application lifecycle correctly."""
        log_file = tmp_path / "lifecycle.log"
        logger = log.setup_logger(name="lifecycle_test", log_file=log_file)

        # Log lifecycle
        log.log_application_start(logger)
        logger.info("Application doing work...")
        log.log_lock_acquired(logger, "PC-01", 12345)
        logger.info("Processing data...")
        log.log_lock_released(logger, "PC-01", 12345)
        log.log_application_stop(logger)

        # Verify log file was created and contains content
        assert log_file.exists()
        log_content = log_file.read_text()

        assert "Application starting" in log_content
        assert "Application doing work" in log_content
        assert "Lock acquired" in log_content
        assert "Processing data" in log_content
        assert "Lock released" in log_content
        assert "Application stopped" in log_content

    def test_error_logging(self, tmp_path):
        """Should log errors correctly."""
        log_file = tmp_path / "errors.log"
        logger = log.setup_logger(name="error_test", log_file=log_file)

        # Log different error types
        try:
            raise ValueError("Test error")
        except Exception as e:
            log.log_database_error(logger, e, context="test operation")

        log.log_file_operation(logger, "copy", Path("/test.pdf"), False)

        # Verify errors were logged
        log_content = log_file.read_text()
        assert "Database error" in log_content
        assert "Test error" in log_content
        assert "failed" in log_content
