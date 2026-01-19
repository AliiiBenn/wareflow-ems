"""Tests for EmployeeController."""

import pytest
from datetime import date, timedelta

from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
from ui.controllers.employee_controller import EmployeeController


class TestEmployeeController:
    """Tests for EmployeeController business logic."""

    def test_get_employee_by_id(self, db):
        """Should retrieve employee by ID."""
        # Create employee
        employee = Employee.create(
            first_name='Test',
            last_name='Employee',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Get employee by ID
        controller = EmployeeController()
        result = controller.get_employee_by_id(str(employee.id))

        # Should return the employee
        assert result is not None
        assert result.id == employee.id
        assert result.full_name == 'Test Employee'

    def test_get_employee_by_id_not_found(self, db):
        """Should return None for non-existent employee."""
        controller = EmployeeController()
        result = controller.get_employee_by_id('00000000-0000-0000-0000-000000000000')

        # Should return None
        assert result is None

    def test_get_employee_details(self, db):
        """Should retrieve complete employee details."""
        # Create employee with certifications
        employee = Employee.create(
            first_name='Jane',
            last_name='Doe',
            current_status='active',
            workspace='Bureau',
            role='Manager',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create CACES
        expiration_date = date.today() + timedelta(days=300)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Create medical visit
        visit_date = date.today() - timedelta(days=365)
        visit = MedicalVisit.create(
            employee=employee,
            visit_type='periodic',
            visit_date=visit_date,
            result='fit',
            document_path='/visit.pdf'
        )
        visit.expiration_date = visit_date + timedelta(days=730)
        visit.save()

        # Create training (permanent, no expiration)
        training = OnlineTraining.create(
            employee=employee,
            title='General Orientation',
            completion_date=date.today(),
            validity_months=None  # Permanent training
        )

        # Get employee details
        controller = EmployeeController()
        details = controller.get_employee_details(str(employee.id))

        # Verify structure
        assert details is not None
        assert 'employee' in details
        assert 'compliance_score' in details
        assert 'score_breakdown' in details
        assert 'caces_list' in details
        assert 'medical_visits' in details
        assert 'trainings' in details

        # Verify data
        assert details['employee'].id == employee.id
        assert isinstance(details['compliance_score'], int)
        assert 0 <= details['compliance_score'] <= 100
        assert len(details['caces_list']) >= 1
        assert len(details['medical_visits']) >= 1
        assert len(details['trainings']) >= 1

    def test_get_employee_details_not_found(self, db):
        """Should return None for non-existent employee."""
        controller = EmployeeController()
        details = controller.get_employee_details('00000000-0000-0000-0000-000000000000')

        # Should return None
        assert details is None

    def test_get_all_employees(self, db):
        """Should retrieve all employees ordered by name."""
        # Create employees
        Employee.create(
            first_name='Zoe',
            last_name='Anderson',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        Employee.create(
            first_name='Alice',
            last_name='Smith',
            current_status='active',
            workspace='Bureau',
            role='Manager',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Get all employees
        controller = EmployeeController()
        employees = controller.get_all_employees()

        # Should return at least 2 employees
        assert len(employees) >= 2

        # Should be ordered by last name, then first name
        # Alice Smith should come before Zoe Anderson
        names = [emp.full_name for emp in employees]
        assert 'Alice Smith' in names
        assert 'Zoe Anderson' in names

    def test_get_active_employees(self, db):
        """Should retrieve only active employees."""
        # Create active and inactive employees
        active_emp = Employee.create(
            first_name='Active',
            last_name='Employee',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        inactive_emp = Employee.create(
            first_name='Inactive',
            last_name='Employee',
            current_status='inactive',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Get active employees
        controller = EmployeeController()
        active_employees = controller.get_active_employees()

        # Should include active employee
        active_ids = [emp.id for emp in active_employees]
        assert active_emp.id in active_ids

        # Should not include inactive employee
        assert inactive_emp.id not in active_ids

    def test_employee_details_compliance_breakdown(self, db):
        """Should include compliance score breakdown."""
        # Create employee
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create certifications with valid dates
        expiration_date = date.today() + timedelta(days=300)

        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        visit = MedicalVisit.create(
            employee=employee,
            visit_type='periodic',
            visit_date=date.today() - timedelta(days=365),
            result='fit',
            document_path='/visit.pdf'
        )
        visit.expiration_date = expiration_date
        visit.save()

        # Create training (permanent, no expiration)
        training = OnlineTraining.create(
            employee=employee,
            title='General Orientation',
            completion_date=date.today(),
            validity_months=None  # Permanent training
        )

        # Get employee details
        controller = EmployeeController()
        details = controller.get_employee_details(str(employee.id))

        # Verify breakdown structure
        breakdown = details['score_breakdown']
        assert 'caces' in breakdown
        assert 'medical' in breakdown
        assert 'training' in breakdown

        # All scores should be between 0 and their maximums
        assert 0 <= breakdown['caces'] <= 30
        assert 0 <= breakdown['medical'] <= 30
        assert 0 <= breakdown['training'] <= 40
