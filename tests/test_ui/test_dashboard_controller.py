"""Tests for DashboardController."""

import pytest
from datetime import date, timedelta

from employee.models import Employee, Caces, MedicalVisit
from ui.controllers.dashboard_controller import DashboardController


class TestDashboardController:
    """Tests for DashboardController business logic."""

    def test_get_statistics(self, db):
        """Should return dashboard statistics."""
        # Create active employee
        employee = Employee.create(
            first_name='John',
            last_name='Doe',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expiring CACES
        expiration_date = date.today() + timedelta(days=15)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Get statistics
        controller = DashboardController()
        stats = controller.get_statistics()

        # Verify statistics
        assert stats['total_employees'] >= 1
        assert stats['active_employees'] >= 1
        assert stats['expiring_caces'] >= 1
        assert isinstance(stats['expiring_visits'], int)
        assert isinstance(stats['unfit_employees'], int)

    def test_get_compliance_percentage(self, db):
        """Should calculate global compliance percentage."""
        # Create employee with high compliance
        employee = Employee.create(
            first_name='Jane',
            last_name='Smith',
            current_status='active',
            workspace='Bureau',
            role='Manager',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create valid CACES
        expiration_date = date.today() + timedelta(days=300)
        caces = Caces.create(
            employee=employee,
            kind='R489-1B',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Get compliance percentage
        controller = DashboardController()
        percentage = controller.get_compliance_percentage()

        # Should be a percentage between 0 and 100
        assert 0 <= percentage <= 100
        assert isinstance(percentage, int)

    def test_get_total_alerts_count(self, db):
        """Should return total number of alerts."""
        controller = DashboardController()
        total = controller.get_total_alerts_count(days=30)

        # Should be a non-negative integer
        assert total >= 0
        assert isinstance(total, int)

    def test_format_alerts_for_ui(self, db):
        """Should format alerts correctly for UI display."""
        # Create employee with expiring items
        employee = Employee.create(
            first_name='Bob',
            last_name='Johnson',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDD',
            entry_date=date(2020, 1, 1)
        )

        # Create expiring CACES
        expiration_date = date.today() + timedelta(days=10)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Get formatted alerts
        controller = DashboardController()
        alerts = controller.format_alerts_for_ui(days=30, limit=10)

        # Should have at least one alert
        assert len(alerts) >= 1

        # Check alert structure
        alert = alerts[0]
        assert 'employee_id' in alert
        assert 'employee_name' in alert
        assert 'type' in alert
        assert 'description' in alert
        assert 'days_until' in alert
        assert 'priority' in alert

        # Check priority levels
        assert alert['priority'] in ['urgent', 'high', 'normal']

    def test_get_alerts_grouped_by_employee(self, db):
        """Should return alerts grouped by employee."""
        # Create employees
        emp1 = Employee.create(
            first_name='Alice',
            last_name='Williams',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expiring items for emp1
        expiration_date = date.today() + timedelta(days=20)
        caces = Caces.create(
            employee=emp1,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Get alerts grouped by employee
        controller = DashboardController()
        alerts = controller.get_alerts(days=30)

        # Check structure
        if alerts:  # Only check if we have alerts
            emp_id = list(alerts.keys())[0]
            assert 'employee' in alerts[emp_id]
            assert 'caces' in alerts[emp_id]
            assert 'medical_visits' in alerts[emp_id]
            assert 'trainings' in alerts[emp_id]

    def test_priority_level_calculation(self, db):
        """Should calculate priority levels correctly."""
        controller = DashboardController()

        # Test urgent priority (< 15 days)
        assert controller._get_priority_level(5) == 'urgent'
        assert controller._get_priority_level(-5) == 'urgent'  # Expired

        # Test high priority (< 30 days)
        assert controller._get_priority_level(20) == 'high'

        # Test normal priority (>= 30 days)
        assert controller._get_priority_level(45) == 'normal'
        assert controller._get_priority_level(90) == 'normal'
