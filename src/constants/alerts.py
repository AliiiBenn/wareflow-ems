"""Alert-related constants.

This module contains all constants related to alert thresholds,
renewal periods, and expiration warnings.
"""

# ========== ALERT THRESHOLDS ==========

DEFAULT_ALERT_DAYS = 90  # Default days to look ahead for alerts
MAX_ALERT_DAYS = 365  # Maximum days allowed for alert queries
MIN_ALERT_DAYS = 7  # Minimum days allowed for alert queries

# ========== ALERT WARNING LEVELS ==========

ALERT_CRITICAL_DAYS = 30  # Red: Critical urgency (< 30 days or expired)
ALERT_WARNING_DAYS = 60  # Yellow: Warning urgency (30-60 days)
ALERT_INFO_DAYS = 90  # Green: Info urgency (60-90 days)

# ========== RENEWAL PERIODS ==========

MEDICAL_VISIT_RENEWAL_DAYS = 30  # Days before medical visit expiration to warn
CACES_RENEWAL_DAYS = 30  # Days before CACES expiration to warn
TRAINING_RENEWAL_DAYS = 30  # Days before training expiration to warn

# ========== DISPLAY THRESHOLDS ==========

ALERT_EXPIRED_DAYS = 0  # Already expired
ALERT_EXPIRING_SOON_DAYS = 30  # Expiring within 30 days (urgent)
ALERT_EXPIRING_WARNING_DAYS = 60  # Expiring within 60 days (soon)
ALERT_EXPIRING_FUTURE_DAYS = 90  # Expiring within 90 days (future)
