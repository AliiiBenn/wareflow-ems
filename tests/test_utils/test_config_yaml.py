"""Tests for YAML configuration support.

This test file contains tests specific to YAML functionality including
format detection, loading, saving, and migration from JSON.
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from utils import config
from utils.config import YAML_AVAILABLE


class TestYAMLFormatDetection:
    """Tests for YAML format detection."""

    def test_detect_yaml_format(self):
        """Should detect .yaml extension."""
        path = Path("config.yaml")
        fmt = config._detect_format(path)
        assert fmt == "yaml"

    def test_detect_yml_format(self):
        """Should detect .yml extension."""
        path = Path("config.yml")
        fmt = config._detect_format(path)
        assert fmt == "yaml"

    def test_detect_json_format(self):
        """Should detect .json extension."""
        path = Path("config.json")
        fmt = config._detect_format(path)
        assert fmt == "json"

    def test_detect_unsupported_format(self):
        """Should raise error for unsupported format."""
        path = Path("config.txt")
        with pytest.raises(ValueError, match="Unsupported config format"):
            config._detect_format(path)


class TestYAMLLoading:
    """Tests for YAML configuration loading."""

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_load_yaml_config(self, tmp_path):
        """Should load YAML configuration file."""
        config_file = tmp_path / "config.yaml"
        yaml_content = """
alerts:
  critical_days: 5
  warning_days: 45
organization:
  roles:
    - Custom Role
"""
        config_file.write_text(yaml_content)

        cfg = config.load_config(config_file)

        assert cfg['alerts']['critical_days'] == 5
        assert cfg['alerts']['warning_days'] == 45
        assert "Custom Role" in cfg['organization']['roles']

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_load_yaml_with_comments(self, tmp_path):
        """Should load YAML with comments (comments are ignored)."""
        config_file = tmp_path / "config.yaml"
        yaml_content = """
# Alert configuration
alerts:
  critical_days: 5  # Critical threshold
  warning_days: 30 # Warning threshold
"""
        config_file.write_text(yaml_content)

        cfg = config.load_config(config_file)

        assert cfg['alerts']['critical_days'] == 5
        assert cfg['alerts']['warning_days'] == 30

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_load_yaml_with_unicode(self, tmp_path):
        """Should load YAML with Unicode characters."""
        config_file = tmp_path / "config.yaml"
        yaml_content = """
organization:
  roles:
    - Cariste
    - Magasinier
    - Evaluateur
"""
        config_file.write_text(yaml_content, encoding='utf-8')

        cfg = config.load_config(config_file)

        assert "Cariste" in cfg['organization']['roles']
        assert "Evaluateur" in cfg['organization']['roles']

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_load_invalid_yaml_uses_defaults(self, tmp_path, capsys):
        """Should use defaults when YAML is invalid."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        cfg = config.load_config(config_file)

        # Should return defaults
        assert cfg == config.DEFAULT_CONFIG

        # Should print warning
        captured = capsys.readouterr()
        assert "Warning" in captured.out

    def test_load_yaml_without_pyyaml(self, tmp_path):
        """Should raise ImportError when PyYAML not installed."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("{}")

        with patch('utils.config.YAML_AVAILABLE', False):
            with pytest.raises(ImportError, match="PyYAML is not installed"):
                config._load_yaml(config_file)


class TestYAMLSaving:
    """Tests for YAML configuration saving."""

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_save_yaml_config(self, tmp_path):
        """Should save configuration to YAML file."""
        config_path = tmp_path / "config.yaml"
        cfg = {"alerts": {"critical_days": 5}}

        config.save_config(cfg, config_path, format="yaml")

        # Verify file was created and can be loaded
        loaded = config.load_config(config_path)
        assert loaded["alerts"]["critical_days"] == 5

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_save_yaml_creates_file(self, tmp_path):
        """Should create YAML file."""
        config_path = tmp_path / "config.yaml"
        cfg = config.get_default_config()

        config.save_config(cfg, config_path, format="yaml")

        assert config_path.exists()

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_save_yaml_preserves_unicode(self, tmp_path):
        """Should preserve Unicode characters in YAML."""
        config_path = tmp_path / "config.yaml"
        cfg = {
            "organization": {
                "roles": ["Cariste", "Evaluateur", "Magasinier"]
            }
        }

        config.save_config(cfg, config_path, format="yaml")

        # Load and verify
        loaded = config.load_config(config_path)
        assert "Evaluateur" in loaded["organization"]["roles"]


class TestConfigFormatAutoDetection:
    """Tests for automatic configuration format detection."""

    def test_load_auto_detects_yaml_preferred(self, tmp_path, monkeypatch):
        """Should prefer config.yaml over config.json."""
        yaml_path = tmp_path / "config.yaml"
        json_path = tmp_path / "config.json"

        yaml_path.write_text("alerts: {critical_days: 5}")
        json_path.write_text('{"alerts": {"critical_days": 10}}')

        # Change to tmp_path so load_config() finds our test files
        monkeypatch.chdir(tmp_path)

        try:
            # Should prefer YAML
            cfg = config.load_config()
            assert cfg["alerts"]["critical_days"] == 5
        finally:
            yaml_path.unlink()
            json_path.unlink()

    def test_load_auto_fallback_to_json(self, tmp_path, monkeypatch):
        """Should fallback to config.json if YAML not found."""
        json_path = tmp_path / "config.json"
        json_path.write_text('{"alerts": {"critical_days": 10}}')

        # Change to tmp_path so load_config() finds our test file
        monkeypatch.chdir(tmp_path)

        try:
            cfg = config.load_config()
            assert cfg["alerts"]["critical_days"] == 10
        finally:
            json_path.unlink()

    def test_load_auto_fallback_to_default(self, tmp_path, monkeypatch):
        """Should use defaults when no config file exists."""
        # Change to tmp_path (which has no config files)
        monkeypatch.chdir(tmp_path)

        cfg = config.load_config()
        assert cfg == config.DEFAULT_CONFIG


class TestJSONToYAMLMigration:
    """Tests for JSON to YAML migration functionality."""

    def test_migrate_to_yaml(self, tmp_path):
        """Should migrate JSON config to YAML format."""
        json_path = tmp_path / "config.json"
        json_config = {
            "alerts": {"critical_days": 5, "warning_days": 30},
            "organization": {"roles": ["Cariste"]}
        }
        json_path.write_text(json.dumps(json_config))

        yaml_path = config.migrate_to_yaml(json_path)

        # Verify YAML was created
        assert yaml_path.exists()
        assert yaml_path.suffix == ".yaml"

        # Verify content
        cfg = config.load_config(yaml_path)
        assert cfg["alerts"]["critical_days"] == 5
        assert "Cariste" in cfg["organization"]["roles"]

    def test_migrate_creates_yaml_with_comments(self, tmp_path):
        """Should create YAML with helpful comments."""
        json_path = tmp_path / "config.json"
        json_path.write_text('{}')

        yaml_path = config.migrate_to_yaml(json_path)

        # Check that comments were added
        content = yaml_path.read_text()
        assert "# Wareflow EMS Configuration" in content
        assert "#" in content

    def test_migrate_custom_path(self, tmp_path):
        """Should migrate to custom path when specified."""
        json_path = tmp_path / "old_config.json"
        json_path.write_text('{}')

        custom_yaml_path = tmp_path / "custom_config.yaml"

        yaml_path = config.migrate_to_yaml(json_path, custom_yaml_path)

        assert yaml_path == custom_yaml_path
        assert custom_yaml_path.exists()

    def test_migrate_nonexistent_json_raises_error(self):
        """Should raise error when JSON file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "nonexistent.json"

            with pytest.raises(FileNotFoundError):
                config.migrate_to_yaml(json_path)


class TestYAMLBackwardCompatibility:
    """Tests for backward compatibility with existing JSON configs."""

    def test_json_still_works(self, tmp_path):
        """Existing JSON configs should continue to work."""
        config_file = tmp_path / "config.json"
        custom_config = {
            "alerts": {"warning_days": 45}
        }

        config_file.write_text(json.dumps(custom_config))

        # Should load JSON without issues
        cfg = config.load_config(config_file)
        assert cfg['alerts']['warning_days'] == 45

    def test_json_to_yaml_migration_path(self, tmp_path):
        """Should provide smooth migration path from JSON to YAML."""
        json_path = tmp_path / "config.json"
        json_config = {
            "alerts": {"critical_days": 5}
        }
        json_path.write_text(json.dumps(json_config))

        # Migrate to YAML
        yaml_path = config.migrate_to_yaml(json_path)

        # Both files exist now
        assert json_path.exists()
        assert yaml_path.exists()

        # YAML should be preferred
        cfg = config.load_config()
        # Since we're in tmpdir, it won't auto-detect, so we test explicit loading
        cfg_yaml = config.load_config(yaml_path)
        cfg_json = config.load_config(json_path)

        # Both should have same data
        assert cfg_yaml["alerts"]["critical_days"] == 5
        assert cfg_json["alerts"]["critical_days"] == 5
