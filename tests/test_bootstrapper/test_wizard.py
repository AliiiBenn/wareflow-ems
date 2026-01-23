"""Tests for setup wizard functionality.

This test module covers the interactive setup wizard that helps
users configure Wareflow EMS without manual file editing.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bootstrapper import wizard
from utils import config


class TestPrintFunctions:
    """Tests for wizard print/display functions."""

    def test_print_header(self, capsys):
        """Should print wizard header."""
        wizard.print_header()

        captured = capsys.readouterr()
        assert "Wareflow EMS Configuration Wizard" in captured.out
        assert "Welcome" in captured.out

    def test_print_step(self, capsys):
        """Should print step header."""
        wizard.print_step(1, 7, "Test Step")

        captured = capsys.readouterr()
        assert "Step 1/7" in captured.out
        assert "Test Step" in captured.out


class TestAskFunctions:
    """Tests for wizard question functions."""

    @patch("bootstrapper.wizard.questionary.text")
    @patch("bootstrapper.wizard.questionary.confirm")
    def test_ask_company_info(self, mock_confirm, mock_text, capsys):
        """Should collect company information."""
        mock_text.side_effect = [
            Mock(ask=lambda: "Test Company"),
            Mock(ask=lambda: "test@example.com"),
            Mock(ask=lambda: "1234567890"),
        ]

        result = wizard.ask_company_info()

        assert result["company_name"] == "Test Company"
        assert result["contact_email"] == "test@example.com"
        assert result["contact_phone"] == "1234567890"

    @patch("bootstrapper.wizard.questionary.text")
    @patch("bootstrapper.wizard.questionary.confirm")
    def test_ask_company_info_defaults(self, mock_confirm, mock_text):
        """Should use defaults when user provides empty values."""
        mock_text.side_effect = [
            Mock(ask=lambda: ""),
            Mock(ask=lambda: ""),
            Mock(ask=lambda: ""),
        ]

        result = wizard.ask_company_info()

        assert result["company_name"] == "My Warehouse"
        assert result["contact_email"] == ""
        assert result["contact_phone"] == ""

    @patch("bootstrapper.wizard.questionary.confirm")
    @patch("bootstrapper.wizard.questionary.text")
    def test_ask_organization_with_defaults(self, mock_text, mock_confirm):
        """Should use default workspaces and roles when confirmed."""
        mock_confirm.return_value = Mock(ask=lambda: True)

        result = wizard.ask_organization()

        assert result["workspaces"] == wizard.DEFAULT_WORKSPACES
        assert result["roles"] == wizard.DEFAULT_ROLES

    @patch("bootstrapper.wizard.questionary.confirm")
    @patch("bootstrapper.wizard.questionary.text")
    def test_ask_organization_custom_workspaces(self, mock_text, mock_confirm):
        """Should accept custom workspace values."""
        # First confirm for workspaces (False = use custom)
        # Second confirm for roles (True = use default)
        mock_confirm.side_effect = [Mock(ask=lambda: False), Mock(ask=lambda: True)]

        mock_text.return_value = Mock(ask=lambda: "Zone A, Zone B, Zone C")

        result = wizard.ask_organization()

        assert result["workspaces"] == ["Zone A", "Zone B", "Zone C"]
        assert result["roles"] == wizard.DEFAULT_ROLES

    @patch("bootstrapper.wizard.questionary.text")
    def test_ask_alerts(self, mock_text):
        """Should collect alert thresholds."""
        mock_text.side_effect = [
            Mock(ask=lambda: "5"),
            Mock(ask=lambda: "20"),
            Mock(ask=lambda: "60"),
        ]

        result = wizard.ask_alerts()

        assert result["critical_days"] == 5
        assert result["warning_days"] == 20
        assert result["info_days"] == 60

    @patch("bootstrapper.wizard.questionary.confirm")
    @patch("bootstrapper.wizard.questionary.text")
    def test_ask_database(self, mock_text, mock_confirm):
        """Should collect database configuration."""
        mock_text.side_effect = [
            Mock(ask=lambda: "test.db"),
            Mock(ask=lambda: "60"),
        ]
        mock_confirm.return_value = Mock(ask=lambda: True)

        result = wizard.ask_database()

        assert result["database_filename"] == "test.db"
        assert result["backup_retention"] == 60
        assert result["enable_auto_backup"] is True

    @patch("bootstrapper.wizard.questionary.text")
    @patch("bootstrapper.wizard.questionary.select")
    def test_ask_interface(self, mock_select, mock_text):
        """Should collect interface preferences."""
        # Mock select for theme
        mock_select.return_value = Mock(ask=lambda: "light")
        mock_text.return_value = Mock(ask=lambda: "Test App")

        result = wizard.ask_interface()

        assert result["theme"] == "light"
        assert result["app_title"] == "Test App"

    @patch("bootstrapper.wizard.questionary.confirm")
    def test_ask_advanced(self, mock_confirm):
        """Should collect advanced feature preferences."""
        mock_confirm.return_value = Mock(ask=lambda: True)

        result = wizard.ask_advanced()

        assert result["enable_audit"] is True


class TestBuildConfigDict:
    """Tests for configuration dictionary building."""

    def test_build_config_dict_complete(self):
        """Should build complete config from wizard answers."""
        answers = {
            "company": {
                "company_name": "Test Company",
                "contact_email": "test@example.com",
                "contact_phone": "1234567890",
            },
            "organization": {
                "workspaces": ["Zone A", "Zone B"],
                "roles": ["Role A", "Role B"],
            },
            "alerts": {
                "critical_days": 5,
                "warning_days": 20,
                "info_days": 60,
            },
            "database": {
                "database_filename": "test.db",
                "backup_retention": 30,
                "enable_auto_backup": True,
            },
            "interface": {
                "app_title": "Test App",
                "theme": "dark",
            },
            "advanced": {
                "enable_audit": True,
            },
        }

        result = wizard.build_config_dict(answers)

        assert result["organization"]["company_name"] == "Test Company"
        assert result["organization"]["workspaces"] == ["Zone A", "Zone B"]
        assert result["organization"]["roles"] == ["Role A", "Role B"]
        assert result["alerts"]["critical_days"] == 5
        assert result["alerts"]["warning_days"] == 20
        assert "lock" in result
        assert result["lock"]["timeout_minutes"] == 2


class TestSaveConfig:
    """Tests for configuration saving."""

    def test_save_config_creates_file(self, tmp_path):
        """Should create YAML configuration file."""
        config_path = tmp_path / "config.yaml"
        cfg = {"organization": {"company_name": "Test"}}

        wizard.save_config(cfg, config_path)

        assert config_path.exists()

        # Verify it's valid
        loaded = config.load_config(config_path)
        assert loaded["organization"]["company_name"] == "Test"


class TestCreateDirectoryStructure:
    """Tests for directory structure creation."""

    def test_create_directory_structure(self, tmp_path):
        """Should create all required directories."""
        wizard.create_directory_structure(tmp_path)

        assert (tmp_path / "data").exists()
        assert (tmp_path / "documents").exists()
        assert (tmp_path / "documents" / "caces").exists()
        assert (tmp_path / "documents" / "medical").exists()
        assert (tmp_path / "documents" / "training").exists()
        assert (tmp_path / "backups").exists()
        assert (tmp_path / "logs").exists()


class TestPrintSummary:
    """Tests for configuration summary display."""

    def test_print_summary(self, capsys):
        """Should print configuration summary."""
        answers = {
            "company": {
                "company_name": "Test Company",
                "contact_email": "test@example.com",
                "contact_phone": "",
            },
            "organization": {
                "workspaces": ["Zone A", "Zone B", "Zone C"],
                "roles": ["Role A", "Role B", "Role C"],
            },
            "alerts": {
                "critical_days": 5,
                "warning_days": 20,
                "info_days": 60,
            },
            "database": {
                "database_filename": "test.db",
                "backup_retention": 30,
                "enable_auto_backup": True,
            },
            "interface": {
                "theme": "dark",
            },
        }

        wizard.print_summary(answers)

        captured = capsys.readouterr()
        assert "Test Company" in captured.out
        assert "Zone A" in captured.out
        assert "Role A" in captured.out
        assert "5d" in captured.out
        assert "test.db" in captured.out


class TestConfirmConfiguration:
    """Tests for configuration confirmation."""

    @patch("bootstrapper.wizard.questionary.confirm")
    def test_confirm_configuration_accepted(self, mock_confirm):
        """Should return True when user confirms."""
        mock_confirm.return_value = Mock(ask=lambda: True)

        answers = {
            "company": {
                "company_name": "Test Company",
                "contact_email": "test@example.com",
                "contact_phone": "1234567890",
            },
            "organization": {
                "workspaces": ["Zone A"],
                "roles": ["Role A"],
            },
            "alerts": {
                "critical_days": 5,
                "warning_days": 20,
                "info_days": 60,
            },
            "database": {
                "database_filename": "test.db",
                "backup_retention": 30,
                "enable_auto_backup": True,
            },
            "interface": {
                "theme": "dark",
            },
        }

        result = wizard.confirm_configuration(answers)

        assert result is True

    @patch("bootstrapper.wizard.questionary.confirm")
    def test_confirm_configuration_rejected(self, mock_confirm):
        """Should return False when user rejects."""
        mock_confirm.return_value = Mock(ask=lambda: False)

        answers = {
            "company": {
                "company_name": "Test Company",
                "contact_email": "test@example.com",
                "contact_phone": "1234567890",
            },
            "organization": {
                "workspaces": ["Zone A"],
                "roles": ["Role A"],
            },
            "alerts": {
                "critical_days": 5,
                "warning_days": 20,
                "info_days": 60,
            },
            "database": {
                "database_filename": "test.db",
                "backup_retention": 30,
                "enable_auto_backup": True,
            },
            "interface": {
                "theme": "dark",
            },
        }

        result = wizard.confirm_configuration(answers)

        assert result is False


class TestRunSetupWizard:
    """Tests for complete setup wizard flow."""

    @patch("bootstrapper.wizard.create_directory_structure")
    @patch("bootstrapper.wizard.save_config")
    @patch("bootstrapper.wizard.questionary.confirm")
    @patch("bootstrapper.wizard.build_config_dict")
    @patch("bootstrapper.wizard.ask_advanced")
    @patch("bootstrapper.wizard.ask_interface")
    @patch("bootstrapper.wizard.ask_database")
    @patch("bootstrapper.wizard.ask_alerts")
    @patch("bootstrapper.wizard.ask_organization")
    @patch("bootstrapper.wizard.ask_company_info")
    @patch("bootstrapper.wizard.Path")
    def test_run_setup_wizard_success(
        self,
        mock_path,
        mock_ask_company,
        mock_ask_org,
        mock_ask_alerts,
        mock_ask_db,
        mock_ask_interface,
        mock_ask_advanced,
        mock_build_config,
        mock_confirm,
        mock_save,
        mock_create_dirs,
    ):
        """Should run complete wizard and create configuration."""
        # Mock all the wizard steps
        mock_ask_company.return_value = {
            "company_name": "Test Company",
            "contact_email": "",
            "contact_phone": "",
        }
        mock_ask_org.return_value = {
            "workspaces": ["Zone A"],
            "roles": ["Role A"],
        }
        mock_ask_alerts.return_value = {
            "critical_days": 7,
            "warning_days": 30,
            "info_days": 90,
        }
        mock_ask_db.return_value = {
            "database_filename": "test.db",
            "backup_retention": 30,
            "enable_auto_backup": True,
        }
        mock_ask_interface.return_value = {"app_title": "Test", "theme": "system"}
        mock_ask_advanced.return_value = {"enable_audit": False}

        # Mock config file not exists
        mock_path.return_value.exists.return_value = False

        # Mock confirmation accepted
        mock_confirm.return_value = Mock(ask=lambda: True)

        # Mock built config
        test_config = {"organization": {"company_name": "Test"}}
        mock_build_config.return_value = test_config

        result = wizard.run_setup_wizard()

        assert result == test_config
        mock_save.assert_called_once()
        mock_create_dirs.assert_called_once()

    @patch("bootstrapper.wizard.Path")
    @patch("bootstrapper.wizard.questionary.confirm")
    def test_run_setup_wizard_cancel_on_existing(
        self,
        mock_confirm,
        mock_path,
    ):
        """Should cancel when config exists and user chooses not to overwrite."""
        # Mock config file exists
        mock_path.return_value.exists.return_value = True

        # User chooses not to overwrite
        mock_confirm.return_value = Mock(ask=lambda: False)

        result = wizard.run_setup_wizard()

        assert result == {}

    @patch("bootstrapper.wizard.ask_company_info")
    @patch("bootstrapper.wizard.Path")
    def test_run_setup_wizard_keyboard_interrupt(
        self,
        mock_path,
        mock_ask_company,
    ):
        """Should handle keyboard interrupt gracefully."""
        mock_path.return_value.exists.return_value = False
        mock_ask_company.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            wizard.run_setup_wizard()
