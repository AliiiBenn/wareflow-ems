"""Tests for utils/file_validation.py module."""

import pytest
from pathlib import Path
from utils.file_validation import (
    FileValidationError,
    DEFAULT_ALLOWED_EXTENSIONS,
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_DOCUMENTS_DIR,
    validate_document_path,
    sanitize_file_path,
    generate_safe_filename,
    is_safe_filename,
    validate_file_basic,
    validate_magic_number,
    validate_pdf_structure,
    validate_filename_characters,
    validate_file_not_empty,
    validate_comprehensive,
    validate_and_copy_document,
)


# =============================================================================
# TESTS: FileValidationError
# =============================================================================

class TestFileValidationError:
    """Tests for FileValidationError exception."""

    def test_file_validation_error_creation(self):
        """Should create error instance."""
        error = FileValidationError("Test error")
        assert str(error) == "Test error"


# =============================================================================
# TESTS: validate_document_path
# =============================================================================

class TestValidateDocumentPath:
    """Tests for validate_document_path function."""

    def test_valid_document_path(self, tmp_path):
        """Should accept valid document path."""
        # Create test file
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test content")

        is_valid, error = validate_document_path(str(test_file), allowed_dir=tmp_path)

        assert is_valid
        assert error is None

    def test_path_traversal_attack(self, tmp_path):
        """Should reject path traversal attempts."""
        is_valid, error = validate_document_path("../../etc/passwd", allowed_dir=tmp_path)

        assert not is_valid
        assert "Path traversal" in error or "not allowed" in error

    def test_nonexistent_file(self, tmp_path):
        """Should reject nonexistent files."""
        # Create the path within tmp_path so it passes the directory check
        nonexistent = tmp_path / "nonexistent.pdf"
        is_valid, error = validate_document_path(str(nonexistent), allowed_dir=tmp_path)

        assert not is_valid
        assert "does not exist" in error

    def test_directory_instead_of_file(self, tmp_path):
        """Should reject directory path."""
        is_valid, error = validate_document_path(str(tmp_path), allowed_dir=tmp_path.parent)

        assert not is_valid
        assert "not a directory" in error.lower()

    def test_invalid_extension(self, tmp_path):
        """Should reject files with disallowed extensions."""
        test_file = tmp_path / "test.exe"
        test_file.write_text("test")

        is_valid, error = validate_document_path(
            str(test_file),
            allowed_dir=tmp_path,
            allowed_extensions={".pdf"}
        )

        assert not is_valid
        assert "Only" in error and ".pdf" in error

    def test_file_too_large(self, tmp_path):
        """Should reject files exceeding size limit."""
        test_file = tmp_path / "large.pdf"
        test_file.write_bytes(b"0" * (11 * 1024 * 1024))  # 11 MB

        is_valid, error = validate_document_path(
            str(test_file),
            allowed_dir=tmp_path,
            max_size_mb=10
        )

        assert not is_valid
        assert "exceeds maximum" in error

    def test_empty_file_path(self, tmp_path):
        """Should reject empty file path."""
        is_valid, error = validate_document_path("", allowed_dir=tmp_path)

        assert not is_valid
        assert "required" in error


# =============================================================================
# TESTS: sanitize_file_path
# =============================================================================

class TestSanitizeFilePath:
    """Tests for sanitize_file_path function."""

    def test_safe_relative_path(self):
        """Should accept safe relative paths."""
        result = sanitize_file_path("documents/report.pdf", "/safe/base")
        assert "report.pdf" in result

    def test_path_traversal_with_base_dir(self):
        """Should detect and reject path traversal."""
        with pytest.raises(ValueError) as exc:
            sanitize_file_path("../../../etc/passwd", "/safe/base")

        assert "Path traversal" in str(exc.value)

    def test_absolute_path_without_base_dir(self):
        """Should reject absolute path when no base_dir provided."""
        # Use Windows absolute path
        with pytest.raises(ValueError) as exc:
            sanitize_file_path("C:\\Windows\\System32\\config")

        assert "absolute path" in str(exc.value)

    def test_double_dots_without_base_dir(self):
        """Should reject paths with .. when no base_dir."""
        with pytest.raises(ValueError) as exc:
            sanitize_file_path("../file.pdf")

        assert ".." in str(exc.value)

    def test_normalizes_path_separators(self):
        """Should normalize path separators."""
        result = sanitize_file_path("documents\\report.pdf", "/safe/base")
        assert "report.pdf" in result

    def test_preserves_safe_subdirectories(self, tmp_path):
        """Should preserve safe directory structure."""
        result = sanitize_file_path("subdir/file.pdf", str(tmp_path))
        assert "subdir" in result


# =============================================================================
# TESTS: generate_safe_filename
# =============================================================================

class TestGenerateSafeFilename:
    """Tests for generate_safe_filename function."""

    def test_unique_filename(self, tmp_path):
        """Should return filename as-is if it doesn't exist."""
        result = generate_safe_filename("test.pdf", str(tmp_path))
        assert result == "test.pdf"

    def test_existing_file_gets_suffix(self, tmp_path):
        """Should add numeric suffix for existing files."""
        # Create first file
        (tmp_path / "test.pdf").write_text("content")

        result = generate_safe_filename("test.pdf", str(tmp_path))
        assert result == "test_1.pdf"

    def test_multiple_existing_files(self, tmp_path):
        """Should increment suffix until finding unique name."""
        (tmp_path / "test.pdf").write_text("content1")
        (tmp_path / "test_1.pdf").write_text("content2")
        (tmp_path / "test_2.pdf").write_text("content3")

        result = generate_safe_filename("test.pdf", str(tmp_path))
        assert result == "test_3.pdf"

    def test_preserves_subdirectories(self, tmp_path):
        """Should preserve directory structure in filename."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        result = generate_safe_filename("subdir/test.pdf", str(tmp_path))
        assert "subdir" in result

    def test_rejects_unsafe_path(self, tmp_path):
        """Should reject unsafe paths."""
        with pytest.raises(ValueError):
            generate_safe_filename("../../etc/passwd", str(tmp_path))


# =============================================================================
# TESTS: is_safe_filename
# =============================================================================

class TestIsSafeFilename:
    """Tests for is_safe_filename function."""

    def test_safe_filename(self):
        """Should accept safe filenames."""
        assert is_safe_filename("document.pdf") == True
        assert is_safe_filename("report-2020.txt") == True
        assert is_safe_filename("image_v2.png") == True

    def test_rejects_path_traversal(self):
        """Should reject path traversal patterns."""
        assert is_safe_filename("../../etc/passwd") == False
        assert is_safe_filename("..\\windows\\system32") == False
        assert is_safe_filename("../file.pdf") == False

    def test_rejects_directory_separators(self):
        """Should reject paths with separators."""
        assert is_safe_filename("path/to/file.pdf") == False
        assert is_safe_filename("path\\file.pdf") == False

    def test_rejects_null_bytes(self):
        """Should reject filenames with null bytes."""
        assert is_safe_filename("file\x00.pdf") == False

    def test_rejects_control_characters(self):
        """Should reject control characters."""
        assert is_safe_filename("file\x01.pdf") == False
        assert is_safe_filename("file\x1f.pdf") == False

    def test_rejects_windows_reserved_names(self):
        """Should reject Windows reserved device names."""
        assert is_safe_filename("CON.txt") == False
        assert is_safe_filename("PRN.pdf") == False
        assert is_safe_filename("AUX.dat") == False
        assert is_safe_filename("NUL") == False
        assert is_safe_filename("COM1.txt") == False
        assert is_safe_filename("LPT1.pdf") == False

    def test_rejects_empty_filename(self):
        """Should reject empty filename."""
        assert is_safe_filename("") == False


# =============================================================================
# TESTS: validate_file_basic
# =============================================================================

class TestValidateFileBasic:
    """Tests for validate_file_basic function."""

    def test_valid_file(self, tmp_path):
        """Should accept valid file."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("content")

        is_valid, error = validate_file_basic(str(test_file))

        assert is_valid
        assert error is None

    def test_nonexistent_file(self, tmp_path):
        """Should reject nonexistent file."""
        is_valid, error = validate_file_basic(str(tmp_path / "nonexistent.pdf"))

        assert not is_valid
        assert "does not exist" in error

    def test_invalid_extension(self, tmp_path):
        """Should reject invalid file extension."""
        test_file = tmp_path / "test.exe"
        test_file.write_text("content")

        is_valid, error = validate_file_basic(str(test_file))

        assert not is_valid
        assert "Only" in error

    def test_file_too_large(self, tmp_path):
        """Should reject oversized file."""
        test_file = tmp_path / "large.pdf"
        test_file.write_bytes(b"0" * (11 * 1024 * 1024))  # 11 MB

        is_valid, error = validate_file_basic(str(test_file), max_size_mb=10)

        assert not is_valid
        assert "exceeds maximum" in error

    def test_directory_rejected(self, tmp_path):
        """Should reject directory path."""
        is_valid, error = validate_file_basic(str(tmp_path))

        assert not is_valid
        assert "not a directory" in error.lower()


# =============================================================================
# TESTS: validate_magic_number
# =============================================================================

class TestValidateMagicNumber:
    """Tests for validate_magic_number function."""

    def test_magic_not_available_graceful_degradation(self, tmp_path, monkeypatch):
        """Should gracefully handle missing python-magic."""
        # Mock MAGIC_AVAILABLE as False
        import utils.file_validation as fv
        monkeypatch.setattr(fv, "MAGIC_AVAILABLE", False)

        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4")

        is_valid, error = validate_magic_number(test_file)
        # Should pass (graceful degradation)
        assert is_valid
        assert error is None


# =============================================================================
# TESTS: validate_pdf_structure
# =============================================================================

class TestValidatePdfStructure:
    """Tests for validate_pdf_structure function."""

    def test_pypdf_not_available_graceful_degradation(self, tmp_path, monkeypatch):
        """Should gracefully handle missing pypdf."""
        import utils.file_validation as fv
        monkeypatch.setattr(fv, "PYPDF_AVAILABLE", False)

        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4")

        is_valid, error = validate_pdf_structure(test_file)
        # Should pass (graceful degradation)
        assert is_valid
        assert error is None


# =============================================================================
# TESTS: validate_filename_characters
# =============================================================================

class TestValidateFilenameCharacters:
    """Tests for validate_filename_characters function."""

    def test_valid_filename(self):
        """Should accept valid filenames."""
        is_valid, error = validate_filename_characters("document.pdf")
        assert is_valid
        assert error is None

    def test_empty_filename(self):
        """Should reject empty filename."""
        is_valid, error = validate_filename_characters("")
        assert not is_valid
        assert "empty" in error

    def test_null_bytes(self):
        """Should reject null bytes."""
        is_valid, error = validate_filename_characters("file\x00.pdf")
        assert not is_valid
        assert "null" in error

    def test_suspicious_characters(self):
        """Should reject suspicious characters."""
        suspicious = ["file<.pdf", "file>.pdf", "file:.pdf",
                      "file|.pdf", 'file".pdf', "file*.pdf", "file?.pdf"]

        for filename in suspicious:
            is_valid, error = validate_filename_characters(filename)
            assert not is_valid, f"Should reject {filename}"
            assert "invalid characters" in error

    def test_excessively_long_filename(self):
        """Should reject filenames exceeding 255 characters."""
        long_name = "a" * 256 + ".pdf"
        is_valid, error = validate_filename_characters(long_name)

        assert not is_valid
        assert "too long" in error


# =============================================================================
# TESTS: validate_file_not_empty
# =============================================================================

class TestValidateFileNotEmpty:
    """Tests for validate_file_not_empty function."""

    def test_non_empty_file(self, tmp_path):
        """Should accept non-empty file."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("content")

        is_valid, error = validate_file_not_empty(test_file)

        assert is_valid
        assert error is None

    def test_empty_file(self, tmp_path):
        """Should reject empty file."""
        test_file = tmp_path / "empty.pdf"
        test_file.write_text("")

        is_valid, error = validate_file_not_empty(test_file)

        assert not is_valid
        assert "empty" in error


# =============================================================================
# TESTS: validate_comprehensive
# =============================================================================

class TestValidateComprehensive:
    """Tests for validate_comprehensive function."""

    def test_valid_pdf_file(self, tmp_path):
        """Should accept valid PDF file."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4\ntest content\n%%EOF")

        is_valid, error = validate_comprehensive(
            str(test_file),
            validate_magic=False,  # Disable magic if libmagic not available
            validate_pdf=False     # Disable PDF validation if pypdf not available
        )

        assert is_valid
        assert error is None

    def test_nonexistent_file(self, tmp_path):
        """Should reject nonexistent file."""
        is_valid, error = validate_comprehensive(
            str(tmp_path / "nonexistent.pdf")
        )

        assert not is_valid
        assert "does not exist" in error

    def test_invalid_extension(self, tmp_path):
        """Should reject invalid file extension."""
        test_file = tmp_path / "test.exe"
        test_file.write_text("content")

        is_valid, error = validate_comprehensive(str(test_file))

        assert not is_valid
        assert "Invalid file type" in error

    def test_file_too_large(self, tmp_path):
        """Should reject oversized file."""
        test_file = tmp_path / "large.pdf"
        test_file.write_bytes(b"0" * (11 * 1024 * 1024))

        is_valid, error = validate_comprehensive(
            str(test_file),
            max_size_mb=10,
            validate_magic=False,
            validate_pdf=False
        )

        assert not is_valid
        assert "too large" in error

    def test_empty_file(self, tmp_path):
        """Should reject empty file."""
        test_file = tmp_path / "empty.pdf"
        test_file.write_text("")

        is_valid, error = validate_comprehensive(
            str(test_file),
            validate_magic=False,
            validate_pdf=False
        )

        assert not is_valid
        assert "empty" in error

    def test_invalid_filename_characters(self, tmp_path):
        """Should reject filenames with invalid characters."""
        # Test directly with validate_filename_characters
        is_valid, error = validate_filename_characters("file<.pdf")

        assert not is_valid
        assert "invalid characters" in error


# =============================================================================
# TESTS: validate_and_copy_document
# =============================================================================

class TestValidateAndCopyDocument:
    """Tests for validate_and_copy_document function."""

    def test_valid_document_copied(self, tmp_path):
        """Should validate and copy valid document."""
        # Create source file
        source = tmp_path / "source.pdf"
        source.write_bytes(b"%PDF-1.4\ntest\n%%EOF")

        # Create destination dir
        dest_dir = tmp_path / "documents"
        dest_dir.mkdir()

        success, error, secure_path = validate_and_copy_document(
            str(source),
            dest_dir=dest_dir,
            validate_magic=False,
            validate_pdf=False
        )

        assert success
        assert error is None
        assert secure_path is not None
        assert Path(secure_path).exists()

    def test_invalid_document_rejected(self, tmp_path):
        """Should reject invalid document."""
        source = tmp_path / "test.exe"
        source.write_text("content")

        dest_dir = tmp_path / "documents"
        dest_dir.mkdir()

        success, error, secure_path = validate_and_copy_document(
            str(source),
            dest_dir=dest_dir,
            allowed_extensions={".pdf"}
        )

        assert not success
        assert error is not None
        assert secure_path is None

    def test_creates_unique_filename(self, tmp_path):
        """Should create unique filename to prevent collisions."""
        # Create source file
        source = tmp_path / "source.pdf"
        source.write_bytes(b"%PDF-1.4\ntest\n%%EOF")

        dest_dir = tmp_path / "documents"
        dest_dir.mkdir()

        # Copy twice - should generate different names
        success1, error1, path1 = validate_and_copy_document(
            str(source),
            dest_dir=dest_dir,
            validate_magic=False,
            validate_pdf=False
        )

        success2, error2, path2 = validate_and_copy_document(
            str(source),
            dest_dir=dest_dir,
            validate_magic=False,
            validate_pdf=False
        )

        assert success1 and success2
        assert path1 != path2  # Different paths
        assert Path(path1).exists()
        assert Path(path2).exists()

    def test_uses_default_documents_dir(self, tmp_path):
        """Should use default documents directory if not specified."""
        source = tmp_path / "source.pdf"
        source.write_bytes(b"%PDF-1.4\ntest\n%%EOF")

        # Create default documents dir
        docs_dir = tmp_path / "documents"
        docs_dir.mkdir()

        # Change to tmp_path context
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            success, error, secure_path = validate_and_copy_document(
                str(source),
                validate_magic=False,
                validate_pdf=False
            )

            assert success
            assert secure_path is not None
        finally:
            os.chdir(old_cwd)
