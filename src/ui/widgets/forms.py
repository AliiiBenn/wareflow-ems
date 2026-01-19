"""Form widgets - Reusable form components for employee data."""

import flet as ft
from datetime import date
from typing import Optional, Callable


class DateField(ft.Row):
    """
    A date input field with calendar picker.

    Args:
        label: Field label
        value: Initial date value (datetime.date or None)
        on_change: Callback when date changes
        required: Whether field is required
    """

    def __init__(
        self,
        label: str,
        value: Optional[date] = None,
        on_change: Optional[Callable] = None,
        required: bool = False,
        **kwargs
    ):
        self.label = label
        self.on_change = on_change
        self.required = required
        self._value = value

        # Date picker button
        date_text = value.strftime("%d/%m/%Y") if value else "Select date"

        self.date_button = ft.ElevatedButton(
            date_text,
            icon=ft.icons.CALENDAR_MONTH,
            on_click=self._pick_date,
        )

        self.label_text = ft.Text(
            f"{label} {'*' if required else ''}",
            size=14,
            weight=ft.FontWeight.BOLD,
            width=150,
        )

        super().__init__(
            [
                self.label_text,
                self.date_button,
            ],
            **kwargs
        )

    def _pick_date(self, e):
        """Show date picker dialog."""
        # For now, just use a text input (Flet's date picker is limited)
        # In a full implementation, would use ft.DatePicker
        pass

    @property
    def value(self) -> Optional[date]:
        """Get the current date value."""
        return self._value

    def set_value(self, value: date):
        """Set the date value."""
        self._value = value
        if value:
            self.date_button.text = value.strftime("%d/%m/%Y")
        else:
            self.date_button.text = "Select date"


class DropdownField(ft.Row):
    """
    A dropdown select field.

    Args:
        label: Field label
        options: List of (value, label) tuples
        value: Initial selected value
        on_change: Callback when selection changes
        required: Whether field is required
    """

    def __init__(
        self,
        label: str,
        options: list,
        value: Optional[str] = None,
        on_change: Optional[Callable] = None,
        required: bool = False,
        **kwargs
    ):
        self.on_change = on_change

        # Build dropdown options
        dropdown_options = []
        for opt_value, opt_label in options:
            dropdown_options.append(
                ft.dropdown.Option(opt_value, opt_label)
            )

        self.dropdown = ft.Dropdown(
            options=dropdown_options,
            value=value,
            on_change=self._on_dropdown_change,
            width=300,
        )

        self.label_text = ft.Text(
            f"{label} {'*' if required else ''}",
            size=14,
            weight=ft.FontWeight.BOLD,
            width=150,
        )

        super().__init__(
            [
                self.label_text,
                self.dropdown,
            ],
            **kwargs
        )

    def _on_dropdown_change(self, e):
        """Handle dropdown change."""
        if self.on_change:
            self.on_change(e.control.value)

    @property
    def value(self) -> Optional[str]:
        """Get the current selected value."""
        return self.dropdown.value


class TextFormField(ft.Row):
    """
    A text input field with label.

    Args:
        label: Field label
        value: Initial text value
        on_change: Callback when text changes
        required: Whether field is required
        hint_text: Placeholder text
        max_length: Maximum character length
    """

    def __init__(
        self,
        label: str,
        value: str = "",
        on_change: Optional[Callable] = None,
        required: bool = False,
        hint_text: Optional[str] = None,
        max_length: Optional[int] = None,
        **kwargs
    ):
        self.on_change = on_change

        self.text_field = ft.TextField(
            value=value,
            hint_text=hint_text,
            max_length=max_length,
            width=300,
            on_change=self._on_text_change,
        )

        self.label_text = ft.Text(
            f"{label} {'*' if required else ''}",
            size=14,
            weight=ft.FontWeight.BOLD,
            width=150,
        )

        super().__init__(
            [
                self.label_text,
                self.text_field,
            ],
            **kwargs
        )

    def _on_text_change(self, e):
        """Handle text change."""
        if self.on_change:
            self.on_change(e.control.value)

    @property
    def value(self) -> str:
        """Get the current text value."""
        return self.text_field.value


class FormSection(ft.Container):
    """
    A section container for form fields with title.

    Args:
        title: Section title
        fields: List of form field widgets
    """

    def __init__(
        self,
        title: str,
        fields: list,
        **kwargs
    ):
        content = ft.Column(
            [
                ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE,
                ),
                ft.Divider(),
                ft.Column(fields, spacing=15),
            ],
            spacing=10,
        )

        super().__init__(
            content=content,
            padding=20,
            bgcolor=ft.Colors.GREY_50,
            border_radius=12,
            **kwargs
        )
