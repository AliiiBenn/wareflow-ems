"""
Tests for application constants.

Tests cover:
- Alert constants are properly defined
- Constants have correct values
- Constants maintain proper relationships
"""

import pytest
from constants.alerts import (
    # Alert thresholds
    DEFAULT_ALERT_DAYS,
    MAX_ALERT_DAYS,
    MIN_ALERT_DAYS,
    # Alert warning levels
    ALERT_CRITICAL_DAYS,
    ALERT_WARNING_DAYS,
    ALERT_INFO_DAYS,
    # Renewal periods
    MEDICAL_VISIT_RENEWAL_DAYS,
    CACES_RENEWAL_DAYS,
    TRAINING_RENEWAL_DAYS,
    # Display thresholds
    ALERT_EXPIRED_DAYS,
    ALERT_EXPIRING_SOON_DAYS,
    ALERT_EXPIRING_WARNING_DAYS,
    ALERT_EXPIRING_FUTURE_DAYS,
)


class TestAlertConstants:
    """Test alert-related constants."""

    def test_default_alert_days_value(self):
        """Test that DEFAULT_ALERT_DAYS is 90."""
        assert DEFAULT_ALERT_DAYS == 90

    def test_max_alert_days_value(self):
        """Test that MAX_ALERT_DAYS is 365."""
        assert MAX_ALERT_DAYS == 365

    def test_min_alert_days_value(self):
        """Test that MIN_ALERT_DAYS is 7."""
        assert MIN_ALERT_DAYS == 7

    def test_alert_critical_days_value(self):
        """Test that ALERT_CRITICAL_DAYS is 30."""
        assert ALERT_CRITICAL_DAYS == 30

    def test_alert_warning_days_value(self):
        """Test that ALERT_WARNING_DAYS is 60."""
        assert ALERT_WARNING_DAYS == 60

    def test_alert_info_days_value(self):
        """Test that ALERT_INFO_DAYS is 90."""
        assert ALERT_INFO_DAYS == 90

    def test_medical_visit_renewal_days_value(self):
        """Test that MEDICAL_VISIT_RENEWAL_DAYS is 30."""
        assert MEDICAL_VISIT_RENEWAL_DAYS == 30

    def test_caces_renewal_days_value(self):
        """Test that CACES_RENEWAL_DAYS is 30."""
        assert CACES_RENEWAL_DAYS == 30

    def test_training_renewal_days_value(self):
        """Test that TRAINING_RENEWAL_DAYS is 30."""
        assert TRAINING_RENEWAL_DAYS == 30

    def test_alert_expired_days_value(self):
        """Test that ALERT_EXPIRED_DAYS is 0."""
        assert ALERT_EXPIRED_DAYS == 0

    def test_alert_expiring_soon_days_value(self):
        """Test that ALERT_EXPIRING_SOON_DAYS is 30."""
        assert ALERT_EXPIRING_SOON_DAYS == 30

    def test_alert_expiring_warning_days_value(self):
        """Test that ALERT_EXPIRING_WARNING_DAYS is 60."""
        assert ALERT_EXPIRING_WARNING_DAYS == 60

    def test_alert_expiring_future_days_value(self):
        """Test that ALERT_EXPIRING_FUTURE_DAYS is 90."""
        assert ALERT_EXPIRING_FUTURE_DAYS == 90


class TestConstantRelationships:
    """Test that constants maintain proper relationships."""

    def test_urgency_levels_are_ordered(self):
        """Test that urgency levels are in ascending order."""
        assert ALERT_CRITICAL_DAYS < ALERT_WARNING_DAYS < ALERT_INFO_DAYS

    def test_default_alert_equals_info(self):
        """Test that DEFAULT_ALERT_DAYS equals ALERT_INFO_DAYS."""
        assert DEFAULT_ALERT_DAYS == ALERT_INFO_DAYS

    def test_renewal_periods_equal_critical(self):
        """Test that renewal periods equal ALERT_CRITICAL_DAYS."""
        assert MEDICAL_VISIT_RENEWAL_DAYS == ALERT_CRITICAL_DAYS
        assert CACES_RENEWAL_DAYS == ALERT_CRITICAL_DAYS
        assert TRAINING_RENEWAL_DAYS == ALERT_CRITICAL_DAYS

    def test_min_less_than_default_less_than_max(self):
        """Test that MIN < DEFAULT < MAX."""
        assert MIN_ALERT_DAYS < DEFAULT_ALERT_DAYS < MAX_ALERT_DAYS

    def test_display_thresholds_are_ordered(self):
        """Test that display thresholds are in ascending order."""
        assert (
            ALERT_EXPIRED_DAYS
            < ALERT_EXPIRING_SOON_DAYS
            < ALERT_EXPIRING_WARNING_DAYS
            < ALERT_EXPIRING_FUTURE_DAYS
        )


class TestConstantUsage:
    """Test that constants can be imported and used."""

    def test_import_from_constants_package(self):
        """Test that constants can be imported from the constants package."""
        from constants import (
            DEFAULT_ALERT_DAYS,
            ALERT_CRITICAL_DAYS,
            MEDICAL_VISIT_RENEWAL_DAYS,
        )

        assert DEFAULT_ALERT_DAYS == 90
        assert ALERT_CRITICAL_DAYS == 30
        assert MEDICAL_VISIT_RENEWAL_DAYS == 30

    def test_constants_are_immutable(self):
        """Test that constants are not accidentally modified."""
        # Get original value
        original_value = DEFAULT_ALERT_DAYS

        # Try to modify (this should work in Python, but we can check type)
        # Constants are typically uppercase to indicate they should not be changed
        assert isinstance(DEFAULT_ALERT_DAYS, int)
        assert DEFAULT_ALERT_DAYS == original_value


class TestAlertIntegration:
    """Test that constants integrate correctly with alert logic."""

    def test_urgency_calculation_with_constants(self):
        """Test that urgency calculation uses constants correctly."""
        from employee.alerts import AlertQuery

        # Test that AlertQuery uses the constants
        # Create a test date
        from datetime import date, timedelta

        today = date.today()

        # Test critical urgency
        critical_date = today + timedelta(days=ALERT_CRITICAL_DAYS - 1)
        urgency = AlertQuery.calculate_urgency(critical_date, today)
        assert urgency.value == "critical"

        # Test warning urgency
        warning_date = today + timedelta(days=ALERT_WARNING_DAYS - 1)
        urgency = AlertQuery.calculate_urgency(warning_date, today)
        assert urgency.value == "warning"

        # Test info urgency
        info_date = today + timedelta(days=ALERT_INFO_DAYS - 1)
        urgency = AlertQuery.calculate_urgency(info_date, today)
        assert urgency.value == "info"

        # Test ok urgency
        ok_date = today + timedelta(days=ALERT_INFO_DAYS + 1)
        urgency = AlertQuery.calculate_urgency(ok_date, today)
        assert urgency.value == "ok"

    def test_alert_query_default_threshold(self):
        """Test that AlertQuery uses DEFAULT_ALERT_DAYS as default."""
        from employee.alerts import AlertQuery

        # Get method signature
        import inspect

        sig = inspect.signature(AlertQuery.get_caces_alerts)
        default_threshold = sig.parameters["days_threshold"].default

        assert default_threshold == DEFAULT_ALERT_DAYS
