"""Tests for file operations utilities."""

import pytest
from pathlib import Path
from datetime import date

from utils import files


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_removes_special_chars(self):
        """Should remove special characters."""
        result = files.sanitize_filename("file@#$%.pdf")
        assert result == "file.pdf"

    def test_replaces_spaces_with_underscores(self):
        """Should replace spaces with underscores."""
        result = files.sanitize_filename("my document.pdf")
        assert result == "my_document.pdf"

    def test_removes_path_traversal(self):
        """Should remove path traversal attempts."""
        result = files.sanitize_filename("../../../etc/passwd")
        assert "../" not in result

    def test_keeps_safe_chars(self):
        """Should keep letters, numbers, hyphens, underscores, dots."""
        result = files.sanitize_filename("File-123_Test.pdf")
        assert result == "File-123_Test.pdf"

    def test_removes_leading_trailing_spaces(self):
        """Should remove leading and trailing spaces."""
        result = files.sanitize_filename("  file.pdf  ")
        assert result == "file.pdf"

    def test_replaces_multiple_underscores(self):
        """Should replace multiple underscores with single."""
        result = files.sanitize_filename("file___name.pdf")
        assert result == "file_name.pdf"

    def test_returns_default_for_empty_result(self):
        """Should return 'document' for empty result."""
        result = files.sanitize_filename("@#$%")
        assert result == "document"


class TestGenerateDocumentName:
    """Tests for generate_document_name function."""

    def test_generates_correct_format(self):
        """Should generate name in correct format."""
        name = files.generate_document_name(
            category="caces",
            employee_external_id="WMS-001",
            document_date=date(2026, 1, 15),
            title="Test Document",
            extension=".pdf"
        )

        assert name == "WMS-001_caces_20260115_Test_Document.pdf"

    def test_sanitizes_title(self):
        """Should sanitize title in filename."""
        name = files.generate_document_name(
            category="medical",
            employee_external_id="WMS-002",
            document_date=date(2026, 6, 1),
            title="Visit Report (Final)!",
            extension=".pdf"
        )

        assert "Visit_Report_Final" in name
        assert "!" not in name

    def test_adds_dot_to_extension(self):
        """Should add dot to extension if missing."""
        name = files.generate_document_name(
            category="training",
            employee_external_id="WMS-003",
            document_date=date(2026, 3, 10),
            title="Certificate",
            extension="pdf"
        )

        assert name.endswith(".pdf")


class TestEnsureDirectoryExists:
    """Tests for ensure_directory_exists function."""

    def test_creates_directory(self, tmp_path):
        """Should create directory if it doesn't exist."""
        new_dir = tmp_path / "new" / "nested" / "dir"

        files.ensure_directory_exists(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_handles_existing_directory(self, tmp_path):
        """Should not raise error if directory exists."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        # Should not raise exception
        files.ensure_directory_exists(existing_dir)

        assert existing_dir.exists()


class TestValidateFileType:
    """Tests for validate_file_type function."""

    def test_validates_pdf_extension(self):
        """Should accept .pdf extension."""
        result = files.validate_file_type(
            Path("document.pdf"),
            ['.pdf', '.jpg']
        )
        assert result is True

    def test_validates_without_dot(self):
        """Should handle extensions without dot."""
        result = files.validate_file_type(
            Path("document.pdf"),
            ['pdf', 'jpg']
        )
        assert result is True

    def test_case_insensitive(self):
        """Should be case insensitive."""
        result = files.validate_file_type(
            Path("document.PDF"),
            ['.pdf']
        )
        assert result is True

    def test_rejects_invalid_extension(self):
        """Should reject invalid extensions."""
        result = files.validate_file_type(
            Path("document.txt"),
            ['.pdf', '.jpg']
        )
        assert result is False


class TestGetFileSizeMb:
    """Tests for get_file_size_mb function."""

    def test_returns_size_in_mb(self, tmp_path):
        """Should return file size in MB."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("x" * (1024 * 1024))  # 1 MB

        size = files.get_file_size_mb(test_file)

        assert size == pytest.approx(1.0, rel=0.1)

    def test_raises_error_for_missing_file(self):
        """Should raise FileNotFoundError if file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            files.get_file_size_mb(Path("nonexistent.pdf"))


class TestDeleteDocument:
    """Tests for delete_document function."""

    def test_deletes_existing_file(self, tmp_path):
        """Should delete existing file."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("content")

        result = files.delete_document(test_file)

        assert result is True
        assert not test_file.exists()

    def test_returns_false_for_missing_file(self):
        """Should return False for missing file."""
        result = files.delete_document(Path("nonexistent.pdf"))

        assert result is False


class TestMoveDocument:
    """Tests for move_document function."""

    def test_moves_file(self, tmp_path):
        """Should move file to destination."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"

        source.write_text("content")

        result = files.move_document(source, dest)

        assert dest.exists()
        assert dest.read_text() == "content"
        assert not source.exists()

    def test_creates_destination_directory(self, tmp_path):
        """Should create destination directory if needed."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "nested" / "dir" / "dest.txt"

        source.write_text("content")

        files.move_document(source, dest)

        assert dest.exists()

    def test_raises_error_for_missing_source(self, tmp_path):
        """Should raise FileNotFoundError if source doesn't exist."""
        with pytest.raises(FileNotFoundError):
            files.move_document(
                tmp_path / "nonexistent.txt",
                tmp_path / "dest.txt"
            )


class TestGetDocumentCategoryFromPath:
    """Tests for get_document_category_from_path function."""

    def test_extracts_caces_category(self):
        """Should extract 'caces' category."""
        result = files.get_document_category_from_path(
            Path("documents/caces/file.pdf")
        )
        assert result == "caces"

    def test_extracts_medical_category(self):
        """Should extract 'medical' category."""
        result = files.get_document_category_from_path(
            Path("documents/medical/visit.pdf")
        )
        assert result == "medical"

    def test_extracts_training_category(self):
        """Should extract 'training' category."""
        result = files.get_document_category_from_path(
            Path("documents/training/cert.pdf")
        )
        assert result == "training"

    def test_returns_none_for_invalid_category(self):
        """Should return None for invalid category."""
        result = files.get_document_category_from_path(
            Path("documents/other/file.pdf")
        )
        assert result is None


class TestIsValidDocumentPath:
    """Tests for is_valid_document_path function."""

    def test_validates_caces_path(self):
        """Should validate caces path."""
        result = files.is_valid_document_path(
            Path("documents/caces/file.pdf")
        )
        assert result is True

    def test_validates_medical_path(self):
        """Should validate medical path."""
        result = files.is_valid_document_path(
            Path("documents/medical/file.pdf")
        )
        assert result is True

    def test_validates_training_path(self):
        """Should validate training path."""
        result = files.is_valid_document_path(
            Path("documents/training/file.pdf")
        )
        assert result is True

    def test_rejects_invalid_category(self):
        """Should reject invalid category."""
        result = files.is_valid_document_path(
            Path("documents/other/file.pdf")
        )
        assert result is False

    def test_rejects_wrong_root(self):
        """Should reject path not under documents."""
        result = files.is_valid_document_path(
            Path("other/caces/file.pdf")
        )
        assert result is False

    def test_rejects_shallow_path(self):
        """Should reject shallow path."""
        result = files.is_valid_document_path(
            Path("documents.pdf")
        )
        assert result is False


class TestCopyDocumentToStorage:
    """Tests for copy_document_to_storage function."""

    def test_copies_document_to_storage(self, tmp_path):
        """Should copy document to standardized storage location."""
        # Create source file
        source = tmp_path / "source.pdf"
        source.write_text("PDF content")

        # Copy to storage
        storage_root = tmp_path / "documents"
        result = files.copy_document_to_storage(
            source_path=source,
            category="caces",
            employee_external_id="WMS-001",
            document_date=date(2026, 1, 15),
            title="R489-1A",
            storage_root=storage_root
        )

        # Verify
        assert result.exists()
        assert result.parent.name == "caces"
        assert "WMS-001" in result.name
        assert "20260115" in result.name
        assert result.suffix == ".pdf"

    def test_creates_storage_directory(self, tmp_path):
        """Should create storage directory if needed."""
        source = tmp_path / "source.pdf"
        source.write_text("content")

        storage_root = tmp_path / "documents"

        files.copy_document_to_storage(
            source_path=source,
            category="medical",
            employee_external_id="WMS-002",
            document_date=date(2026, 6, 1),
            title="Visit Report",
            storage_root=storage_root
        )

        assert (storage_root / "medical").exists()

    def test_raises_error_for_missing_source(self, tmp_path):
        """Should raise FileNotFoundError if source doesn't exist."""
        with pytest.raises(FileNotFoundError):
            files.copy_document_to_storage(
                source_path=tmp_path / "nonexistent.pdf",
                category="caces",
                employee_external_id="WMS-001",
                document_date=date(2026, 1, 15),
                title="Test"
            )

    def test_raises_error_for_invalid_category(self, tmp_path):
        """Should raise ValueError for invalid category."""
        source = tmp_path / "source.pdf"
        source.write_text("content")

        with pytest.raises(ValueError):
            files.copy_document_to_storage(
                source_path=source,
                category="invalid",
                employee_external_id="WMS-001",
                document_date=date(2026, 1, 15),
                title="Test"
            )
