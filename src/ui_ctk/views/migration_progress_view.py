"""Migration progress view for showing database migration status.

This view displays the progress of database migrations when the application
starts, showing which migrations are being applied and their status.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import customtkinter as ctk
from typing import List, Optional, Callable


class MigrationProgressView(ctk.CTkFrame):
    """
    View for showing database migration progress.

    Displays:
    - Migration plan (which migrations will be applied)
    - Progress indicator during migration
    - Success/failure status
    - Option to continue or exit after migration
    """

    def __init__(self, master, migration_plan: dict, on_complete: Callable):
        """Initialize migration progress view.

        Args:
            master: Parent widget
            migration_plan: Dictionary with migration plan details
            on_complete: Callback when migration completes (success: bool)
        """
        super().__init__(master)

        self.migration_plan = migration_plan
        self.on_complete = on_complete
        self.migration_status = []  # List of (name, status) tuples

        self.create_ui()

    def create_ui(self):
        """Create the user interface."""
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=40)

        # Title
        title = ctk.CTkLabel(
            container,
            text="Database Migration",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(0, 20))

        # Info panel
        info_text = (
            f"Current version: {self.migration_plan['current_version']}\n"
            f"Target version: {self.migration_plan['target_version']}\n"
            f"Pending migrations: {self.migration_plan['pending_count']}"
        )
        info_label = ctk.CTkLabel(
            container,
            text=info_text,
            font=("Arial", 12),
            anchor="w"
        )
        info_label.pack(fill="x", pady=(0, 20))

        # Migrations list
        if self.migration_plan['migrations']:
            list_frame = ctk.CTkFrame(container)
            list_frame.pack(fill="both", expand=True, pady=(0, 20))

            # Header
            header = ctk.CTkLabel(
                list_frame,
                text="Migrations to apply:",
                font=("Arial", 14, "bold"),
                anchor="w"
            )
            header.pack(fill="x", padx=10, pady=(10, 5))

            # Scrollable list
            scrollable = ctk.CTkScrollableFrame(list_frame, height=200)
            scrollable.pack(fill="both", expand=True, padx=10, pady=(0, 10))

            # Migration items
            for migration_name in self.migration_plan['migrations']:
                item = self._create_migration_item(scrollable, migration_name, "pending")
                self.migration_status.append((migration_name, item))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(container, width=400)
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.set(0)

        # Status label
        self.status_label = ctk.CTkLabel(
            container,
            text="Preparing migration...",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=(0, 20))

        # Action buttons (initially hidden)
        self.button_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.button_frame.pack(pady=(20, 0))

        self.btn_continue = ctk.CTkButton(
            self.button_frame,
            text="Continue",
            width=120,
            command=self.on_continue,
            state="disabled"
        )
        self.btn_continue.pack(side="left", padx=5)

        self.btn_exit = ctk.CTkButton(
            self.button_frame,
            text="Exit",
            width=120,
            command=self.on_exit,
            fg_color="#c42b1f",
            hover_color="#a33d2e",
            state="disabled"
        )
        self.btn_exit.pack(side="left", padx=5)

    def _create_migration_item(self, parent, name: str, status: str) -> dict:
        """Create a migration item row.

        Args:
            parent: Parent widget
            name: Migration name
            status: Migration status ('pending', 'running', 'success', 'error')

        Returns:
            Dictionary with label widgets for updating
        """
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=2)

        # Status indicator
        status_label = ctk.CTkLabel(frame, text="⏳", width=30)
        status_label.pack(side="left", padx=(10, 5))

        # Migration name
        name_label = ctk.CTkLabel(
            frame,
            text=name,
            font=("Arial", 11),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True, padx=5)

        return {
            "frame": frame,
            "status": status_label,
            "name": name_label
        }

    def update_migration_status(self, migration_name: str, status: str):
        """Update the status of a migration.

        Args:
            migration_name: Name of the migration
            status: New status ('running', 'success', 'error')
        """
        for name, item in self.migration_status:
            if name == migration_name:
                if status == "running":
                    item["status"].configure(text="⚙️")
                    item["name"].configure(text_color="yellow")
                elif status == "success":
                    item["status"].configure(text="✅")
                    item["name"].configure(text_color="green")
                elif status == "error":
                    item["status"].configure(text="❌")
                    item["name"].configure(text_color="red")
                break

    def update_progress(self, current: int, total: int):
        """Update the progress bar.

        Args:
            current: Current step number
            total: Total steps
        """
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress)

    def update_status(self, message: str):
        """Update the status message.

        Args:
            message: New status message
        """
        self.status_label.configure(text=message)

    def show_success(self):
        """Show success state."""
        self.update_status("Migration completed successfully!")
        self.btn_continue.configure(state="normal")
        self.btn_exit.configure(state="disabled")

    def show_error(self, error_message: str):
        """Show error state.

        Args:
            error_message: Error message to display
        """
        self.update_status(f"Migration failed: {error_message}")
        self.btn_continue.configure(state="disabled")
        self.btn_exit.configure(state="normal")

    def on_continue(self):
        """Handle continue button click."""
        if self.on_complete:
            self.on_complete(success=True)

    def on_exit(self):
        """Handle exit button click."""
        if self.on_complete:
            self.on_complete(success=False)


class MigrationProgressWindow(ctk.CTk):
    """
    Standalone window for showing migration progress.

    This can be used as a modal dialog before the main application
    window is shown.
    """

    def __init__(self, migration_plan: dict, on_complete: Callable):
        """Initialize migration progress window.

        Args:
            migration_plan: Dictionary with migration plan details
            on_complete: Callback when migration completes (success: bool)
        """
        super().__init__()

        self.title("Database Migration")
        self.geometry("600x500")

        # Create progress view
        self.progress_view = MigrationProgressView(self, migration_plan, on_complete)
        self.progress_view.pack(fill="both", expand=True)

        # Store result
        self.migration_success = None

    def set_migration_result(self, success: bool, error_message: str = None):
        """Set the migration result.

        Args:
            success: Whether migration succeeded
            error_message: Optional error message
        """
        self.migration_success = success

        if success:
            self.progress_view.show_success()
        else:
            self.progress_view.show_error(error_message or "Unknown error")

    def update_migration_status(self, migration_name: str, status: str):
        """Update migration status (delegates to view)."""
        self.progress_view.update_migration_status(migration_name, status)

    def update_progress(self, current: int, total: int):
        """Update progress (delegates to view)."""
        self.progress_view.update_progress(current, total)

    def update_status(self, message: str):
        """Update status message (delegates to view)."""
        self.progress_view.update_status(message)


if __name__ == "__main__":
    # Test the migration progress view
    def test_complete(success: bool):
        print(f"Migration completed: {success}")
        import sys
        sys.exit(0 if success else 1)

    test_plan = {
        "current_version": "0.0.1",
        "target_version": "0.1.0",
        "pending_count": 3,
        "migrations": [
            "20250126_120000_add_soft_delete",
            "20250126_120001_add_employee_status",
            "20250126_120002_add_audit_log"
        ]
    }

    app = MigrationProgressWindow(test_plan, test_complete)

    # Simulate migration
    def simulate_migration():
        app.update_status("Starting migration...")

        import time

        for i, migration_name in enumerate(test_plan['migrations'], 1):
            app.update_migration_status(migration_name, "running")
            app.update_progress(i, len(test_plan['migrations']))
            app.update_status(f"Applying {migration_name}...")

            time.sleep(1)  # Simulate work

            app.update_migration_status(migration_name, "success")

        app.set_migration_result(True)

    app.after(100, simulate_migration)
    app.mainloop()
