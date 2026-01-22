# [CRITICAL] No Error Boundaries in UI Components

## Type
**Error Handling / User Experience**

## Severity
**CRITICAL** - Application crashes become user-facing errors, poor error recovery

## Affected Components
- **ENTIRE UI** - All views and forms lack proper error boundaries

## Description
The application uses broad exception handling (`except:`) throughout the UI code, which:
1. **Silences errors** - Bugs become invisible until crash
2. **Hides stack traces** - Impossible to debug issues
3. **No user feedback** - Users don't know what went wrong
4. **No error recovery** - Cannot gracefully handle failures

## Problematic Patterns

### Pattern 1: Bare Except (Critical Security Issue)

#### Found in Multiple Files
```python
# src/ui_ctk/forms/employee_form.py:514-517
try:
    # ... code ...
except:
    print(f"[ERROR] {message}")
```

#### Why This is Dangerous
```python
try:
    delete_employee()
except:  # ← Catches EVERYTHING including:
              # - SystemExit
              # - KeyboardInterrupt
              # - MemoryError
              # - GeneratorExit
    print("error")
```

### Pattern 2: Generic Exception Catching

```python
# src/ui_ctk/views/employee_list.py:315-317
try:
    # ... code ...
except Exception as e:
    print(f"[ERROR] Failed to load employee list: {e}")
    # ↑ What exceptions might be raised? Are they all handled the same way?
```

### Pattern 3: No Error Classification

```python
# src/ui_ctk/views/employee_detail.py:471-473
try:
    # ... code ...
except Exception as e:
    self.show_error(f"{ERROR_DELETE_EMPLOYEE}: {e}")
    # ↑ All exceptions treated equally
    # No distinction between:
    #   - Database errors (recoverable?)
    #   - Network errors (retry?)
    #   - Validation errors (user error?)
    #   - System errors (fatal?)
```

## Impact

### For Developers
1. **Cannot debug issues** - Stack traces lost
2. **Cannot identify patterns** - All errors look the same
3. **No error categorization** - Can't prioritize issues

### For Users
1. **Confusing messages** - Generic "An error occurred"
2. **No guidance** - Don't know what to do next
3. **Application crashes** - No graceful degradation
4. **Data loss risk** - Errors during save may lose work

### For Operations
1. **Cannot recover** - No automatic retry mechanisms
2. **Cannot triage** - Can't prioritize issues
3. **Cannot monitor** - No error statistics

## Real-World Examples

### Example 1: Database Connection Lost
```python
try:
    employees = Employee.select()
except:
    print("[ERROR] Failed to load employees")
    # ↑ Error could be:
    #   - Database locked
    #   - Network error (if remote DB)
    #   - Permission denied
    #   - Schema mismatch
    # But user just sees "Failed to load"
```

### Example 2: Import Failure
```python
try:
    result = importer.import_employees()
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    # ↑ What kind of error?
    # - File corruption?
    #   - Invalid data?
    #   - Permission denied?
    #   - Out of memory?
```

### Example 3: File Permission Error
```python
try:
    file_path = open(path, 'w')
except:
    print("[ERROR] File operation failed")
    # ↑ No information about:
    #   - File doesn't exist?
    #   - Permission denied?
    #   - Invalid path?
```

## Proposed Solution

### Option 1: Exception Hierarchy (Recommended)

```python
# src/utils/error_handler.py

from enum import Enum
from typing import Optional, Callable
import logging

# Setup proper logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    filename='wareflow_ems.log'
)

class ErrorCategory(Enum):
    """Categories of errors for different handling."""
    USER_ERROR = "user"           # User input validation errors
    VALIDATION_ERROR = "validation"   # Data validation failures
    DATABASE_ERROR = "database"     # Database connectivity/errors
    FILE_ERROR = "file"            # File system operations
    NETWORK_ERROR = "network"       # Network-related errors
    PERMISSION_ERROR = "permission"   # File/system permissions
    CRITICAL_ERROR = "critical"     # System-level errors
    UNKNOWN_ERROR = "unknown"       # Unclassified errors

class ApplicationError(Exception):
    """Base class for all application errors."""

class ValidationError(ApplicationError):
    """Data validation failed."""
    def __init__(self, message: str, field: str, value=None):
        self.message = message
        self.field = field
        self.value = value

class DatabaseError(ApplicationError):
    """Database operation failed."""
    def __init__(self, message: str, query=None):
        self.message = message
        self.query = query

class FilePermissionError(ApplicationError):
    """File permission or access error."""
    def __init__(self, message: str, path=None):
        self.message = message
        self.path = path

def handle_error(
    error: Exception,
    context: str = "",
    show_to_user: bool = True,
    on_recovery: Optional[Callable] = None
):
    """
    Centralized error handling with proper categorization.

    Args:
        error: The exception that occurred
        context: Where the error occurred (function name, operation)
        show_to_user: Whether to show error to user
        on_recovery: Optional callback to attempt recovery
    """
    # Categorize error
    error_type = categorize_error(error)

    # Log with appropriate level
    if error_type == ErrorCategory.CRITICAL:
        logging.critical(f"{context}: {error}", exc_info=True)
    elif error_type == ErrorCategory.DATABASE_ERROR:
        logging.error(f"{context}: {error}", exc_info=True)
    elif error_type == ErrorCategory.FILE_ERROR:
        logging.warning(f"{context}: {error}")
    elif error_type == ErrorCategory.PERMISSION_ERROR:
        logging.error(f"{context}: {error}")
    elif error_type == ErrorCategory.VALIDATION_ERROR:
        logging.info(f"{context}: {error}")
    elif error_type == ErrorCategory.USER_ERROR:
        logging.info(f"{context}: {error}")
    else:
        logging.error(f"{context}: {error}", exc_info=True)

    # Show to user if needed
    if show_to_user:
        show_error_to_user(error, error_type)

    # Attempt recovery if possible
    if on_recovery:
        try:
            on_recovery(error)
        except Exception as recovery_error:
            logging.error(f"{context}: Recovery failed: {recovery_error}")

def categorize_error(error: Exception) -> ErrorCategory:
    """Categorize error by type."""
    error_type = ErrorCategory.UNKNOWN_ERROR

    if isinstance(error, ValidationError):
        error_type = ErrorCategory.VALIDATION_ERROR
    elif isinstance(error, DatabaseError):
        error_type = ErrorCategory.DATABASE_ERROR
    elif isinstance(error, FilePermissionError):
        error_type = ErrorCategory.PERMISSION_ERROR
    elif isinstance(error, FileNotFoundError):
        error_type = ErrorCategory.FILE_ERROR
    elif isinstance(error, PermissionError):
        error_type = ErrorCategory.PERMISSION_ERROR
    elif isinstance(error, ConnectionError):
        error_type = ErrorCategory.NETWORK_ERROR
    elif isinstance(error, OSError):
        error_type = ErrorCategory.FILE_ERROR
    elif "permission denied" in str(error).lower():
        error_type = ErrorCategory.PERMISSION_ERROR

    return error_type

def show_error_to_user(error: Exception, error_type: ErrorCategory):
    """Show appropriate error message to user."""
    from tkinter import messagebox
    import customtkinter as ctk

    # Determine severity
    if error_type == ErrorCategory.CRITICAL:
        icon = "error"
        title = "Erreur Critique"
    elif error_type == ErrorCategory.DATABASE_ERROR:
        icon = "error"
        title = "Erreur Base de Données"
    elif error_type == ErrorCategory.FILE_ERROR:
        icon = "warning"
        title = "Erreur Fichier"
    elif error_type == ErrorCategory.PERMISSION_ERROR:
        icon = "error"
        title = "Erreur Permission"
    else:
        icon = "info"
        title = "Information"

    # Format user-friendly message
    user_message = format_user_message(error)

    # Show message
    if error_type in [ErrorCategory.CRITICAL, ErrorCategory.DATABASE_ERROR]:
        messagebox.showerror(title, user_message, icon=icon)
    else:
        messagebox.showinfo(title, user_message, icon=icon)
```

### Option 2: Try-Except with Specific Exceptions

#### Before (Current - BAD)
```python
# src/ui_ctk/forms/employee_form.py:494-506
def delete_employee(self):
    try:
        self.employee.delete_instance()
    except Exception as e:
        print(f"[ERROR] Failed to delete employee: {e}")
```

#### After (GOOD)
```python
def delete_employee(self):
    try:
        self.employee.delete_instance()
    except peewee.IntegrityError as e:
        show_error_to_user(
            DatabaseError(
                f"Cannot delete employee: {e}",
                query=self.employee
            ),
            ErrorCategory.DATABASE_ERROR
        )
    except peewee.DatabaseError as e:
        show_error_to_user(
            DatabaseError(f"Database error: {e}"),
            ErrorCategory.DATABASE_ERROR
        )
    except Exception as e:
        # Log full details
        logging.error(f"Unexpected error deleting employee: {e}", exc_info=True)
        show_error_to_user(e, ErrorCategory.UNKNOWN_ERROR)
```

### Option 3: Circuit Breaker Pattern

```python
# Try-retry-circuit-breaker pattern for common operations

import time

def safe_import_employees(filepath, max_retries=3, retry_delay=1.0):
    """Import employees with retry logic."""
    for attempt in range(max_retries):
        try:
            importer = ExcelImporter(filepath)
            result = importer.import_employees()
            return result

        except DatabaseError as e:
            if attempt < max_retries - 1:
                print(f"[WARN] Database busy, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                continue
            else:
                raise  # Re-raise after final attempt

        except FileNotFoundError as e:
            raise  # Don't retry file not found
```

## Implementation Plan

### Phase 1: Create Error Classes (2 hours)
1. Create `src/utils/error_handler.py`
2. Define exception hierarchy
3. Create error categorization
4. Add logging configuration
5. Write tests

### Phase 2: Update Exception Handling (8-12 hours)
1. Replace bare `except:` with specific exception types
2. Add `handle_error()` calls throughout UI
3. Update all forms to use custom exceptions
4. Update all views to use proper error handling
5. Add recovery mechanisms where appropriate

### Phase 3: Add Monitoring (2-3 hours)
1. Set up structured logging
2. Add error statistics collection
3. Add error reporting dashboard (optional)
4. Create error analysis scripts

## Files to Create
- `src/utils/error_handler.py`
- `src/utils/exceptions.py`
- `tests/test_error_handling.py`
- `src/utils/performance_monitor.py`
- `logs/.gitignore` (add)

## Files to Modify (Estimated)
- `src/ui_ctk/forms/*.py` (5 files)
- `src/ui_ctk/views/*.py` (4 files)
- `src/controllers/*.py` (3 files)
- Total: ~12 files

## Error Handling Examples

### Database Connection Errors

```python
# Before
try:
    employees = Employee.select()
except Exception as e:
    print(f"[ERROR] Failed to load: {e}")

# After
from src.utils.exceptions import DatabaseError

try:
    employees = Employee.select()
except DatabaseConnectionError as e:
    handle_error(e, "load_employees", show_to_user=True, on_recovery=lambda _: reconnect_database())
except DatabaseError as e:
    handle_error(e, "load_employees")
```

### File Permission Errors

```python
# Before
try:
    with open(path, 'w') as f:
        f.write(data)
except:
    print(f"[ERROR] Failed to write file")

# After
from src.utils.exceptions import FilePermissionError

try:
    with open(path, 'w') as f:
        f.write(data)
except FilePermissionError as e:
    handle_error(e, "write_file", show_to_user=True)
```

### Validation Errors

```python
# Before
if not employee.first_name:
    return False, "First name is required"

# After
from src.utils.exceptions import ValidationError

if not employee.first_name:
    raise ValidationError(
        "First name is required",
        field="first_name",
        value=None
    )
```

## Related Issues
- #012: Broad exception handling (this issue describes the problem)
- #022: No error recovery mechanisms

## References
- Python Exception Handling Best Practices: https://docs.python.org/3/library/exceptions.html
- OWASP Exception Handling: https://owasp.org/www-community/OWASP_Exception_Handling_Cheat_Sheet.html
- Python Logging Best Practices: https://docs.python.org/3/library/logging.html
- SQLite Error Codes: https://www.sqlite.org/rescode.html

## Priority
**CRITICAL** - Blocks debugging and error recovery

## Estimated Effort
10-14 hours (comprehensive error handling overhaul)

## Mitigation
While waiting for fix:
1. Add `import traceback` to error logging
2. Print full stack traces to console
3. Add more context to error messages
4. Document common error scenarios
5. Train support team on common issues
