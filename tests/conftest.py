"""Test configuration and shared fixtures."""

import pytest
from datetime import date, datetime, timedelta
from pathlib import Path
from peewee import SqliteDatabase

# Use in-memory SQLite for fast, isolated tests
test_db = SqliteDatabase(':memory:', pragmas={'foreign_keys': 1})


@pytest.fixture(scope='function')
def db():
    """Create a fresh database for each test."""
    # Import here to avoid circular imports
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

    from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
    from lock.models import AppLock

    # Bind models to test database BEFORE creating tables
    test_db.bind([Employee, Caces, MedicalVisit, OnlineTraining, AppLock])

    test_db.create_tables([
        Employee,
        Caces,
        MedicalVisit,
        OnlineTraining,
        AppLock,
    ], safe=True)

    yield test_db

    # Clean up after test
    test_db.drop_tables([
        Employee,
        Caces,
        MedicalVisit,
        OnlineTraining,
        AppLock,
    ])

    test_db.close()


@pytest.fixture
def sample_employee(db):
    """Create a sample employee for tests."""
    from employee.models import Employee

    employee = Employee.create(
        first_name='John',
        last_name='Doe',
        current_status='active',
        workspace='Quai',
        role='Préparateur',
        contract_type='CDI',
        entry_date=date(2020, 1, 15)
    )
    return employee


@pytest.fixture
def inactive_employee(db):
    """Create an inactive employee for tests."""
    from employee.models import Employee

    employee = Employee.create(
        first_name='Jane',
        last_name='Smith',
        current_status='inactive',
        workspace='Bureau',
        role='Réceptionnaire',
        contract_type='CDD',
        entry_date=date(2023, 6, 1)
    )
    return employee


@pytest.fixture
def sample_caces(db, sample_employee):
    """Create a sample CACES certification."""
    from employee.models import Caces

    caces = Caces.create(
        employee=sample_employee,
        kind='R489-1A',
        completion_date=date(2023, 1, 1),
        document_path='/documents/caces/test.pdf'
    )
    return caces


@pytest.fixture
def expired_caces(db, sample_employee):
    """Create an expired CACES certification."""
    from employee.models import Caces

    # Create CACES that expired in 2020
    caces = Caces.create(
        employee=sample_employee,
        kind='R489-1B',
        completion_date=date(2015, 1, 1),
        document_path='/documents/caces/expired.pdf'
    )
    return caces


@pytest.fixture
def medical_visit(db, sample_employee):
    """Create a sample medical visit."""
    from employee.models import MedicalVisit

    visit = MedicalVisit.create(
        employee=sample_employee,
        visit_type='periodic',
        visit_date=date(2023, 6, 15),
        result='fit',
        document_path='/documents/medical/test.pdf'
    )
    return visit


@pytest.fixture
def unfit_visit(db, sample_employee):
    """Create an unfit medical visit."""
    from employee.models import MedicalVisit

    visit = MedicalVisit.create(
        employee=sample_employee,
        visit_type='recovery',
        visit_date=date(2023, 1, 1),
        result='unfit',
        document_path='/documents/medical/unfit.pdf'
    )
    return visit


@pytest.fixture
def online_training(db, sample_employee):
    """Create a sample online training."""
    from employee.models import OnlineTraining

    training = OnlineTraining.create(
        employee=sample_employee,
        title='Safety Training',
        completion_date=date(2023, 3, 1),
        validity_months=12,
        certificate_path='/documents/training/test.pdf'
    )
    return training


@pytest.fixture
def permanent_training(db, sample_employee):
    """Create a permanent (non-expiring) training."""
    from employee.models import OnlineTraining

    training = OnlineTraining.create(
        employee=sample_employee,
        title='General Orientation',
        completion_date=date(2023, 1, 1),
        validity_months=None  # Permanent
    )
    return training


