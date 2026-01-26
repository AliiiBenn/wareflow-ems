"""Tests for FormStateManager module."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


# Import CustomTkinter AFTER pytest setup
import customtkinter as ctk

from utils.state_tracker import FormStateManager


class MockForm:
    """Mock form for testing."""

    def __init__(self):
        self.string_var = ctk.StringVar(value="initial")
        self.int_var = ctk.IntVar(value=42)
        self.bool_var = ctk.BooleanVar(value=True)
        self.double_var = ctk.DoubleVar(value=3.14)


class TestFormStateManager:
    """Test suite for FormStateManager class."""

    def test_init(self):
        """Should initialize with empty state."""
        form = MockForm()
        manager = FormStateManager(form)

        assert manager.form == form
        assert manager.initial_state == {}
        assert manager.current_state == {}
        assert manager.has_unsaved_changes is False
        assert manager._tracked_vars == {}

    def test_capture_initial_state(self):
        """Should capture initial state of all tracked variables."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Check that all variables were tracked
        assert 'string_var' in manager.initial_state
        assert 'int_var' in manager.initial_state
        assert 'bool_var' in manager.initial_state
        assert 'double_var' in manager.initial_state

        # Check initial values
        assert manager.initial_state['string_var'] == "initial"
        assert manager.initial_state['int_var'] == 42
        assert manager.initial_state['bool_var'] in ["1", "True", True]  # BooleanVar can vary
        assert manager.initial_state['double_var'] == 3.14

        # Check that variables are tracked
        assert 'string_var' in manager._tracked_vars
        assert 'int_var' in manager._tracked_vars
        assert 'bool_var' in manager._tracked_vars
        assert 'double_var' in manager._tracked_vars

    def test_check_for_changes_no_changes(self):
        """Should return False when no changes detected."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # No changes made
        assert manager.check_for_changes() is False

    def test_check_for_changes_with_string_change(self):
        """Should detect changes in StringVar."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make a change
        form.string_var.set("changed")

        assert manager.check_for_changes() is True

    def test_check_for_changes_with_int_change(self):
        """Should detect changes in IntVar."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make a change
        form.int_var.set(100)

        assert manager.check_for_changes() is True

    def test_check_for_changes_with_bool_change(self):
        """Should detect changes in BooleanVar."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make a change
        form.bool_var.set(False)

        assert manager.check_for_changes() is True

    def test_check_for_changes_with_double_change(self):
        """Should detect changes in DoubleVar."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make a change
        form.double_var.set(2.71)

        assert manager.check_for_changes() is True

    def test_check_for_changes_multiple_changes(self):
        """Should detect multiple changes."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make multiple changes
        form.string_var.set("changed")
        form.int_var.set(200)
        form.bool_var.set(False)

        assert manager.check_for_changes() is True

    def test_update_has_unsaved_true(self):
        """Should update has_unsaved_changes to True when changes detected."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()
        form.string_var.set("changed")

        result = manager.update_has_unsaved()

        assert result is True
        assert manager.has_unsaved_changes is True

    def test_update_has_unsaved_false(self):
        """Should keep has_unsaved_changes False when no changes."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        result = manager.update_has_unsaved()

        assert result is False
        assert manager.has_unsaved_changes is False

    def test_mark_as_saved(self):
        """Should mark form as saved and update initial state."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make changes
        form.string_var.set("changed")
        form.int_var.set(100)

        # Update unsaved status
        manager.update_has_unsaved()
        assert manager.has_unsaved_changes is True

        # Mark as saved
        manager.mark_as_saved()

        # Should be marked as saved
        assert manager.has_unsaved_changes is False

        # Initial state should now match current state
        assert manager.initial_state == manager.current_state
        assert manager.initial_state['string_var'] == "changed"
        assert manager.initial_state['int_var'] == 100

    def test_mark_as_saved_then_no_changes(self):
        """After marking as saved, check_for_changes should return False."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make changes
        form.string_var.set("changed")

        # Check has changes
        assert manager.check_for_changes() is True

        # Mark as saved
        manager.mark_as_saved()

        # Now should have no changes
        assert manager.check_for_changes() is False

    def test_get_changed_fields_no_changes(self):
        """Should return empty dict when no fields changed."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        changed = manager.get_changed_fields()

        assert changed == {}

    def test_get_changed_fields_single_change(self):
        """Should return dict with changed field."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make a change
        form.string_var.set("changed")
        manager.update_has_unsaved()

        changed = manager.get_changed_fields()

        assert 'string_var' in changed
        assert changed['string_var'] == ("initial", "changed")

    def test_get_changed_fields_multiple_changes(self):
        """Should return dict with all changed fields."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make changes
        form.string_var.set("changed")
        form.int_var.set(100)
        form.bool_var.set(False)
        manager.update_has_unsaved()

        changed = manager.get_changed_fields()

        assert len(changed) == 3
        assert changed['string_var'] == ("initial", "changed")
        assert changed['int_var'] == (42, 100)

    def test_reset(self):
        """Should reset manager to initial state."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make changes
        form.string_var.set("changed")
        manager.update_has_unsaved()

        assert manager.has_unsaved_changes is True

        # Reset
        manager.reset()

        assert manager.initial_state == {}
        assert manager.current_state == {}
        assert manager.has_unsaved_changes is False
        assert manager._tracked_vars == {}

    def test_tracked_vars_persist_after_capture(self):
        """Tracked variables should remain after capture."""
        form = MockForm()
        manager = FormStateManager(form)

        manager.capture_initial_state()

        # Make sure tracked vars are still there
        assert len(manager._tracked_vars) == 4

        # Make another capture (simulating re-tracking)
        manager.capture_initial_state()

        # Should still have tracked vars
        assert len(manager._tracked_vars) == 4

    def test_ignores_private_attributes(self):
        """Should ignore attributes starting with underscore."""
        form = MockForm()
        # Add a private variable
        form._private_var = ctk.StringVar(value="private")

        manager = FormStateManager(form)
        manager.capture_initial_state()

        # Private var should not be tracked
        assert '_private_var' not in manager.initial_state
        assert '_private_var' not in manager._tracked_vars

    def test_handles_non_variable_attributes(self):
        """Should ignore non-variable attributes gracefully."""
        form = MockForm()
        # Add non-variable attributes
        form.string_attr = "string"
        form.int_attr = 123
        form.list_attr = [1, 2, 3]

        manager = FormStateManager(form)
        manager.capture_initial_state()

        # Non-variable attributes should not be tracked
        assert 'string_attr' not in manager.initial_state
        assert 'int_attr' not in manager.initial_state
        assert 'list_attr' not in manager.initial_state
