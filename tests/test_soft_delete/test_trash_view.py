"""Tests for TrashView functionality."""

from unittest.mock import MagicMock, Mock, patch

import customtkinter as ctk
import pytest


@pytest.fixture
def trash_view(ctk_app, db_connection):
    """Create a TrashView instance for testing."""
    from ui_ctk.views.trash_view import TrashView

    # Create a mock main window as parent
    main_window = MagicMock()
    main_window.master_window = main_window

    view = TrashView(main_window)
    return view


class TestTrashView:
    """Tests for TrashView UI."""

    def test_trash_view_initialization(self, ctk_app, db_connection):
        """Test that TrashView initializes correctly."""
        from ui_ctk.views.trash_view import TrashView

        # Create a mock main window
        main_window = MagicMock()
        main_window.master_window = main_window

        view = TrashView(main_window)

        # Verify view is created
        assert view is not None
        assert view.title() == "Trash"

    def test_load_deleted_items_empty_database(self, trash_view):
        """Test loading deleted items when database is empty."""
        # Load deleted items
        trash_view.load_deleted_items()

        # Verify count is 0
        assert "0" in trash_view.count_label.cget("text")

    def test_load_deleted_items_with_deleted_employee(self, trash_view, sample_employee):
        """Test loading deleted items with one deleted employee."""
        # Soft delete the employee
        sample_employee.soft_delete(reason="Test deletion")

        # Load deleted items
        trash_view.load_deleted_items()

        # Verify count is 1
        assert "1" in trash_view.count_label.cget("text")

    def test_load_deleted_items_with_multiple_deleted_types(
        self, trash_view, sample_employee, sample_caces, sample_medical_visit, sample_training
    ):
        """Test loading deleted items of different types."""
        # Soft delete all items
        sample_employee.soft_delete(reason="Test deletion")
        sample_caces.soft_delete(reason="Test deletion")
        sample_medical_visit.soft_delete(reason="Test deletion")
        sample_training.soft_delete(reason="Test deletion")

        # Load deleted items
        trash_view.load_deleted_items()

        # Verify count is 4
        assert "4" in trash_view.count_label.cget("text")

    def test_restore_item_employee(self, trash_view, sample_employee):
        """Test restoring a deleted employee."""
        # Soft delete the employee
        sample_employee.soft_delete(reason="Test deletion")

        # Load deleted items
        trash_view.load_deleted_items()

        # Restore the item
        trash_view.restore_item(sample_employee, "employee")

        # Reload from database
        employee = Employee.get_by_id(sample_employee.id)

        # Verify employee is restored
        assert employee.is_deleted is False

        # Refresh view and verify count is 0
        trash_view.load_deleted_items()
        assert "0" in trash_view.count_label.cget("text")

    def test_restore_item_caces(self, trash_view, sample_caces):
        """Test restoring a deleted CACES certification."""
        # Soft delete the CACES
        sample_caces.soft_delete(reason="Test deletion")

        # Load deleted items
        trash_view.load_deleted_items()

        # Restore the item
        trash_view.restore_item(sample_caces, "caces")

        # Reload from database
        caces = Caces.get_by_id(sample_caces.id)

        # Verify CACES is restored
        assert caces.is_deleted is False

        # Refresh view and verify count is 0
        trash_view.load_deleted_items()
        assert "0" in trash_view.count_label.cget("text")

    def test_restore_item_medical_visit(self, trash_view, sample_medical_visit):
        """Test restoring a deleted medical visit."""
        # Soft delete the visit
        sample_medical_visit.soft_delete(reason="Test deletion")

        # Load deleted items
        trash_view.load_deleted_items()

        # Restore the item
        trash_view.restore_item(sample_medical_visit, "visit")

        # Reload from database
        visit = MedicalVisit.get_by_id(sample_medical_visit.id)

        # Verify visit is restored
        assert visit.is_deleted is False

        # Refresh view and verify count is 0
        trash_view.load_deleted_items()
        assert "0" in trash_view.count_label.cget("text")

    def test_restore_item_online_training(self, trash_view, sample_training):
        """Test restoring a deleted online training."""
        # Soft delete the training
        sample_training.soft_delete(reason="Test deletion")

        # Load deleted items
        trash_view.load_deleted_items()

        # Restore the item
        trash_view.restore_item(sample_training, "training")

        # Reload from database
        training = OnlineTraining.get_by_id(sample_training.id)

        # Verify training is restored
        assert training.is_deleted is False

        # Refresh view and verify count is 0
        trash_view.load_deleted_items()
        assert "0" in trash_view.count_label.cget("text")

    @patch("tkinter.messagebox.askyesno")
    def test_confirm_permanent_delete_employee(self, mock_askyesno, trash_view, sample_employee):
        """Test permanently deleting an employee from trash."""
        # Soft delete the employee first
        sample_employee.soft_delete(reason="Test deletion")

        # Mock user confirmation
        mock_askyesno.return_value = True

        # Confirm permanent delete
        trash_view.confirm_permanent_delete(sample_employee, "employee")

        # Verify employee is permanently deleted
        employee = Employee.get_or_none(Employee.id == sample_employee.id)
        assert employee is None

    @patch("tkinter.messagebox.askyesno")
    def test_confirm_permanent_delete_canceled(self, mock_askyesno, trash_view, sample_employee):
        """Test canceling permanent delete from trash."""
        # Soft delete the employee first
        sample_employee.soft_delete(reason="Test deletion")

        # Mock user cancellation
        mock_askyesno.return_value = False

        # Confirm permanent delete (user cancels)
        trash_view.confirm_permanent_delete(sample_employee, "employee")

        # Verify employee still exists (still soft deleted)
        employee = Employee.get_by_id(sample_employee.id)
        assert employee is not None
        assert employee.is_deleted is True

    @patch("tkinter.messagebox.askyesno")
    def test_confirm_empty_trash(self, mock_askyesno, trash_view, sample_employee, sample_caces):
        """Test emptying all items from trash."""
        # Soft delete items
        sample_employee.soft_delete(reason="Test deletion")
        sample_caces.soft_delete(reason="Test deletion")

        # Mock user confirmation
        mock_askyesno.return_value = True

        # Empty trash
        trash_view.confirm_empty_trash()

        # Verify items are permanently deleted
        employee = Employee.get_or_none(Employee.id == sample_employee.id)
        caces = Caces.get_or_none(Caces.id == sample_caces.id)

        assert employee is None
        assert caces is None

    @patch("tkinter.messagebox.askyesno")
    @patch("tkinter.messagebox.showinfo")
    def test_confirm_empty_trash_already_empty(
        self, mock_showinfo, mock_askyesno, trash_view
    ):
        """Test emptying trash when already empty."""
        # Mock should not be called because trash is empty
        mock_askyesno.return_value = True

        # Empty trash
        trash_view.confirm_empty_trash()

        # Verify showinfo was called to indicate trash is empty
        mock_showinfo.assert_called_once()
        assert "empty" in str(mock_showinfo.call_args).lower()

    def test_format_datetime(self, trash_view):
        """Test datetime formatting."""
        from datetime import datetime

        dt = datetime(2023, 6, 15, 14, 30)
        formatted = trash_view._format_datetime(dt)

        assert formatted == "2023-06-15 14:30"

    def test_format_datetime_none(self, trash_view):
        """Test formatting None datetime."""
        formatted = trash_view._format_datetime(None)
        assert formatted == "Unknown"

    def test_refresh_view(self, trash_view, sample_employee):
        """Test refreshing the trash view."""
        # Soft delete an employee
        sample_employee.soft_delete(reason="Test deletion")

        # Load deleted items
        trash_view.load_deleted_items()

        # Verify count
        assert "1" in trash_view.count_label.cget("text")

        # Restore the item
        sample_employee.restore()

        # Refresh view
        trash_view.refresh_view()

        # Verify count is updated to 0
        assert "0" in trash_view.count_label.cget("text")
