"""Tests for soft delete functionality in models."""

from datetime import date, datetime
from uuid import uuid4

import pytest

from employee.models import Caces, Employee, MedicalVisit, OnlineTraining


class TestEmployeeSoftDelete:
    """Tests for Employee soft delete."""

    def test_soft_delete_employee(self, db_connection, sample_employee):
        """Test soft deleting an employee."""
        # Verify employee is not deleted
        assert sample_employee.is_deleted is False
        assert sample_employee.deleted_at is None

        # Soft delete
        sample_employee.soft_delete(reason="Test deletion", deleted_by="admin")

        # Reload from database
        employee = Employee.get_by_id(sample_employee.id)

        # Verify soft delete fields are set
        assert employee.is_deleted is True
        assert employee.deleted_at is not None
        assert employee.deletion_reason == "Test deletion"
        assert employee.deleted_by == "admin"

    def test_restore_employee(self, db_connection, sample_employee):
        """Test restoring a soft deleted employee."""
        # Soft delete first
        sample_employee.soft_delete(reason="Test deletion")

        # Restore
        sample_employee.restore()

        # Reload from database
        employee = Employee.get_by_id(sample_employee.id)

        # Verify employee is restored
        assert employee.is_deleted is False
        assert employee.deleted_at is None
        assert employee.deletion_reason is None
        assert employee.deleted_by is None

    def test_without_deleted_employees(self, db_connection):
        """Test getting only non-deleted employees."""
        # Create 3 employees
        emp1 = Employee.create(
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
        emp2 = Employee.create(
            external_id=str(uuid4()),
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            workspace="Zone B",
            role="Manager",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        emp3 = Employee.create(
            external_id=str(uuid4()),
            first_name="Bob",
            last_name="Johnson",
            email="bob@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDD",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )

        # Soft delete emp2
        emp2.soft_delete(reason="Test deletion")

        # Get non-deleted employees
        active_employees = list(Employee.without_deleted())

        # Should return emp1 and emp3, not emp2
        assert len(active_employees) == 2
        assert emp1 in active_employees
        assert emp3 in active_employees
        assert emp2 not in active_employees

    def test_deleted_employees(self, db_connection):
        """Test getting only deleted employees."""
        # Create 3 employees
        emp1 = Employee.create(
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
        emp2 = Employee.create(
            external_id=str(uuid4()),
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            workspace="Zone B",
            role="Manager",
            contract_type="CDI",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )
        emp3 = Employee.create(
            external_id=str(uuid4()),
            first_name="Bob",
            last_name="Johnson",
            email="bob@test.com",
            workspace="Zone A",
            role="Operator",
            contract_type="CDD",
            entry_date=date(2023, 1, 1),
            current_status="active",
        )

        # Soft delete emp1 and emp3
        emp1.soft_delete(reason="Test deletion 1")
        emp3.soft_delete(reason="Test deletion 2")

        # Get deleted employees
        deleted_employees = list(Employee.deleted())

        # Should return emp1 and emp3, not emp2
        assert len(deleted_employees) == 2
        assert emp1 in deleted_employees
        assert emp3 in deleted_employees
        assert emp2 not in deleted_employees

    def test_soft_delete_does_not_affect_other_fields(self, db_connection, sample_employee):
        """Test that soft delete doesn't modify other fields."""
        # Store original values
        original_first_name = sample_employee.first_name
        original_email = sample_employee.email
        original_role = sample_employee.role

        # Soft delete
        sample_employee.soft_delete(reason="Test deletion")

        # Reload from database
        employee = Employee.get_by_id(sample_employee.id)

        # Verify other fields are unchanged
        assert employee.first_name == original_first_name
        assert employee.email == original_email
        assert employee.role == original_role


class TestCacesSoftDelete:
    """Tests for CACES soft delete."""

    def test_soft_delete_caces(self, db_connection, sample_caces):
        """Test soft deleting a CACES certification."""
        # Verify CACES is not deleted
        assert sample_caces.is_deleted is False
        assert sample_caces.deleted_at is None

        # Soft delete
        sample_caces.soft_delete(reason="Test deletion", deleted_by="admin")

        # Reload from database
        caces = Caces.get_by_id(sample_caces.id)

        # Verify soft delete fields are set
        assert caces.is_deleted is True
        assert caces.deleted_at is not None
        assert caces.deletion_reason == "Test deletion"
        assert caces.deleted_by == "admin"

    def test_restore_caces(self, db_connection, sample_caces):
        """Test restoring a soft deleted CACES certification."""
        # Soft delete first
        sample_caces.soft_delete(reason="Test deletion")

        # Restore
        sample_caces.restore()

        # Reload from database
        caces = Caces.get_by_id(sample_caces.id)

        # Verify CACES is restored
        assert caces.is_deleted is False
        assert caces.deleted_at is None
        assert caces.deletion_reason is None
        assert caces.deleted_by is None

    def test_without_deleted_caces(self, db_connection, sample_employee):
        """Test getting only non-deleted CACES certifications."""
        # Create 3 CACES certifications
        caces1 = Caces.create(
            employee=sample_employee,
            kind="R489-1A",
            completion_date=date(2023, 1, 1),
            expiration_date=date(2024, 1, 1),
        )
        caces2 = Caces.create(
            employee=sample_employee,
            kind="R489-1B",
            completion_date=date(2023, 1, 1),
            expiration_date=date(2024, 1, 1),
        )
        caces3 = Caces.create(
            employee=sample_employee,
            kind="R489-3",
            completion_date=date(2023, 1, 1),
            expiration_date=date(2024, 1, 1),
        )

        # Soft delete caces2
        caces2.soft_delete(reason="Test deletion")

        # Get non-deleted CACES
        active_caces = list(Caces.without_deleted())

        # Should return caces1 and caces3, not caces2
        assert len(active_caces) == 2
        assert caces1 in active_caces
        assert caces3 in active_caces
        assert caces2 not in active_caces


class TestMedicalVisitSoftDelete:
    """Tests for MedicalVisit soft delete."""

    def test_soft_delete_medical_visit(self, db_connection, sample_medical_visit):
        """Test soft deleting a medical visit."""
        # Verify visit is not deleted
        assert sample_medical_visit.is_deleted is False
        assert sample_medical_visit.deleted_at is None

        # Soft delete
        sample_medical_visit.soft_delete(reason="Test deletion", deleted_by="admin")

        # Reload from database
        visit = MedicalVisit.get_by_id(sample_medical_visit.id)

        # Verify soft delete fields are set
        assert visit.is_deleted is True
        assert visit.deleted_at is not None
        assert visit.deletion_reason == "Test deletion"
        assert visit.deleted_by == "admin"

    def test_restore_medical_visit(self, db_connection, sample_medical_visit):
        """Test restoring a soft deleted medical visit."""
        # Soft delete first
        sample_medical_visit.soft_delete(reason="Test deletion")

        # Restore
        sample_medical_visit.restore()

        # Reload from database
        visit = MedicalVisit.get_by_id(sample_medical_visit.id)

        # Verify visit is restored
        assert visit.is_deleted is False
        assert visit.deleted_at is None
        assert visit.deletion_reason is None
        assert visit.deleted_by is None

    def test_without_deleted_medical_visits(self, db_connection, sample_employee):
        """Test getting only non-deleted medical visits."""
        # Create 3 medical visits
        visit1 = MedicalVisit.create(
            employee=sample_employee,
            visit_type="periodic",
            visit_date=date(2023, 1, 1),
            expiration_date=date(2024, 1, 1),
            result="fit",
        )
        visit2 = MedicalVisit.create(
            employee=sample_employee,
            visit_type="recovery",
            visit_date=date(2023, 2, 1),
            expiration_date=date(2024, 2, 1),
            result="fit_with_restrictions",
        )
        visit3 = MedicalVisit.create(
            employee=sample_employee,
            visit_type="periodic",
            visit_date=date(2023, 3, 1),
            expiration_date=date(2024, 3, 1),
            result="fit",
        )

        # Soft delete visit2
        visit2.soft_delete(reason="Test deletion")

        # Get non-deleted visits
        active_visits = list(MedicalVisit.without_deleted())

        # Should return visit1 and visit3, not visit2
        assert len(active_visits) == 2
        assert visit1 in active_visits
        assert visit3 in active_visits
        assert visit2 not in active_visits


class TestOnlineTrainingSoftDelete:
    """Tests for OnlineTraining soft delete."""

    def test_soft_delete_online_training(self, db_connection, sample_training):
        """Test soft deleting an online training."""
        # Verify training is not deleted
        assert sample_training.is_deleted is False
        assert sample_training.deleted_at is None

        # Soft delete
        sample_training.soft_delete(reason="Test deletion", deleted_by="admin")

        # Reload from database
        training = OnlineTraining.get_by_id(sample_training.id)

        # Verify soft delete fields are set
        assert training.is_deleted is True
        assert training.deleted_at is not None
        assert training.deletion_reason == "Test deletion"
        assert training.deleted_by == "admin"

    def test_restore_online_training(self, db_connection, sample_training):
        """Test restoring a soft deleted online training."""
        # Soft delete first
        sample_training.soft_delete(reason="Test deletion")

        # Restore
        sample_training.restore()

        # Reload from database
        training = OnlineTraining.get_by_id(sample_training.id)

        # Verify training is restored
        assert training.is_deleted is False
        assert training.deleted_at is None
        assert training.deletion_reason is None
        assert training.deleted_by is None

    def test_without_deleted_online_trainings(self, db_connection, sample_employee):
        """Test getting only non-deleted online trainings."""
        # Create 3 online trainings
        training1 = OnlineTraining.create(
            employee=sample_employee,
            title="Safety Training",
            completion_date=date(2023, 1, 1),
            expiration_date=date(2024, 1, 1),
            validity_months=12,
        )
        training2 = OnlineTraining.create(
            employee=sample_employee,
            title="Fire Safety",
            completion_date=date(2023, 2, 1),
            expiration_date=date(2024, 2, 1),
            validity_months=12,
        )
        training3 = OnlineTraining.create(
            employee=sample_employee,
            title="First Aid",
            completion_date=date(2023, 3, 1),
            expiration_date=date(2024, 3, 1),
            validity_months=12,
        )

        # Soft delete training2
        training2.soft_delete(reason="Test deletion")

        # Get non-deleted trainings
        active_trainings = list(OnlineTraining.without_deleted())

        # Should return training1 and training3, not training2
        assert len(active_trainings) == 2
        assert training1 in active_trainings
        assert training3 in active_trainings
        assert training2 not in active_trainings
