"""Alert settings management system.

This module provides a configurable alert settings system that allows
users to customize warning thresholds for different document types.
"""

import json
from copy import deepcopy
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List


@dataclass
class AlertLevel:
    """Configuration for a single alert level.

    Attributes:
        days: Days threshold for this alert level
        color: Hex color code for display
        label: Display label for this level
        notification: Whether to trigger notifications
        email: Whether to send email alerts
    """

    days: int
    color: str
    label: str
    notification: bool = False
    email: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AlertLevel":
        """Create AlertLevel from dictionary."""
        return cls(**data)


@dataclass
class CategoryAlertSettings:
    """Alert settings for a document category.

    Attributes:
        enabled: Whether alerts are enabled for this category
        info: Info level configuration (least urgent)
        warning: Warning level configuration
        alert: Alert level configuration
        critical: Critical level configuration (most urgent, optional)
    """

    enabled: bool
    info: AlertLevel
    warning: AlertLevel
    alert: AlertLevel
    critical: Optional[AlertLevel] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = {
            "enabled": self.enabled,
            "levels": {
                "info": self.info.to_dict(),
                "warning": self.warning.to_dict(),
                "alert": self.alert.to_dict(),
            },
        }
        if self.critical:
            data["levels"]["critical"] = self.critical.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "CategoryAlertSettings":
        """Create CategoryAlertSettings from dictionary."""
        levels = data["levels"]
        critical_data = levels.get("critical")

        return cls(
            enabled=data["enabled"],
            info=AlertLevel.from_dict(levels["info"]),
            warning=AlertLevel.from_dict(levels["warning"]),
            alert=AlertLevel.from_dict(levels["alert"]),
            critical=AlertLevel.from_dict(critical_data) if critical_data else None,
        )


class AlertSettingsManager:
    """Manage alert settings configuration.

    This class handles loading, saving, and accessing alert settings
    from a JSON configuration file. It provides default settings for
    all document categories and allows customization of thresholds.

    Attributes:
        config_path: Path to configuration file
        settings: Dictionary of category settings
    """

    VERSION = "1.0"

    DEFAULT_SETTINGS: Dict[str, CategoryAlertSettings] = {
        "caces": CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=90, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=60, color="#FFA500", label="Warning", notification=True),
            alert=AlertLevel(days=30, color="#FF0000", label="Alert", notification=True),
            critical=AlertLevel(days=7, color="#8B0000", label="Critical", notification=True, email=True),
        ),
        "medical": CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=90, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=60, color="#FFA500", label="Warning", notification=True),
            alert=AlertLevel(days=30, color="#FF0000", label="Alert", notification=True),
            critical=AlertLevel(days=7, color="#8B0000", label="Critical", notification=True),
        ),
        "training": CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=60, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=30, color="#FFA500", label="Warning", notification=True),
            alert=AlertLevel(days=14, color="#FF0000", label="Alert", notification=True),
            critical=AlertLevel(days=7, color="#8B0000", label="Critical", notification=True),
        ),
        "contracts": CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=90, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=60, color="#FFA500", label="Warning", notification=True),
            alert=AlertLevel(days=30, color="#FF0000", label="Alert", notification=True),
        ),
    }

    VALID_CATEGORIES = ["caces", "medical", "training", "contracts"]
    VALID_LEVELS = ["info", "warning", "alert", "critical"]

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize AlertSettingsManager.

        Args:
            config_path: Path to configuration file (default: config/alert_settings.json)
        """
        self.config_path = config_path or Path("config/alert_settings.json")
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, CategoryAlertSettings]:
        """Load settings from config file.

        Returns:
            Dictionary of category settings (defaults if file doesn't exist)
        """
        if not self.config_path.exists():
            return deepcopy(self.DEFAULT_SETTINGS)

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            settings = {}
            for category in self.VALID_CATEGORIES:
                if category in data.get("alert_settings", {}):
                    config = data["alert_settings"][category]
                    settings[category] = CategoryAlertSettings.from_dict(config)
                else:
                    settings[category] = self.DEFAULT_SETTINGS[category]

            return settings

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # If config is corrupted, use defaults
            return deepcopy(self.DEFAULT_SETTINGS)

    def save_settings(self) -> bool:
        """Save settings to config file.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            data = {"version": self.VERSION, "last_updated": datetime.now().isoformat(), "alert_settings": {}}

            for category, settings in self.settings.items():
                data["alert_settings"][category] = settings.to_dict()

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except (OSError, IOError) as e:
            return False

    def get_alert_level(self, category: str, days_until: int) -> Optional[AlertLevel]:
        """
        Get the alert level for a given number of days.

        Checks from most critical to least critical and returns the
        first matching level.

        Args:
            category: Document category (caces, medical, training, contracts)
            days_until: Days until expiration (negative if expired)

        Returns:
            AlertLevel if applicable, None otherwise
        """
        if category not in self.settings:
            return None

        cat_settings = self.settings[category]
        if not cat_settings.enabled:
            return None

        # Check from most critical to least
        if cat_settings.critical and days_until <= cat_settings.critical.days:
            return cat_settings.critical
        elif days_until <= cat_settings.alert.days:
            return cat_settings.alert
        elif days_until <= cat_settings.warning.days:
            return cat_settings.warning
        elif days_until <= cat_settings.info.days:
            return cat_settings.info

        return None

    def get_category_settings(self, category: str) -> Optional[CategoryAlertSettings]:
        """
        Get settings for a specific category.

        Args:
            category: Document category

        Returns:
            CategoryAlertSettings if found, None otherwise
        """
        return self.settings.get(category)

    def update_category(
        self,
        category: str,
        info_days: int,
        warning_days: int,
        alert_days: int,
        critical_days: Optional[int] = None,
        enabled: bool = True,
    ) -> bool:
        """
        Update alert thresholds for a category.

        Args:
            category: Document category to update
            info_days: Days threshold for info level
            warning_days: Days threshold for warning level
            alert_days: Days threshold for alert level
            critical_days: Days threshold for critical level (optional)
            enabled: Whether alerts are enabled for this category

        Returns:
            True if successful, False otherwise
        """
        if category not in self.settings:
            return False

        # Validate thresholds (must be positive and descending)
        if not all(d > 0 for d in [info_days, warning_days, alert_days] if d is not None):
            return False

        if not (info_days > warning_days > alert_days):
            return False

        if critical_days is not None and critical_days >= alert_days:
            return False

        # Update settings
        self.settings[category].info.days = info_days
        self.settings[category].warning.days = warning_days
        self.settings[category].alert.days = alert_days
        self.settings[category].enabled = enabled

        if critical_days is not None and self.settings[category].critical:
            self.settings[category].critical.days = critical_days

        return self.save_settings()

    def reset_to_defaults(self, category: Optional[str] = None) -> bool:
        """
        Reset settings to defaults.

        Args:
            category: Specific category to reset (None = all categories)

        Returns:
            True if successful, False otherwise
        """
        if category:
            if category not in self.VALID_CATEGORIES:
                return False
            self.settings[category] = deepcopy(self.DEFAULT_SETTINGS[category])
        else:
            self.settings = deepcopy(self.DEFAULT_SETTINGS)

        return self.save_settings()

    def is_enabled(self, category: str) -> bool:
        """
        Check if alerts are enabled for a category.

        Args:
            category: Document category

        Returns:
            True if enabled, False otherwise
        """
        if category not in self.settings:
            return False
        return self.settings[category].enabled

    def get_all_categories(self) -> List[str]:
        """Get list of all configured categories."""
        return list(self.settings.keys())

    def get_config_path(self) -> Path:
        """Get the configuration file path."""
        return self.config_path

    def config_exists(self) -> bool:
        """Check if configuration file exists."""
        return self.config_path.exists()
