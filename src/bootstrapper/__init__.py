"""Bootstrapper module for Wareflow EMS.

This module provides initialization and setup functionality for
Wareflow EMS, including the interactive setup wizard and
first-run configuration.
"""

from . import update_checker, wizard

__all__ = ["update_checker", "wizard"]
