"""StatCard widget - Displays a statistic with icon and styling."""

import flet as ft
from typing import Union


class StatCard(ft.Container):
    """
    A card widget displaying a single statistic.

    Shows an icon, value, and label with color coding.

    Args:
        label: Description text (e.g., "Total Employees")
        value: The statistic value (number or string)
        icon: Flet icon constant (e.g., ft.icons.PEOPLE)
        color: Background/icon color (e.g., ft.Colors.BLUE)

    Example:
        StatCard(
            "Total Employees",
            42,
            ft.icons.PEOPLE,
            ft.Colors.BLUE
        )
    """

    def __init__(
        self,
        label: str,
        value: Union[int, str],
        icon: str,
        color: str,
        **kwargs
    ):
        # Build the card content
        content = ft.Column(
            [
                # Icon and value row
                ft.Row(
                    [
                        ft.Icon(
                            icon,
                            size=32,
                            color=color,
                        ),
                        ft.Text(
                            str(value),
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=color,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Label
                ft.Text(
                    label,
                    size=14,
                    color=ft.Colors.GREY_700,
                ),
            ],
            spacing=5,
        )

        # Container styling
        super().__init__(
            content=content,
            width=200,
            padding=20,
            bgcolor=ft.Colors.GREY_100,
            border_radius=12,
            **kwargs
        )
