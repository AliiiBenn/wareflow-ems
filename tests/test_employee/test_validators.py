"""Tests for employee validators."""

import pytest
from datetime import date

from employee.validators import (
    ValidationError,
    validate_external_id,
    validate_entry_date,
    validate_caces_kind,
    validate_medical_visit_consistency,
    validate_path_safe,
    UniqueValidator,
    DateRangeValidator,
)
from employee.models import Employee


# =============================================================================
# TESTS: ValidationError
# =============================================================================

class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error_creation(self):
        """Should create error with all attributes."""
        error = ValidationError(
            field="test_field",
            value="test_value",
            message="Test error message",
            details={"key": "value"}
        )

        assert error.field == "test_field"
        assert error.value == "test_value"
        assert error.message == "Test error message"
        assert error.details == {"key": "value"}

    def test_validation_error_str_without_details(self):
        """Should format error message without details."""
        error = ValidationError(
            field="test_field",
            value="test_value",
            message="Test error"
        )

        assert str(error) == "Validation failed for field 'test_field': Test error"

    def test_validation_error_str_with_details(self):
        """Should format error message with details."""
        error = ValidationError(
            field="test_field",
            value="test_value",
            message="Test error",
            details={"min_length": 3, "actual_length": 2}
        )

        error_str = str(error)
        assert "Test error" in error_str
        assert "min_length=3" in error_str
        assert "actual_length=2" in error_str

    def test_validation_error_to_dict(self):
        """Should convert error to dictionary."""
        error = ValidationError(
            field="test_field",
            value="test_value",
            message="Test error",
            details={"key": "value"}
        )

        error_dict = error.to_dict()
        assert error_dict == {
            "field": "test_field",
            "value": "test_value",
            "message": "Test error",
            "details": {"key": "value"}
        }

    def test_validation_error_to_dict_with_none_value(self):
        """Should handle None value in to_dict."""
        error = ValidationError(
            field="test_field",
            value=None,
            message="Test error"
        )

        error_dict = error.to_dict()
        assert error_dict["value"] is None


# =============================================================================
# TESTS: validate_external_id
# =============================================================================

class TestValidateExternalID:
    """Tests for validate_external_id function."""

    def test_valid_external_id(self):
        """Should accept valid external IDs."""
        assert validate_external_id("WMS-001") == "WMS-001"
        assert validate_external_id("R489_1A") == "R489_1A"
        assert validate_external_id("ABC") == "ABC"
        assert validate_external_id("123") == "123"
        assert validate_external_id("aB1-_") == "aB1-_"

    def test_external_id_with_special_chars(self):
        """Should reject special characters."""
        with pytest.raises(ValidationError) as exc:
            validate_external_id("R489 1A")

        assert exc.value.field == "external_id"
        assert "invalid characters" in exc.value.message.lower()

    def test_external_id_too_short(self):
        """Should reject IDs shorter than 3 characters."""
        with pytest.raises(ValidationError) as exc:
            validate_external_id("AB")

        assert exc.value.field == "external_id"
        assert "too short" in exc.value.message.lower()
        assert exc.value.details["min_length"] == 3

    def test_external_id_too_long(self):
        """Should reject IDs longer than 50 characters."""
        long_id = "A" * 51
        with pytest.raises(ValidationError) as exc:
            validate_external_id(long_id)

        assert exc.value.field == "external_id"
        assert "too long" in exc.value.message.lower()
        assert exc.value.details["max_length"] == 50

    def test_external_id_empty(self):
        """Should reject empty string."""
        with pytest.raises(ValidationError) as exc:
            validate_external_id("")

        assert exc.value.field == "external_id"
        assert "cannot be empty" in exc.value.message.lower()

    def test_external_id_none(self):
        """Should reject None value."""
        with pytest.raises(ValidationError) as exc:
            validate_external_id(None)

        assert exc.value.field == "external_id"

    def test_external_id_not_string(self):
        """Should reject non-string values."""
        with pytest.raises(ValidationError) as exc:
            validate_external_id(123)

        assert exc.value.field == "external_id"
        assert "must be a string" in exc.value.message.lower()

    def test_external_id_path_traversal_double_dot(self):
        """Should reject path traversal with ../ pattern."""
        with pytest.raises(ValidationError) as exc:
            validate_external_id("../etc/passwd")

        assert exc.value.field == "external_id"
        assert "path traversal" in exc.value.message.lower()

    def test_external_id_path_traversal_double_dot_windows(self):
        """Should reject Windows path traversal."""
        with pytest.raises(ValidationError) as exc:
            validate_external_id("..\\windows\\system32")

        assert exc.value.field == "external_id"
        assert "path traversal" in exc.value.message.lower()

    def test_external_id_single_dot(self):
        """Should reject ./ pattern."""
        with pytest.raises(ValidationError) as exc:
            validate_external_id("./config.yml")

        assert exc.value.field == "external_id"
        assert "path traversal" in exc.value.message.lower()

    def test_external_id_forward_slash(self):
        """Should reject forward slash."""
        with pytest.raises(ValidationError) as exc:
            validate_external_id("path/to/file")

        assert exc.value.field == "external_id"
        assert "path traversal" in exc.value.message.lower()

    def test_external_id_backslash(self):
        """Should reject backslash."""
        with pytest.raises(ValidationError) as exc:
            validate_external_id("path\\to\\file")

        assert exc.value.field == "external_id"
        assert "path traversal" in exc.value.message.lower()


# =============================================================================
# TESTS: validate_entry_date
# =============================================================================

class TestValidateEntryDate:
    """Tests for validate_entry_date function."""

    def test_valid_entry_date(self):
        """Should accept valid dates."""
        assert validate_entry_date(date(2020, 1, 15)) == date(2020, 1, 15)
        assert validate_entry_date(date(1900, 1, 1)) == date(1900, 1, 1)
        assert validate_entry_date(date.today()) == date.today()

    def test_entry_date_future(self):
        """Should reject future dates."""
        future_date = date(2100, 1, 1)
        with pytest.raises(ValidationError) as exc:
            validate_entry_date(future_date)

        assert exc.value.field == "entry_date"
        assert "future" in exc.value.message.lower()
        assert exc.value.details["entry_date"] == "2100-01-01"

    def test_entry_date_too_old(self):
        """Should reject dates before 1900."""
        old_date = date(1800, 1, 1)
        with pytest.raises(ValidationError) as exc:
            validate_entry_date(old_date)

        assert exc.value.field == "entry_date"
        assert "too old" in exc.value.message.lower()
        assert exc.value.details["min_date"] == "1900-01-01"

    def test_entry_date_none(self):
        """Should reject None value."""
        with pytest.raises(ValidationError) as exc:
            validate_entry_date(None)

        assert exc.value.field == "entry_date"
        assert "required" in exc.value.message.lower()

    def test_entry_date_not_date(self):
        """Should reject non-date values."""
        with pytest.raises(ValidationError) as exc:
            validate_entry_date("2020-01-15")

        assert exc.value.field == "entry_date"
        assert "must be a date" in exc.value.message.lower()


# =============================================================================
# TESTS: validate_caces_kind
# =============================================================================

class TestValidateCacesKind:
    """Tests for validate_caces_kind function."""

    def test_valid_caces_kind(self):
        """Should accept valid CACES types."""
        assert validate_caces_kind("R489-1A") == "R489-1A"
        assert validate_caces_kind("r489-1b") == "R489-1B"  # Test uppercase
        assert validate_caces_kind("R489-3") == "R489-3"
        assert validate_caces_kind("R489-4") == "R489-4"
        assert validate_caces_kind("R489-5") == "R489-5"

    def test_caces_kind_invalid_type(self):
        """Should reject invalid CACES type."""
        with pytest.raises(ValidationError) as exc:
            validate_caces_kind("R489-2")

        assert exc.value.field == "kind"
        assert "invalid" in exc.value.message.lower()
        assert "R489-2" in exc.value.details["provided"]

    def test_caces_kind_none(self):
        """Should reject None value."""
        with pytest.raises(ValidationError) as exc:
            validate_caces_kind(None)

        assert exc.value.field == "kind"
        assert "required" in exc.value.message.lower()

    def test_caces_kind_not_string(self):
        """Should reject non-string values."""
        with pytest.raises(ValidationError) as exc:
            validate_caces_kind(123)

        assert exc.value.field == "kind"
        assert "must be a string" in exc.value.message.lower()

    def test_caces_kind_empty(self):
        """Should reject empty string."""
        with pytest.raises(ValidationError) as exc:
            validate_caces_kind("")

        assert exc.value.field == "kind"
        assert "required" in exc.value.message.lower()


# =============================================================================
# TESTS: validate_medical_visit_consistency
# =============================================================================

class TestValidateMedicalVisitConsistency:
    """Tests for validate_medical_visit_consistency function."""

    def test_valid_combinations(self):
        """Should accept valid visit type and result combinations."""
        assert validate_medical_visit_consistency("initial", "fit") == ("initial", "fit")
        assert validate_medical_visit_consistency("periodic", "unfit") == ("periodic", "unfit")
        assert validate_medical_visit_consistency("periodic", "fit_with_restrictions") == ("periodic", "fit_with_restrictions")

    def test_recovery_with_restrictions(self):
        """Should accept recovery visit with restrictions."""
        assert validate_medical_visit_consistency("recovery", "fit_with_restrictions") == ("recovery", "fit_with_restrictions")

    def test_recovery_without_restrictions_fit(self):
        """Should reject recovery visit with 'fit' result."""
        with pytest.raises(ValidationError) as exc:
            validate_medical_visit_consistency("recovery", "fit")

        assert exc.value.field == "result"
        assert "restrictions" in exc.value.message.lower()
        assert exc.value.details["expected_result"] == "fit_with_restrictions"

    def test_recovery_without_restrictions_unfit(self):
        """Should reject recovery visit with 'unfit' result."""
        with pytest.raises(ValidationError) as exc:
            validate_medical_visit_consistency("recovery", "unfit")

        assert exc.value.field == "result"
        assert "restrictions" in exc.value.message.lower()

    def test_invalid_visit_type(self):
        """Should reject invalid visit type."""
        with pytest.raises(ValidationError) as exc:
            validate_medical_visit_consistency("invalid", "fit")

        assert exc.value.field == "visit_type"
        assert "invalid" in exc.value.message.lower()

    def test_invalid_result(self):
        """Should reject invalid result."""
        with pytest.raises(ValidationError) as exc:
            validate_medical_visit_consistency("initial", "invalid")

        assert exc.value.field == "result"
        assert "invalid" in exc.value.message.lower()

    def test_missing_visit_type(self):
        """Should reject missing visit type."""
        with pytest.raises(ValidationError) as exc:
            validate_medical_visit_consistency("", "fit")

        assert exc.value.field == "visit_type"
        assert "required" in exc.value.message.lower()

    def test_missing_result(self):
        """Should reject missing result."""
        with pytest.raises(ValidationError) as exc:
            validate_medical_visit_consistency("initial", "")

        assert exc.value.field == "result"
        assert "required" in exc.value.message.lower()


# =============================================================================
# TESTS: validate_path_safe
# =============================================================================

class TestValidatePathSafe:
    """Tests for validate_pathSafe function."""

    def test_valid_paths(self):
        """Should accept valid relative paths."""
        assert validate_path_safe("documents/caces.pdf") == "documents/caces.pdf"
        assert validate_path_safe("certificates/R489-1A.pdf") == "certificates/R489-1A.pdf"
        assert validate_path_safe("file.txt") == "file.txt"

    def test_path_traversal_double_dot(self):
        """Should reject ../ pattern."""
        with pytest.raises(ValidationError) as exc:
            validate_path_safe("../../../etc/passwd")

        assert exc.value.field == "file_path"
        assert "path traversal" in exc.value.message.lower()

    def test_path_traversal_double_dot_windows(self):
        """Should reject ..\\ pattern."""
        with pytest.raises(ValidationError) as exc:
            validate_path_safe("..\\..\\windows\\system32")

        assert exc.value.field == "file_path"
        assert "path traversal" in exc.value.message.lower()

    def test_path_traversal_single_dot(self):
        """Should reject ./ pattern."""
        with pytest.raises(ValidationError) as exc:
            validate_path_safe("./config.yml")

        assert exc.value.field == "file_path"
        assert "path traversal" in exc.value.message.lower()

    def test_absolute_path_unix(self):
        """Should reject Unix absolute paths."""
        with pytest.raises(ValidationError) as exc:
            validate_path_safe("/etc/passwd")

        assert exc.value.field == "file_path"
        assert "absolute" in exc.value.message.lower()

    def test_absolute_path_windows(self):
        """Should reject Windows absolute paths."""
        with pytest.raises(ValidationError) as exc:
            validate_path_safe("C:\\Windows\\System32")

        assert exc.value.field == "file_path"
        assert "absolute" in exc.value.message.lower()

    def test_valid_extension(self):
        """Should accept files with allowed extensions."""
        assert validate_path_safe("file.pdf", allowed_extensions=[".pdf", ".jpg"]) == "file.pdf"
        assert validate_path_safe("file.jpg", allowed_extensions=[".pdf", ".jpg"]) == "file.jpg"

    def test_invalid_extension(self):
        """Should reject files with disallowed extensions."""
        with pytest.raises(ValidationError) as exc:
            validate_path_safe("file.exe", allowed_extensions=[".pdf", ".jpg"])

        assert exc.value.field == "file_path"
        assert "extension not allowed" in exc.value.message.lower()
        assert exc.value.details["provided_extension"] == ".exe"

    def test_no_extension_with_allowed_list(self):
        """Should reject files without extension when extensions are required."""
        with pytest.raises(ValidationError) as exc:
            validate_path_safe("file", allowed_extensions=[".pdf"])

        assert exc.value.field == "file_path"
        assert "no extension" in exc.value.message.lower()

    def test_empty_path(self):
        """Should reject empty string."""
        with pytest.raises(ValidationError) as exc:
            validate_path_safe("")

        assert exc.value.field == "file_path"
        assert "cannot be empty" in exc.value.message.lower()

    def test_none_path(self):
        """Should reject None value."""
        with pytest.raises(ValidationError) as exc:
            validate_path_safe(None)

        assert exc.value.field == "file_path"

    def test_not_string_path(self):
        """Should reject non-string values."""
        with pytest.raises(ValidationError) as exc:
            validate_path_safe(123)

        assert exc.value.field == "file_path"
        assert "must be a string" in exc.value.message.lower()


# =============================================================================
# TESTS: UniqueValidator
# =============================================================================

class TestUniqueValidator:
    """Tests for UniqueValidator class."""

    def test_unique_validator_new_value(self, db):
        """Should accept new unique value."""
        validator = UniqueValidator(Employee, Employee.external_id)
        result = validator.validate("NEW-UNIQUE-ID")
        assert result == "NEW-UNIQUE-ID"

    def test_unique_validator_duplicate(self, db, sample_employee):
        """Should reject duplicate value."""
        validator = UniqueValidator(Employee, Employee.external_id)

        with pytest.raises(ValidationError) as exc:
            validator.validate(sample_employee.external_id)

        assert exc.value.field == "external_id"
        assert "already exists" in exc.value.message.lower()

    def test_unique_validator_update_same_value(self, db, sample_employee):
        """Should allow same value when updating."""
        validator = UniqueValidator(
            Employee,
            Employee.external_id,
            exclude_instance=sample_employee
        )

        result = validator.validate(sample_employee.external_id)
        assert result == sample_employee.external_id

    def test_unique_validator_update_different_value(self, db, sample_employee):
        """Should validate new value when updating."""
        validator = UniqueValidator(
            Employee,
            Employee.external_id,
            exclude_instance=sample_employee
        )

        # Should accept new unique value
        result = validator.validate("NEW-ID-FOR-UPDATE")
        assert result == "NEW-ID-FOR-UPDATE"

    def test_unique_validator_update_duplicate_other(self, db):
        """Should reject value that exists for another employee."""
        # Create two employees
        employee1 = Employee.create(
            external_id="EMP-001",
            first_name="John",
            last_name="Doe",
            current_status="active",
            workspace="Quai",
            role="Cariste",
            contract_type="CDI",
            entry_date=date(2020, 1, 15)
        )

        employee2 = Employee.create(
            external_id="EMP-002",
            first_name="Jane",
            last_name="Smith",
            current_status="active",
            workspace="Zone A",
            role="Magasinier",
            contract_type="CDI",
            entry_date=date(2020, 2, 1)
        )

        # Try to update employee2 with employee1's external_id
        validator = UniqueValidator(
            Employee,
            Employee.external_id,
            exclude_instance=employee2
        )

        with pytest.raises(ValidationError) as exc:
            validator.validate("EMP-001")

        assert exc.value.field == "external_id"


# =============================================================================
# TESTS: DateRangeValidator
# =============================================================================

class TestDateRangeValidator:
    """Tests for DateRangeValidator class."""

    def test_date_range_valid(self, db):
        """Should accept date within range."""
        validator = DateRangeValidator(
            min_date=date(1900, 1, 1),
            max_date=date.today(),
            field_name="entry_date"
        )

        result = validator.validate(date(2020, 1, 15))
        assert result == date(2020, 1, 15)

    def test_date_range_too_early(self, db):
        """Should reject date before minimum."""
        validator = DateRangeValidator(
            min_date=date(2000, 1, 1),
            max_date=date.today(),
            field_name="birth_date"
        )

        with pytest.raises(ValidationError) as exc:
            validator.validate(date(1990, 1, 1))

        assert exc.value.field == "birth_date"
        assert "too early" in exc.value.message.lower()

    def test_date_range_too_late(self, db):
        """Should reject date after maximum."""
        validator = DateRangeValidator(
            min_date=date(1900, 1, 1),
            max_date=date(2020, 1, 1),
            field_name="hire_date"
        )

        with pytest.raises(ValidationError) as exc:
            validator.validate(date(2025, 1, 1))

        assert exc.value.field == "hire_date"
        assert "too late" in exc.value.message.lower()

    def test_date_range_no_minimum(self, db):
        """Should accept any date when no minimum set."""
        validator = DateRangeValidator(
            min_date=None,
            max_date=date.today(),
            field_name="event_date"
        )

        # Very old date should be accepted
        result = validator.validate(date(1800, 1, 1))
        assert result == date(1800, 1, 1)

    def test_date_range_no_maximum(self, db):
        """Should accept any date when no maximum set."""
        validator = DateRangeValidator(
            min_date=date(1900, 1, 1),
            max_date=None,
            field_name="event_date"
        )

        # Future date should be accepted
        future_date = date(2100, 1, 1)
        result = validator.validate(future_date)
        assert result == future_date

    def test_date_range_none_value(self, db):
        """Should reject None value."""
        validator = DateRangeValidator(
            min_date=date(1900, 1, 1),
            max_date=date.today(),
            field_name="test_date"
        )

        with pytest.raises(ValidationError) as exc:
            validator.validate(None)

        assert exc.value.field == "test_date"
        assert "required" in exc.value.message.lower()

    def test_date_range_not_date(self, db):
        """Should reject non-date values."""
        validator = DateRangeValidator(
            min_date=date(1900, 1, 1),
            max_date=date.today(),
            field_name="test_date"
        )

        with pytest.raises(ValidationError) as exc:
            validator.validate("2020-01-15")

        assert exc.value.field == "test_date"
        assert "must be a date" in exc.value.message.lower()
