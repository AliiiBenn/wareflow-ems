"""Flet application entry point."""

import sys
import os
from pathlib import Path

# Force web server mode to avoid flet-desktop dependency issues
os.environ["FLET_FORCE_WEB_SERVER"] = "1"

# Add src directory to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import flet as ft
from .state.app_state import get_app_state, reset_app_state
from .state.navigation import NavigationHandler, Route, create_basic_view


def ensure_database():
    """Ensure database is initialized before starting the app."""
    db_path = Path("employee_manager.db")

    # If database doesn't exist, initialize it
    if not db_path.exists():
        from database.connection import init_database
        init_database(db_path)
        print(f"Database initialized: {db_path}")


def run_app():
    """Main entry point for the Flet application."""
    # Ensure database exists before starting
    ensure_database()
    ft.run(entry_point, view=ft.AppView.WEB_BROWSER, port=8080)


def entry_point(page: ft.Page):
    """
    Initialize and run the Flet application.

    Args:
        page: The Flet page instance
    """
    # Get or create the global application state
    app_state = get_app_state()

    # Try to acquire the application lock
    if not app_state.acquire_lock():
        # If lock acquisition fails, show error and exit
        page.window.width = 400
        page.window.height = 200
        page.title = "Employee Manager - Lock Error"
        page.theme_mode = ft.ThemeMode.LIGHT

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.icons.LOCK_OUTLINE,
                            size=64,
                            color=ft.colors.RED
                        ),
                        ft.Text(
                            "Unable to acquire application lock",
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            app_state.lock_status,
                            size=14,
                            color=ft.colors.GREY_600
                        ),
                        ft.Text(
                            "Another instance may be running.",
                            size=12,
                            color=ft.colors.GREY_500
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            )
        )
        return

    # Configure the page
    configure_page(page, app_state)

    # Initialize navigation
    nav_handler = NavigationHandler(page)

    # Register placeholder views (will be replaced with actual implementations)
    register_placeholder_views(nav_handler)

    # Navigate to dashboard by default
    nav_handler.navigate(Route.DASHBOARD)

    # Set up route change handler
    def route_change(route: str):
        """Handle route changes."""
        nav_handler.navigate(route)

    page.on_route_change = route_change

    # Set up view pop handler (for back navigation)
    def view_pop(view):
        """Handle back navigation."""
        nav_handler.go_back()

    page.on_view_pop = view_pop

    # Update the page
    page.update()


def configure_page(page: ft.Page, app_state):
    """
    Configure the Flet page with basic settings.

    Args:
        page: The Flet page instance
        app_state: The application state instance
    """
    # Window settings
    page.title = "Employee Manager"
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 800
    page.window.min_height = 600
    page.window.center()

    # Theme settings
    page.theme_mode = app_state.get_flet_theme_mode()

    # Configure theme with our color palette
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#0EA5E9",      # Sky blue
            on_primary="#FFFFFF",
            primary_container="#E0F2FE",
            on_primary_container="#0C4A6E",
            secondary="#64748B",    # Slate
            on_secondary="#FFFFFF",
            error="#EF4444",        # Red
            on_error="#FFFFFF",
            error_container="#FEE2E2",
            on_error_container="#7F1D1D",
            warning="#F59E0B",      # Orange
            success="#10B981",      # Green
        ),
        use_material3=True,
    )

    # Page settings
    page.padding = 0
    page.bgcolor = ft.colors.GREY_50

    # Configure app bar
    page.appbar = ft.AppBar(
        title=ft.Text("Employee Manager", weight=ft.FontWeight.BOLD),
        bgcolor=ft.colors.SURFACE,
        actions=[
            # Lock status indicator
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.icons.LOCK_OPEN if "Unlocked" in app_state.lock_status
                            else ft.icons.LOCK,
                            size=16,
                            color=ft.colors.GREEN if "Locked" in app_state.lock_status
                            else ft.colors.RED
                        ),
                        ft.Text(
                            app_state.lock_status,
                            size=12,
                            color=ft.colors.GREY_700
                        ),
                    ],
                    spacing=5,
                ),
                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                bgcolor=ft.colors.GREY_100,
                border_radius=20,
            ),
        ],
    )


def register_placeholder_views(nav_handler: NavigationHandler):
    """
    Register placeholder views for all routes.

    These will be replaced with actual view implementations in later phases.

    Args:
        nav_handler: The navigation handler instance
    """
    # Dashboard/Alerts placeholder
    nav_handler.register_view(
        Route.DASHBOARD,
        lambda page, args: create_basic_view(
            Route.DASHBOARD,
            "Dashboard",
            ft.Column(
                [
                    ft.Text("Dashboard coming soon...", size=24),
                    ft.Text("This will show statistics and alerts", size=16),
                ],
                spacing=10,
            )
        )
    )

    # Employees list placeholder
    nav_handler.register_view(
        Route.EMPLOYEES,
        lambda page, args: create_basic_view(
            Route.EMPLOYEES,
            "Employees",
            ft.Column(
                [
                    ft.Text("Employee list coming soon...", size=24),
                    ft.Text("This will show all employees", size=16),
                ],
                spacing=10,
            )
        )
    )

    # Employee detail placeholder
    nav_handler.register_view(
        Route.EMPLOYEE_DETAIL,
        lambda page, args: create_basic_view(
            Route.EMPLOYEE_DETAIL,
            f"Employee {args.get('id', 'Unknown')}",
            ft.Column(
                [
                    ft.Text(f"Employee detail for ID: {args.get('id', 'Unknown')}", size=24),
                    ft.Text("This will show employee details", size=16),
                ],
                spacing=10,
            )
        )
    )

    # Documents placeholder
    nav_handler.register_view(
        Route.DOCUMENTS,
        lambda page, args: create_basic_view(
            Route.DOCUMENTS,
            "Documents",
            ft.Column(
                [
                    ft.Text("Documents management coming soon...", size=24),
                    ft.Text("This will show document management", size=16),
                ],
                spacing=10,
            )
        )
    )

    # Settings placeholder
    nav_handler.register_view(
        Route.SETTINGS,
        lambda page, args: create_basic_view(
            Route.SETTINGS,
            "Settings",
            ft.Column(
                [
                    ft.Text("Settings coming soon...", size=24),
                    ft.Text("This will show application settings", size=16),
                ],
                spacing=10,
            )
        )
    )


if __name__ == "__main__":
    run_app()
