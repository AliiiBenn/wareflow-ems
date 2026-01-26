"""Script to run database migrations manually."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.connection import database, init_database
from database.migrations import get_pending_migrations, run_migration
from database.migration_model import get_applied_migrations
from utils.config import get_database_path


def main():
    """Run pending database migrations."""
    try:
        # Get database path from config
        db_path = get_database_path()

        print(f"Database: {db_path}")

        # Initialize database connection
        init_database(db_path)

        # Get applied migrations
        applied = get_applied_migrations()
        print(f"Applied migrations: {len(applied)}")

        # Get migrations directory
        migrations_dir = Path(__file__).parent.parent / "src" / "database" / "migrations"

        # Get pending migrations
        pending = get_pending_migrations(migrations_dir)
        print(f"Pending migrations: {len(pending)}")

        if not pending:
            print("Database is up to date!")
            return

        # Show pending migrations
        print("\nPending migrations:")
        for i, migration in enumerate(pending, 1):
            print(f"  {i}. {migration.name}")

        # Run migrations
        print("\nRunning migrations...")
        for migration in pending:
            print(f"  Running: {migration.name}...", end=" ")
            run_migration(migration)
            print("OK")

        print("\nAll migrations applied successfully!")

    except Exception as e:
        print(f"\nMigration failed: {e}")
        raise


if __name__ == "__main__":
    main()
