"""AlertListItem widget - Displays a single alert with priority styling."""

import flet as ft


class AlertListItem(ft.Container):
    """
    A list item widget displaying an alert with priority indication.

    Shows icon, description, employee info, and days remaining.
    Color-coded by priority/urgency.

    Args:
        employee_name: Name of the employee
        description: Alert description (e.g., "CACES 48")
        days_until: Days until expiration (can be negative)
        priority: 'urgent' | 'high' | 'normal'
        employee_id: ID for navigation (optional)
        on_click: Click handler (optional)

    Example:
        AlertListItem(
            "John Doe",
            "CACES 48",
            5,
            'urgent',
            employee_id=123
        )
    """

    def __init__(
        self,
        employee_name: str,
        description: str,
        days_until: int,
        priority: str,
        employee_id: int = None,
        on_click=None,
        **kwargs
    ):
        # Determine styling based on priority
        icon, color, bgcolor = self._get_priority_style(days_until, priority)

        # Format days text
        if days_until < 0:
            days_text = f"Expired {abs(days_until)} days ago"
        else:
            days_text = f"Expires in {days_until} days"

        # Build content
        content = ft.ListTile(
            leading=ft.Text(icon, size=24),
            title=ft.Text(employee_name),
            subtitle=ft.Text(f"{description} • {days_text}"),
            trailing=ft.Icon(
                ft.icons.CHEVRON_RIGHT,
                color=ft.Colors.GREY_400,
            ),
        )

        # Container styling
        super().__init__(
            content=content,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            bgcolor=bgcolor,
            border_radius=8,
            margin=ft.margin.only(bottom=5),
            on_click=on_click,
            ink=True,
            **kwargs
        )

    def _get_priority_style(self, days_until: int, priority: str):
        """
        Get icon, text color, and background color based on priority.

        Args:
            days_until: Days until expiration
            priority: Priority level

        Returns:
            Tuple of (icon_emoji, color, bgcolor)
        """
        if days_until < 0 or priority == 'urgent':
            return ("🔴", ft.Colors.RED, ft.Colors.RED_50)
        elif days_until < 15 or priority == 'high':
            return ("🟠", ft.Colors.ORANGE, ft.Colors.ORANGE_50)
        elif days_until < 30 or priority == 'normal':
            return ("🟡", ft.Colors.YELLOW_800, ft.Colors.YELLOW_50)
        else:
            return ("🟢", ft.Colors.GREEN, ft.Colors.GREEN_50)
