"""Update checker for detecting new application versions.

This module provides functionality to check for updates via GitHub Releases API,
compare versions, and notify users when updates are available.

Usage:
    checker = UpdateChecker()
    update_info = checker.check_for_updates()
    if update_info:
        print(f"Update available: {update_info['version']}")
"""

import os
import sys
from typing import Dict, Optional

try:
    import requests
    from packaging.version import parse as parse_version
except ImportError:
    requests = None
    parse_version = None


from utils.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO", enable_console=True, enable_file=False)
logger = get_logger(__name__)


class UpdateChecker:
    """Check for application updates from GitHub Releases."""

    GITHUB_API_URL = "https://api.github.com/repos/wareflowx/wareflow-ems/releases/latest"
    GITHUB_RELEASES_URL = "https://api.github.com/repos/wareflowx/wareflow-weapons/releases"

    def __init__(self, current_version: str = None, timeout: int = 10):
        """Initialize update checker.

        Args:
            current_version: Current application version (e.g., "1.2.0")
            timeout: Request timeout in seconds
        """
        if current_version is None:
            current_version = self._get_current_version()

        self.current_version = current_version
        self.timeout = timeout

    def _get_current_version(self) -> str:
        """Get current version from employee_manager module."""
        try:
            from employee_manager import __version__
            # Remove 'v' prefix if present
            version = __version__.lstrip('v')
            return version
        except ImportError:
            logger.warning("Could not import __version__ from employee_manager")
            return "0.0.0"

    def check_for_updates(self) -> Optional[Dict]:
        """Check for updates from GitHub Releases API.

        Returns:
            Dictionary with update information if update available:
            {
                'version': '1.3.0',
                'tag_name': 'v1.3.0',
                'html_url': 'https://github.com/wareflowx/wareflow-ems/releases/tag/v1.3.0',
                'body': 'Release notes...',
                'published_at': '2025-01-15T10:00:00Z',
                'prerelease': False
            }
            None if no update available or error occurs
        """
        if requests is None:
            logger.error("requests library not available")
            return None

        try:
            logger.info(f"Checking for updates (current: {self.current_version})...")

            # Fetch latest release from GitHub API
            response = requests.get(
                self.GITHUB_API_URL,
                timeout=self.timeout
            )
            response.raise_for_status()

            release = response.json()

            # Extract version from tag name
            tag_name = release.get('tag_name', '')
            latest_version = tag_name.lstrip('v')

            # Skip if prerelease
            if release.get('prerelease', False):
                logger.info(f"Latest release {tag_name} is prerelease, skipping")
                return None

            # Compare versions
            if parse_version and self._is_newer_version(latest_version):
                logger.info(f"Update available: {self.current_version} → {latest_version}")

                return {
                    'version': latest_version,
                    'tag_name': tag_name,
                    'html_url': release.get('html_url', ''),
                    'body': release.get('body', ''),
                    'published_at': release.get('published_at', ''),
                    'prerelease': release.get('prerelease', False),
                    'author': release.get('author', {}).get('login', 'unknown'),
                }
            else:
                logger.info(f"No update available (current: {self.current_version}, latest: {latest_version})")
                return None

        except requests.RequestException as e:
            logger.error(f"Failed to check for updates: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error checking for updates: {e}")
            return None

    def _is_newer_version(self, latest_version: str) -> bool:
        """Check if latest version is newer than current version.

        Args:
            latest_version: Latest version string (e.g., "1.3.0")

        Returns:
            True if latest_version is newer
        """
        try:
            return parse_version(latest_version) > parse_version(self.current_version)
        except Exception as e:
            logger.error(f"Failed to compare versions: {e}")
            return False

    def get_update_info(self) -> Optional[Dict]:
        """Get detailed update information.

        Returns:
            Dictionary with current and latest version info
        """
        update_available = self.check_for_updates()

        return {
            'current_version': self.current_version,
            'latest_version': update_available['version'] if update_available else self.current_version,
            'update_available': update_available is not None,
            'update_info': update_available if update_available else None,
        }


def check_for_updates(current_version: str = None) -> Optional[Dict]:
    """Convenience function to check for updates.

    Args:
        current_version: Current application version

    Returns:
        Dictionary with update information if update available, None otherwise
    """
    checker = UpdateChecker(current_version)
    return checker.check_for_updates()


def get_update_info(current_version: str = None) -> Dict:
    """Convenience function to get update information.

    Args:
        current_version: Current application version

    Returns:
        Dictionary with current and latest version info
    """
    checker = UpdateChecker(current_version)
    return checker.get_update_info()


def is_update_available(current_version: str = None) -> bool:
    """Check if an update is available.

    Args:
        current_version: Current application version

    Returns:
        True if update available, False otherwise
    """
    info = get_update_info(current_version)
    return info['update_available']


if __name__ == "__main__":
    # Test update checker
    import json

    info = get_update_info()
    print(json.dumps(info, indent=2))
