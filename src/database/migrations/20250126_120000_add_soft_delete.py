"""Migration script to add soft delete support to all tables.

This script adds soft delete fields to existing databases:
- employees: deleted_at, deleted_by, deletion_reason
- caces: deleted_at, deleted_by, deletion_reason
- medical_visits: deleted_at, deleted_by, deletion_reason
- online_trainings: deleted_at, deleted_by, deletion_reason

Soft delete allows marking records as deleted without permanently removing them.
Records can be restored from the trash view.

Run this script to upgrade existing databases.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import database
from utils.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO", enable_console=True, enable_file=True)
logger = get_logger(__name__)


def migrate():
    """
    Add soft delete fields to existing database.

    This function adds:
    - deleted_at TIMESTAMP NULL
    - deleted_by TEXT NULL
    - deletion_reason TEXT NULL

    To all main tables: employees, caces, medical_visits, online_trainings
    It's safe to run multiple times - columns will only be added if they don't exist.
    """
    logger.info("Starting soft delete migration...")

    try:
        # Connect to database
        if database.is_closed():
            database.connect()

        cursor = database.cursor()

        # Employees table
        logger.info("Adding soft delete fields to employees table...")

        employee_columns = [
            ("deleted_at", "TIMESTAMP NULL"),
            ("deleted_by", "TEXT NULL"),
            ("deletion_reason", "TEXT NULL"),
        ]

        for column_name, column_type in employee_columns:
            try:
                cursor.execute(
                    f"ALTER TABLE employees ADD COLUMN {column_name} {column_type}"
                )
                logger.info(f"Added column: employees.{column_name}")
            except Exception as e:
                # Column might already exist
                if "duplicate column" in str(e).lower():
                    logger.info(f"Column already exists: employees.{column_name}")
                else:
                    logger.warning(f"Failed to add column {column_name}: {e}")

        # CACES table
        logger.info("Adding soft delete fields to caces table...")

        for column_name, column_type in employee_columns:
            try:
                cursor.execute(
                    f"ALTER TABLE caces ADD COLUMN {column_name} {column_type}"
                )
                logger.info(f"Added column: caces.{column_name}")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info(f"Column already exists: caces.{column_name}")
                else:
                    logger.warning(f"Failed to add column {column_name}: {e}")

        # Medical visits table
        logger.info("Adding soft delete fields to medical_visits table...")

        for column_name, column_type in employee_columns:
            try:
                cursor.execute(
                    f"ALTER TABLE medical_visits ADD COLUMN {column_name} {column_type}"
                )
                logger.info(f"Added column: medical_visits.{column_name}")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info(f"Column already exists: medical_visits.{column_name}")
                else:
                    logger.warning(f"Failed to add column {column_name}: {e}")

        # Online trainings table
        logger.info("Adding soft delete fields to online_trainings table...")

        for column_name, column_type in employee_columns:
            try:
                cursor.execute(
                    f"ALTER TABLE online_trainings ADD COLUMN {column_name} {column_type}"
                )
                logger.info(f"Added column: online_trainings.{column_name}")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info(f"Column already exists: online_trainings.{column_name}")
                else:
                    logger.warning(f"Failed to add column {column_name}: {e}")

        # Commit changes
        database.commit()

        logger.info("Soft delete migration completed successfully!")
        logger.info("")
        logger.info("What's new:")
        logger.info("- All records can now be soft-deleted instead of permanently removed")
        logger.info("- Use soft_delete() method on models to mark as deleted")
        logger.info("- Use restore() method on models to restore deleted records")
        logger.info("- Use without_deleted() query helper to filter out deleted records")
        logger.info("- Use deleted() query helper to get only deleted records")
        logger.info("")
        logger.info("Next steps:")
        logger.info("- Update your code to use soft_delete() instead of delete_instance()")
        logger.info("- Add trash view to allow users to restore deleted items")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        database.rollback()
        raise
    finally:
        if not database.is_closed():
            database.close()


def rollback():
    """
    Rollback soft delete migration (NOT RECOMMENDED).

    WARNING: This will remove the soft delete columns but any data
    in those columns will be LOST. Soft-deleted records will become
    permanently inaccessible.

    Only use this if you're sure you want to remove soft delete functionality.
    """
    logger.warning("Starting soft delete ROLLBACK...")
    logger.warning("WARNING: This will permanently delete all soft delete metadata!")
    logger.warning("Soft-deleted records will become permanently lost.")

    # For safety, we don't implement rollback
    logger.error("Rollback not implemented for safety reasons.")
    logger.error("Soft delete columns should be kept to maintain data integrity.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback()
    else:
        migrate()
