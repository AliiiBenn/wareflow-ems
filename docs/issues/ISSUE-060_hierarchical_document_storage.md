# ISSUE-060: Hierarchical Document Storage Structure

## Description

The current document storage system for imported files (CACES certificates, medical visit records, training documents) lacks proper organization. All documents are stored flat without a structured hierarchy, making it difficult to track and manage documentation over time.

## Current State

Documents are currently stored in a flat structure:
- No separation by document type
- No employee-based organization
- Difficult to track document history
- No clear audit trail for document changes
- Hard to find specific documents

## Expected Behavior

### Hierarchical Folder Structure

```
documents/
├── caces/
│   ├── employee_MATR001/
│   │   ├── 2024-01-15_caces_1a_certificat.pdf
│   │   ├── 2024-01-15_caces_1a_certificat_metadata.json
│   │   └── 2023-06-20_caces_3_certificat.pdf
│   ├── employee_MATR002/
│   │   └── ...
│   └── ...
├── medical/
│   ├── employee_MATR001/
│   │   ├── 2024-01-20_visite_initiale.pdf
│   │   ├── 2024-01-20_visite_initiale_metadata.json
│   │   ├── 2023-07-15_visite_periodique.pdf
│   │   └── ...
│   └── ...
├── training/
│   ├── employee_MATR001/
│   │   ├── 2024-02-01_habilitation_elecrrique.pdf
│   │   └── ...
│   └── ...
└── contracts/
    ├── employee_MATR001/
    │   ├── 2024-01-01_contrat_cdi.pdf
    │   ├── 2024-01-01_contrat_cdi_metadata.json
    │   └── ...
    └── ...
```

### Metadata Files

Each document should have a corresponding JSON metadata file:

```json
{
  "document_id": "uuid-v4",
  "employee_matricule": "MATR001",
  "document_type": "caces",
  "file_name": "caces_1a_certificat.pdf",
  "upload_date": "2024-01-15T10:30:00Z",
  "issue_date": "2024-01-15",
  "expiration_date": "2029-01-15",
  "certificate_number": "CACES-1A-2024-001",
  "version": 1,
  "hash": "sha256:abc123...",
  "file_size_bytes": 1048576,
  "mime_type": "application/pdf",
  "uploader": "admin",
  "notes": "Renouvellement du certificat"
}
```

### Document Versioning

When a document is updated:
1. Keep old document with version number
2. Add new document with incremented version
3. Update metadata to link versions

Example:
```
employee_MATR001/
├── v1_2023-06-20_caces_1a_certificat.pdf
├── v1_2023-06-20_caces_1a_certificat_metadata.json
├── v2_2024-01-15_caces_1a_certificat.pdf
└── v2_2024-01-15_caces_1a_certificat_metadata.json
```

## Affected Files

- `src/utils/file_storage.py` - New file for storage management
- `src/ui_ctk/forms/caces_form.py` - Update to use new structure
- `src/ui_ctk/forms/medical_form.py` - Update to use new structure
- `src/ui_ctk/forms/training_form.py` - Update to use new structure
- `src/employee/models.py` - Add document tracking fields
- Database migration for document tracking

## Implementation Plan

### Phase 1: Storage Manager (2 days)

**Create: `src/utils/file_storage.py`**

```python
from pathlib import Path
from datetime import datetime
import json
import hashlib
import shutil
from typing import Optional

class DocumentStorageManager:
    """Manages hierarchical document storage."""

    def __init__(self, base_dir: Path = Path("documents")):
        self.base_dir = base_dir
        self.base_dir.mkdir(exist_ok=True)

    def get_employee_folder(self, doc_type: str, matricule: str) -> Path:
        """
        Get the folder path for an employee's documents.

        Args:
            doc_type: Document type (caces, medical, training, contracts)
            matricule: Employee matricule

        Returns:
            Path to employee's document folder
        """
        folder = self.base_dir / doc_type / f"employee_{matricule}"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def store_document(
        self,
        doc_type: str,
        matricule: str,
        file_path: Path,
        metadata: dict
    ) -> Path:
        """
        Store a document in the hierarchical structure.

        Args:
            doc_type: Document type
            matricule: Employee matricule
            file_path: Path to source file
            metadata: Document metadata

        Returns:
            Path to stored document
        """
        # Get employee folder
        folder = self.get_employee_folder(doc_type, matricule)

        # Generate filename with date
        upload_date = datetime.now()
        date_str = upload_date.strftime("%Y-%m-%d")
        version = metadata.get("version", 1)
        new_filename = f"v{version}_{date_str}_{metadata['file_name']}"
        dest_path = folder / new_filename

        # Copy file
        shutil.copy2(file_path, dest_path)

        # Calculate hash
        with open(dest_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Add metadata
        metadata.update({
            "document_id": str(uuid.uuid4()),
            "upload_date": upload_date.isoformat(),
            "hash": f"sha256:{file_hash}",
            "file_size_bytes": dest_path.stat().st_size
        })

        # Save metadata
        metadata_path = folder / f"v{version}_{date_str}_{metadata['file_name']}.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        return dest_path

    def get_document_history(
        self,
        doc_type: str,
        matricule: str,
        document_name: str
    ) -> list[dict]:
        """
        Get all versions of a document.

        Args:
            doc_type: Document type
            matricule: Employee matricule
            document_name: Base document name

        Returns:
            List of metadata dicts for each version
        """
        folder = self.get_employee_folder(doc_type, matricule)
        versions = []

        for metadata_file in folder.glob(f"*_{document_name}.json"):
            with open(metadata_file) as f:
                metadata = json.load(f)
                versions.append(metadata)

        # Sort by version number
        versions.sort(key=lambda x: x["version"])
        return versions

    def delete_document(
        self,
        doc_type: str,
        matricule: str,
        file_name: str,
        version: Optional[int] = None
    ) -> bool:
        """
        Delete a document (and its metadata).

        Args:
            doc_type: Document type
            matricule: Employee matricule
            file_name: Document file name
            version: Specific version to delete (None = all versions)

        Returns:
            True if deleted successfully
        """
        folder = self.get_employee_folder(doc_type, matricule)

        if version:
            # Delete specific version
            pattern = f"v{version}_*_{file_name}"
            for file in folder.glob(pattern):
                file.unlink()
        else:
            # Delete all versions
            pattern = f"*_*_{file_name}"
            for file in folder.glob(pattern):
                file.unlink()

        return True
```

### Phase 2: Database Tracking (1 day)

**Add document tracking table:**

```python
# src/employee/models.py
class Document(BaseModel):
    """Track stored documents."""

    document_id = CharField(max_length=36, primary_key=True)
    employee = ForeignKeyField(Employee, backref="documents")
    document_type = CharField(max_length=50)  # caces, medical, training, contract
    file_name = CharField(max_length=255)
    file_path = CharField(max_length=500)
    upload_date = DateTimeField(default=datetime.now)
    issue_date = DateField(null=True)
    expiration_date = DateField(null=True)
    version = IntegerField(default=1)
    hash = CharField(max_length=128)
    file_size_bytes = IntegerField()
    mime_type = CharField(max_length=100)
    uploader = CharField(max_length=100)
    notes = TextField(null=True)
    active = BooleanField(default=True)  # False if replaced by newer version

    class Meta:
        indexes = (
            (("employee", "document_type", "active"), False),
        )
```

### Phase 3: UI Integration (2 days)

**Update forms to use new storage:**

```python
# src/ui_ctk/forms/caces_form.py
from utils.file_storage import DocumentStorageManager

class CACESForm(ctk.CTkFrame):
    def __init__(self, parent, employee, **kwargs):
        super().__init__(parent, **kwargs)
        self.employee = employee
        self.storage = DocumentStorageManager()
        # ... rest of init

    def _save_document(self):
        """Save uploaded document with new structure."""
        if self.document_path:
            metadata = {
                "file_name": Path(self.document_path).name,
                "document_type": "caces",
                "caces_type": self.caces_type.get(),
                "certificate_number": self.certificate_number.get(),
                "issue_date": self.issue_date.get(),
                "expiration_date": self.expiration_date.get(),
                "version": self._get_next_version(),
                "uploader": get_current_user(),
                "notes": self.notes.get("1.0", "")
            }

            stored_path = self.storage.store_document(
                doc_type="caces",
                matricule=self.employee.matricule,
                file_path=Path(self.document_path),
                metadata=metadata
            )

            # Save to database
            Document.create(
                document_id=metadata["document_id"],
                employee=self.employee,
                document_type="caces",
                file_name=metadata["file_name"],
                file_path=str(stored_path),
                **metadata
            )
```

### Phase 4: Document History Viewer (2 days)

**Add dialog to view document history:**

```python
# src/ui_ctk/dialogs/document_history_dialog.py
class DocumentHistoryDialog(ctk.CTkToplevel):
    """Dialog showing document version history."""

    def __init__(self, parent, doc_type, employee, document_name):
        super().__init__(parent)
        self.storage = DocumentStorageManager()
        self.doc_type = doc_type
        self.employee = employee
        self.document_name = document_name

        self.title(f"Document History: {document_name}")
        self.geometry("800x600")

        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        """Create dialog widgets."""
        # Table showing all versions
        # Columns: Version, Date, File Name, Uploader, Actions
        # Actions: View, Download, Restore (make active)
        pass

    def load_history(self):
        """Load document history from storage."""
        history = self.storage.get_document_history(
            self.doc_type,
            self.employee.matricule,
            self.document_name
        )
        # Display in table
```

## Migration Strategy

### Migrate Existing Documents

1. **Scan existing flat storage**
2. **Identify document ownership** (from database)
3. **Move to new structure**
4. **Generate metadata files**
5. **Update database records**

```python
def migrate_documents():
    """Migrate existing documents to new structure."""
    storage = DocumentStorageManager()

    for caces in CACES.select():
        if caces.document_path and Path(caces.document_path).exists():
            old_path = Path(caces.document_path)
            metadata = {
                "file_name": old_path.name,
                "document_type": "caces",
                "caces_type": caces.caces_type,
                "certificate_number": caces.certificate_number,
                "issue_date": caces.issue_date,
                "expiration_date": caces.expiration_date,
                "version": 1,
                "uploader": "migration"
            }

            new_path = storage.store_document(
                doc_type="caces",
                matricule=caces.employee.matricule,
                file_path=old_path,
                metadata=metadata
            )

            # Update database
            caces.document_path = str(new_path)
            caces.save()
```

## Benefits

1. **Better Organization**: Clear structure by type and employee
2. **Easy Tracking**: See all documents for an employee
3. **Version History**: Track document changes over time
4. **Audit Trail**: Know who uploaded what and when
5. **Easy Backup**: Can backup per employee or per type
6. **Scalability**: Handles thousands of documents efficiently

## Dependencies

- None (new functionality)

## Related Issues

- ISSUE-062: Equipment Operation Conditions (needs valid documents)
- ISSUE-061: Configurable Warning Levels (uses document dates)
- ISSUE-064: Contract History Tracking

## Acceptance Criteria

- [ ] DocumentStorageManager implemented and tested
- [ ] Database table for document tracking created
- [ ] All forms use new storage structure
- [ ] Document versioning works correctly
- [ ] Can view document history in UI
- [ ] Old documents migrated to new structure
- [ ] Metadata files generated for all documents
- [ ] File system structure matches specification
- [ ] Performance acceptable with 1000+ documents
- [ ] All tests pass

## Estimated Effort

**Total:** 7-9 days
- Storage manager: 2 days
- Database tracking: 1 day
- UI integration: 2 days
- Document history viewer: 2 days
- Migration script and testing: 1-2 days

## Notes

This is a critical improvement for document management. The hierarchical structure makes it easy to track document history and maintain proper audit trails. The migration should be done carefully to avoid data loss.

## Future Enhancements

- Document compression for old versions
- Document archiving (move old versions to archive storage)
- Document deduplication (detect duplicate files)
- Document preview generation (thumbnail images)
- Full-text search across documents
