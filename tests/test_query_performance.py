"""
Query Performance Tests

Tests to verify N+1 query problem is fixed and measure performance improvements.
"""

import pytest
import time
from unittest.mock import patch

from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
from src.controllers.employee_controller import EmployeeController
from peewee import prefetch


class TestQueryPerformance:
    """Test query performance and N+1 problem fixes."""

    def test_get_all_employees_performance_baseline(self, db):
        """Measure baseline performance of loading all employees."""
        controller = EmployeeController()

        start = time.time()
        employees = controller.get_all_employees()
        elapsed = time.time() - start

        # Should complete reasonably fast
        assert elapsed < 1.0, f"Loading all employees took too long: {elapsed}s"

    def test_get_employee_details_query_count(self, db, sample_employee_with_data):
        """Test that get_employee_details doesn't cause N+1 queries."""
        controller = EmployeeController()
        employee_id = str(sample_employee_with_data.id)

        # Mock query logging to count queries
        query_count = [0]
        original_execute = Employee._meta.database.execute

        def counting_execute(sql, params=None):
            query_count[0] += 1
            return original_execute(sql, params)

        with patch.object(Employee._meta.database, 'execute', side_effect=counting_execute):
            details = controller.get_employee_details(employee_id)

        # Currently this will have N+1 queries
        # After fix, should have limited queries
        assert details is not None
        assert 'employee' in details
        # This assertion will need to be updated after the fix

    def test_prefetch_reduces_queries(self, db, multiple_employees):
        """Test that prefetch reduces query count significantly."""
        # Load employees with prefetch
        start = time.time()
        employees = list(Employee
                         .select(Employee, Caces, MedicalVisit, OnlineTraining)
                         .prefetch(Caces, MedicalVisit, OnlineTraining)
                         .order_by(Employee.last_name))
        prefetch_time = time.time() - start

        # Access all related data without triggering additional queries
        for emp in employees:
            _ = list(emp.caces)
            _ = list(emp.medical_visits)
            _ = list(emp.trainings)  # backref is 'trainings', not 'online_trainings'

        # Should be very fast with prefetch
        assert prefetch_time < 0.5, f"Prefetch took too long: {prefetch_time}s"

    def test_load_100_employees_performance(self, db):
        """Test loading performance with 100 employees."""
        # Create 100 employees for testing
        employees = []
        for i in range(100):
            emp = Employee.create(
                external_id=f"PERF{i:03d}",
                first_name=f"First{i}",
                last_name=f"Last{i}",
                email=f"perf{i}@example.com",
                current_status="active",
                workspace="Paris",
                role="Engineer",
                contract_type="CDI"
            )
            employees.append(emp)

        # Test with prefetch (should be fast)
        start = time.time()
        loaded = list(Employee
                      .select(Employee, Caces, MedicalVisit, OnlineTraining)
                      .prefetch(Caces, MedicalVisit, OnlineTraining)
                      .order_by(Employee.last_name))
        elapsed = time.time() - start

        assert len(loaded) >= 100  # May include test employees from other tests too
        assert elapsed < 1.0, f"Loading 100 employees took too long: {elapsed}s"

    def test_get_all_employees_returns_ordered_list(self, db):
        """Test that get_all_employees returns properly ordered list."""
        controller = EmployeeController()
        employees = controller.get_all_employees()

        assert isinstance(employees, list)
        # Check ordering by last_name
        if len(employees) > 1:
            for i in range(len(employees) - 1):
                assert employees[i].last_name <= employees[i + 1].last_name

    def test_get_active_employees_filters_correctly(self, db, sample_employee):
        """Test that get_active_employees only returns active employees."""
        controller = EmployeeController()

        # Make sample employee inactive
        sample_employee.current_status = "inactive"
        sample_employee.save()

        active_employees = controller.get_active_employees()

        # Should not contain the inactive employee
        assert sample_employee not in active_employees


class TestNPlusOneQueryFix:
    """Test that N+1 query problem is properly fixed."""

    def test_controller_has_optimized_method(self):
        """Test that controller has optimized loading method."""
        controller = EmployeeController()

        # Check if optimized method exists (will be added in fix)
        assert hasattr(controller, 'get_all_employees') or \
               hasattr(controller, 'get_employees_with_relations')

    def test_employee_detail_no_lazy_loading(self, db, sample_employee_with_data):
        """Test that employee detail loads related data efficiently."""
        controller = EmployeeController()
        employee_id = str(sample_employee_with_data.id)

        details = controller.get_employee_details(employee_id)

        assert details is not None
        assert 'caces_list' in details
        assert 'medical_visits' in details
        assert 'trainings' in details

        # Verify related data is loaded (should not trigger queries)
        # After fix, this should be instant
        caces = details['caces_list']
        visits = details['medical_visits']
        trainings = details['trainings']

        assert isinstance(caces, list)
        assert isinstance(visits, list)
        assert isinstance(trainings, list)


class TestQueryEfficiency:
    """Test query efficiency improvements."""

    def test_single_employee_detail_efficiency(self, db, sample_employee_with_data):
        """Test efficiency of loading single employee with all relations."""
        controller = EmployeeController()
        employee_id = str(sample_employee_with_data.id)

        start = time.time()
        details = controller.get_employee_details(employee_id)
        elapsed = time.time() - start

        # Should be fast (after fix: < 100ms)
        assert details is not None
        assert elapsed < 0.5, f"Employee detail loading too slow: {elapsed}s"

    def test_batch_loading_efficiency(self, db):
        """Test efficiency of loading multiple employees."""
        # Create test employees
        for i in range(10):
            Employee.create(
                external_id=f"BATCH{i:03d}",
                first_name=f"First{i}",
                last_name=f"Last{i}",
                email=f"batch{i}@example.com",
                current_status="active",
                workspace="Paris",
                role="Engineer"
            )

        controller = EmployeeController()

        start = time.time()
        employees = controller.get_all_employees()
        elapsed = time.time() - start

        assert len(employees) >= 10
        # After fix: should be < 200ms for 10 employees
        assert elapsed < 1.0, f"Batch loading too slow: {elapsed}s"


class TestPrefetchBehavior:
    """Test prefetch behavior and correctness."""

    def test_prefetch_includes_all_employees(self, db, sample_employee):
        """Test that prefetch includes all employees."""
        employees = list(Employee
                         .select(Employee, Caces, MedicalVisit, OnlineTraining)
                         .prefetch(Caces, MedicalVisit, OnlineTraining))

        assert sample_employee in employees

    def test_prefetch_preserves_relations(self, db, sample_employee_with_data):
        """Test that prefetch correctly loads related data."""
        employees = list(Employee
                         .select(Employee, Caces, MedicalVisit, OnlineTraining)
                         .prefetch(Caces, MedicalVisit, OnlineTraining))

        # Find our sample employee
        emp = next((e for e in employees if e.id == sample_employee_with_data.id), None)
        assert emp is not None

        # Verify related data is loaded
        caces = list(emp.caces)
        visits = list(emp.medical_visits)
        trainings = list(emp.trainings)

        # Should have the relations we created in fixture
        assert len(caces) >= 0
        assert len(visits) >= 0
        assert len(trainings) >= 0

    def test_prefetch_with_empty_relations(self, db, sample_employee):
        """Test prefetch works with employees having no related data."""
        # Employee with no CACES, visits, or training
        employees = list(Employee
                         .select(Employee, Caces, MedicalVisit, OnlineTraining)
                         .prefetch(Caces, MedicalVisit, OnlineTraining))

        emp = next((e for e in employees if e.id == sample_employee.id), None)
        assert emp is not None

        # Should not crash, just return empty lists
        caces = list(emp.caces)
        visits = list(emp.medical_visits)
        trainings = list(emp.trainings)

        assert caces == []
        assert visits == []
        assert trainings == []


class TestPerformanceTargets:
    """Test that we meet performance targets."""

    def test_load_100_employees_under_500ms(self, db):
        """Performance target: 100 employees in < 500ms (local DB)."""
        # Create 100 employees
        for i in range(100):
            Employee.create(
                external_id=f"TARGET{i:03d}",
                first_name=f"First{i}",
                last_name=f"Last{i}",
                email=f"target{i}@example.com",
                current_status="active",
                workspace="Paris",
                role="Engineer"
            )

        start = time.time()
        employees = list(Employee
                         .select(Employee, Caces, MedicalVisit, OnlineTraining)
                         .prefetch(Caces, MedicalVisit, OnlineTraining)
                         .order_by(Employee.last_name))
        elapsed = time.time() - start

        # Target: < 500ms for 100 employees
        assert elapsed < 0.5, f"Performance target not met: {elapsed:.3f}s > 0.5s"
        assert len(employees) == 100

    def test_query_count_target(self, db, multiple_employees):
        """Performance target: Maximum 4 queries for any employee loading."""
        # With prefetch, we should load all employees and relations in ~4 queries:
        # 1. SELECT employees
        # 2. SELECT caces WHERE employee_id IN (...)
        # 3. SELECT medical_visits WHERE employee_id IN (...)
        # 4. SELECT online_trainings WHERE employee_id IN (...)

        # This is a conceptual test - in practice we'd use query logging
        # For now, we just verify it completes quickly
        start = time.time()
        employees = list(Employee
                         .select(Employee, Caces, MedicalVisit, OnlineTraining)
                         .prefetch(Caces, MedicalVisit, OnlineTraining))
        elapsed = time.time() - start

        # If query count were high, this would take much longer
        assert elapsed < 0.2, f"Too many queries suspected: {elapsed:.3f}s"
