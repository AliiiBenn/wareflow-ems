"""Tests for the undo/redo manager."""

import pickle
from datetime import date
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from employee.models import Caces, Employee, MedicalVisit, OnlineTraining
from utils.undo_manager import (
    CreateAction,
    DeleteAction,
    UndoManager,
    UndoableAction,
    UpdateAction,
    get_undo_manager,
    record_create,
    record_delete,
    record_update,
)


class MockUndoableAction(UndoableAction):
    """Mock undoable action for testing."""

    def __init__(self, description: str, execute_result: bool = True, undo_result: bool = True):
        super().__init__(description)
        self._execute_result = execute_result
        self._undo_result = undo_result
        self.execute_count = 0
        self.undo_count = 0
        self.redo_count = 0

    def execute(self) -> bool:
        self.execute_count += 1
        return self._execute_result

    def undo(self) -> bool:
        self.undo_count += 1
        return self._undo_result

    def redo(self) -> bool:
        self.redo_count += 1
        return self._execute_result


class TestUndoableAction:
    """Test the base UndoableAction class."""

    def test_action_has_id(self):
        """Test that each action has a unique ID."""
        action1 = UndoableAction("Test action 1")
        action2 = UndoableAction("Test action 2")
        assert action1.action_id != action2.action_id

    def test_action_has_timestamp(self):
        """Test that action has a timestamp."""
        action = UndoableAction("Test action")
        assert action.timestamp is not None

    def test_action_requires_implementation(self):
        """Test that execute and undo raise NotImplementedError."""
        action = UndoableAction("Test action")
        with pytest.raises(NotImplementedError):
            action.execute()
        with pytest.raises(NotImplementedError):
            action.undo()

    def test_redo_defaults_to_execute(self):
        """Test that redo defaults to calling execute."""
        action = UndoableAction("Test action")
        # Since execute raises NotImplementedError, redo should too
        with pytest.raises(NotImplementedError):
            action.redo()

    def test_action_repr(self):
        """Test action string representation."""
        action = UndoableAction("Test action")
        assert "UndoableAction" in repr(action)
        assert "Test action" in repr(action)


class TestDeleteAction:
    """Test the DeleteAction class for soft delete operations."""

    def test_delete_action_captures_snapshot(self, db):
        """Test that delete action captures instance snapshot."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        emp.soft_delete(reason="Test deletion")

        action = DeleteAction(emp, "Delete John Doe", "employee")

        assert action.instance_id == emp.id
        assert action.model_class == Employee
        assert action.item_type == "employee"
        assert action._snapshot is not None
        assert action._snapshot["first_name"] == "John"

    def test_delete_action_execute_returns_true(self, db):
        """Test that execute returns True (delete already done)."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        emp.soft_delete(reason="Test deletion")

        action = DeleteAction(emp, "Delete John Doe", "employee")
        assert action.execute() is True

    def test_delete_action_undo_restores_employee(self, db):
        """Test that undo restores the soft-deleted employee."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        emp.soft_delete(reason="Test deletion")

        action = DeleteAction(emp, "Delete John Doe", "employee")
        result = action.undo()

        assert result is True
        # Reload and check
        emp_reloaded = Employee.get_by_id(emp.id)
        assert emp_reloaded.is_deleted is False

    def test_delete_action_undo_restores_caces(self, db):
        """Test that undo restores a soft-deleted CACES."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        caces = Caces.create(
            employee=emp, kind="R489-1A", completion_date=date(2023, 1, 1), expiration_date=date(2024, 1, 1)
        )
        caces.soft_delete(reason="Test deletion")

        action = DeleteAction(caces, "Delete CACES R489-1A", "caces")
        result = action.undo()

        assert result is True
        caces_reloaded = Caces.get_by_id(caces.id)
        assert caces_reloaded.is_deleted is False

    def test_delete_action_redo_deletes_again(self, db):
        """Test that redo soft deletes again."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        emp.soft_delete(reason="Test deletion")

        action = DeleteAction(emp, "Delete John Doe", "employee")
        action.undo()  # Restore it
        result = action.redo()  # Delete again

        assert result is True
        emp_reloaded = Employee.get_by_id(emp.id)
        assert emp_reloaded.is_deleted is True


class TestUpdateAction:
    """Test the UpdateAction class for update operations."""

    def test_update_action_stores_values(self, db):
        """Test that update action stores old and new values."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )

        old_values = {"first_name": "John", "email": "john@test.com"}
        new_values = {"first_name": "Jane", "email": "jane@test.com"}

        action = UpdateAction(emp, old_values, new_values, "Update employee info", "employee")

        assert action.old_values == old_values
        assert action.new_values == new_values
        assert action.instance_id == emp.id

    def test_update_action_undo_reverts_values(self, db):
        """Test that undo reverts to old values."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )

        # Make an update
        emp.first_name = "Jane"
        emp.email = "jane@test.com"
        emp.save()

        old_values = {"first_name": "John", "email": "john@test.com"}
        new_values = {"first_name": "Jane", "email": "jane@test.com"}

        action = UpdateAction(emp, old_values, new_values, "Update employee info", "employee")
        result = action.undo()

        assert result is True
        emp_reloaded = Employee.get_by_id(emp.id)
        assert emp_reloaded.first_name == "John"
        assert emp_reloaded.email == "john@test.com"

    def test_update_action_redo_applies_new_values(self, db):
        """Test that redo applies new values again."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )

        # Make an update
        emp.first_name = "Jane"
        emp.save()

        old_values = {"first_name": "John"}
        new_values = {"first_name": "Jane"}

        action = UpdateAction(emp, old_values, new_values, "Update name", "employee")
        action.undo()  # Revert to John
        result = action.redo()  # Apply Jane again

        assert result is True
        emp_reloaded = Employee.get_by_id(emp.id)
        assert emp_reloaded.first_name == "Jane"


class TestCreateAction:
    """Test the CreateAction class for create operations."""

    def test_create_action_captures_snapshot(self, db):
        """Test that create action captures instance snapshot."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )

        action = CreateAction(emp, "Create John Doe", "employee")

        assert action.instance_id == emp.id
        assert action._snapshot is not None
        assert action._snapshot["first_name"] == "John"

    def test_create_action_undo_deletes(self, db):
        """Test that undo soft deletes the created item."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )

        action = CreateAction(emp, "Create John Doe", "employee")
        result = action.undo()

        assert result is True
        emp_reloaded = Employee.get_by_id(emp.id)
        assert emp_reloaded.is_deleted is True

    def test_create_action_redo_restores(self, db):
        """Test that redo restores the deleted created item."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )

        action = CreateAction(emp, "Create John Doe", "employee")
        action.undo()  # Soft delete
        result = action.redo()  # Should restore

        assert result is True
        emp_reloaded = Employee.get_by_id(emp.id)
        assert emp_reloaded.is_deleted is False
        assert emp_reloaded.first_name == "John"


class TestUndoManager:
    """Test the UndoManager class."""

    def setup_method(self):
        """Reset the UndoManager singleton before each test."""
        UndoManager.reset_instance()

    def test_singleton_pattern(self):
        """Test that UndoManager is a singleton."""
        manager1 = UndoManager.get_instance()
        manager2 = UndoManager.get_instance()
        assert manager1 is manager2

    def test_max_history_limit(self):
        """Test that history respects max_history limit."""
        manager = UndoManager(max_history=3)
        for i in range(5):
            action = MockUndoableAction(f"Action {i}")
            manager.record_action(action)

        assert len(manager.undo_stack) == 3
        # Should keep the most recent 3 actions (indices 2, 3, 4)
        assert manager.undo_stack[0].description == "Action 2"
        assert manager.undo_stack[2].description == "Action 4"

    def test_can_undo(self):
        """Test can_undo returns correct state."""
        manager = UndoManager.get_instance()
        assert manager.can_undo() is False

        action = MockUndoableAction("Test action")
        manager.record_action(action)
        assert manager.can_undo() is True

    def test_can_redo(self):
        """Test can_redo returns correct state."""
        manager = UndoManager.get_instance()
        assert manager.can_redo() is False

        action = MockUndoableAction("Test action")
        manager.record_action(action)
        assert manager.can_redo() is False  # Nothing to redo yet

        manager.undo()
        assert manager.can_redo() is True

    def test_record_action(self):
        """Test recording an action."""
        manager = UndoManager.get_instance()
        action = MockUndoableAction("Test action")
        manager.record_action(action)

        assert len(manager.undo_stack) == 1
        assert manager.undo_stack[0] is action
        assert len(manager.redo_stack) == 0  # Redo stack cleared

    def test_record_action_clears_redo_stack(self):
        """Test that recording action clears redo stack."""
        manager = UndoManager.get_instance()
        action1 = MockUndoableAction("Action 1")
        action2 = MockUndoableAction("Action 2")

        manager.record_action(action1)
        manager.undo()  # Move to redo stack
        assert len(manager.redo_stack) == 1

        manager.record_action(action2)  # Should clear redo stack
        assert len(manager.redo_stack) == 0

    def test_undo(self):
        """Test undo operation."""
        manager = UndoManager.get_instance()
        action = MockUndoableAction("Test action")

        manager.record_action(action)
        result = manager.undo()

        assert result is action
        assert len(manager.undo_stack) == 0
        assert len(manager.redo_stack) == 1
        assert action.undo_count == 1

    def test_undo_failure(self):
        """Test that failed undo puts action back."""
        manager = UndoManager.get_instance()
        action = MockUndoableAction("Test action", undo_result=False)

        manager.record_action(action)
        result = manager.undo()

        assert result is None
        assert len(manager.undo_stack) == 1  # Still in undo stack
        assert len(manager.redo_stack) == 0

    def test_redo(self):
        """Test redo operation."""
        manager = UndoManager.get_instance()
        action = MockUndoableAction("Test action")

        manager.record_action(action)
        manager.undo()
        result = manager.redo()

        assert result is action
        assert len(manager.undo_stack) == 1
        assert len(manager.redo_stack) == 0
        assert action.redo_count == 1

    def test_redo_failure(self):
        """Test that failed redo puts action back."""
        manager = UndoManager.get_instance()
        action = MockUndoableAction("Test action", execute_result=False)

        manager.record_action(action)
        manager.undo()
        result = manager.redo()

        assert result is None
        assert len(manager.redo_stack) == 1  # Still in redo stack
        assert len(manager.undo_stack) == 0

    def test_get_undo_description(self):
        """Test getting description of next undo action."""
        manager = UndoManager.get_instance()
        assert manager.get_undo_description() is None

        action = MockUndoableAction("Test action")
        manager.record_action(action)
        assert manager.get_undo_description() == "Test action"

    def test_get_redo_description(self):
        """Test getting description of next redo action."""
        manager = UndoManager.get_instance()
        assert manager.get_redo_description() is None

        action = MockUndoableAction("Test action")
        manager.record_action(action)
        manager.undo()
        assert manager.get_redo_description() == "Test action"

    def test_clear_history(self):
        """Test clearing history."""
        manager = UndoManager.get_instance()
        action = MockUndoableAction("Test action")
        manager.record_action(action)
        manager.undo()

        manager.clear_history()
        assert len(manager.undo_stack) == 0
        assert len(manager.redo_stack) == 0

    def test_get_history(self):
        """Test getting history as dict."""
        manager = UndoManager.get_instance()
        action1 = MockUndoableAction("Action 1")
        action2 = MockUndoableAction("Action 2")

        manager.record_action(action1)
        manager.record_action(action2)

        history = manager.get_history()
        assert "undo" in history
        assert "redo" in history
        assert len(history["undo"]) == 2
        assert len(history["redo"]) == 0
        # Most recent action should be first
        assert history["undo"][0]["description"] == "Action 2"
        assert history["undo"][1]["description"] == "Action 1"

    def test_callbacks(self):
        """Test history change callbacks."""
        manager = UndoManager.get_instance()
        callback_called = []

        def callback():
            callback_called.append(True)

        manager.register_history_callback(callback)
        action = MockUndoableAction("Test action")
        manager.record_action(action)

        assert len(callback_called) == 1


class TestUndoManagerIntegration:
    """Integration tests with real model operations."""

    def setup_method(self):
        """Reset the UndoManager singleton before each test."""
        UndoManager.reset_instance()

    def test_full_undo_redo_cycle_employee(self, db):
        """Test full undo/redo cycle with employee."""
        manager = UndoManager.get_instance()

        # Create employee
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        record_create(emp, "Create John Doe", "employee")

        # Update employee
        old_values = {"first_name": "John"}
        emp.first_name = "Jane"
        emp.save()
        new_values = {"first_name": "Jane"}
        record_update(emp, old_values, new_values, "Update name", "employee")

        # Delete employee
        emp.soft_delete(reason="Test")
        record_delete(emp, "Delete John Doe", "employee")

        # Undo delete
        action = manager.undo()
        assert action is not None
        assert "Delete" in action.description
        emp_check = Employee.get_by_id(emp.id)
        assert emp_check.is_deleted is False

        # Undo update
        action = manager.undo()
        assert action is not None
        assert "Update" in action.description
        emp_check = Employee.get_by_id(emp.id)
        assert emp_check.first_name == "John"

        # Undo create
        action = manager.undo()
        assert action is not None
        assert "Create" in action.description
        emp_check = Employee.get_by_id(emp.id)
        assert emp_check.is_deleted is True

        # Redo create
        action = manager.redo()
        assert action is not None
        emp_check = Employee.get_by_id(emp.id)
        assert emp_check.is_deleted is False
        assert emp_check.first_name == "John"

    def test_multiple_actions_employee_with_caces(self, db):
        """Test undo/redo with employee and related CACES."""
        manager = UndoManager.get_instance()

        # Create employee
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        record_create(emp, "Create John Doe", "employee")

        # Create CACES
        caces = Caces.create(
            employee=emp, kind="R489-1A", completion_date=date(2023, 1, 1), expiration_date=date(2024, 1, 1)
        )
        record_create(caces, "Add CACES R489-1A", "caces")

        # Delete CACES
        caces.soft_delete(reason="Test")
        record_delete(caces, "Delete CACES", "caces")

        # Undo CACES delete
        manager.undo()
        caces_check = Caces.get_by_id(caces.id)
        assert caces_check.is_deleted is False

        # Undo CACES create
        manager.undo()
        caces_check = Caces.get_by_id(caces.id)
        assert caces_check.is_deleted is True


class TestConvenienceFunctions:
    """Test convenience functions for recording actions."""

    def setup_method(self):
        """Reset the UndoManager singleton before each test."""
        UndoManager.reset_instance()

    def test_record_delete(self, db):
        """Test record_delete convenience function."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        emp.soft_delete(reason="Test")
        record_delete(emp, "Delete John Doe", "employee")

        manager = get_undo_manager()
        assert manager.can_undo() is True
        assert manager.get_undo_description() == "Delete John Doe"

    def test_record_update(self, db):
        """Test record_update convenience function."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        old_values = {"first_name": "John"}
        emp.first_name = "Jane"
        emp.save()
        record_update(emp, old_values, {"first_name": "Jane"}, "Update name", "employee")

        manager = get_undo_manager()
        assert manager.can_undo() is True
        assert manager.get_undo_description() == "Update name"

    def test_record_create(self, db):
        """Test record_create convenience function."""
        emp = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        record_create(emp, "Create John Doe", "employee")

        manager = get_undo_manager()
        assert manager.can_undo() is True
        assert manager.get_undo_description() == "Create John Doe"
