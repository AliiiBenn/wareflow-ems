# [CRITICAL] No Undo/Redo Functionality for Destructive Operations

## Type
**User Experience / Data Safety**

## Severity
**CRITICAL** - High risk of accidental data loss with no recovery mechanism

## Affected Components
- `src/ui_ctk/views/employee_detail.py`
  - Employee deletion (lines 494-516)
  - CACES deletion (lines 568-589)
  - Medical visit deletion (lines 623-647)

## Description
The application allows permanent deletion of critical data with NO way to:
- Undo accidental deletions
- Recover from mistakes
- Restore deleted records
- Audit what was deleted

This is especially dangerous for:
- Human error (clicking wrong button)
- Misunderstanding of UI
- Training/onboarding accidents
- Malicious actions by disgruntled employees

## Problematic Code

### Employee Deletion (PERMANENT)
```python
# employee_detail.py:494-516
def delete_employee(self):
    """Delete employee and all related data."""
    # Confirmation dialog
    confirm = messagebox.askyesno(
        "Confirmation",
        CONFIRM_DELETE_EMPLOYEE
    )

    if confirm:
        try:
            self.employee.delete_instance()  # ← PERMANENT! No undo!
            print(f"[OK] Employee deleted: {self.employee.full_name}")

            # Go back to list
            self.show_employee_list()

        except Exception as e:
            print(f"[ERROR] Failed to delete employee: {e}")
            self.show_error(f"{ERROR_DELETE_EMPLOYEE}: {e}")
```

### Impact of Deletion
When employee is deleted with `delete_instance()`:
- ✅ Employee record deleted
- ❌ All CACES certifications DELETED (CASCADE)
- ❌ All medical visits DELETED (CASCADE)
- ❌ All training records DELETED (CASCADE)
- ❌ Audit trail LOST (no record of deletion)
- ❌ **NO WAY TO RECOVER**

## Real-World Scenarios

### Scenario 1: Accidental Click
User intends to edit employee but accidentally clicks "Supprimer" (Delete):
1. User clicks "Supprimer" thinking it's "Modifier"
2. Confirmation dialog appears
3. User instinctively clicks "Oui" (yes)
4. **ALL DATA LOST PERMANENTLY**
5. No way to undo
6. Must re-enter all data from scratch

### Scenario 2: Wrong Employee Selected
User wants to delete employee "Smith, John" but accidentally has "Dupont, Jean" selected:
1. User clicks delete
2. Confirms deletion
3. **Wrong employee deleted**
4. Critical certifications lost
5. No recovery mechanism

### Scenario 3: Testing/Development
Developer or QA testing deletion functionality:
1. Deletes test employee
2. Needs to recreate employee multiple times
3. Inefficient workflow
4. Time wasted

### Scenario 4: Malicious Insider
Disgruntled employee about to leave:
1. Deletes critical employees
2. Deletes their own records
3. **Cannot trace or recover**

## Missing Features

### Undo Functionality
- [ ] Undo last action (Ctrl+Z)
- [ ] Undo history (last 10 actions)
- [ ] Redo capability

### Soft Delete
- [ ] Mark as deleted instead of permanent delete
- [ ] Restore from trash
- [ ] Empty trash periodically
- [ ] Audit trail of deletion

### Confirmation Improvements
- [ ] Show employee name in confirmation
- [ ] Show what will be deleted
- [ ] Count related records to be deleted
- [ ] Warning if employee has critical certifications

### Recovery Options
- [ ] Recycle bin/trash functionality
- [ ] Data export before deletion
- [ ] Backup/restore functionality
- [ ] Undelete utility (admin only)

## Proposed Solution

### Option 1: Soft Delete with Trash (Recommended)

#### Add Deleted Field to Models
```python
# src/employee/models.py
class Employee(Model):
    # ... existing fields ...

    # Soft delete
    deleted_at = DateTimeField(null=True, index=True)
    deleted_by = ForeignKeyField('user', null=True)  # Who deleted

    @property
    def is_active(self):
        """Check if employee is active (not soft deleted)."""
        return self.deleted_at is None
```

#### Update Queries to Filter Deleted Records
```python
# All queries must filter: where(deleted_at__isnull=True)
active_employees = Employee.select().where(Employee.deleted_at__isnull=True)
```

#### Add Trash Functionality
```python
# src/ui_ctk/views/trash_view.py (new)
class TrashView(BaseView):
    """View deleted items that can be restored."""

    def __init__(self, master, title: str = "Corbeille"):
        super().__init__(master, title=title)

        # Load deleted employees
        self.deleted_employees = Employee.select().where(
            Employee.deleted_at__isnull=False
        ).order_by(Employee.deleted_at.desc())

        # Display with restore buttons
        self.display_deleted_employees()

    def restore_employee(self, employee):
        """Restore deleted employee."""
        employee.deleted_at = None
        employee.save()
        print(f"[OK] Restored: {employee.full_name}")
        self.refresh_view()
```

#### Deletion Flow with Soft Delete
```python
def delete_employee(self):
    """Soft delete employee (moves to trash)."""
    # Show confirmation with details
    n_caces = self.employee.caces.count()
    n_visits = self.employee.medical_visits.count()

    confirm = messagebox.askyesno(
        "Confirmer la suppression",
        f"Voulez-vous vraiment supprimer {self.employee.full_name} ?\n\n"
        f"Cette action déplacera l'employé dans la corbeille.\n"
        f"CACES: {n_caces}, Visites: {n_visits}"
    )

    if confirm:
        import datetime
        from src.auth import get_current_user  # When auth added

        # Soft delete
        self.employee.deleted_at = datetime.datetime.now()
        # self.employee.deleted_by = get_current_user()  # When auth added
        self.employee.save()

        print(f"[OK] Employee moved to trash: {self.employee.full_name}")
        self.show_employee_list()
```

### Option 2: Undo Buffer

```python
# src/state/undo_manager.py
from typing import List, Any, Callable
from dataclasses import dataclass

@dataclass
class UndoAction:
    """Represents an undoable action."""
    action_type: str  # 'delete_employee', 'delete_caces', etc.
    object_type: str   # 'employee', 'caces', 'visit'
    object_id: str
    previous_state: dict
    timestamp: datetime

class UndoManager:
    """Manages undo/redo functionality."""

    def __init__(self, max_history: int = 50):
        self.undo_stack: List[UndoAction] = []
        self.redo_stack: List[UndoAction] = []
        self.max_history = max_history

    def record_action(self, action: UndoAction):
        """Record an action for potential undo."""
        self.undo_stack.append(action)
        self.redo_stack.clear()  # Clear redo on new action

        # Trim history if needed
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

    def undo(self) -> bool:
        """Undo last action. Returns True if successful."""
        if not self.undo_stack:
            return False

        action = self.undo_stack.pop()
        self.redo_stack.append(action)

        # Restore based on action type
        if action.action_type == 'delete_employee':
            self._restore_employee(action)
        elif action.action_type == 'delete_caces':
            self._restore_caces(action)

        return True

    def redo(self) -> bool:
        """Redo last undone action. Returns True if successful."""
        if not self.redo_stack:
            return False

        action = self.redo_stack.pop()
        self.undo_stack.append(action)

        # Re-apply the action
        # ...

        return True

# Global instance
undo_manager = UndoManager()
```

#### Usage in Delete Operations
```python
def delete_employee(self):
    """Delete employee with undo support."""
    # Save state before deletion
    import copy
    previous_state = {
        'employee': copy.deepcopy(self.employee.__dict__),
        'caces': list(self.employee.caces),
        'visits': list(self.employee.medical_visits),
    }

    # Confirm and delete
    if self._confirm_deletion():
        # Delete
        employee_id = self.employee.id
        self.employee.delete_instance()

        # Record action for undo
        action = UndoAction(
            action_type='delete_employee',
            object_type='employee',
            object_id=str(employee_id),
            previous_state=previous_state,
            timestamp=datetime.now()
        )
        undo_manager.record_action(action)

        self.show_employee_list()

def _confirm_deletion(self) -> bool:
    """Show deletion confirmation."""
    return messagebox.askyesno(
        "Confirmer",
        f"Supprimer {self.employee.full_name} ?"
    )
```

### Option 3: Data Export Before Deletion

```python
def delete_employee(self):
    """Delete employee with automatic backup."""
    # Export data before deletion
    backup_file = export_employee_data(self.employee)

    # Confirm with backup information
    confirm = messagebox.askyesno(
        "Confirmer",
        f"Supprimer {self.employee.full_name} ?\n\n"
        f"Données sauvegardées dans:\n{backup_file}\n\n"
        f"Confirmer la suppression ?"
    )

    if confirm:
        # Perform deletion
        self.employee.delete_instance()
        print(f"[OK] Employee deleted: {self.employee.full_name}")
        print(f"[INFO] Backup: {backup_file}")

        self.show_employee_list()
```

## Implementation Plan

### Phase 1: Add Soft Delete (2-3 hours)
1. Add `deleted_at` field to Employee model
2. Create database migration
3. Update all queries to filter soft-deleted records
4. Add trash view
5. Add restore functionality
6. Write tests

### Phase 2: Add Undo/Redo (3-4 hours)
1. Create UndoManager
2. Record actions before destructive operations
3. Add Ctrl+Z keyboard shortcut
4. Add undo/redo buttons to UI
5. Write tests

### Phase 3: Enhanced Confirmations (1 hour)
1. Show detailed deletion info
2. Display count of related records
3. Show warnings for critical data
4. Add countdown timer (optional)

### Phase 4: Backup Integration (2 hours)
1. Auto-export before deletion
2. Keep backups for 30 days
3. Allow manual backup restore
4. Add backup management UI

## Files to Create
- `src/state/undo_manager.py`
- `src/ui_ctk/views/trash_view.py`
- `src/utils/backup_manager.py`
- `tests/test_undo_redo.py`

## Files to Modify
- `src/employee/models.py` - Add deleted_at field
- `src/ui_ctk/views/employee_detail.py` - Update delete operations
- `src/ui_ctk/views/employee_list.py` - Filter deleted employees
- `src/ui_ctk/views/alerts_view.py` - Filter deleted employees
- `src/ui_ctk/main_window.py` - Add undo/redo buttons

## Database Migration

```sql
-- Migration: Add soft delete to employees
ALTER TABLE employees ADD COLUMN deleted_at TIMESTAMP NULL;
CREATE INDEX idx_employee_deleted_at ON employees(deleted_at);

-- For existing records that should be active
ALTER TABLE employees ADD COLUMN deleted_by TEXT NULL;

-- Create table for tracking (when we add users)
-- CREATE TABLE deleted_records (
--     id UUID PRIMARY KEY,
--     table_name TEXT NOT NULL,
--     record_id TEXT NOT NULL,
--     deleted_at TIMESTAMP NOT NULL,
--     deleted_by TEXT,
--     reason TEXT
-- );
```

## Keyboard Shortcuts

### Undo
- **Windows/Linux**: Ctrl+Z
- **macOS**: Cmd+Z

### Redo
- **Windows/Linux**: Ctrl+Y or Ctrl+Shift+Z
- **macOS**: Cmd+Y or Cmd+Shift+Z

### Delete
- **Windows**: Delete key
- **macOS**: Backspace or Cmd+Delete

## UI Design for Trash

### Trash View
```
┌─────────────────────────────────────────────┐
│ 🗑️ Corbeille                        [Vider] │
├─────────────────────────────────────────────┤
│ Total: 3 employés                         │
│ ┌─────────────────────────────────────┐   │
│ │ ☐ Dupont Jean  [Restaurer]  [Supprimer] │   │
│ │ ☐ Smith John  [Restaurer]  [Supprimer] │   │
│ │ ☐ Martin Marie [Restaurer]  [Supprimer] │   │
│ └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Confirmation Dialog (Enhanced)
```
┌─────────────────────────────────────────────┐
│ ⚠️ Confirmer la suppression               │
├─────────────────────────────────────────────┤
│                                          │
│  Voulez-vous vraiment supprimer :          │
│                                          │
│  📋 Dupont Jean                          │
│  • ID: WMS-001                          │
│  • CACES: 3 certifications actives          │
│  • Visites: 2 visites médicales            │
│                                          │
│  Cette action :                            │
│  • Déplacera l'employé dans la corbeille     │
│  • Supprimera TOUTES les données liées      │
│  • NE PEUT PAS ÊTRE ANNULÉE                │
│                                          │
│  [ ] Ne plus demander pour cette session       │
│                                          │
│      [Annuler]  [Supprimer définitivement]     │
└─────────────────────────────────────────────┘
```

## Testing Requirements
- Test soft delete (employee marked as deleted, not removed)
- Test restore from trash
- Test undo (Ctrl+Z) for each operation
- Test redo (Ctrl+Y or Ctrl+Shift+Z)
- Test permanent delete from trash
- Test auto-delete from trash after N days
- Test that deleted employees don't appear in lists
- Test that deleted employees can be restored
- Test undo/redo for CACES and medical visits

## User Benefits
- **Safety**: Accidental deletions are recoverable
- **Confidence**: Can experiment without fear
- **Efficiency**: Don't need to recreate data from scratch
- **Audit**: Trail of what was deleted when
- **Compliance**: GDPR requires right to be forgotten AND data protection

## Related Issues
- #018: No audit trail (need tracking)
- #019: Cascade delete without soft delete (compounds this issue)
- #020: No optimistic locking (concurrent modification risk)

## References
- GDPR Right to be Forgotten vs Right to Rectification: https://gdpr-info.eu/issues/rights/gdpr-rights/
- Soft Delete Pattern: https://www.martinfowler.com/articles/soft-delete-pattern/
- Undo/Redo Pattern: https://www.python-design-patterns.com/2020/08/16/undo-redo-pattern.html

## Priority
**CRITICAL** - High risk of accidental data loss

## Estimated Effort
6-8 hours (soft delete + undo/redo + UI + tests)

## Mitigation
While waiting for full implementation:
1. Add strong confirmation dialogs
2. Show employee name and ID in confirmation
3. Count related records to be deleted
4. Add manual backup export before deletion
5. Document deletion procedure in user manual
6. Train users on data backup procedures
7. Use database backups as recovery mechanism
