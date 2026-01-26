"""Export button widget for reusable Excel export functionality."""

from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk

from employee.models import Employee
from ui_ctk.dialogs.export_dialog import ExportDialog


class ExportButton(ctk.CTkButton):
    """Reusable button for triggering Excel exports."""

    def __init__(
        self,
        master,
        get_employees_func: Callable[[], list[Employee]],
        title: str = "Export to Excel",
        default_filename: str = "employees_export.xlsx",
        on_export_complete: Optional[Callable[[bool, Optional[Path]], None]] = None,
        **kwargs,
    ):
        """
        Initialize export button.

        Args:
            master: Parent widget
            get_employees_func: Function that returns list of employees to export
            title: Dialog title
            default_filename: Default filename for export
            on_export_complete: Optional callback after export (success, output_path)
            **kwargs: Additional button arguments
        """
        # Set default values
        kwargs.setdefault("text", "Export to Excel")
        kwargs.setdefault("width", 140)
        kwargs.setdefault("fg_color", ("#2CC985", "#1A6B54"))
        kwargs.setdefault("hover_color", ("#23A070", "#145543"))

        super().__init__(master, command=self._on_click, **kwargs)

        self.get_employees_func = get_employees_func
        self.title = title
        self.default_filename = default_filename
        self.on_export_complete = on_export_complete

    def _on_click(self):
        """Handle button click - show export dialog."""
        try:
            # Get employees to export
            employees = self.get_employees_func()

            if not employees:
                self._show_no_data_message()
                return

            # Show export dialog
            dialog = ExportDialog(
                parent=self.winfo_toplevel(),
                employees=employees,
                title=self.title,
                default_filename=self.default_filename,
            )

            # Show dialog modally and get result
            success, output_path = dialog.run()

            # Call completion callback if provided
            if self.on_export_complete:
                self.on_export_complete(success, output_path)

        except Exception as e:
            self._show_error_message(str(e))

    def _show_no_data_message(self):
        """Show message when no data is available to export."""
        from tkinter import messagebox

        messagebox.showinfo(
            title="Export",
            message="No data available to export.",
            parent=self.winfo_toplevel(),
        )

    def _show_error_message(self, error_message: str):
        """
        Show error message.

        Args:
            error_message: Error message to display
        """
        from tkinter import messagebox

        messagebox.showerror(
            title="Export Error",
            message=f"Failed to export:\n{error_message}",
            parent=self.winfo_toplevel(),
        )
