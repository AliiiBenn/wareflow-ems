"""Main application window with navigation bar."""

from typing import Optional

import customtkinter as ctk

from ui_ctk.constants import (
    APP_TITLE,
    NAV_ALERTS,
    NAV_EMPLOYEES,
    NAV_IMPORT,
    NAV_BACKUPS,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
)
from ui_ctk.views.base_view import BaseView
from utils.undo_manager import get_undo_manager


class MainWindow(ctk.CTkFrame):
    """
    Main application window with navigation bar.

    Features:
    - Navigation bar with 3 main sections
    - Dynamic view container
    - View switching mechanism
    - Clean layout management
    """

    def __init__(self, master: ctk.CTk):
        """
        Initialize main window.

        Args:
            master: Root CTk application
        """
        super().__init__(master, fg_color="transparent")

        # Store reference to master for navigation
        self.master_window = master

        # Track current view
        self.current_view: Optional[BaseView] = None

        # Get undo manager instance
        self.undo_manager = get_undo_manager()

        # Create UI components
        self.create_navigation_bar()
        self.create_view_container()

        # Bind keyboard shortcuts
        self.bind_keyboard_shortcuts()

        # Register callback for undo/redo state changes
        self.undo_manager.register_history_callback(self.update_undo_redo_buttons)

        # Show default view (employee list)
        self.show_employee_list()

    def create_navigation_bar(self):
        """Create navigation bar with buttons."""
        # Navigation container
        self.nav_bar = ctk.CTkFrame(self, height=60)
        self.nav_bar.pack(side="top", fill="x", padx=10, pady=10)
        self.nav_bar.pack_propagate(False)

        # Title label
        title_label = ctk.CTkLabel(self.nav_bar, text=APP_TITLE, font=("Arial", 16, "bold"))
        title_label.pack(side="left", padx=20)

        # Button container (right side)
        button_container = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
        button_container.pack(side="right")

        # Employee list button
        self.btn_employees = ctk.CTkButton(
            button_container, text=NAV_EMPLOYEES, width=120, command=self.show_employee_list
        )
        self.btn_employees.pack(side="left", padx=5)

        # Alerts button
        self.btn_alerts = ctk.CTkButton(button_container, text=NAV_ALERTS, width=120, command=self.show_alerts)
        self.btn_alerts.pack(side="left", padx=5)

        # Import button
        self.btn_import = ctk.CTkButton(button_container, text=NAV_IMPORT, width=140, command=self.show_import)
        self.btn_import.pack(side="left", padx=5)

        # Backups button
        self.btn_backups = ctk.CTkButton(
            button_container,
            text=NAV_BACKUPS,
            width=140,
            command=self.show_backups
        )
        self.btn_backups.pack(side="left", padx=5)

        # Trash button
        self.btn_trash = ctk.CTkButton(
            button_container,
            text="🗑️ Trash",
            width=120,
            command=self.show_trash
        )
        self.btn_trash.pack(side="left", padx=5)

        # Separator
        separator = ctk.CTkLabel(button_container, text="|", width=20)
        separator.pack(side="left", padx=5)

        # Undo button
        self.btn_undo = ctk.CTkButton(
            button_container,
            text="↶ Undo",
            width=100,
            command=self.perform_undo,
            state="disabled"
        )
        self.btn_undo.pack(side="left", padx=5)

        # Redo button
        self.btn_redo = ctk.CTkButton(
            button_container,
            text="↷ Redo",
            width=100,
            command=self.perform_redo,
            state="disabled"
        )
        self.btn_redo.pack(side="left", padx=5)

    def create_view_container(self):
        """Create container for dynamic views."""
        self.view_container = ctk.CTkFrame(self)
        self.view_container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    def clear_view(self):
        """Remove current view from container."""
        if self.current_view:
            # Call cleanup method if exists
            if hasattr(self.current_view, "cleanup"):
                try:
                    self.current_view.cleanup()
                except Exception as e:
                    print(f"[WARN] View cleanup error: {e}")

            # Destroy view
            self.current_view.destroy()
            self.current_view = None

    def switch_view(self, view_class: type, *args, **kwargs):
        """
        Switch to a new view with unsaved changes detection.

        Args:
            view_class: View class to instantiate
            *args: Positional arguments for view constructor
            **kwargs: Keyword arguments for view constructor
        """
        # Check if current view has unsaved changes
        if self._check_current_view_unsaved():
            response = self._prompt_unsaved_changes()

            if response == 'cancel':
                return  # Cancel navigation
            elif response == 'save':
                if not self._save_current_view():
                    return  # Save failed, cancel navigation

        # Remove current view
        self.clear_view()

        # Create new view
        self.current_view = view_class(self.view_container, *args, **kwargs)
        self.current_view.pack(fill="both", expand=True)

        # Update button states
        self.update_navigation_state()

    def _check_current_view_unsaved(self) -> bool:
        """Check if current view has unsaved changes.

        Returns:
            True if there are unsaved changes, False otherwise
        """
        if not self.current_view:
            return False

        # Check if view has unsaved_changes method
        if hasattr(self.current_view, 'has_unsaved_changes'):
            try:
                if self.current_view.has_unsaved_changes():
                    return True
            except Exception as e:
                print(f"[WARN] Error checking unsaved changes: {e}")

        # Check for open form dialogs
        try:
            # Get all open toplevel windows
            for widget in self.view_container.winfo_children():
                if hasattr(widget, 'has_unsaved_changes'):
                    try:
                        if widget.has_unsaved_changes():
                            return True
                    except Exception:
                        pass
        except Exception as e:
            print(f"[WARN] Error checking child widgets: {e}")

        return False

    def _prompt_unsaved_changes(self) -> str:
        """Prompt user about unsaved changes before navigation.

        Returns:
            'save', 'discard', or 'cancel'
        """
        try:
            import tkinter.messagebox as messagebox

            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes in the current view.\n\n"
                "Do you want to save them before switching?",
                icon='warning'
            )

            if response is None:  # Cancel
                return 'cancel'
            elif response:  # Yes - save
                return 'save'
            else:  # No - discard
                return 'discard'
        except Exception:
            # Fallback if messagebox fails
            return 'discard'

    def _save_current_view(self) -> bool:
        """Attempt to save the current view.

        Returns:
            True if save successful, False otherwise
        """
        if not self.current_view:
            return True

        # Try to call save method on current view
        if hasattr(self.current_view, 'save'):
            try:
                self.current_view.save()
                return True
            except Exception as e:
                print(f"[ERROR] Failed to save current view: {e}")

                # Show error to user
                try:
                    import tkinter.messagebox as messagebox
                    messagebox.showerror(
                        "Save Error",
                        f"Failed to save changes:\n{e}\n\n"
                        "Navigation cancelled."
                    )
                except Exception:
                    pass

                return False

        # No save method, assume no save needed
        return True

    def update_navigation_state(self):
        """Update navigation button states to show active section."""
        # Reset all buttons to default state
        # Note: In future versions, we could highlight active button
        # For now, all buttons remain neutral
        pass

    # ===== Navigation Methods =====

    def show_employee_list(self):
        """Display employee list view."""
        try:
            from ui_ctk.views.employee_list import EmployeeListView

            self.switch_view(EmployeeListView, title="Liste des Employés")
            print("[NAV] Showing employee list view")
        except ImportError as e:
            print(f"[WARN] EmployeeListView not implemented: {e}")
            # Show placeholder
            from ui_ctk.views.placeholder import PlaceholderView

            self.switch_view(PlaceholderView, title="Liste des Employés")
            print("[NAV] Showing placeholder for employee list")
        except Exception as e:
            print(f"[ERROR] Failed to load employee list: {e}")
            self.show_error(f"Failed to load employee list: {e}")

    def show_alerts(self):
        """Display alerts view."""
        try:
            from ui_ctk.views.alerts_view import AlertsView

            self.switch_view(AlertsView, title="Alertes")
            print("[NAV] Showing alerts view")
        except ImportError as e:
            print(f"[WARN] AlertsView not implemented: {e}")
            # Show placeholder
            from ui_ctk.views.placeholder import PlaceholderView

            self.switch_view(PlaceholderView, title="Alertes")
            print("[NAV] Showing placeholder for alerts")
        except Exception as e:
            print(f"[ERROR] Failed to load alerts view: {e}")
            self.show_error(f"Failed to load alerts: {e}")

    def show_import(self):
        """Display import view."""
        try:
            from ui_ctk.views.import_view import ImportView

            self.switch_view(ImportView, title="Import Excel")
            print("[NAV] Showing import view")
        except ImportError as e:
            print(f"[WARN] ImportView not implemented: {e}")
            # Show placeholder
            from ui_ctk.views.placeholder import PlaceholderView

            self.switch_view(PlaceholderView, title="Import Excel")
            print("[NAV] Showing placeholder for import")
        except Exception as e:
            print(f"[ERROR] Failed to load import view: {e}")
            self.show_error(f"Failed to load import: {e}")

    def show_backups(self):
        """Display backup and export management view."""
        try:
            from ui_ctk.views.backup_view import BackupView
            self.switch_view(BackupView)
            print("[NAV] Showing backup view")
        except ImportError as e:
            print(f"[WARN] BackupView not implemented: {e}")
            # Show placeholder
            from ui_ctk.views.placeholder import PlaceholderView
            self.switch_view(PlaceholderView, title="Sauvegardes")
            print("[NAV] Showing placeholder for backups")
        except Exception as e:
            print(f"[ERROR] Failed to load backup view: {e}")
            self.show_error(f"Failed to load backup view: {e}")

    def show_trash(self):
        """Display trash view for viewing and restoring deleted items."""
        try:
            from ui_ctk.views.trash_view import TrashView
            self.switch_view(TrashView)
            print("[NAV] Showing trash view")
        except ImportError as e:
            print(f"[WARN] TrashView not implemented: {e}")
            # Show placeholder
            from ui_ctk.views.placeholder import PlaceholderView

            self.switch_view(PlaceholderView, title="Trash")
            print("[NAV] Showing placeholder for trash")
        except Exception as e:
            print(f"[ERROR] Failed to load trash view: {e}")
            self.show_error(f"Failed to load trash: {e}")

    def show_error(self, message: str):
        """Show error message to user."""
        try:
            import tkinter.messagebox as messagebox

            messagebox.showerror("Error", message)
        except:
            print(f"[ERROR] {message}")

    # ===== Undo/Redo Methods =====

    def bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts for undo and redo."""
        try:
            # Bind Ctrl+Z for undo
            self.master_window.bind_all("<Control-z>", lambda e: self.perform_undo())
            # Bind Ctrl+Y for redo
            self.master_window.bind_all("<Control-y>", lambda e: self.perform_redo())
            # Also bind Ctrl+Shift+Z for redo (common alternative)
            self.master_window.bind_all("<Control-Z>", lambda e: self.perform_redo())
        except Exception as e:
            print(f"[WARN] Failed to bind keyboard shortcuts: {e}")

    def perform_undo(self):
        """Perform undo operation."""
        try:
            action = self.undo_manager.undo()
            if action:
                print(f"[UNDO] Undone: {action.description}")
                self._show_undo_redo_notification(f"Undone: {action.description}")
            else:
                print("[UNDO] Nothing to undo")
        except Exception as e:
            print(f"[ERROR] Undo failed: {e}")
            self.show_error(f"Undo failed: {e}")

    def perform_redo(self):
        """Perform redo operation."""
        try:
            action = self.undo_manager.redo()
            if action:
                print(f"[REDO] Redone: {action.description}")
                self._show_undo_redo_notification(f"Redone: {action.description}")
            else:
                print("[REDO] Nothing to redo")
        except Exception as e:
            print(f"[ERROR] Redo failed: {e}")
            self.show_error(f"Redo failed: {e}")

    def update_undo_redo_buttons(self):
        """Update undo/redo button states based on history."""
        try:
            # Update undo button
            if self.undo_manager.can_undo():
                self.btn_undo.configure(state="normal")
                description = self.undo_manager.get_undo_description()
                if description:
                    self.btn_undo.configure(text=f"↶ Undo: {description[:30]}...")
            else:
                self.btn_undo.configure(state="disabled", text="↶ Undo")

            # Update redo button
            if self.undo_manager.can_redo():
                self.btn_redo.configure(state="normal")
                description = self.undo_manager.get_redo_description()
                if description:
                    self.btn_redo.configure(text=f"↷ Redo: {description[:30]}...")
            else:
                self.btn_redo.configure(state="disabled", text="↷ Redo")
        except Exception as e:
            print(f"[WARN] Failed to update undo/redo buttons: {e}")

    def _show_undo_redo_notification(self, message: str):
        """Show a brief notification for undo/redo actions.

        Args:
            message: Notification message to display
        """
        # For now, just print to console
        # In future versions, this could show a toast notification
        # or update a status bar
        pass
