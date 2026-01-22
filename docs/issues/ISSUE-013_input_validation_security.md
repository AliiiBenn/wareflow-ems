# [CRITICAL] Insufficient Input Validation and Sanitization

## Type
**Security / Data Integrity**

## Severity
**CRITICAL** - Attack surface for injection attacks, data corruption, and system crashes

## Affected Components
- **ALL INPUT POINTS** - Forms, imports, file operations, database queries

## Description
The application lacks comprehensive input validation and sanitization throughout. While using Peewee ORM provides SOME protection against SQL injection, there are multiple other attack vectors and data integrity issues:

### Security Risks
1. **No input length limits** - Buffer overflow attacks, DoS
2. **No character validation** - Unicode attacks, control characters
3. **No type checking** - Type confusion attacks
4. **No range validation** - Integer overflow, negative values
5. **No format validation** - Malformed data, parsing attacks
6. **No XSS protection** - Script injection in displayed fields
7. **No path traversal protection** - File system access (partially addressed in ISSUE-001)

### Data Integrity Risks
1. **Invalid emails** - Cannot contact employees
2. **Invalid dates** - Calculation errors, crashes
3. **Empty required fields** - Null data in database
4. **Duplicate data** - Business logic violations
5. **Orphaned records** - Referential integrity issues

## Problematic Code

### Example 1: No Length Validation

```python
# src/ui_ctk/forms/employee_form.py
class EmployeeForm(BaseFormDialog):
    def create_form(self):
        # Input fields with NO length limits
        self.first_name = ctk.StringVar()
        self.last_name = ctk.StringVar()
        self.email = ctk.StringVar()
        self.comment = ctk.StringVar()  # ← Can be megabytes of text!

        # User could enter:
        # - 10 MB string → Memory exhaustion
        # - Unicode control characters → Display corruption
        # - NULL bytes → String truncation
        # - Bidirectional text → Spoofing attacks
```

**Attack Scenario**:
```python
# Attacker enters 10 MB of 'A' characters
first_name = "A" * 10_000_000

# Results in:
# 1. UI freezes during rendering
# 2. Database storage bloat
# 3. Export operations timeout
# 4. Memory exhaustion crashes
```

### Example 2: No Character Validation

```python
# src/controllers/employee_controller.py:70-90
def create_employee(**kwargs) -> Employee:
    # Directly pass user input to database
    employee = Employee.create(**kwargs)

    # What if:
    # - email contains: "test\x00@example.com" (NULL byte)
    # - first_name contains: "Jean<script>alert('xss')</script>"
    # - last_name contains: "\u202E" (Right-to-Left override)
    # - external_id contains: "../../etc/passwd" (path traversal)

    # No validation occurs!
```

**Attack Scenarios**:
```python
# NULL byte injection
email = "test\x00@example.com"
# → String operations truncate at NULL byte
# → "Valid" email passes validation but corrupted

# XSS (Cross-Site Scripting) - if web interface added later
first_name = "<img src=x onerror=alert('XSS')>"
# → Renders as HTML in UI
# → Executes JavaScript in user context

# Unicode homograph attack
first_name = "аdmin"  # Cyrillic 'а', not Latin 'a'
# → Looks like "admin" but different character
# → Bypasses "admin" name filters
# → Spoofing attack

# Bidirectional text attack
last_name = "\u202EbtXO"  # RTL override
# → Displays as "OXTb" (reversed)
# → "Admin" becomes "nimAd" visually
```

### Example 3: No Type Validation

```python
# src/controllers/employee_controller.py:70-90
def create_employee(**kwargs) -> Employee:
    # Peewee validates types BUT:
    # 1. Validation happens AFTER business logic
    # 2. Error messages are cryptic
    # 3. No input sanitization

    # What if user passes:
    employee = Employee.create(
        first_name=["list", "instead", "of", "string"],  # Wrong type
        entry_date="invalid-date",                        # Invalid format
        external_id=None,                                 # Required field
    )

    # → Cryptic Peewee error
    # → No user-friendly validation
    # → Application may crash
```

### Example 4: No Range Validation

```python
# src/controllers/employee_controller.py
# No validation on dates:
entry_date = "1800-01-01"  # Employee from 1800?
entry_date = "2100-01-01"  # Employee from future?

# No validation on numeric fields:
phone = "0"  # Invalid phone number
email = "a@b"  # Too short

# No validation on enums:
current_status = "invalid_status"  # Not in allowed values
workspace = "../../"  # Path traversal?
```

### Example 5: Excel Import - No Validation

```python
# src/excel_import/excel_importer.py:73-117
def import_employees(self) -> dict:
    for row_num, row in enumerate(self.sheet.iter_rows(min_row=2), start=2):
        # Extract data from Excel
        external_id = row[0].value  # ← No validation!
        first_name = row[1].value   # ← Could be anything!
        last_name = row[2].value
        # ...

        # What if Excel contains:
        # - Formulas instead of values
        # - HTML entities
        # - Script code
        # - Control characters
        # - Extremely long strings
        # - Invalid data types

        employee = Employee.create(
            external_id=external_id,
            first_name=first_name,
            last_name=last_name,
            # ...
        )
```

**Import Attack Scenario**:
```python
# Malicious Excel file:
Row 1: external_id = "' OR 1=1 --"  # SQL injection attempt (blocked by Peewee)
Row 2: first_name = "<script>alert(1)</script>"  # XSS
Row 3: last_name = "A" * 1000000  # 1 MB string
Row 4: email = "\t\n\r" * 10000  # Control characters

# Results:
# - Database filled with garbage
# - UI rendering crashes
# - Performance degradation
# - Data corruption
```

### Example 6: File Path Validation (Partial Fix)

```python
# src/ui_ctk/forms/caces_form.py:254-265
# ISSUE-001 addresses path traversal, but what about:
# - Symlink attacks?
# - Device files? (/dev/tty, CON:)
# - Named pipes?
# - Reserved filenames? (CON, PRN, AUX in Windows)
```

## Current Validation (Insufficient)

```python
# src/ui_ctk/forms/employee_form.py:177-241
def validate(self) -> tuple[bool, Optional[str]]:
    """Current validation (insufficient)."""
    first_name = self.first_name.get().strip()
    last_name = self.last_name.get().strip()

    # Only checks emptiness!
    if not first_name:
        return False, ERROR_FIRST_NAME_REQUIRED
    if not last_name:
        return False, ERROR_LAST_NAME_REQUIRED

    # NO:
    # - Length checks
    # - Character validation
    # - Format validation
    # - Type validation
    # - Range validation
    # - XSS prevention
    # - Unicode normalization

    return True, None
```

## OWASP Top 3 Coverage

### OWASP #1: Injection (Partial Protection)
- ✅ **SQL Injection**: Protected by Peewee ORM
- ❌ **Command Injection**: No protection (if system commands added)
- ❌ **LDAP Injection**: No protection (if LDAP added)
- ❌ **XPath Injection**: No protection (if XML parsing added)

### OWASP #2: Broken Authentication (No Validation)
- ❌ Username format validation
- ❌ Password strength validation
- ❌ Email format validation

### OWASP #3: XSS (No Protection)
```python
# If web interface added OR CustomTkinter renders HTML:
first_name = "<script>alert('XSS')</script>"

# Current code:
label = ctk.CTkLabel(master, text=employee.first_name)
# → CustomTkinter doesn't render HTML (safe for now)
# → BUT no defense-in-depth
```

## Proposed Solution

### Part 1: Input Validation Framework

```python
# src/utils/validation.py
import re
import unicodedata
from typing import Any, Optional, Tuple, List
from datetime import datetime
from pathlib import Path

class ValidationError(Exception):
    """Raised when input validation fails."""
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"{field}: {message}")

class InputValidator:
    """Comprehensive input validation framework."""

    # Character sets
    ALLOWED_NAME_CHARS = re.compile(r"^[\p{L}\p{M}'\- ]+$", re.UNICODE)
    ALLOWED_EMAIL_CHARS = re.compile(r"^[a-zA-Z0-9._%+\-@]+$")
    ALLOWED_PHONE_CHARS = re.compile(r"^[0-9+()\-\s.]+$")

    # Length limits
    MAX_LENGTH_FIRST_NAME = 50
    MAX_LENGTH_LAST_NAME = 50
    MAX_LENGTH_EMAIL = 255
    MAX_LENGTH_PHONE = 20
    MAX_LENGTH_COMMENT = 2000
    MAX_LENGTH_EXTERNAL_ID = 50
    MAX_LENGTH_WORKSPACE = 50
    MAX_LENGTH_ROLE = 100
    MAX_LENGTH_CONTRACT_TYPE = 50

    # Allowed values
    ALLOWED_STATUSES = ['active', 'inactive', 'on_leave', 'terminated']
    ALLOWED_CONTRACT_TYPES = ['CDI', 'CDD', 'Intérim', 'Alternance', 'Stage']

    @staticmethod
    def sanitize_string(value: str, max_length: int) -> str:
        """
        Sanitize string input.

        - Remove NULL bytes
        - Remove control characters (except newline, tab)
        - Normalize Unicode (NFC - canonical composition)
        - Trim whitespace
        - Enforce max length

        Args:
            value: Input string
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            raise ValidationError("string", "Must be string type", value)

        # Remove NULL bytes
        value = value.replace('\x00', '')

        # Normalize Unicode to NFC form
        value = unicodedata.normalize('NFC', value)

        # Remove control characters (except \t, \n, \r)
        value = ''.join(
            char for char in value
            if char == '\t' or char == '\n' or char == '\r'
            or not unicodedata.category(char).startswith('C')
        )

        # Trim whitespace
        value = value.strip()

        # Enforce max length
        if len(value) > max_length:
            value = value[:max_length]

        return value

    @staticmethod
    def validate_name(value: str, field_name: str = "name", max_length: int = 50) -> str:
        """
        Validate person name.

        Args:
            value: Name to validate
            field_name: Field name for error messages
            max_length: Maximum allowed length

        Returns:
            Sanitized name

        Raises:
            ValidationError: If validation fails
        """
        # Type check
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be string type", value)

        # Sanitize
        value = InputValidator.sanitize_string(value, max_length)

        # Length check
        if len(value) == 0:
            raise ValidationError(field_name, "Cannot be empty")
        if len(value) > max_length:
            raise ValidationError(field_name, f"Cannot exceed {max_length} characters")

        # Character validation (allow Unicode letters, marks, hyphen, apostrophe, space)
        # Use Unicode categories:
        # - L (Letter), M (Mark)
        if not all(
            unicodedata.category(char).startswith(('L', 'M', 'Zs'))  # Letter, Mark, space
            or char in "'\-"
            for char in value
        ):
            raise ValidationError(field_name, "Contains invalid characters", value)

        # Check for suspicious patterns
        if re.search(r'<script|javascript:|onerror=|onload=', value, re.IGNORECASE):
            raise ValidationError(field_name, "Contains suspicious content", value)

        return value

    @staticmethod
    def validate_email(value: str) -> str:
        """
        Validate email address.

        Args:
            value: Email to validate

        Returns:
            Sanitized email

        Raises:
            ValidationError: If validation fails
        """
        # Type check
        if not isinstance(value, str):
            raise ValidationError("email", "Must be string type", value)

        # Allow empty email (optional field)
        value = value.strip()
        if value == "":
            return ""

        # Sanitize
        value = InputValidator.sanitize_string(value, InputValidator.MAX_LENGTH_EMAIL)

        # Length check
        if len(value) > InputValidator.MAX_LENGTH_EMAIL:
            raise ValidationError("email", f"Cannot exceed {InputValidator.MAX_LENGTH_EMAIL} characters")

        # Format validation (RFC 5322 basic)
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(value):
            raise ValidationError("email", "Invalid format", value)

        # Check for suspicious patterns
        if '..' in value or value.startswith('.') or value.endswith('.'):
            raise ValidationError("email", "Invalid format", value)

        return value.lower()  # Normalize to lowercase

    @staticmethod
    def validate_phone(value: str) -> str:
        """
        Validate phone number.

        Args:
            value: Phone number to validate

        Returns:
            Sanitized phone number

        Raises:
            ValidationError: If validation fails
        """
        # Type check
        if not isinstance(value, str):
            raise ValidationError("phone", "Must be string type", value)

        # Allow empty phone (optional field)
        value = value.strip()
        if value == "":
            return ""

        # Sanitize
        value = InputValidator.sanitize_string(value, InputValidator.MAX_LENGTH_PHONE)

        # Remove common formatting
        digits_only = re.sub(r'[^\d+]', '', value)

        # Length check (reasonable phone number length)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValidationError("phone", "Invalid length (must be 10-15 digits)", value)

        return value

    @staticmethod
    def validate_date(value: Any, field_name: str = "date") -> datetime:
        """
        Validate date input.

        Args:
            value: Date to validate (string or datetime)
            field_name: Field name for error messages

        Returns:
            Datetime object

        Raises:
            ValidationError: If validation fails
        """
        # If already datetime, validate range
        if isinstance(value, datetime):
            if value.year < 1900 or value.year > 2100:
                raise ValidationError(field_name, "Year out of range (1900-2100)", value)
            return value

        # If string, parse
        if isinstance(value, str):
            value = value.strip()

            try:
                # Try common formats
                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'):
                    try:
                        parsed_date = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValidationError(field_name, f"Invalid date format (use YYYY-MM-DD)", value)

                # Validate range
                if parsed_date.year < 1900 or parsed_date.year > 2100:
                    raise ValidationError(field_name, "Year out of range (1900-2100)", value)

                # Cannot be in future (for entry_date)
                if parsed_date > datetime.now():
                    raise ValidationError(field_name, "Date cannot be in future", value)

                return parsed_date

            except Exception as e:
                raise ValidationError(field_name, f"Invalid date: {e}", value) from e

        raise ValidationError(field_name, "Must be date or string", value)

    @staticmethod
    def validate_status(value: str) -> str:
        """Validate employee status."""
        if value not in InputValidator.ALLOWED_STATUSES:
            raise ValidationError("current_status", f"Must be one of: {InputValidator.ALLOWED_STATUSES}", value)
        return value

    @staticmethod
    def validate_enum(value: str, field_name: str, allowed_values: List[str]) -> str:
        """
        Validate enum/choice field.

        Args:
            value: Value to validate
            field_name: Field name for errors
            allowed_values: List of allowed values

        Returns:
            Validated value
        """
        if value not in allowed_values:
            raise ValidationError(field_name, f"Must be one of: {allowed_values}", value)
        return value

    @staticmethod
    def validate_comment(value: str) -> str:
        """Validate comment field."""
        if not isinstance(value, str):
            raise ValidationError("comment", "Must be string type", value)

        value = InputValidator.sanitize_string(value, InputValidator.MAX_LENGTH_COMMENT)

        # Allow most characters in comments (free text)
        # But remove control characters
        return value

    @staticmethod
    def validate_external_id(value: str) -> str:
        """Validate external ID."""
        if not isinstance(value, str):
            raise ValidationError("external_id", "Must be string type", value)

        value = InputValidator.sanitize_string(value, InputValidator.MAX_LENGTH_EXTERNAL_ID)

        if len(value) == 0:
            raise ValidationError("external_id", "Cannot be empty")

        # Alphanumeric, underscore, hyphen only
        if not re.match(r'^[a-zA-Z0-9_\-]+$', value):
            raise ValidationError("external_id", "Invalid format (alphanumeric, _, - only)", value)

        return value

    @classmethod
    def validate_employee_data(cls, data: dict) -> dict:
        """
        Validate all employee data.

        Args:
            data: Dictionary of employee data

        Returns:
            Sanitized and validated data

        Raises:
            ValidationError: If any validation fails
        """
        validated = {}

        try:
            # Required fields
            validated['external_id'] = cls.validate_external_id(data.get('external_id', ''))
            validated['first_name'] = cls.validate_name(data.get('first_name', ''), 'first_name', cls.MAX_LENGTH_FIRST_NAME)
            validated['last_name'] = cls.validate_name(data.get('last_name', ''), 'last_name', cls.MAX_LENGTH_LAST_NAME)

            # Optional fields
            email = data.get('email', '')
            if email:
                validated['email'] = cls.validate_email(email)

            phone = data.get('phone', '')
            if phone:
                validated['phone'] = cls.validate_phone(phone)

            entry_date = data.get('entry_date')
            if entry_date:
                validated['entry_date'] = cls.validate_date(entry_date, 'entry_date')

            # Enums
            current_status = data.get('current_status', 'active')
            validated['current_status'] = cls.validate_status(current_status)

            # Optional text fields
            workspace = data.get('workspace', '')
            if workspace:
                validated['workspace'] = cls.sanitize_string(workspace, cls.MAX_LENGTH_WORKSPACE)

            role = data.get('role', '')
            if role:
                validated['role'] = cls.sanitize_string(role, cls.MAX_LENGTH_ROLE)

            contract_type = data.get('contract_type', '')
            if contract_type:
                validated['contract_type'] = cls.validate_enum(
                    contract_type, 'contract_type', cls.ALLOWED_CONTRACT_TYPES
                )

            comment = data.get('comment', '')
            if comment:
                validated['comment'] = cls.validate_comment(comment)

            return validated

        except ValidationError as e:
            # Re-raise with context
            raise e
```

### Part 2: Update Controllers

```python
# src/controllers/employee_controller.py
from src.utils.validation import InputValidator, ValidationError

def create_employee(**kwargs) -> Employee:
    """Create employee with comprehensive validation."""
    try:
        # Validate and sanitize ALL input
        validated_data = InputValidator.validate_employee_data(kwargs)

        # Check for duplicate external_id
        if Employee.select().where(Employee.external_id == validated_data['external_id']).exists():
            raise ValueError(f"Employee with external_id '{validated_data['external_id']}' already exists")

        # Create employee with validated data
        employee = Employee.create(**validated_data)

        logger.info(f"Employee created: {employee.full_name}")
        return employee

    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        raise ValueError(f"Validation error: {e.message}")

def update_employee(employee: Employee, **kwargs) -> Employee:
    """Update employee with validation."""
    try:
        # Validate all input
        validated_data = InputValidator.validate_employee_data(kwargs)

        # Update employee
        for key, value in validated_data.items():
            setattr(employee, key, value)

        employee.save()

        logger.info(f"Employee updated: {employee.full_name}")
        return employee

    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        raise ValueError(f"Validation error: {e.message}")
```

### Part 3: Update Forms

```python
# src/ui_ctk/forms/employee_form.py
from src.utils.validation import InputValidator, ValidationError

def validate(self) -> tuple[bool, Optional[str]]:
    """Validate form with comprehensive checks."""
    try:
        # Get raw values
        data = {
            'external_id': self.external_id.get().strip(),
            'first_name': self.first_name.get().strip(),
            'last_name': self.last_name.get().strip(),
            'email': self.email.get().strip(),
            'phone': self.phone.get().strip(),
            'entry_date': self.entry_date.get().strip(),
            'current_status': self.current_status.get(),
            'workspace': self.workspace.get().strip(),
            'role': self.role.get().strip(),
            'contract_type': self.contract_type.get(),
            'comment': self.comment.get().strip(" \n\r\t"),
        }

        # Remove empty optional fields
        if not data['email']:
            del data['email']
        if not data['phone']:
            del data['phone']
        if not data['workspace']:
            del data['workspace']
        if not data['role']:
            del data['role']
        if not data['comment']:
            del data['comment']

        # Validate using InputValidator
        validated_data = InputValidator.validate_employee_data(data)

        # Store validated data
        self.validated_data = validated_data

        return True, None

    except ValidationError as e:
        # User-friendly error message
        return False, f"{e.field}: {e.message}"

    except Exception as e:
        return False, f"Validation error: {str(e)}"
```

### Part 4: Excel Import Validation

```python
# src/excel_import/excel_importer.py
from src.utils.validation import InputValidator, ValidationError

def import_employees(self) -> dict:
    """Import employees with comprehensive validation."""
    imported = 0
    failed = 0
    errors = []

    for row_num, row in enumerate(self.sheet.iter_rows(min_row=2), start=2):
        try:
            # Extract data from Excel
            data = {
                'external_id': str(row[0].value) if row[0].value else None,
                'first_name': str(row[1].value) if row[1].value else None,
                'last_name': str(row[2].value) if row[2].value else None,
                'email': str(row[3].value) if row[3].value else None,
                'phone': str(row[4].value) if row[4].value else None,
                'entry_date': str(row[5].value) if row[5].value else None,
                'current_status': str(row[6].value) if row[6].value else 'active',
                'workspace': str(row[7].value) if row[7].value else None,
                'role': str(row[8].value) if row[8].value else None,
                'contract_type': str(row[9].value) if row[9].value else None,
                'comment': str(row[10].value) if row[10].value else None,
            }

            # Validate ALL data
            validated_data = InputValidator.validate_employee_data(data)

            # Check for duplicates
            if Employee.select().where(Employee.external_id == validated_data['external_id']).exists():
                failed += 1
                errors.append(f"Row {row_num}: Duplicate external_id '{validated_data['external_id']}'")
                continue

            # Create employee
            Employee.create(**validated_data)
            imported += 1

        except ValidationError as e:
            failed += 1
            errors.append(f"Row {row_num}: {e.message}")
            continue

        except Exception as e:
            failed += 1
            errors.append(f"Row {row_num}: {str(e)}")
            continue

    return {
        'imported': imported,
        'failed': failed,
        'errors': errors,
    }
```

## Implementation Plan

### Phase 1: Validation Framework (2 hours)
1. Create `src/utils/validation.py`
2. Implement InputValidator class
3. Add unit tests for validation
4. Test edge cases

### Phase 2: Update Controllers (1 hour)
1. Add validation to employee_controller
2. Add validation to caces_controller
3. Add validation to medical_controller
4. Update error handling

### Phase 3: Update Forms (1 hour)
1. Update employee_form validation
2. Update caces_form validation
3. Update medical_form validation
4. Improve error messages

### Phase 4: Update Import (1 hour)
1. Add validation to excel_importer
2. Add detailed error reporting
3. Test with malicious Excel files
4. Document validation rules

## Files to Create
- `src/utils/validation.py`
- `tests/test_validation.py`
- `tests/test_validation_edge_cases.py`

## Files to Modify
- `src/controllers/employee_controller.py`
- `src/controllers/caces_controller.py`
- `src/controllers/medical_controller.py`
- `src/ui_ctk/forms/employee_form.py`
- `src/ui_ctk/forms/caces_form.py`
- `src/ui_ctk/forms/medical_form.py`
- `src/excel_import/excel_importer.py`

## Testing Requirements
- Test valid inputs (normal cases)
- Test invalid formats
- Test malicious inputs:
  - XSS attempts
  - SQL injection attempts (should be blocked by ORM)
  - Unicode attacks
  - Buffer overflow attempts
  - NULL byte injection
  - Control characters
- Test boundary conditions:
  - Empty strings
  - Maximum length strings
  - Minimum/maximum dates
  - Edge cases

## Related Issues
- #001: Path Traversal Vulnerability (file-specific validation)
- #004: File Upload Validation (file-specific validation)
- #010: Broad Exception Handling (validation errors should be specific)

## References
- OWASP Input Validation Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
- Unicode Security: https://unicode.org/reports/tr36/
- RFC 5322 (Email Format): https://tools.ietf.org/html/rfc5322
- Python unicodedata: https://docs.python.org/3/library/unicodedata.html

## Priority
**CRITICAL** - Attack surface for injection attacks and data corruption

## Estimated Effort
5-6 hours (validation framework + integration + tests)

## Mitigation
While waiting for full implementation:
1. **Add basic length limits** to all form fields
2. **Strip HTML** from all inputs (even if not currently rendered)
3. **Reject NULL bytes** in all strings
4. **Validate email format** with regex
5. **Validate date formats** before database insert
6. **Test Excel imports** with small batches first
7. **Review database** for invalid data and clean up
