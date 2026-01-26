"""Tests for soft delete migration script."""

import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from employee.models import Caces, Employee, MedicalVisit, OnlineTraining


class TestSoftDeleteMigration:
    """Tests for add_soft_delete migration."""

    def test_migration_adds_columns_to_employees(self, db_connection):
        """Test that migration adds soft delete columns to employees table."""
        # Get an employee
        employee = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )

        # Verify soft delete columns exist and are None by default
        assert employee.deleted_at is None
        assert employee.deleted_by is None
        assert employee.deletion_reason is None

        # Set soft delete fields
        employee.soft_delete(reason="Test", deleted_by="admin")

        # Verify fields are persisted
        emp = Employee.get_by_id(employee.id)
        assert emp.deleted_at is not None
        assert emp.deleted_by == "admin"
        assert emp.deletion_reason == "Test"

    def test_migration_adds_columns_to_caces(self, db_connection, sample_employee):
        """Test that migration adds soft delete columns to CACES table."""
        # Create a CACES
        caces = Caces.create(
            employee=sample_employee,
            kind="R489-1A",
            completion_date=date(2023, 1, 1),
            expiration_date=date(2024, 1, 1),
        )

        # Verify soft delete columns exist and are None by default
        assert caces.deleted_at is None
        assert caces.deleted_by is None
        assert caces.deletion_reason is None

        # Set soft delete fields
        caces.soft_delete(reason="Test", deleted_by="admin")

        # Verify fields are persisted
        c = Caces.get_by_id(caces.id)
        assert c.deleted_at is not None
        assert c.deleted_by == "admin"
        assert c.deletion_reason == "Test"

    def test_migration_adds_columns_to_medical_visits(self, db_connection, sample_employee):
        """Test that migration adds soft delete columns to medical_visits table."""
        # Create a medical visit
        visit = MedicalVisit.create(
            employee=sample_employee,
            visit_type="periodic",
            visit_date=date(2023, 6, 1),
            expiration_date=date(2024, 6, 1),
            result="fit",
        )

        # Verify soft delete columns exist and are None by default
        assert visit.deleted_at is None
        assert visit.deleted_by is None
        assert visit.deletion_reason is None

        # Set soft delete fields
        visit.soft_delete(reason="Test", deleted_by="admin")

        # Verify fields are persisted
        v = MedicalVisit.get_by_id(visit.id)
        assert v.deleted_at is not None
        assert v.deleted_by == "admin"
        assert v.deletion_reason == "Test"

    def test_migration_adds_columns_to_online_trainings(self, db_connection, sample_employee):
        """Test that migration adds soft delete columns to online_trainings table."""
        # Create an online training
        training = OnlineTraining.create(
            employee=sample_employee,
            title="Safety Training",
            completion_date=date(2023, 6, 1),
            expiration_date=date(2024, 6, 1),
            validity_months=12,
        )

        # Verify soft delete columns exist and are None by default
        assert training.deleted_at is None
        assert training.deleted_by is None
        assert training.deletion_reason is None

        # Set soft delete fields
        training.soft_delete(reason="Test", deleted_by="admin")

        # Verify fields are persisted
        t = OnlineTraining.get_by_id(training.id)
        assert t.deleted_at is not None
        assert t.deleted_by == "admin"
        assert t.deletion_reason == "Test"

    def test_existing_records_have_null_soft_delete_fields(self, db_connection):
        """Test that existing records have NULL soft delete fields."""
        # Create records before migration would run
        employee = Employee.create(
            external_id=str(uuid4()),
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )

        # Verify all soft delete fields are None (not deleted by default)
        assert employee.deleted_at is None
        assert employee.deleted_by is None
        assert employee.deletion_reason is None
        assert employee.is_deleted is False
