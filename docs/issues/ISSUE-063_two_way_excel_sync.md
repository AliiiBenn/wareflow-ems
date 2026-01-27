# ISSUE-063: Two-Way Excel Synchronization

## Description

The current system only supports one-way data flow: database → Excel export. Users need the ability to export data to Excel, edit it in Excel, and import changes back into the database (round-trip synchronization). This enables bulk updates and data management through Excel.

## Current State

- Export: Database → Excel (works, ~60% complete)
- Import: Excel → Database (partial, ~50% complete)
- **Missing:** Round-trip capability with change tracking

## Expected Behavior

### Export with Change Tracking

When exporting to Excel, add metadata to track changes:

**Excel File Structure:**

```
workflow_export_20240127.xlsx
├── Metadata (hidden sheet)
│   ├── export_date: "2024-01-27T10:00:00Z"
│   ├── export_version: "2.0"
│   ├── database_id: "unique-export-id"
│   └── row_identifiers: [list of database IDs]
│
├── Employees
│   ├── _id (hidden column A): Database primary key
│   ├── _hash (hidden column B): Record hash for change detection
│   ├── _version (hidden column C): Version for optimistic locking
│   ├── matricule
│   ├── first_name
│   ├── last_name
│   ├── position
│   ├── department
│   ├── ... (other fields)
│
├── CACES
│   ├── _id (hidden): Database primary key
│   ├── _employee_matricule (link to employee)
│   ├── _hash (hidden): Record hash
│   ├── caces_type
│   ├── certificate_number
│   ├── issue_date
│   ├── expiration_date
│   └── ...
│
└── Medical Visits
    ├── _id (hidden)
    ├── _employee_matricule
    ├── _hash (hidden)
    ├── visit_date
    ├── visit_type
    ├── next_due_date
    └── ...
```

### Import with Change Detection

When importing edited Excel:

1. **Validate export metadata** - Ensure file is a valid export
2. **Compare hashes** - Detect which rows changed
3. **Identify operations:**
   - **Unchanged**: Hash matches, no update
   - **Modified**: Hash differs, update existing record
   - **New**: No database ID, insert new record
   - **Deleted**: ID in export but not in import, mark as deleted

4. **Preview changes** - Show what will be updated/inserted/deleted
5. **Confirm and apply** - Execute changes in transaction
6. **Report results** - Show summary of changes

### Change Detection Algorithm

```python
# src/import_export/change_tracker.py
from typing import Dict, List, Tuple
import hashlib
import json

class ChangeTracker:
    """Track changes between database and Excel import."""

    def __init__(self, export_metadata: dict):
        self.export_date = export_metadata["export_date"]
        self.export_id = export_metadata["database_id"]
        self.row_identifiers = export_metadata["row_identifiers"]

    def detect_changes(
        self,
        imported_data: List[dict],
        model_class
    ) -> Dict[str, List[dict]]:
        """
        Detect changes between imported data and database.

        Returns:
            Dict with keys: 'unchanged', 'modified', 'new', 'deleted'
        """
        changes = {
            "unchanged": [],
            "modified": [],
            "new": [],
            "deleted": []
        }

        # Get current database records
        current_records = {
            record.id: record
            for record in model_class.select()
        }

        imported_ids = set()

        for row in imported_data:
            # Extract metadata
            db_id = row.get("_id")
            row_hash = row.get("_hash")
            employee_matricule = row.get("_employee_matricule")

            # Calculate hash of current data (excluding metadata)
            current_hash = self._calculate_row_hash(row)

            if db_id:
                imported_ids.add(db_id)
                existing_record = current_records.get(db_id)

                if existing_record:
                    existing_hash = self._calculate_record_hash(existing_record)

                    if existing_hash == current_hash:
                        changes["unchanged"].append(row)
                    else:
                        changes["modified"].append({
                            "id": db_id,
                            "old": existing_record,
                            "new": row
                        })

            else:
                # New record (no database ID)
                changes["new"].append(row)

        # Find deleted records (in export but not in import)
        for db_id in current_records:
            if db_id not in imported_ids:
                changes["deleted"].append(current_records[db_id])

        return changes

    def _calculate_row_hash(self, row: dict) -> str:
        """Calculate hash of row data (excluding metadata columns)."""
        # Remove metadata columns
        data = {
            k: v for k, v in row.items()
            if not k.startswith("_")
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def _calculate_record_hash(self, record) -> str:
        """Calculate hash of database record."""
        data = {
            field: getattr(record, field)
            for field in record._meta.fields
            if field != "id" and not field.startswith("_")
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()
```

### Import Preview Dialog

**Create: `src/ui_ctk/dialogs/import_preview_dialog.py`**

```python
class ImportPreviewDialog(ctk.CTkToplevel):
    """Dialog showing changes preview before applying import."""

    def __init__(self, parent, changes: dict):
        super().__init__(parent)
        self.changes = changes
        self.confirmed = False

        self.title("Import Preview")
        self.geometry("1000x700")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets."""
        # Summary
        summary_frame = ctk.CTkFrame(self)
        summary_frame.pack(fill="x", padx=20, pady=20)

        summary_frame.create_label(
            f"New records: {len(self.changes['new'])}"
        ).pack(side="left", padx=10)
        summary_frame.create_label(
            f"Modified: {len(self.changes['modified'])}"
        ).pack(side="left", padx=10)
        summary_frame.create_label(
            f"Deleted: {len(self.changes['deleted'])}"
        ).pack(side="left", padx=10)
        summary_frame.create_label(
            f"Unchanged: {len(self.changes['unchanged'])}"
        ).pack(side="left", padx=10)

        # Tabbed view for each change type
        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=20, pady=10)

        # New records tab
        self.create_changes_tab(
            tabs.tab("New"),
            self.changes["new"],
            change_type="new"
        )

        # Modified records tab
        self.create_changes_tab(
            tabs.tab("Modified"),
            self.changes["modified"],
            change_type="modified"
        )

        # Deleted records tab
        self.create_changes_tab(
            tabs.tab("Deleted"),
            self.changes["deleted"],
            change_type="deleted"
        )

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame,
            text="Apply All Changes",
            command=self.apply_changes,
            fg_color="green"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side="left", padx=5)

    def apply_changes(self):
        """Apply all changes to database."""
        try:
            with database.atomic():
                # Apply new records
                for row in self.changes["new"]:
                    self._insert_record(row)

                # Apply modifications
                for change in self.changes["modified"]:
                    self._update_record(change)

                # Apply deletions
                for record in self.changes["deleted"]:
                    self._delete_record(record)

            self.confirmed = True
            messagebox.showinfo(
                "Import Complete",
                f"Applied {len(self.changes['new'])} new, "
                f"{len(self.changes['modified'])} modified, "
                f"{len(self.changes['deleted'])} deleted"
            )
            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Import Failed",
                f"Error applying changes: {e}"
            )
```

### Optimistic Locking

To prevent concurrent modification conflicts:

```python
# src/import_export/optimistic_lock.py
class OptimisticLockError(Exception):
    """Raised when record was modified by another user."""

class OptimisticLock:
    """Handle optimistic locking for round-trip sync."""

    def verify_version(self, record, expected_version: int):
        """
        Verify record version for optimistic locking.

        Raises:
            OptimisticLockError: If record was modified
        """
        if record.version != expected_version:
            raise OptimisticLockError(
                f"Record {record.id} was modified by another user. "
                f"Expected version {expected_version}, current version {record.version}"
            )

    def update_with_lock(self, record, data: dict, expected_version: int):
        """
        Update record with optimistic locking.

        Args:
            record: Database record to update
            data: New data
            expected_version: Expected version number

        Raises:
            OptimisticLockError: If version mismatch
        """
        self.verify_version(record, expected_version)

        # Update record
        for field, value in data.items():
            setattr(record, field, value)

        # Increment version
        record.version += 1
        record.save()

        return record
```

## Affected Files

- `src/export/data_exporter.py` - Add metadata and hidden columns to export
- `src/import_export/change_tracker.py` - New file for change detection
- `src/import_export/optimistic_lock.py` - New file for optimistic locking
- `src/excel_import/excel_importer.py` - Update to handle round-trip import
- `src/ui_ctk/dialogs/import_preview_dialog.py` - New preview dialog
- `src/employee/models.py` - Add version field to models

## Implementation Plan

### Phase 1: Export Enhancement (2 days)
1. Add metadata sheet to export
2. Add hidden columns (_id, _hash, _version)
3. Generate hashes for each row
4. Add export metadata (date, version, IDs)

### Phase 2: Change Detection (2 days)
1. Implement ChangeTracker class
2. Add hash calculation methods
3. Detect new, modified, unchanged, deleted rows
4. Handle edge cases (null values, relationships)

### Phase 3: Import Preview (2 days)
1. Create ImportPreviewDialog UI
2. Display changes by type
3. Show before/after for modifications
4. Add apply/cancel buttons

### Phase 4: Optimistic Locking (1 day)
1. Add version field to models
2. Implement OptimisticLock class
3. Handle version conflicts
4. Add retry mechanism

### Phase 5: Apply Changes (2 days)
1. Implement insert logic for new records
2. Implement update logic for modified records
3. Implement soft delete for deleted records
4. Add transaction support
5. Add error handling and rollback

### Phase 6: Testing (1 day)
1. Unit tests for change detection
2. Integration tests for round-trip
3. Test concurrent modifications
4. Test edge cases

## Dependencies

- openpyxl (already installed)

## Related Issues

- ISSUE-052: Incomplete Bulk Import Functionality
- ISSUE-053: Incomplete Excel Export Functionality
- ISSUE-060: Hierarchical Document Storage

## Acceptance Criteria

- [ ] Export includes metadata sheet
- [ ] Export includes hidden columns (_id, _hash, _version)
- [ ] Changes detected correctly (new, modified, deleted)
- [ ] Preview dialog shows all changes
- [ ] Can confirm/cancel import
- [ ] Changes applied in transaction
- [ ] Optimistic locking prevents conflicts
- [ ] Rollback on error
- [ ] Import report generated
- [ ] Performance acceptable (1000 records < 30 seconds)
- [ ] All tests pass

## Estimated Effort

**Total:** 9-10 days
- Export enhancement: 2 days
- Change detection: 2 days
- Import preview: 2 days
- Optimistic locking: 1 day
- Apply changes: 2 days
- Testing: 1 day

## Notes

This is a complex feature that requires careful implementation to avoid data loss. The round-trip capability is essential for users who prefer Excel for data management. Optimistic locking prevents data corruption when multiple users edit simultaneously.

## Example Workflow

### Example 1: Round-Trip Edit

1. **Export** database to Excel (includes hidden columns)
2. **Edit** in Excel (change employee position, add new employee)
3. **Import** modified Excel file
4. **Preview** shows:
   - Modified: 1 employee (position changed)
   - New: 1 employee (added in Excel)
5. **Confirm** changes
6. **Database** updated with changes

### Example 2: Conflict Detection

1. User A exports at 10:00
2. User B exports at 10:05
3. User B imports changes (updates employee)
4. User A tries to import changes
5. **Conflict**: Record version mismatch
6. **Solution**: Re-export and try again, or manual merge

## Future Enhancements

- Merge conflict resolution UI
- Partial import (select which changes to apply)
- Import history/audit trail
- Automatic backup before import
- Scheduled imports (watch folder for changes)
- Multi-user merge capabilities
