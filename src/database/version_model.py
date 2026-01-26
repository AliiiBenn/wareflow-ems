"""Application version tracking model.

This model tracks the current application and schema version in the database,
enabling automatic migration detection and execution.
"""

from datetime import datetime
from typing import Optional

from peewee import *

from database.connection import database


class AppVersion(Model):
    """Track application and schema version."""

    id = AutoField()
    app_version = CharField(max_length=20, unique=True)  # e.g., "0.1.0"
    schema_version = IntegerField(default=1)  # e.g., 1
    applied_at = DateTimeField(default=datetime.now, index=True)
    description = CharField(max_length=255, null=True)

    class Meta:
        database = database
        table_name = "app_version"


def get_current_app_version() -> Optional[str]:
    """Get the current application version from database.

    Returns:
        Current app version string or None if not set
    """
    if database.is_closed():
        database.connect()

    try:
        latest = (AppVersion
                  .select()
                  .order_by(AppVersion.applied_at.desc())
                  .first())
        return latest.app_version if latest else None
    except Exception:
        return None


def set_version(app_version: str, schema_version: int, description: Optional[str] = None) -> AppVersion:
    """Set the current application and schema version.

    Args:
        app_version: Application version string
        schema_version: Schema version number
        description: Optional description of the version

    Returns:
        Created AppVersion record
    """
    if database.is_closed():
        database.connect()

    return AppVersion.create(
        app_version=app_version,
        schema_version=schema_version,
        description=description
    )


def get_current_schema_version() -> Optional[int]:
    """Get the current schema version from database.

    Returns:
        Current schema version or None if not set
    """
    if database.is_closed():
        database.connect()

    try:
        latest = (AppVersion
                  .select()
                  .order_by(AppVersion.applied_at.desc())
                  .first())
        return latest.schema_version if latest else None
    except Exception:
        return None
