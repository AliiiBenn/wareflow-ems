# ISSUE-061: Configurable Multi-Level Warning System

## Description

The current alert system uses hardcoded warning thresholds (90, 60, 30 days). Users need the ability to configure multiple warning levels through settings, allowing customization of when warnings and alerts appear based on different time periods before expiration.

## Current State

Hardcoded warning levels:
```python
# src/employee/alerts.py
ALERT_CRITICAL_DAYS = 30   # Red
ALERT_WARNING_DAYS = 60    # Orange
ALERT_INFO_DAYS = 90       # Yellow
```

These values are:
- Not configurable by users
- Same for all document types
- Cannot adapt to different operational needs
- No flexibility for different risk tolerances

## Expected Behavior

### Configuration Interface

Add a new **Alert Settings** dialog in the application:

```python
# src/ui_ctk/dialogs/alert_settings_dialog.py
class AlertSettingsDialog(ctk.CTkToplevel):
    """Dialog for configuring alert thresholds."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Alert Settings")
        self.geometry("700x500")

        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        """Create settings widgets."""
        # CACES Settings
        caces_frame = ctk.CTkFrame(self)
        caces_frame.pack(fill="x", padx=20, pady=10)

        caces_label = ctk.CTkLabel(
            caces_frame,
            text="CACES Certification Alerts",
            font=("Arial", 14, "bold")
        )
        caces_label.pack(pady=(10, 10))

        # Warning levels
        self.caces_info_days = self.create_days_input(
            caces_frame,
            "Info (Yellow): Alert X days before expiration",
            default=90
        )

        self.caces_warning_days = self.create_days_input(
            caces_frame,
            "Warning (Orange): Alert X days before expiration",
            default=60
        )

        self.caces_alert_days = self.create_days_input(
            caces_frame,
            "Alert (Red): Alert X days before expiration",
            default=30
        )

        self.caces_critical_days = self.create_days_input(
            caces_frame,
            "Critical: Alert X days before expiration",
            default=7
        )

        # Medical Visit Settings (similar structure)
        # Training Settings (similar structure)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame,
            text="Save Settings",
            command=self.save_settings
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_defaults
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side="left", padx=5)
```

### Configuration File Structure

**File: `config/alert_settings.json`**

```json
{
  "version": "1.0",
  "last_updated": "2024-01-27T10:00:00Z",
  "alert_settings": {
    "caces": {
      "enabled": true,
      "levels": {
        "info": {
          "days": 90,
          "color": "#FFFF00",
          "label": "Info",
          "notification": false
        },
        "warning": {
          "days": 60,
          "color": "#FFA500",
          "label": "Warning",
          "notification": true
        },
        "alert": {
          "days": 30,
          "color": "#FF0000",
          "label": "Alert",
          "notification": true
        },
        "critical": {
          "days": 7,
          "color": "#8B0000",
          "label": "Critical",
          "notification": true,
          "email": true
        }
      }
    },
    "medical": {
      "enabled": true,
      "levels": {
        "info": {"days": 90, "color": "#FFFF00", "label": "Info"},
        "warning": {"days": 60, "color": "#FFA500", "label": "Warning"},
        "alert": {"days": 30, "color": "#FF0000", "label": "Alert"},
        "critical": {"days": 7, "color": "#8B0000", "label": "Critical"}
      }
    },
    "training": {
      "enabled": true,
      "levels": {
        "info": {"days": 60, "color": "#FFFF00", "label": "Info"},
        "warning": {"days": 30, "color": "#FFA500", "label": "Warning"},
        "alert": {"days": 14, "color": "#FF0000", "label": "Alert"},
        "critical": {"days": 7, "color": "#8B0000", "label": "Critical"}
      }
    },
    "contracts": {
      "enabled": true,
      "levels": {
        "info": {"days": 90, "color": "#FFFF00", "label": "Info"},
        "warning": {"days": 60, "color": "#FFA500", "label": "Warning"},
        "alert": {"days": 30, "color": "#FF0000", "label": "Alert"}
      }
    }
  },
  "notification_settings": {
    "desktop_notifications": true,
    "sound_enabled": false,
    "check_frequency_hours": 24,
    "supervisor_email": "",
    "require_acknowledgment": false
  }
}
```

### Alert Settings Model

**File: `src/employee/alert_settings.py`**

```python
from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path
import json
from datetime import datetime

@dataclass
class AlertLevel:
    """Configuration for a single alert level."""
    days: int
    color: str
    label: str
    notification: bool = False
    email: bool = False

@dataclass
class CategoryAlertSettings:
    """Alert settings for a document category."""
    enabled: bool
    info: AlertLevel
    warning: AlertLevel
    alert: AlertLevel
    critical: Optional[AlertLevel] = None

class AlertSettingsManager:
    """Manage alert settings configuration."""

    DEFAULT_SETTINGS = {
        "caces": CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=90, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=60, color="#FFA500", label="Warning", notification=True),
            alert=AlertLevel(days=30, color="#FF0000", label="Alert", notification=True),
            critical=AlertLevel(days=7, color="#8B0000", label="Critical", notification=True, email=True)
        ),
        "medical": CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=90, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=60, color="#FFA500", label="Warning", notification=True),
            alert=AlertLevel(days=30, color="#FF0000", label="Alert", notification=True),
            critical=AlertLevel(days=7, color="#8B0000", label="Critical", notification=True)
        ),
        "training": CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=60, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=30, color="#FFA500", label="Warning", notification=True),
            alert=AlertLevel(days=14, color="#FF0000", label="Alert", notification=True),
            critical=AlertLevel(days=7, color="#8B0000", label="Critical", notification=True)
        ),
        "contracts": CategoryAlertSettings(
            enabled=True,
            info=AlertLevel(days=90, color="#FFFF00", label="Info"),
            warning=AlertLevel(days=60, color="#FFA500", label="Warning", notification=True),
            alert=AlertLevel(days=30, color="#FF0000", label="Alert", notification=True)
        )
    }

    def __init__(self, config_path: Path = Path("config/alert_settings.json")):
        self.config_path = config_path
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, CategoryAlertSettings]:
        """Load settings from config file."""
        if not self.config_path.exists():
            return self.DEFAULT_SETTINGS

        with open(self.config_path) as f:
            data = json.load(f)

        settings = {}
        for category, config in data["alert_settings"].items():
            levels = config["levels"]
            settings[category] = CategoryAlertSettings(
                enabled=config["enabled"],
                info=AlertLevel(**levels["info"]),
                warning=AlertLevel(**levels["warning"]),
                alert=AlertLevel(**levels["alert"]),
                critical=AlertLevel(**levels["critical"]) if "critical" in levels else None
            )

        return settings

    def save_settings(self):
        """Save settings to config file."""
        self.config_path.parent.mkdir(exist_ok=True)

        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "alert_settings": {}
        }

        for category, settings in self.settings.items():
            levels = {
                "info": settings.info.__dict__,
                "warning": settings.warning.__dict__,
                "alert": settings.alert.__dict__
            }
            if settings.critical:
                levels["critical"] = settings.critical.__dict__

            data["alert_settings"][category] = {
                "enabled": settings.enabled,
                "levels": levels
            }

        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_alert_level(self, category: str, days_until: int) -> Optional[AlertLevel]:
        """
        Get the alert level for a given number of days.

        Args:
            category: Document category (caces, medical, training, contracts)
            days_until: Days until expiration

        Returns:
            AlertLevel if applicable, None otherwise
        """
        if category not in self.settings:
            return None

        settings = self.settings[category]
        if not settings.enabled:
            return None

        # Check from most critical to least
        if settings.critical and days_until <= settings.critical.days:
            return settings.critical
        elif days_until <= settings.alert.days:
            return settings.alert
        elif days_until <= settings.warning.days:
            return settings.warning
        elif days_until <= settings.info.days:
            return settings.info

        return None

    def update_category(
        self,
        category: str,
        info_days: int,
        warning_days: int,
        alert_days: int,
        critical_days: Optional[int] = None
    ):
        """Update alert thresholds for a category."""
        if category not in self.settings:
            return

        self.settings[category].info.days = info_days
        self.settings[category].warning.days = warning_days
        self.settings[category].alert.days = alert_days

        if critical_days is not None and self.settings[category].critical:
            self.settings[category].critical.days = critical_days

        self.save_settings()
```

### Integration with Alert System

**Update: `src/employee/alerts.py`**

```python
from employee.alert_settings import AlertSettingsManager

class AlertManager:
    """Manage employee alerts with configurable thresholds."""

    def __init__(self):
        self.settings_manager = AlertSettingsManager()

    def get_employee_alerts(self, employee: Employee) -> list[dict]:
        """Get all alerts for an employee based on configured settings."""
        alerts = []

        # Check CACES
        for caces in employee.caces:
            if caces.expiration_date:
                days_until = (caces.expiration_date - date.today()).days

                if days_until < 0:
                    alerts.append({
                        "type": "caces",
                        "level": "expired",
                        "message": f"{caces.caces_type} expired {abs(days_until)} days ago",
                        "color": "#8B0000"
                    })
                else:
                    level = self.settings_manager.get_alert_level("caces", days_until)
                    if level:
                        alerts.append({
                            "type": "caces",
                            "level": level.label,
                            "message": f"{caces.caces_type} expires in {days_until} days",
                            "color": level.color,
                            "notification": level.notification
                        })

        # Check medical visits
        # Check training
        # Check contracts

        return alerts
```

## Affected Files

- `src/employee/alert_settings.py` - New file for settings management
- `src/employee/alerts.py` - Update to use configurable settings
- `src/ui_ctk/dialogs/alert_settings_dialog.py` - New settings dialog
- `src/ui_ctk/views/alerts_view.py` - Update to display custom levels
- `src/ui_ctk/main_window.py` - Add menu item for alert settings
- `config/alert_settings.json` - Configuration file

## Implementation Plan

### Phase 1: Alert Settings Infrastructure (2 days)
1. Create `AlertSettingsManager` class
2. Implement configuration file loading/saving
3. Define default settings for all categories
4. Add validation for settings

### Phase 2: Settings Dialog (2 days)
1. Create alert settings dialog UI
2. Implement input widgets for all categories
3. Add save/reset functionality
4. Integrate with main window menu

### Phase 3: Update Alert System (1 day)
1. Modify alert generation to use configurable thresholds
2. Update alert display to show custom colors
3. Implement notification triggers
4. Test all alert levels

### Phase 4: Testing (1 day)
1. Unit tests for settings manager
2. Integration tests for alert system
3. Manual UI testing
4. Verify settings persistence

## Dependencies

- None (new functionality)

## Related Issues

- ISSUE-062: Equipment Operation Conditions (uses alert levels)
- ISSUE-060: Hierarchical Document Storage (document tracking)
- ISSUE-064: Contract History Tracking (contract alerts)

## Acceptance Criteria

- [ ] AlertSettingsManager implemented and tested
- [ ] Configuration file structure defined
- [ ] Settings dialog UI functional
- [ ] Can configure different thresholds per category
- [ ] Can configure 4 alert levels (info, warning, alert, critical)
- [ ] Settings persist across application restarts
- [ ] Alert system uses configured thresholds
- [ ] Colors and labels customizable
- [ ] Notifications triggered based on settings
- [ ] Reset to defaults works correctly
- [ ] Validation prevents invalid settings
- [ ] All tests pass

## Estimated Effort

**Total:** 5-6 days
- Settings infrastructure: 2 days
- Settings dialog: 2 days
- Alert system integration: 1 day
- Testing: 1 day

## Notes

This is a high-value feature that gives users control over alert thresholds. Different organizations have different risk tolerances and operational needs, so configurability is essential.

## Future Enhancements

- Per-employee alert overrides (special cases)
- Alert templates (save/load preset configurations)
- Alert escalation rules (auto-escalate over time)
- Integration with email/SMS notifications
- Alert scheduling (don't alert at night/weekends)
- Alert acknowledgment system (require user to acknowledge alerts)
