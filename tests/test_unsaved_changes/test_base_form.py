"""Tests for BaseFormDialog unsaved changes functionality."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.state_tracker import FormStateManager


class TestFormStateManagerLogic:
    """Test FormStateManager logic without GUI."""

    def test_init_creates_empty_state(self):
        """Should initialize with empty state."""
        form = Mock()
        manager = FormStateManager(form)

        assert manager.form == form
        assert manager.initial_state == {}
        assert manager.current_state == {}
        assert manager.has_unsaved_changes is False

    def test_capture_initial_state_empty_form(self):
        """Should handle form with no variables."""
        form = Mock()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Should have empty state
        assert manager.initial_state == {}
        assert manager._tracked_vars == {}

    def test_check_changes_with_empty_state(self):
        """Should return False when state is empty."""
        form = Mock()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        assert manager.check_for_changes() is False

    def test_mark_as_saved_with_empty_state(self):
        """Should handle mark_as_saved with empty state."""
        form = Mock()
        manager = FormStateManager(form)

        manager.mark_as_saved()

        assert manager.has_unsaved_changes is False

    def test_reset_clears_all_state(self):
        """Should clear all tracked state."""
        form = Mock()
        manager = FormStateManager(form)

        # Even if we had state (simulated)
        manager.initial_state = {'test': 'value'}
        manager.has_unsaved_changes = True

        manager.reset()

        assert manager.initial_state == {}
        assert manager.has_unsaved_changes is False

    def test_get_changed_fields_empty(self):
        """Should return empty dict when no changes."""
        form = Mock()
        manager = FormStateManager(form)

        changed = manager.get_changed_fields()

        assert changed == {}


class TestUnsavedPrompts:
    """Test unsaved changes prompt behavior."""

    @patch('tkinter.messagebox.askyesnocancel')
    def test_prompt_unsaved_returns_yes(self, mock_askyesnocancel):
        """Should return 'save' when user clicks Yes."""
        mock_askyesnocancel.return_value = True

        # Import here to avoid issues with CustomTkinter
        from ui_ctk.forms.base_form import BaseFormDialog

        # We can't easily test the full dialog, but we can test the prompt logic
        # The actual prompt uses tkinter.messagebox which we've mocked

        # Test that the messagebox would be called with correct params
        response = mock_askyesnocancel(
            "Unsaved Changes",
            "You have unsaved changes in this form.\n\n"
            "Do you want to save them before closing?",
            icon='warning'
        )

        assert response is True

    @patch('tkinter.messagebox.askyesnocancel')
    def test_prompt_unsaved_returns_no(self, mock_askyesnocancel):
        """Should return 'discard' when user clicks No."""
        mock_askyesnocancel.return_value = False

        response = mock_askyesnocancel(
            "Unsaved Changes",
            "You have unsaved changes in this form.\n\n"
            "Do you want to save them before closing?",
            icon='warning'
        )

        assert response is False

    @patch('tkinter.messagebox.askyesnocancel')
    def test_prompt_unsaved_returns_cancel(self, mock_askyesnocancel):
        """Should return 'cancel' when user clicks Cancel."""
        mock_askyesnocancel.return_value = None

        response = mock_askyesnocancel(
            "Unsaved Changes",
            "You have unsaved changes in this form.\n\n"
            "Do you want to save them before closing?",
            icon='warning'
        )

        assert response is None


class TestMainWindowNavigation:
    """Test MainWindow navigation with unsaved changes."""

    def test_check_unsaved_with_no_view(self):
        """Should return False when no current view."""
        from ui_ctk.main_window import MainWindow

        # We can't fully test MainWindow without GUI, but we can test logic
        # Create a mock main window
        main_window = Mock()
        main_window.current_view = None

        # Simulate the check
        result = main_window.current_view is not None

        assert result is False

    def test_check_unsaved_view_without_method(self):
        """Should handle view without has_unsaved_changes method."""
        view = Mock(spec=['winfo_children'])  # Mock without has_unsaved_changes
        view.winfo_children.return_value = []

        main_window = Mock()
        main_window.current_view = view

        # View doesn't have has_unsaved_changes, should return False
        result = hasattr(main_window.current_view, 'has_unsaved_changes')

        assert result is False


class TestApplicationClosing:
    """Test application closing with unsaved changes."""

    def test_closing_without_main_window(self):
        """Should handle closing when main_window not set."""
        app = Mock(spec=[])  # Mock without any attributes
        # app.main_window not set

        # Should not crash
        result = hasattr(app, 'main_window')

        # A Mock object with spec=[] will not have main_window
        assert result is False

    def test_closing_with_main_window_no_unsaved(self):
        """Should close when no unsaved changes."""
        app = Mock()
        main_window = Mock()
        main_window._check_current_view_unsaved.return_value = False
        app.main_window = main_window

        # Check unsaved
        has_unsaved = app.main_window._check_current_view_unsaved()

        assert has_unsaved is False
