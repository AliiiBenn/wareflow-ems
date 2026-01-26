"""Centralized version information for Wareflow EMS.

This module provides the single source of truth for application versioning.
Version is defined in pyproject.toml and extracted here during build.
"""

__version__ = "0.1.0"
__version_info__ = (0, 1, 0)

# Additional metadata
__author__ = "Wareflow"
__license__ = "MIT"
__description__ = "Warehouse Employee Management System"


def get_version() -> str:
    """Get the current application version.

    Returns:
        Version string (e.g., "0.1.0")
    """
    return __version__


def get_version_info() -> tuple:
    """Get the current application version as tuple.

    Returns:
        Version tuple (e.g., (0, 1, 0))
    """
    return __version_info__


def parse_version(version_string: str) -> tuple:
    """Parse version string into tuple.

    Args:
        version_string: Version string (e.g., "0.1.0")

    Returns:
        Version tuple (major, minor, patch)
    """
    try:
        parts = version_string.split(".")
        if len(parts) == 3:
            return tuple(int(p) for p in parts)
        raise ValueError(f"Invalid version format: {version_string}")
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Cannot parse version '{version_string}': {e}")
