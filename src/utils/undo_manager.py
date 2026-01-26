"""Undo/Redo manager for tracking and reverting destructive operations.

This module provides functionality to track user actions and allow
undoing/redoing them, particularly for destructive operations like delete.
"""

import copy
import pickle
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from employee.models import Caces, Employee, MedicalVisit, OnlineTraining


class UndoableAction:
    """Base class for undoable actions.

    Each action stores the information needed to execute, undo, and redo
    a user operation.
    """

    action_id: int = 0

    def __init__(self, description: str):
        """Initialize an undoable action.

        Args:
            description: Human-readable description of the action
        """
        self.action_id = UndoableAction.action_id
        UndoableAction.action_id += 1
        self.description = description
        self.timestamp = datetime.now()

    def execute(self) -> bool:
        """Execute the action.

        Returns:
            True if action succeeded, False otherwise
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def undo(self) -> bool:
        """Undo the action.

        Returns:
            True if undo succeeded, False otherwise
        """
        raise NotImplementedError("Subclasses must implement undo()")

    def redo(self) -> bool:
        """Redo the action.

        Returns:
            True if redo succeeded, False otherwise
        """
        # Default implementation is to execute again
        return self.execute()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.description})"


class DeleteAction(UndoableAction):
    """Action for soft delete operations that can be undone via restore."""

    def __init__(self, model_instance, description: str, item_type: str):
        """Initialize a delete action.

        Args:
            model_instance: The model instance that was soft deleted
            description: Human-readable description
            item_type: Type of item ('employee', 'caces', 'medical_visit', 'training')
        """
        super().__init__(description)
        self.model_class = type(model_instance)
        self.instance_id = model_instance.id
        self.item_type = item_type
        # Store a snapshot of the instance data for reference
        self._snapshot = self._capture_snapshot(model_instance)

    def _capture_snapshot(self, instance) -> Dict[str, Any]:
        """Capture a snapshot of the instance data.

        Args:
            instance: The model instance to snapshot

        Returns:
            Dictionary containing instance data
        """
        snapshot = {}
        for field_name in instance._meta.fields:
            if field_name == "id":
                continue
            value = getattr(instance, field_name, None)
            # Handle foreign keys
            if hasattr(value, "id"):
                snapshot[field_name] = value.id
            else:
                snapshot[field_name] = value
        return snapshot

    def execute(self) -> bool:
        """Execute the delete (already done, just confirm).

        Returns:
            True (delete was already executed)
        """
        # The delete is already executed before action is recorded
        return True

    def undo(self) -> bool:
        """Undo the delete by restoring the soft-deleted item.

        Returns:
            True if restore succeeded, False otherwise
        """
        try:
            instance = self.model_class.get_by_id(self.instance_id)
            if instance and hasattr(instance, "restore"):
                instance.restore()
                return True
            return False
        except Exception:
            return False

    def redo(self) -> bool:
        """Redo the delete by soft deleting again.

        Returns:
            True if redo succeeded, False otherwise
        """
        try:
            instance = self.model_class.get_by_id(self.instance_id)
            if instance and hasattr(instance, "soft_delete"):
                instance.soft_delete(reason="Redo of delete action", deleted_by=None)
                return True
            return False
        except Exception:
            return False


class UpdateAction(UndoableAction):
    """Action for update operations that can be undone by reverting to old values."""

    def __init__(
        self,
        model_instance,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        description: str,
        item_type: str,
    ):
        """Initialize an update action.

        Args:
            model_instance: The model instance that was updated
            old_values: Dictionary of field names to old values
            new_values: Dictionary of field names to new values
            description: Human-readable description
            item_type: Type of item ('employee', 'caces', 'medical_visit', 'training')
        """
        super().__init__(description)
        self.model_class = type(model_instance)
        self.instance_id = model_instance.id
        self.old_values = copy.deepcopy(old_values)
        self.new_values = copy.deepcopy(new_values)
        self.item_type = item_type

    def execute(self) -> bool:
        """Execute the update (already done, just confirm).

        Returns:
            True (update was already executed)
        """
        # The update is already executed before action is recorded
        return True

    def undo(self) -> bool:
        """Undo the update by reverting to old values.

        Returns:
            True if undo succeeded, False otherwise
        """
        try:
            instance = self.model_class.get_by_id(self.instance_id)
            if instance:
                for field_name, value in self.old_values.items():
                    setattr(instance, field_name, value)
                instance.save()
                return True
            return False
        except Exception:
            return False

    def redo(self) -> bool:
        """Redo the update by applying new values again.

        Returns:
            True if redo succeeded, False otherwise
        """
        try:
            instance = self.model_class.get_by_id(self.instance_id)
            if instance:
                for field_name, value in self.new_values.items():
                    setattr(instance, field_name, value)
                instance.save()
                return True
            return False
        except Exception:
            return False


class CreateAction(UndoableAction):
    """Action for create operations that can be undone by deleting the created item."""

    def __init__(self, model_instance, description: str, item_type: str):
        """Initialize a create action.

        Args:
            model_instance: The model instance that was created
            description: Human-readable description
            item_type: Type of item ('employee', 'caces', 'medical_visit', 'training')
        """
        super().__init__(description)
        self.model_class = type(model_instance)
        self.instance_id = model_instance.id
        self.item_type = item_type
        # Store snapshot for potential redo
        self._snapshot = self._capture_snapshot(model_instance)

    def _capture_snapshot(self, instance) -> Dict[str, Any]:
        """Capture a snapshot of the instance data.

        Args:
            instance: The model instance to snapshot

        Returns:
            Dictionary containing instance data
        """
        snapshot = {}
        for field_name in instance._meta.fields:
            if field_name in ["id", "created_at", "updated_at"]:
                continue
            value = getattr(instance, field_name, None)
            # Handle foreign keys
            if hasattr(value, "id"):
                snapshot[field_name] = value.id
            else:
                snapshot[field_name] = value
        return snapshot

    def execute(self) -> bool:
        """Execute the create (already done, just confirm).

        Returns:
            True (create was already executed)
        """
        # The create is already executed before action is recorded
        return True

    def undo(self) -> bool:
        """Undo the create by soft deleting the created item.

        Returns:
            True if undo succeeded, False otherwise
        """
        try:
            instance = self.model_class.get_by_id(self.instance_id)
            if instance and hasattr(instance, "soft_delete"):
                instance.soft_delete(reason="Undo of create action", deleted_by=None)
                return True
            return False
        except Exception:
            return False

    def redo(self) -> bool:
        """Redo the create by restoring and updating with snapshot data.

        Returns:
            True if redo succeeded, False otherwise
        """
        try:
            instance = self.model_class.get_by_id(self.instance_id)
            if instance and hasattr(instance, "restore"):
                # First restore if soft deleted
                if instance.is_deleted:
                    instance.restore()
                # Then update with snapshot data
                for field_name, value in self._snapshot.items():
                    if field_name not in ["id", "created_at", "updated_at"]:
                        setattr(instance, field_name, value)
                instance.save()
                return True
            return False
        except Exception:
            return False


class UndoManager:
    """Manager for tracking and executing undo/redo operations.

    This singleton class maintains stacks of undoable and redoable actions,
    providing a centralized way to revert and re-apply user operations.

    Features:
    - Track destructive operations (delete, update, create)
    - Undo last action with Ctrl+Z
    - Redo last undone action with Ctrl+Y
    - Configurable history size
    - Action callbacks for UI updates
    """

    _instance: Optional["UndoManager"] = None

    def __init__(self, max_history: int = 100):
        """Initialize the undo manager.

        Args:
            max_history: Maximum number of actions to keep in history
        """
        if UndoManager._instance is not None:
            raise RuntimeError("UndoManager is a singleton. Use get_instance() instead.")

        self.undo_stack: List[UndoableAction] = []
        self.redo_stack: List[UndoableAction] = []
        self.max_history = max_history
        self._undo_callbacks: List[Callable[[], None]] = []
        self._redo_callbacks: List[Callable[[], None]] = []
        self._history_callbacks: List[Callable[[], None]] = []

    @classmethod
    def get_instance(cls) -> "UndoManager":
        """Get the singleton UndoManager instance.

        Returns:
            The UndoManager singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (mainly for testing)."""
        cls._instance = None

    def record_action(self, action: UndoableAction) -> None:
        """Record an action for potential undo.

        Args:
            action: The undoable action to record
        """
        # Add to undo stack
        self.undo_stack.append(action)

        # Clear redo stack (new action invalidates redo history)
        self.redo_stack.clear()

        # Enforce max history size
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        # Notify listeners
        self._notify_history_changed()

    def undo(self) -> Optional[UndoableAction]:
        """Undo the last action.

        Returns:
            The action that was undone, or None if nothing to undo
        """
        if not self.undo_stack:
            return None

        action = self.undo_stack.pop()
        success = action.undo()

        if success:
            # Add to redo stack
            self.redo_stack.append(action)
            self._notify_history_changed()
            return action
        else:
            # Put it back if undo failed
            self.undo_stack.append(action)
            return None

    def redo(self) -> Optional[UndoableAction]:
        """Redo the last undone action.

        Returns:
            The action that was redone, or None if nothing to redo
        """
        if not self.redo_stack:
            return None

        action = self.redo_stack.pop()
        success = action.redo()

        if success:
            # Add back to undo stack
            self.undo_stack.append(action)
            self._notify_history_changed()
            return action
        else:
            # Put it back if redo failed
            self.redo_stack.append(action)
            return None

    def can_undo(self) -> bool:
        """Check if there's something to undo.

        Returns:
            True if undo is available, False otherwise
        """
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if there's something to redo.

        Returns:
            True if redo is available, False otherwise
        """
        return len(self.redo_stack) > 0

    def get_undo_description(self) -> Optional[str]:
        """Get description of the next undo action.

        Returns:
            Description of action that would be undone, or None
        """
        if self.undo_stack:
            return self.undo_stack[-1].description
        return None

    def get_redo_description(self) -> Optional[str]:
        """Get description of the next redo action.

        Returns:
            Description of action that would be redone, or None
        """
        if self.redo_stack:
            return self.redo_stack[-1].description
        return None

    def clear_history(self) -> None:
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._notify_history_changed()

    def register_undo_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to be called when undo availability changes.

        Args:
            callback: Function to call when undo state changes
        """
        if callback not in self._undo_callbacks:
            self._undo_callbacks.append(callback)

    def register_redo_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to be called when redo availability changes.

        Args:
            callback: Function to call when redo state changes
        """
        if callback not in self._redo_callbacks:
            self._redo_callbacks.append(callback)

    def register_history_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to be called when history changes.

        Args:
            callback: Function to call when history changes
        """
        if callback not in self._history_callbacks:
            self._history_callbacks.append(callback)

    def _notify_history_changed(self) -> None:
        """Notify all registered callbacks that history has changed."""
        for callback in self._history_callbacks:
            try:
                callback()
            except Exception:
                pass  # Ignore callback errors

    def get_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the current undo/redo history.

        Returns:
            Dictionary with 'undo' and 'redo' lists of action descriptions
        """
        return {
            "undo": [
                {
                    "id": action.action_id,
                    "description": action.description,
                    "timestamp": action.timestamp.isoformat(),
                    "type": action.__class__.__name__,
                }
                for action in reversed(self.undo_stack)
            ],
            "redo": [
                {
                    "id": action.action_id,
                    "description": action.description,
                    "timestamp": action.timestamp.isoformat(),
                    "type": action.__class__.__name__,
                }
                for action in reversed(self.redo_stack)
            ],
        }


def get_undo_manager() -> UndoManager:
    """Get the singleton UndoManager instance.

    Returns:
        The UndoManager singleton instance
    """
    return UndoManager.get_instance()


def record_delete(model_instance, description: str, item_type: str) -> None:
    """Convenience function to record a delete action.

    Args:
        model_instance: The model instance that was deleted
        description: Human-readable description
        item_type: Type of item
    """
    manager = get_undo_manager()
    action = DeleteAction(model_instance, description, item_type)
    manager.record_action(action)


def record_update(
    model_instance, old_values: Dict[str, Any], new_values: Dict[str, Any], description: str, item_type: str
) -> None:
    """Convenience function to record an update action.

    Args:
        model_instance: The model instance that was updated
        old_values: Dictionary of old field values
        new_values: Dictionary of new field values
        description: Human-readable description
        item_type: Type of item
    """
    manager = get_undo_manager()
    action = UpdateAction(model_instance, old_values, new_values, description, item_type)
    manager.record_action(action)


def record_create(model_instance, description: str, item_type: str) -> None:
    """Convenience function to record a create action.

    Args:
        model_instance: The model instance that was created
        description: Human-readable description
        item_type: Type of item
    """
    manager = get_undo_manager()
    action = CreateAction(model_instance, description, item_type)
    manager.record_action(action)
