"""Flet application entry point."""

import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import flet as ft
from .state.app_state import get_app_state
from .theme import AppTheme
from .constants import MAX_CONTENT_WIDTH


def ensure_database():
    """Ensure database is initialized before starting the app."""
    db_path = Path("employee_manager.db")

    # If database doesn't exist, initialize it
    if not db_path.exists():
        from database.connection import init_database
        init_database(db_path)
        print(f"Database initialized: {db_path}")


def main(page: ft.Page):
    """Main entry point for the Flet application."""
    # Ensure database exists BEFORE getting app state (lock manager needs DB)
    ensure_database()

    # Initialize database connection BEFORE acquiring lock
    from database.connection import database
    db_path = Path("employee_manager.db")
    database.init(db_path)

    # Get application state AFTER database is initialized
    app_state = get_app_state()

    # Try to acquire lock
    if not app_state.acquire_lock():
        page.title = "Employee Manager - Lock Error"
        page.add(
            ft.Text(
                            "Unable to acquire application lock",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.RED
                        ),
                    ft.Text(app_state.lock_status, size=14),
                    ft.Text("Another instance may be running.", size=12),
        )
        return

    # Configure page
    page.title = "Employee Manager"
    page.window_width = 1400
    page.window_height = 900
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = AppTheme.get_dark_theme()
    page.dark_theme = AppTheme.get_dark_theme()
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0

    # Add cleanup handler to release lock when app closes
    def on_close(e):
        """Release lock when application closes."""
        app_state.release_lock()

    page.on_close = on_close

    # Register all views with router
    from ui.views_new import register_all_views
    register_all_views()

    # Build and add app shell
    from ui.layout import AppShell

    app_shell = AppShell(page, current_route="/")

    # Add app shell to page
    page.add(app_shell)


if __name__ == "__main__":
    try:
        ft.run(main)
    finally:
        # Ensure lock is released even if app crashes
        try:
            app_state = get_app_state()
            # Check if lock exists (lock manager has _lock attribute)
            if app_state.lock_manager._lock is not None:
                app_state.release_lock()
        except Exception:
            pass  # Silent cleanup
