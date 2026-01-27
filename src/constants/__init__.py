"""Application constants.

This package contains all application-wide constants organized by category.
"""

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

__all__ = [
    # Alert thresholds
    "DEFAULT_ALERT_DAYS",
    "MAX_ALERT_DAYS",
    "MIN_ALERT_DAYS",
    # Alert warning levels
    "ALERT_CRITICAL_DAYS",
    "ALERT_WARNING_DAYS",
    "ALERT_INFO_DAYS",
    # Renewal periods
    "MEDICAL_VISIT_RENEWAL_DAYS",
    "CACES_RENEWAL_DAYS",
    "TRAINING_RENEWAL_DAYS",
    # Display thresholds
    "ALERT_EXPIRED_DAYS",
    "ALERT_EXPIRING_SOON_DAYS",
    "ALERT_EXPIRING_WARNING_DAYS",
    "ALERT_EXPIRING_FUTURE_DAYS",
]
