"""Tests for update checker module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
from packaging.version import parse as parse_version

from bootstrapper.update_checker import (
    UpdateChecker,
    check_for_updates,
    get_update_info,
    is_update_available,
)


class TestUpdateChecker:
    """Test suite for UpdateChecker class."""

    def test_init_with_version(self):
        """Test initialization with version."""
        checker = UpdateChecker(current_version="1.2.0")
        assert checker.current_version == "1.2.0"
        assert checker.timeout == 10

    def test_init_without_version(self):
        """Test initialization without version."""
        with patch('bootstrapper.update_checker.UpdateChecker._get_current_version', return_value="1.0.0"):
            checker = UpdateChecker()
            assert checker.current_version == "1.0.0"

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        checker = UpdateChecker(current_version="1.2.0", timeout=30)
        assert checker.timeout == 30

    def test_get_current_version(self):
        """Test getting current version."""
        with patch('bootstrapper.update_checker.UpdateChecker._get_current_version', return_value="2.0.0"):
            checker = UpdateChecker(current_version="1.5.0")
            version = checker._get_current_version()
            assert version == "2.0.0"

    def test_is_newer_version_true(self):
        """Test version comparison when newer."""
        checker = UpdateChecker(current_version="1.2.0")
        assert checker._is_newer_version("1.3.0") is True
        assert checker._is_newer_version("2.0.0") is True

    def test_is_newer_version_false(self):
        """Test version comparison when not newer."""
        checker = UpdateChecker(current_version="1.2.0")
        assert checker._is_newer_version("1.1.0") is False
        assert checker._is_newer_version("1.2.0") is False

    def test_is_newer_version_equal(self):
        """Test version comparison when equal."""
        checker = UpdateChecker(current_version="1.2.0")
        assert checker._is_newer_version("1.2.0") is False

    def test_is_newer_version_invalid(self):
        """Test version comparison with invalid version."""
        checker = UpdateChecker(current_version="1.2.0")
        # Invalid versions should return False
        assert checker._is_newer_version("invalid") is False

    def test_check_for_updates_newer_available(self):
        """Test check_for_updates with newer version available."""
        mock_release = {
            'tag_name': 'v1.3.0',
            'html_url': 'https://github.com/wareflowx/wareflow-ems/releases/tag/v1.3.0',
            'body': 'Release notes here',
            'published_at': '2025-01-15T10:00:00Z',
            'prerelease': False,
            'author': {'login': 'test'},
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_release
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            checker = UpdateChecker(current_version="1.2.0")
            result = checker.check_for_updates()

        assert result is not None
        assert result['version'] == "1.3.0"
        assert result['tag_name'] == "v1.3.0"
        assert result['html_url'] == "https://github.com/wareflowx/wareflow-ems/releases/tag/v1.3.0"
        assert result['body'] == "Release notes here"

    def test_check_for_updates_prerelease_skipped(self):
        """Test that prerelease versions are skipped."""
        mock_release = {
            'tag_name': 'v2.0.0-beta',
            'html_url': 'https://github.com/wareflowx/wareflow-ems/releases/tag/v2.0.0',
            'body': 'Beta release',
            'published_at': '2025-01-15T10:00:00Z',
            'prerelease': True,
            'author': {'login': 'test'},
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_release
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            checker = UpdateChecker(current_version="1.2.0")
            result = checker.check_for_updates()

        assert result is None  # Prerelease should be skipped

    def test_check_for_updates_same_version(self):
        """Test check_for_updates when already on latest."""
        mock_release = {
            'tag_name': 'v1.2.0',
            'html_url': 'https://github.com/wareflowx/wareflow-ems/releases/tag/v1.2.0',
            'body': 'Same version',
            'prerelease': False,
            'author': {'login': 'test'},
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_release
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            checker = UpdateChecker(current_version="1.2.0")
            result = checker.check_for_updates()

        assert result is None  # Same version, no update

    def test_check_for_updates_request_error(self):
        """Test check_for_updates handles request errors gracefully."""
        with patch('requests.get', side_effect=requests.RequestException("Network error")):
            checker = UpdateChecker(current_version="1.2.0")
            result = checker.check_for_updates()

        assert result is None  # Should return None on error

    def test_check_for_updates_no_requests_library(self):
        """Test check_for_updates when requests is not available."""
        with patch('bootstrapper.update_checker.requests', None):
            checker = UpdateChecker(current_version="1.2.0")
            result = checker.check_for_updates()

        assert result is None

    def test_get_update_info_with_update(self):
        """Test get_update_info when update is available."""
        mock_release = {
            'tag_name': 'v1.3.0',
            'html_url': 'https://github.com/wareflowx/wareflow-ems/releases/tag/v1.3.0',
            'body': 'New release',
            'prerelease': False,
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_release
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            checker = UpdateChecker(current_version="1.2.0")
            info = checker.get_update_info()

        assert info['current_version'] == "1.2.0"
        assert info['latest_version'] == "1.3.0"
        assert info['update_available'] is True
        assert info['update_info'] is not None
        assert info['update_info']['version'] == "1.3.0"

    def test_get_update_info_no_update(self):
        """Test get_update_info when no update available."""
        mock_release = {
            'tag_name': 'v1.2.0',
            'html_url': 'https://github.com/wareflowx/wareflow-ems/releases/tag/v1.2.0',
            'body': 'Same version',
            'prerelease': False,
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_release
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            checker = UpdateChecker(current_version="1.2.0")
            info = checker.get_update_info()

        assert info['current_version'] == "1.2.0"
        assert info['latest_version'] == "1.2.0"
        assert info['update_available'] is False
        assert info['update_info'] is None


class TestConvenienceFunctions:
    """Test suite for convenience functions."""

    def test_check_for_updates_convenience(self):
        """Test check_for_updates convenience function."""
        mock_release = {
            'tag_name': 'v1.3.0',
            'html_url': 'https://github.com/wareflowx/wareflow-ems/releases/tag/v1.3.0',
            'body': 'New release',
            'prerelease': False,
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_release
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = check_for_updates(current_version="1.2.0")

        assert result is not None
        assert result['version'] == "1.3.0"

    def test_get_update_info_convenience(self):
        """Test get_update_info convenience function."""
        mock_release = {
            'tag_name': 'v1.3.0',
            'html_url': 'https://github.com/wareflowx/wareflow-ems/releases/tag/v1.3.0',
            'body': 'New release',
            'prerelease': False,
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_release
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            info = get_update_info(current_version="1.2.0")

        assert info['update_available'] is True
        assert info['latest_version'] == "1.3.0"

    def test_is_update_available_true(self):
        """Test is_update_available when update exists."""
        mock_release = {
            'tag_name': 'v1.3.0',
            'prerelease': False,
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_release
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            available = is_update_available(current_version="1.2.0")

        assert available is True

    def test_is_update_available_false(self):
        """Test is_update_available when no update."""
        mock_release = {
            'tag_name': 'v1.2.0',
            'prerelease': False,
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_release
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            available = is_update_available(current_version="1.2.0")

        assert available is False

    def test_is_update_available_prerelease_skipped(self):
        """Test is_update_available skips prereleases."""
        mock_release = {
            'tag_name': 'v2.0.0-beta',
            'prerelease': True,
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_release
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            available = is_update_available(current_version="1.2.0")

        assert available is False  # Prerelease should be skipped
