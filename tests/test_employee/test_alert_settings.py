"""Tests for alert settings management system.

Unit tests for AlertSettingsManager covering configuration loading,
saving, alert level calculation, and settings management.
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import date
from unittest.mock import patch

import pytest

from employee.alert_settings import AlertSettingsManager, AlertLevel, CategoryAlertSettings


class TestAlertLevel:
    """Test AlertLevel dataclass."""

    def test_alert_level_creation(self):
        """Test creating AlertLevel instance."""
        level = AlertLevel(days=30, color="#FF0000", label="Alert", notification=True)

        assert level.days == 30
        assert level.color == "#FF0000"
        assert level.label == "Alert"
        assert level.notification is True
        assert level.email is False

    def test_alert_level_to_dict(self):
        """Test converting AlertLevel to dictionary."""
        level = AlertLevel(days=60, color="#FFFF00", label="Warning", notification=False, email=True)
        data = level.to_dict()

        assert data == {
            "days": 60,
            "color": "#FFFF00",
            "label": "Warning",
            "notification": False,
            "email": True,
        }

    def test_alert_level_from_dict(self):
        """Test creating AlertLevel from dictionary."""
        data = {"days": 90, "color": "#00FF00", "label": "Info", "notification": True, "email": False}
        level = AlertLevel.from_dict(data)

        assert level.days == 90
        assert level.color == "#00FF00"
        assert level.label == "Info"
        assert level.notification is True
        assert level.email is False


class TestCategoryAlertSettings:
    """Test CategoryAlertSettings dataclass."""

    def test_category_settings_creation(self):
        """Test creating CategoryAlertSettings instance."""
        settings = CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=90, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=60, color="#FFA500", label="Warning"),
            alert=AlertLevel(days=30, color="#FF0000", label="Alert"),
            critical=AlertLevel(days=7, color="#8B0000", label="Critical"),
        )

        assert settings.enabled is True
        assert settings.info.days == 90
        assert settings.warning.days == 60
        assert settings.alert.days == 30
        assert settings.critical.days == 7

    def test_category_settings_without_critical(self):
        """Test CategoryAlertSettings without critical level."""
        settings = CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=90, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=60, color="#FFA500", label="Warning"),
            alert=AlertLevel(days=30, color="#FF0000", label="Alert"),
            critical=None,
        )

        assert settings.critical is None

    def test_category_settings_to_dict(self):
        """Test converting CategoryAlertSettings to dictionary."""
        settings = CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=90, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=60, color="#FFA500", label="Warning"),
            alert=AlertLevel(days=30, color="#FF0000", label="Alert"),
            critical=AlertLevel(days=7, color="#8B0000", label="Critical"),
        )
        data = settings.to_dict()

        assert data["enabled"] is True
        assert "levels" in data
        assert data["levels"]["info"]["days"] == 90
        assert data["levels"]["critical"]["days"] == 7

    def test_category_settings_from_dict(self):
        """Test creating CategoryAlertSettings from dictionary."""
        data = {
            "enabled": True,
            "levels": {
                "info": {"days": 90, "color": "#FFFF00", "label": "Info", "notification": False, "email": False},
                "warning": {"days": 60, "color": "#FFA500", "label": "Warning", "notification": True, "email": False},
                "alert": {"days": 30, "color": "#FF0000", "label": "Alert", "notification": True, "email": False},
                "critical": {"days": 7, "color": "#8B0000", "label": "Critical", "notification": True, "email": True},
            },
        }
        settings = CategoryAlertSettings.from_dict(data)

        assert settings.enabled is True
        assert settings.info.days == 90
        assert settings.warning.days == 60
        assert settings.alert.days == 30
        assert settings.critical.days == 7
        assert settings.critical.email is True


class TestAlertSettingsManager:
    """Test AlertSettingsManager class."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for config files."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def manager(self, temp_config_dir):
        """Create AlertSettingsManager with temporary config."""
        config_path = Path(temp_config_dir) / "alert_settings.json"
        return AlertSettingsManager(config_path=config_path)

    @pytest.fixture
    def valid_config_file(self, temp_config_dir):
        """Create a valid configuration file."""
        config_path = Path(temp_config_dir) / "alert_settings.json"
        data = {
            "version": "1.0",
            "last_updated": "2024-01-27T10:00:00Z",
            "alert_settings": {
                "caces": {
                    "enabled": True,
                    "levels": {
                        "info": {"days": 90, "color": "#FFFF00", "label": "Info", "notification": False, "email": False},
                        "warning": {"days": 60, "color": "#FFA500", "label": "Warning", "notification": True, "email": False},
                        "alert": {"days": 30, "color": "#FF0000", "label": "Alert", "notification": True, "email": False},
                        "critical": {"days": 7, "color": "#8B0000", "label": "Critical", "notification": True, "email": True},
                    },
                },
                "medical": {
                    "enabled": True,
                    "levels": {
                        "info": {"days": 90, "color": "#FFFF00", "label": "Info", "notification": False, "email": False},
                        "warning": {"days": 60, "color": "#FFA500", "label": "Warning", "notification": True, "email": False},
                        "alert": {"days": 30, "color": "#FF0000", "label": "Alert", "notification": True, "email": False},
                        "critical": {"days": 7, "color": "#8B0000", "label": "Critical", "notification": True, "email": False},
                    },
                },
            },
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return config_path

    # Test: Initialization

    def test_init_creates_config_dir(self, temp_config_dir):
        """Test that initialization doesn't create config directory."""
        config_path = Path(temp_config_dir) / "subdir" / "alert_settings.json"
        manager = AlertSettingsManager(config_path=config_path)
        # Config dir should not be created until save_settings is called
        assert config_path.parent.exists() is False

    def test_init_uses_default_path(self):
        """Test initialization with default config path."""
        manager = AlertSettingsManager()
        assert manager.config_path == Path("config/alert_settings.json")

    def test_init_loads_defaults_when_no_config(self, manager):
        """Test that default settings are loaded when config doesn't exist."""
        assert "caces" in manager.settings
        assert "medical" in manager.settings
        assert "training" in manager.settings
        assert "contracts" in manager.settings

    def test_init_loads_from_existing_config(self, temp_config_dir, valid_config_file):
        """Test loading settings from existing config file."""
        # Create manager AFTER valid_config_file fixture creates the file
        config_path = valid_config_file
        manager = AlertSettingsManager(config_path=config_path)

        # Settings should be loaded from file
        assert manager.settings["caces"].info.days == 90
        assert manager.settings["caces"].warning.days == 60
        assert manager.settings["medical"].alert.days == 30
        assert manager.settings["caces"].enabled is True

    # Test: get_alert_level

    def test_get_alert_level_critical(self, manager):
        """Test getting critical alert level."""
        level = manager.get_alert_level("caces", 5)
        assert level is not None
        assert level.label == "Critical"
        assert level.days == 7

    def test_get_alert_level_alert(self, manager):
        """Test getting alert level."""
        level = manager.get_alert_level("caces", 25)
        assert level is not None
        assert level.label == "Alert"
        assert level.days == 30

    def test_get_alert_level_warning(self, manager):
        """Test getting warning level."""
        level = manager.get_alert_level("caces", 55)
        assert level is not None
        assert level.label == "Warning"
        assert level.days == 60

    def test_get_alert_level_info(self, manager):
        """Test getting info level."""
        level = manager.get_alert_level("caces", 85)
        assert level is not None
        assert level.label == "Info"
        assert level.days == 90

    def test_get_alert_level_none(self, manager):
        """Test getting no alert level (beyond info threshold)."""
        level = manager.get_alert_level("caces", 95)
        assert level is None

    def test_get_alert_level_expired(self, manager):
        """Test alert level for expired items."""
        level = manager.get_alert_level("caces", -10)
        assert level is not None
        assert level.label == "Critical"

    def test_get_alert_level_invalid_category(self, manager):
        """Test getting alert level for invalid category."""
        level = manager.get_alert_level("invalid", 30)
        assert level is None

    def test_get_alert_level_disabled_category(self, manager):
        """Test alert level when category is disabled."""
        manager.settings["caces"].enabled = False
        level = manager.get_alert_level("caces", 5)
        assert level is None

    def test_get_alert_level_training_defaults(self, manager):
        """Test training category has different defaults."""
        # Training defaults: info=60, warning=30, alert=14
        # At 25 days: 14 < 25 <= 30, so it's warning level
        level = manager.get_alert_level("training", 25)
        assert level is not None
        assert level.label == "Warning"
        assert level.days == 30

    def test_get_alert_level_contracts_no_critical(self, manager):
        """Test contracts category has no critical level."""
        # Contracts default has no critical, so 5 days should return alert
        level = manager.get_alert_level("contracts", 5)
        assert level is not None
        assert level.label == "Alert"

    # Test: get_category_settings

    def test_get_category_settings_existing(self, manager):
        """Test getting settings for existing category."""
        settings = manager.get_category_settings("caces")
        assert settings is not None
        # Manager uses defaults (no config file exists yet)
        assert settings.enabled is True
        assert settings.info.days == 90

    def test_get_category_settings_nonexistent(self, manager):
        """Test getting settings for nonexistent category."""
        settings = manager.get_category_settings("invalid")
        assert settings is None

    # Test: update_category

    def test_update_category_success(self, manager):
        """Test updating category thresholds."""
        result = manager.update_category("caces", info_days=120, warning_days=80, alert_days=40, critical_days=10)

        assert result is True
        assert manager.settings["caces"].info.days == 120
        assert manager.settings["caces"].warning.days == 80
        assert manager.settings["caces"].alert.days == 40
        assert manager.settings["caces"].critical.days == 10

    def test_update_category_creates_config_file(self, manager):
        """Test that update creates config file."""
        manager.update_category("caces", info_days=120, warning_days=80, alert_days=40)
        assert manager.config_exists()

    def test_update_category_invalid_category(self, manager):
        """Test updating invalid category."""
        result = manager.update_category("invalid", info_days=90, warning_days=60, alert_days=30)
        assert result is False

    def test_update_category_invalid_thresholds_not_descending(self, manager):
        """Test that thresholds must be descending."""
        result = manager.update_category("caces", info_days=60, warning_days=90, alert_days=30)
        assert result is False

    def test_update_category_invalid_thresholds_negative(self, manager):
        """Test that thresholds must be positive."""
        result = manager.update_category("caces", info_days=90, warning_days=-10, alert_days=30)
        assert result is False

    def test_update_category_invalid_critical_threshold(self, manager):
        """Test that critical must be less than alert."""
        result = manager.update_category("caces", info_days=90, warning_days=60, alert_days=30, critical_days=40)
        assert result is False

    def test_update_category_disable(self, manager):
        """Test disabling a category."""
        result = manager.update_category("caces", info_days=90, warning_days=60, alert_days=30, enabled=False)

        assert result is True
        assert manager.settings["caces"].enabled is False

    def test_update_category_without_critical(self, manager):
        """Test updating category without critical level."""
        result = manager.update_category("contracts", info_days=120, warning_days=80, alert_days=40)

        assert result is True
        assert manager.settings["contracts"].info.days == 120

    # Test: save_settings

    def test_save_settings_creates_file(self, manager):
        """Test that save_settings creates config file."""
        result = manager.save_settings()

        assert result is True
        assert manager.config_exists()

    def test_save_settings_creates_directory(self, temp_config_dir):
        """Test that save_settings creates directory structure."""
        config_path = Path(temp_config_dir) / "subdir" / "alert_settings.json"
        manager = AlertSettingsManager(config_path=config_path)
        result = manager.save_settings()

        assert result is True
        assert config_path.parent.exists()
        assert config_path.exists()

    def test_save_settings_valid_json(self, manager):
        """Test that saved file is valid JSON."""
        manager.save_settings()

        with open(manager.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "version" in data
        assert "last_updated" in data
        assert "alert_settings" in data

    def test_save_settings_preserves_changes(self, manager):
        """Test that saved settings persist changes."""
        manager.settings["caces"].info.days = 120
        manager.save_settings()

        # Create new manager to load from file
        new_manager = AlertSettingsManager(config_path=manager.config_path)
        assert new_manager.settings["caces"].info.days == 120

    # Test: reset_to_defaults

    def test_reset_to_defaults_single_category(self, manager):
        """Test resetting single category to defaults."""
        # First modify and save settings
        manager.settings["caces"].info.days = 120
        manager.save_settings()

        # Reset caces to defaults
        result = manager.reset_to_defaults(category="caces")

        assert result is True
        assert manager.settings["caces"].info.days == 90  # Default value
        assert manager.settings["medical"].info.days == 90  # Unchanged

    def test_reset_to_defaults_all_categories(self, manager):
        """Test resetting all categories to defaults."""
        # Modify and save settings
        manager.settings["caces"].info.days = 120
        manager.settings["medical"].warning.days = 80
        manager.save_settings()

        # Reset all
        result = manager.reset_to_defaults()

        assert result is True
        assert manager.settings["caces"].info.days == 90
        assert manager.settings["medical"].warning.days == 60

    def test_reset_to_defaults_invalid_category(self, manager):
        """Test resetting invalid category."""
        result = manager.reset_to_defaults(category="invalid")
        assert result is False

    # Test: is_enabled

    def test_is_enabled_true(self, manager):
        """Test is_enabled returns True for enabled category."""
        assert manager.is_enabled("caces") is True

    def test_is_enabled_false(self, manager):
        """Test is_enabled returns False for disabled category."""
        manager.settings["caces"].enabled = False
        assert manager.is_enabled("caces") is False

    def test_is_enabled_invalid_category(self, manager):
        """Test is_enabled returns False for invalid category."""
        assert manager.is_enabled("invalid") is False

    # Test: Utility methods

    def test_get_all_categories(self, manager):
        """Test getting all categories."""
        categories = manager.get_all_categories()
        assert set(categories) == {"caces", "medical", "training", "contracts"}

    def test_get_config_path(self, manager):
        """Test getting config path."""
        path = manager.get_config_path()
        assert path == manager.config_path

    def test_config_exists_false_initially(self, manager):
        """Test config_exists returns False when file doesn't exist."""
        assert manager.config_exists() is False

    def test_config_exists_true_after_save(self, manager):
        """Test config_exists returns True after saving."""
        manager.save_settings()
        assert manager.config_exists() is True

    # Test: Edge cases and error handling

    def test_load_from_corrupted_json(self, temp_config_dir):
        """Test loading from corrupted JSON file."""
        config_path = Path(temp_config_dir) / "alert_settings.json"
        config_path.write_text("invalid json {")

        manager = AlertSettingsManager(config_path=config_path)
        # Should fall back to defaults
        assert "caces" in manager.settings

    def test_load_from_missing_required_fields(self, temp_config_dir):
        """Test loading from config with missing fields."""
        config_path = Path(temp_config_dir) / "alert_settings.json"
        data = {"version": "1.0", "alert_settings": {"caces": {"enabled": True, "levels": {"info": {"days": 90}}}}}
        with open(config_path, "w") as f:
            json.dump(data, f)

        manager = AlertSettingsManager(config_path=config_path)
        # Should fall back to defaults for corrupted category (except what was loaded)
        # Info was loaded as 90, but other levels should use defaults
        assert manager.settings["caces"].info.days == 90
        assert manager.settings["caces"].warning.days == 60  # Default

    def test_partial_config_uses_defaults_for_missing(self, temp_config_dir):
        """Test that missing categories in config use defaults."""
        config_path = Path(temp_config_dir) / "alert_settings.json"
        data = {
            "version": "1.0",
            "last_updated": "2024-01-27T10:00:00Z",
            "alert_settings": {
                "caces": {
                    "enabled": True,
                    "levels": {
                        "info": {"days": 90, "color": "#FFFF00", "label": "Info", "notification": False, "email": False},
                        "warning": {"days": 60, "color": "#FFA500", "label": "Warning", "notification": True, "email": False},
                        "alert": {"days": 30, "color": "#FF0000", "label": "Alert", "notification": True, "email": False},
                    },
                }
            },
        }
        with open(config_path, "w") as f:
            json.dump(data, f)

        manager = AlertSettingsManager(config_path=config_path)
        # CACES should be loaded from config
        assert manager.settings["caces"].info.days == 90
        # Medical should use defaults
        assert manager.settings["medical"].info.days == 90
