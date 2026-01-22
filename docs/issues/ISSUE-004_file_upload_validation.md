# [CRITICAL] Missing File Upload Validation

## Type
**Security Vulnerability**

## Severity
**CRITICAL** - Allows malicious file uploads, potential system compromise

## Affected Components
- `src/ui_ctk/forms/caces_form.py` (lines 254-265)
- `src/ui_ctk/forms/medical_form.py` (lines 292-303)

## Description
File upload functionality for CACES certificates and medical visit documents lacks comprehensive validation. Currently, the application:
1. Only checks file extension (not content)
2. Does not validate file size
3. Does not check file type using magic numbers
4. Does not scan for malware
5. Does not validate file names (could contain malicious paths)
6. Does not limit total storage

This creates multiple attack vectors for malicious actors.

## Current Vulnerable Code

### caces_form.py:254-265
```python
def browse_document(self):
    """Open file browser for document selection."""
    from tkinter import filedialog

    file_path = filedialog.askopenfilename(
        title="Select CACES Certificate",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]  # Only extension check!
    )

    if file_path:
        # NO VALIDATION:
        # - No file size check
        # - No magic number verification
        # - No malware scanning
        # - No filename sanitization
        self.document_path_var.set(file_path)
```

## Attack Vectors

### 1. File Type Spoofing
Attacker could:
- Rename `malware.exe` to `certificate.pdf`
- Application accepts it based on extension
- File path stored in database, potentially executed later

### 2. Denial of Service
Attacker could:
- Upload massive file (100GB+)
- Fill disk space
- Crash application or system

### 3. Malware Upload
Attacker could:
- Upload infected PDF with embedded malware
- Execute when file is opened
- Spread through network shares

### 4. Directory Traversal
(See Issue #001 for detailed analysis)

### 5. Filename Attacks
Malicious filenames could:
- Contain special characters that break file systems
- Include null bytes for string termination attacks
- Be excessively long (buffer overflows)

## Current Gaps

### What IS Validated
- ✅ File extension (via filedialog filter)
- ✅ File existence (file must exist to select)

### What is NOT Validated
- ❌ File size limits
- ❌ File type verification (magic numbers)
- ❌ Malware scanning
- ❌ Filename sanitization
- ❌ Content validation (PDF structure)
- ❌ Total storage quotas
- ❌ Virus/malware scanning

## Security Impact

### Risk Assessment
| Attack Vector | Likelihood | Impact | Overall Risk |
|--------------|------------|-------|--------------|
| File type spoofing | HIGH | HIGH | **CRITICAL** |
| DoS (large files) | MEDIUM | MEDIUM | **HIGH** |
| Malware upload | MEDIUM | CRITICAL | **CRITICAL** |
| Filename attacks | LOW | LOW | **MEDIUM** |

## Proposed Solution

### Comprehensive File Validation Module

```python
# src/utils/file_validation.py

import magic
import os
from pathlib import Path
from typing import Tuple, Optional

class FileValidator:
    """Comprehensive file upload validation."""

    # Configuration
    MAX_FILE_SIZE_MB = 10
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png',
    }

    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'}

    @staticmethod
    def validate_file_upload(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file upload with comprehensive checks.

        Args:
            file_path: Path to uploaded file

        Returns:
            (is_valid, error_message)
        """
        path = Path(file_path)

        # Check 1: File exists
        if not path.exists():
            return False, "File does not exist"

        # Check 2: Is a file (not directory)
        if not path.is_file():
            return False, "Path must be a file, not a directory"

        # Check 3: File extension
        if path.suffix.lower() not in FileValidator.ALLOWED_EXTENSIONS:
            return False, f"Invalid file type. Allowed: {', '.join(FileValidator.ALLOWED_EXTENSIONS)}"

        # Check 4: File size
        size_bytes = path.stat().st_size
        if size_bytes > FileValidator.MAX_FILE_SIZE_BYTES:
            size_mb = size_bytes / (1024 * 1024)
            return False, f"File too large ({size_mb:.1f}MB). Maximum: {FileValidator.MAX_FILE_SIZE_MB}MB"

        # Check 5: File size > 0
        if size_bytes == 0:
            return False, "File is empty (0 bytes)"

        # Check 6: Magic number validation
        try:
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(str(path))

            if file_type not in FileValidator.ALLOWED_MIME_TYPES:
                return False, f"Invalid file content: {file_type}. Allowed: {', '.join(FileValidator.ALLOWED_MIME_TYPES)}"
        except Exception as e:
            return False, f"Cannot validate file type: {str(e)}"

        # Check 7: Filename sanitization
        try:
            # Remove null bytes
            safe_filename = path.name.replace('\x00', '')

            # Check for suspicious characters
            suspicious_chars = ['<', '>', ':', '|', '"', '*', '?', '\x00']
            if any(char in safe_filename for char in suspicious_chars):
                return False, "Filename contains invalid characters"

            # Check for excessively long names
            if len(safe_filename) > 255:
                return False, "Filename too long (max 255 characters)"

        except Exception as e:
            return False, f"Filename validation error: {str(e)}"

        # Check 8: PDF structure validation (for PDFs)
        if path.suffix.lower() == '.pdf':
            if not FileValidator._validate_pdf_structure(path):
                return False, "Invalid PDF file structure"

        return True, None

    @staticmethod
    def _validate_pdf_structure(file_path: Path) -> bool:
        """Validate PDF file structure."""
        try:
            import pypdf

            with open(file_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                # Check if PDF has pages
                if len(reader.pages) == 0:
                    return False
                # Check if PDF is encrypted
                if reader.is_encrypted:
                    return False
            return True
        except Exception:
            return False
```

### Additional Security Measures

#### 1. File Content Scanning (Optional but Recommended)
```python
import clamdb

def scan_for_malware(file_path: str) -> tuple[bool, str]:
    """Scan file for malware using ClamAV."""
    try:
        cd = clamdb.ClamdUnixSocket('/var/run/clamav/clamd.sock')
        cd.scan_file(file_path)
        return True, "File is clean"
    except Exception as e:
        return False, f"Malware scanning failed: {str(e)}"
```

#### 2. File Storage in Isolated Directory
```python
from pathlib import Path
import shutil
import uuid

SECURE_STORAGE = Path("documents/")

def save_to_secure_storage(source_path: str) -> str:
    """
    Copy file to secure storage with randomized name.

    Prevents directory traversal and stores files in controlled location.
    """
    source = Path(source_path)
    SECURE_STORAGE.mkdir(parents=True, exist_ok=True)

    # Generate unique filename preserving extension
    unique_name = f"{uuid.uuid4().hex}{source.suffix}"
    dest_path = SECURE_STORAGE / unique_name

    # Copy file
    shutil.copy2(source_path, dest_path)

    return str(dest_path)
```

#### 3. Storage Quotas
```python
from pathlib import Path

def check_storage_quota(file_size: int, max_total_mb: int = 1000) -> tuple[bool, str]:
    """Check if adding file would exceed storage quota."""
    documents_dir = Path("documents/")

    if not documents_dir.exists():
        return True, None

    # Calculate current usage
    current_usage = sum(
        f.stat().st_size for f in documents_dir.rglob('*') if f.is_file()
    )

    # Convert to MB
    current_mb = current_usage / (1024 * 1024)

    if current_mb + (file_size / (1024 * 1024)) > max_total_mb:
        return False, f"Storage quota exceeded. Maximum: {max_total_mb}MB, Current: {current_mb:.1f}MB"

    return True, None
```

## Implementation Plan

### Phase 1: Add Validation (2-3 hours)
1. Create `src/utils/file_validation.py`
2. Update `caces_form.py` to validate before accepting
3. Update `medical_form.py` to validate before accepting
4. Add error messages in UI
5. Write tests

### Phase 2: Secure Storage (2 hours)
1. Implement `save_to_secure_storage()`
2. Copy files instead of storing paths
3. Delete original file after copy
4. Add document cleanup utility

### Phase 3: Enhanced Security (Optional, 4-6 hours)
1. Add ClamAV integration
2. Add storage quotas
3. Add document expiration
4. Add virus scanning scheduling

## Files to Create
- `src/utils/file_validation.py`
- `tests/test_file_validation.py`
- `src/utils/secure_storage.py`

## Files to Modify
- `src/ui_ctk/forms/caces_form.py`
- `src/ui_ctk/forms/medical_form.py`
- `src/employee/models.py` - Update document_path to point to secure storage

## Testing Requirements
- Upload valid files (PDF, images)
- Upload invalid extensions (exe, bat, sh)
- Upload oversized files (>10MB)
- Upload files with magic number mismatch
- Upload files with malicious filenames
- Upload empty files
- Upload corrupted PDFs
- Upload encrypted PDFs
- Test storage quota enforcement
- Test concurrent uploads

## Security Checklist
- [x] File extension validation
- [ ] File size validation
- [ ] Magic number verification
- [ ] Filename sanitization
- [ ] PDF structure validation
- [ ] Malware scanning
- [ ] Storage quota enforcement
- [ ] Secure file storage
- [ ] Path traversal prevention
- [ ] Virus scanning

## Related Issues
- #001: Path traversal vulnerability (related security issue)

## References
- OWASP File Upload: https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload
- OWASP File Upload Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- CWE-434: Unrestricted Upload of File with Dangerous Type
- Python magic module: https://github.com/ahupp/python-magic

## Priority
**CRITICAL** - Security vulnerability that could compromise system

## Estimated Effort
3-4 hours (including secure storage and tests)

## Mitigation
While waiting for fix:
- Disable file upload functionality
- Store documents outside application
- Manual vetting of all files before processing
- Add warning in documentation
