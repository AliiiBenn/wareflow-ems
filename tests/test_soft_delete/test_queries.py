"""Tests for query helpers with soft delete filtering."""

from datetime import date, timedelta
from uuid import uuid4

import pytest

from employee.models import Caces, Employee, MedicalVisit, OnlineTraining
from employee.queries import (
    get_dashboard_statistics,
    get_employees_with_expired_caces,
    get_employees_with_expired_medical_visits,
    get_employees_with_expiring_items,
    get_expiring_items_by_type,
    get_unfit_employees,
)


class TestQueriesFilterSoftDeleted:
    """Test that all query helpers properly filter soft-deleted records."""

    def test_get_employees_with_expiring_items_filters_soft_deleted(
        self, db_connection
    ):
        """Test that expiring items query filters soft-deleted employees."""
        # Create employee with expiring CACES
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
        Caces.create(
            employee=emp1,
            kind="R489-1A",
            completion_date=date(2023, 1, 1),
            expiration_date=date.today() + timedelta(days=15),  # Expiring in 15 days
        )

        # Create another employee with expiring CACES but soft-deleted
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
        caces2 = Caces.create(
            employee=emp2,
            kind="R489-1B",
            completion_date=date(2023, 1, 1),
            expiration_date=date.today() + timedelta(days=15),
        )
        # Soft delete the employee
        emp2.soft_delete(reason="Test deletion")

        # Get employees with expiring items
        employees = get_employees_with_expiring_items(days=30)

        # Should only return emp1, not emp2
        assert len(employees) == 1
        assert emp1.id in [e.id for e in employees]
        assert emp2.id not in [e.id for e in employees]

    def test_get_employees_with_expiring_items_filters_soft_deleted_caces(
        self, db_connection
    ):
        """Test that expiring items query filters soft-deleted CACES."""
        # Create employee with expiring CACES
        emp = Employee.create(
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
        Caces.create(
            employee=emp,
            kind="R489-1A",
            completion_date=date(2023, 1, 1),
            expiration_date=date.today() + timedelta(days=15),
        )
        # Create another expiring CACES but soft-delete it
        caces2 = Caces.create(
            employee=emp,
            kind="R489-1B",
            completion_date=date(2023, 1, 1),
            expiration_date=date.today() + timedelta(days=15),
        )
        caces2.soft_delete(reason="Test deletion")

        # Get employees with expiring items
        employees = get_employees_with_expiring_items(days=30)

        # Should return employee but only with non-deleted CACES
        assert len(employees) == 1
        # Employee should have only 1 CACES in the prefetched list (the soft-deleted one is filtered)
        assert len([c for c in employees[0].caces if not c.is_deleted]) == 1

    def test_get_employees_with_expired_caces_filters_soft_deleted(self, db_connection):
        """Test that expired CACES query filters soft-deleted records."""
        # Create employee with expired CACES
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
        Caces.create(
            employee=emp1,
            kind="R489-1A",
            completion_date=date(2022, 1, 1),
            expiration_date=date.today() - timedelta(days=30),  # Expired 30 days ago
        )

        # Create another employee with expired CACES but soft-deleted
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
        Caces.create(
            employee=emp2,
            kind="R489-1B",
            completion_date=date(2022, 1, 1),
            expiration_date=date.today() - timedelta(days=30),
        )
        emp2.soft_delete(reason="Test deletion")

        # Get employees with expired CACES
        employees = get_employees_with_expired_caces()

        # Should only return emp1, not emp2
        assert len(employees) == 1
        assert emp1.id in [e.id for e in employees]
        assert emp2.id not in [e.id for e in employees]

    def test_get_employees_with_expired_medical_visits_filters_soft_deleted(
        self, db_connection
    ):
        """Test that expired medical visits query filters soft-deleted records."""
        # Create employee with expired medical visit
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
        MedicalVisit.create(
            employee=emp1,
            visit_type="periodic",
            visit_date=date(2022, 1, 1),
            expiration_date=date.today() - timedelta(days=30),  # Expired
            result="fit",
        )

        # Create another employee with expired visit but soft-deleted
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
        MedicalVisit.create(
            employee=emp2,
            visit_type="periodic",
            visit_date=date(2022, 1, 1),
            expiration_date=date.today() - timedelta(days=30),
            result="fit",
        )
        emp2.soft_delete(reason="Test deletion")

        # Get employees with expired visits
        employees = get_employees_with_expired_medical_visits()

        # Should only return emp1, not emp2
        assert len(employees) == 1
        assert emp1.id in [e.id for e in employees]
        assert emp2.id not in [e.id for e in employees]

    def test_get_unfit_employees_filters_soft_deleted(self, db_connection):
        """Test that unfit employees query filters soft-deleted records."""
        # Create employee with unfit visit
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
        MedicalVisit.create(
            employee=emp1,
            visit_type="periodic",
            visit_date=date(2023, 6, 1),
            result="unfit",
        )

        # Create another employee with unfit visit but soft-deleted
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
        MedicalVisit.create(
            employee=emp2,
            visit_type="periodic",
            visit_date=date(2023, 6, 1),
            result="unfit",
        )
        emp2.soft_delete(reason="Test deletion")

        # Get unfit employees
        employees = get_unfit_employees()

        # Should only return emp1, not emp2
        assert len(employees) == 1
        assert emp1.id in [e.id for e in employees]
        assert emp2.id not in [e.id for e in employees]

    def test_get_dashboard_statistics_filters_soft_deleted(self, db_connection):
        """Test that dashboard statistics filter soft-deleted records."""
        # Create 5 employees
        for i in range(5):
            Employee.create(
                external_id=f"EMP00{i}",
                first_name=f"Employee{i}",
                last_name="Test",
                email=f"emp{i}@test.com",
                workspace="Zone A",
                role="Operator",
                contract_type="CDI",
                entry_date=date(2023, 1, 1),
                current_status="active",
            )

        # Soft delete 2 employees
        emp_to_delete = Employee.select()[:2]
        for emp in emp_to_delete:
            emp.soft_delete(reason="Test deletion")

        # Get statistics
        stats = get_dashboard_statistics()

        # Total employees should be 3 (not 5)
        assert stats["total_employees"] == 3

    def test_get_expiring_items_by_type_filters_soft_deleted(self, db_connection):
        """Test that expiring items by type query filters soft-deleted records."""
        # Create employee with expiring CACES
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
        Caces.create(
            employee=emp1,
            kind="R489-1A",
            completion_date=date(2023, 1, 1),
            expiration_date=date.today() + timedelta(days=15),
        )

        # Create another employee with expiring CACES but soft-deleted
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
        Caces.create(
            employee=emp2,
            kind="R489-1B",
            completion_date=date(2023, 1, 1),
            expiration_date=date.today() + timedelta(days=15),
        )
        emp2.soft_delete(reason="Test deletion")

        # Get expiring items by type
        items = get_expiring_items_by_type(days=30)

        # Should only include emp1, not emp2
        assert emp1.id in items
        assert emp2.id not in items

    def test_get_expiring_items_by_type_filters_soft_deleted_items(self, db_connection):
        """Test that expiring items by type query filters soft-deleted items."""
        # Create employee with expiring CACES
        emp = Employee.create(
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
        Caces.create(
            employee=emp,
            kind="R489-1A",
            completion_date=date(2023, 1, 1),
            expiration_date=date.today() + timedelta(days=15),
        )
        # Create another expiring CACES but soft-delete it
        caces2 = Caces.create(
            employee=emp,
            kind="R489-1B",
            completion_date=date(2023, 1, 1),
            expiration_date=date.today() + timedelta(days=15),
        )
        caces2.soft_delete(reason="Test deletion")

        # Get expiring items by type
        items = get_expiring_items_by_type(days=30)

        # Should have only 1 CACES for the employee
        assert emp.id in items
        assert len(items[emp.id]["caces"]) == 1
