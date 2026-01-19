"""Flet application entry point."""

import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import flet as ft
from .state.app_state import get_app_state


def ensure_database():
    """Ensure database is initialized before starting the app."""
    db_path = Path("employee_manager.db")

    # If database doesn't exist, initialize it
    if not db_path.exists():
        from database.connection import init_database
        init_database(db_path)
        print(f"Database initialized: {db_path}")


def route_change(route: str, page: ft.Page, app_state):
    """Handle route changes and build views accordingly."""
    page.views.clear()

    # Dashboard view
    if page.route == "/":
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Employee Manager")),
                    ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Coming soon...", size=16),
                ],
            )
        )

    # Employees list view
    elif page.route == "/employees":
        page.views.append(
            ft.View(
                "/employees",
                [
                    ft.AppBar(title=ft.Text("Employees")),
                    ft.Text("Employees", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Coming soon...", size=16),
                ],
            )
        )

    # Employee detail view
    elif page.route.startswith("/employee/"):
        emp_id = page.route.split("/")[-1]
        page.views.append(
            ft.View(
                page.route,
                [
                    ft.AppBar(title=ft.Text(f"Employee {emp_id}")),
                    ft.Text(f"Employee {emp_id}", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Coming soon...", size=16),
                ],
            )
        )

    # Documents view
    elif page.route == "/documents":
        page.views.append(
            ft.View(
                "/documents",
                [
                    ft.AppBar(title=ft.Text("Documents")),
                    ft.Text("Documents", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Coming soon...", size=16),
                ],
            )
        )

    # Settings view
    elif page.route == "/settings":
        page.views.append(
            ft.View(
                "/settings",
                [
                    ft.AppBar(title=ft.Text("Settings")),
                    ft.Text("Settings", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Coming soon...", size=16),
                ],
            )
        )

    page.update()


def view_pop(view, page: ft.Page):
    """Handle back navigation."""
    page.views.pop()
    top_view = page.views[-1]
    page.route = top_view.route
    page.update()


def main(page: ft.Page):
    """Main entry point for the Flet application."""
    # Ensure database exists before starting
    ensure_database()

    # Get application state
    app_state = get_app_state()

    # Try to acquire lock
    if not app_state.acquire_lock():
        page.title = "Employee Manager - Lock Error"
        page.add(
            ft.Text(
                            "⛔ Unable to acquire application lock",
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
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Add content directly to page (like the test)
    page.add(
        ft.AppBar(title=ft.Text("Employee Manager")),
        ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD),
        ft.Text("Coming soon...", size=16),
    )


if __name__ == "__main__":
    ft.run(main)
