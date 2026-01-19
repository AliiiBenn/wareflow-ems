"""EmployeeListItem widget - Displays an employee in a list."""

import flet as ft
from typing import Optional, Callable


class EmployeeListItem(ft.Container):
    """
    A list item widget displaying an employee with quick info.

    Shows name, status, workspace, role, and compliance score.
    Clickable to navigate to employee detail view.

    Args:
        employee_id: Employee UUID
        employee_name: Full name for display
        status: Employee status ('active' or 'inactive')
        workspace: Workspace assignment
        role: Job role
        compliance_score: Compliance score (0-100)
        on_click: Click handler (optional)

    Example:
        EmployeeListItem(
            employee_id='123',
            employee_name='John Doe',
            status='active',
            workspace='Quai',
            role='Préparateur',
            compliance_score=85,
            on_click=lambda e: print("Clicked")
        )
    """

    def __init__(
        self,
        employee_id: str,
        employee_name: str,
        status: str,
        workspace: str,
        role: str,
        compliance_score: int,
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        # Determine styling based on status and compliance
        status_color = self._get_status_color(status)
        compliance_color, compliance_text = self._get_compliance_style(compliance_score)

        # Build content
        content = ft.ListTile(
            leading=ft.Text(
                "👤",
                size=32,
            ),
            title=ft.Text(
                employee_name,
                size=16,
                weight=ft.FontWeight.BOLD,
            ),
            subtitle=ft.Column(
                [
                    ft.Text(
                        f"{workspace} • {role}",
                        size=12,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                status.capitalize(),
                                size=10,
                                color=status_color,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(" • ", size=10, color=ft.Colors.GREY_500),
                            ft.Text(
                                f"{compliance_score}%",
                                size=10,
                                color=compliance_color,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=2,
            ),
            trailing=ft.Column(
                [
                    ft.Text(
                        compliance_text,
                        size=11,
                        color=compliance_color,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Icon(
                        ft.icons.CHEVRON_RIGHT,
                        size=20,
                        color=ft.Colors.GREY_400,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.END,
                spacing=2,
            ),
        )

        # Container styling
        super().__init__(
            content=content,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            bgcolor=ft.Colors.GREY_100 if status == 'inactive' else None,
            border_radius=8,
            margin=ft.margin.only(bottom=5),
            on_click=on_click,
            ink=True,
            **kwargs
        )

    def _get_status_color(self, status: str) -> str:
        """Get color based on employee status."""
        if status == 'active':
            return ft.Colors.GREEN
        else:
            return ft.Colors.GREY_500

    def _get_compliance_style(self, score: int) -> tuple:
        """
        Get color and text based on compliance score.

        Returns:
            Tuple of (color, status_text)
        """
        if score >= 70:
            return (ft.Colors.GREEN, "Compliant")
        elif score >= 50:
            return (ft.Colors.ORANGE, "Warning")
        else:
            return (ft.Colors.RED, "Critical")
