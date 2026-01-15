# Model Testing Strategy

This document details the comprehensive testing strategy for all Peewee ORM models in the Warehouse Employee Management System.

## Overview

Testing strategy:
- **Unit tests**: Test individual model methods, properties, and validations
- **Integration tests**: Test model relationships, CASCADE delete, queries
- **Database tests**: Use in-memory SQLite for fast, isolated tests
- **Fixtures**: Reusable test data with pytest fixtures
- **Coverage**: Aim for >90% code coverage on models

## Test Stack

- **pytest**: Test runner and assertions
- **pytest-cov**: Coverage reporting
- **pytest fixtures**: Test data setup
- **peewee**: Models under test
- **freezegun**: Mock time for date-dependent tests

## 1. Test Configuration

### File: `tests/conftest.py`

```python
"""Test configuration and shared fixtures."""

import pytest
from datetime import date, datetime
from pathlib import Path
from peewee import SqliteDatabase

# Use in-memory SQLite for fast, isolated tests
test_db = SqliteDatabase(':memory:', pragmas={'foreign_keys': 1})


@pytest.fixture(scope='function')
def db():
    """Create a fresh database for each test."""
    from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
    from lock.models import AppLock

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

    caces = Caces.create(
        employee=sample_employee,
        kind='R489-1B',
        completion_date=date(2015, 1, 1),  # Expired 5 years later
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


# Monkey-patch the database used by models
@pytest.fixture(autouse=True)
def use_test_db(db, monkeypatch):
    """Automatically use test database for all models."""
    from employee import models as employee_models
    from lock import models as lock_models

    # Replace database with test database
    employee_models.database = db
    lock_models.database = db

    # Re-bind models to test database
    from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
    from lock.models import AppLock

    Employee._meta.database = db
    Caces._meta.database = db
    MedicalVisit._meta.database = db
    OnlineTraining._meta.database = db
    AppLock._meta.database = db
```

---

## 2. Employee Model Tests

### File: `tests/test_employee/test_models.py`

### Test Categories

#### A. Model Creation and Basic Fields

```python
def test_create_employee_minimal(db):
    """Test creating an employee with minimal required fields."""
    from employee.models import Employee

    employee = Employee.create(
        first_name='Alice',
        last_name='Martin',
        current_status='active',
        workspace='Quai',
        role='Cariste',
        contract_type='CDI',
        entry_date=date.today()
    )

    assert employee.id is not None
    assert employee.first_name == 'Alice'
    assert employee.last_name == 'Martin'
    assert employee.current_status == 'active'
    assert employee.workspace == 'Quai'
    assert employee.role == 'Cariste'
    assert employee.contract_type == 'CDI'
    assert employee.entry_date == date.today()
    assert employee.created_at is not None
    assert employee.updated_at is not None


def test_create_employee_with_optional_fields(db):
    """Test creating an employee with optional fields."""
    from employee.models import Employee

    employee = Employee.create(
        first_name='Bob',
        last_name='Dubois',
        current_status='active',
        workspace='Zone A',
        role='Préparateur',
        contract_type='CDD',
        entry_date=date(2023, 1, 1),
        external_id='WMS-12345',
        avatar_path='/avatars/bob.jpg'
    )

    assert employee.external_id == 'WMS-12345'
    assert employee.avatar_path == '/avatars/bob.jpg'


def test_external_id_must_be_unique(db):
    """Test that external_id uniqueness is enforced."""
    from employee.models import Employee
    from peewee import IntegrityError

    Employee.create(
        first_name='John',
        last_name='Doe',
        current_status='active',
        workspace='Quai',
        role='Cariste',
        contract_type='CDI',
        entry_date=date.today(),
        external_id='UNIQUE-123'
    )

    # Try to create another employee with same external_id
    with pytest.raises(IntegrityError):
        Employee.create(
            first_name='Jane',
            last_name='Smith',
            current_status='active',
            workspace='Bureau',
            role='Réceptionnaire',
            contract_type='CDI',
            entry_date=date.today(),
            external_id='UNIQUE-123'  # Duplicate!
        )
```

#### B. Computed Properties

```python
def test_full_name_property(sample_employee):
    """Test the full_name computed property."""
    assert sample_employee.full_name == 'John Doe'


def test_seniority_property(sample_employee, db):
    """Test the seniority computed property."""
    # Employee started on 2020-01-15
    # If current year is 2024, seniority should be ~4 years
    assert sample_employee.seniority >= 4


def test_is_active_property(sample_employee):
    """Test the is_active computed property."""
    assert sample_employee.is_active is True

    sample_employee.current_status = 'inactive'
    assert sample_employee.is_active is False
```

#### C. Class Methods (Queries)

```python
def test_active_query(sample_employee, inactive_employee, db):
    """Test getting only active employees."""
    from employee.models import Employee

    active_employees = list(Employee.active())

    assert len(active_employees) == 1
    assert active_employees[0].id == sample_employee.id
    assert active_employees[0].current_status == 'active'


def test_inactive_query(sample_employee, inactive_employee, db):
    """Test getting only inactive employees."""
    from employee.models import Employee

    inactive_employees = list(Employee.inactive())

    assert len(inactive_employees) == 1
    assert inactive_employees[0].id == inactive_employee.id


def test_by_workspace_query(sample_employee, inactive_employee, db):
    """Test filtering by workspace."""
    from employee.models import Employee

    # Both employees in 'Quai'
    quai_employees = list(Employee.by_workspace('Quai'))
    assert len(quai_employees) == 2

    # One employee in 'Bureau'
    bureau_employees = list(Employee.by_workspace('Bureau'))
    assert len(bureau_employees) == 1
    assert bureau_employees[0].workspace == 'Bureau'


def test_by_role_query(sample_employee, inactive_employee, db):
    """Test filtering by role."""
    from employee.models import Employee

    preparateurs = list(Employee.by_role('Préparateur'))
    assert len(preparateurs) == 1
    assert preparateurs[0].role == 'Préparateur'
```

#### D. Instance Methods

```python
def test_add_caces_to_employee(sample_employee, db):
    """Test adding a CACES certification to an employee."""
    from employee.models import Caces

    caces = sample_employee.add_caces(
        kind='R489-3',
        completion_date=date(2023, 6, 1),
        document_path='/documents/caces/r489-3.pdf'
    )

    assert caces.employee.id == sample_employee.id
    assert caces.kind == 'R489-3'

    # Verify back-reference works
    assert sample_employee.caces[0].id == caces.id


def test_add_medical_visit_to_employee(sample_employee, db):
    """Test adding a medical visit to an employee."""
    from employee.models import MedicalVisit

    visit = sample_employee.add_medical_visit(
        visit_type='initial',
        visit_date=date(2023, 1, 10),
        result='fit',
        document_path='/documents/medical/initial.pdf'
    )

    assert visit.employee.id == sample_employee.id
    assert visit.visit_type == 'initial'

    # Verify back-reference works
    assert sample_employee.medical_visits[0].id == visit.id


def test_add_training_to_employee(sample_employee, db):
    """Test adding online training to an employee."""
    from employee.models import OnlineTraining

    training = sample_employee.add_training(
        title='Fire Safety',
        completion_date=date(2023, 5, 1),
        validity_months=24,
        certificate_path='/documents/training/fire.pdf'
    )

    assert training.employee.id == sample_employee.id
    assert training.title == 'Fire Safety'

    # Verify back-reference works
    assert sample_employee.trainings[0].id == training.id
```

#### E. Validation Hooks

```python
def test_entry_date_cannot_be_in_future(db):
    """Test that entry_date cannot be in the future."""
    from employee.models import Employee

    future_date = date.today() + timedelta(days=30)

    with pytest.raises(ValueError, match="Entry date cannot be in the future"):
        employee = Employee(
            first_name='Future',
            last_name='Employee',
            current_status='active',
            workspace='Quai',
            role='Cariste',
            contract_type='CDI',
            entry_date=future_date
        )
        employee.save()  # Triggers before_save()


def test_updated_at_auto_updates(sample_employee, db):
    """Test that updated_at is automatically updated on save."""
    from employee.models import Employee

    original_updated_at = sample_employee.updated_at

    # Wait a tiny bit to ensure timestamp difference
    import time
    time.sleep(0.01)

    sample_employee.workspace = 'Zone B'
    sample_employee.save()

    assert sample_employee.updated_at > original_updated_at
```

---

## 3. Caces Model Tests

### File: `tests/test_employee/test_models.py` (continuing)

### Test Categories

#### A. Model Creation and Expiration Calculation

```python
def test_caces_auto_calculates_expiration_r489_1a(sample_caces, db):
    """Test that R489-1A automatically calculates 5-year expiration."""
    # Created on 2023-01-01, should expire on 2028-01-01
    assert sample_caces.expiration_date == date(2028, 1, 1)


def test_caces_auto_calculates_expiration_other_types(db, sample_employee):
    """Test that other CACES types get 10-year expiration."""
    from employee.models import Caces

    caces = Caces.create(
        employee=sample_employee,
        kind='R489-5',  # 10 year validity
        completion_date=date(2023, 1, 1),
        document_path='/documents/caces/r489-5.pdf'
    )

    assert caces.expiration_date == date(2033, 1, 1)


def test_caces_expiration_handles_leap_years(db, sample_employee):
    """Test that expiration calculation handles leap years correctly."""
    from employee.models import Caces

    # Feb 29, 2020 is a leap year
    caces = Caces.create(
        employee=sample_employee,
        kind='R489-1A',
        completion_date=date(2020, 2, 29),  # Leap year!
        document_path='/documents/caces/leap.pdf'
    )

    # 5 years later should be Feb 28, 2025 (not a leap year)
    assert caces.expiration_date == date(2025, 2, 28)


def test_caces_can_override_expiration(db, sample_employee):
    """Test that expiration_date can be manually set."""
    from employee.models import Caces

    custom_expiration = date(2030, 12, 31)
    caces = Caces.create(
        employee=sample_employee,
        kind='R489-1A',
        completion_date=date(2023, 1, 1),
        expiration_date=custom_expiration,  # Manual override
        document_path='/documents/caces/custom.pdf'
    )

    assert caces.expiration_date == custom_expiration
```

#### B. Computed Properties

```python
def test_caces_is_expired_property(expired_caces):
    """Test the is_expired property for expired certification."""
    assert expired_caces.is_expired is True


def test_caces_is_not_expired(sample_caces):
    """Test the is_expired property for valid certification."""
    assert sample_caces.is_expired is False


def test_caces_days_until_expiration(sample_caces):
    """Test the days_until_expiration property."""
    # Created 2023-01-01, expires 2028-01-01
    # Should be roughly 5 years * 365 days
    days = sample_caces.days_until_expiration
    assert 1800 <= days <= 1826  # Allow for leap years


def test_caces_days_until_expiration_negative_when_expired(expired_caces):
    """Test that days_until_expiration is negative when expired."""
    assert expired_caces.days_until_expiration < 0


def test_caces_status_valid(sample_caces):
    """Test status property returns 'valid' for valid CACES."""
    assert sample_caces.status == 'valid'


def test_caces_status_expired(expired_caces):
    """Test status property returns 'expired' for expired CACES."""
    assert expired_caces.status == 'expired'


def test_caces_status_critical(db, sample_employee):
    """Test status property returns 'critical' for soon-to-expire."""
    from employee.models import Caces

    # Create CACES that expires in 15 days
    completion = date.today() - relativedelta(years=5) + timedelta(days=15)
    caces = Caces.create(
        employee=sample_employee,
        kind='R489-1A',
        completion_date=completion,
        document_path='/documents/caces/soon.pdf'
    )

    assert caces.status == 'critical'
```

#### C. Class Methods

```python
def test_caces_expiring_soon(db, sample_employee):
    """Test getting certifications expiring within X days."""
    from employee.models import Caces

    # Create expiring certification (20 days from now)
    expiring_date = date.today() + timedelta(days=20)
    caces = Caces.create(
        employee=sample_employee,
        kind='R489-1A',
        completion_date=expiring_date - relativedelta(years=5),
        document_path='/documents/caces/expiring.pdf'
    )

    expiring = list(Caces.expiring_soon(days=30))
    assert len(expiring) >= 1
    assert caces in expiring


def test_caces_expired_query(expired_caces, sample_caces):
    """Test getting only expired certifications."""
    from employee.models import Caces

    expired = list(Caces.expired())

    assert expired_caces in expired
    assert sample_caces not in expired


def test_caces_by_kind(sample_caces, db):
    """Test filtering by CACES kind."""
    from employee.models import Caces

    r489_1a_caces = list(Caces.by_kind('R489-1A'))
    assert sample_caces in r489_1a_caces
```

#### D. CASCADE Delete

```python
def test_deleting_employee_deletes_caces(sample_employee, sample_caces, db):
    """Test that deleting employee CASCADE deletes their CACES."""
    from employee.models import Employee, Caces

    employee_id = sample_employee.id
    caces_id = sample_caces.id

    # Delete employee
    sample_employee.delete_instance()

    # CACES should be deleted too
    assert Employee.get_or_none(Employee.id == employee_id) is None
    assert Caces.get_or_none(Caces.id == caces_id) is None
```

---

## 4. MedicalVisit Model Tests

### Test Categories

#### A. Model Creation and Expiration Calculation

```python
def test_medical_visit_auto_calculates_expiration_initial(medical_visit, db):
    """Test that initial visit gets 2-year expiration."""
    # Visit date: 2023-06-15
    # Expiration: 2025-06-15 (2 years)
    assert medical_visit.expiration_date == date(2025, 6, 15)


def test_medical_visit_auto_calculates_expiration_periodic(db, sample_employee):
    """Test that periodic visit gets 2-year expiration."""
    from employee.models import MedicalVisit

    visit = MedicalVisit.create(
        employee=sample_employee,
        visit_type='periodic',
        visit_date=date(2023, 3, 1),
        result='fit',
        document_path='/documents/medical/periodic.pdf'
    )

    assert visit.expiration_date == date(2025, 3, 1)


def test_medical_visit_auto_calculates_expiration_recovery(unfit_visit, db):
    """Test that recovery visit gets 1-year expiration."""
    # Visit date: 2023-01-01
    # Expiration: 2024-01-01 (1 year)
    assert unfit_visit.expiration_date == date(2024, 1, 1)
```

#### B. Computed Properties

```python
def test_medical_visit_is_fit_property(medical_visit):
    """Test the is_fit property."""
    assert medical_visit.is_fit is True

    medical_visit.result = 'unfit'
    assert medical_visit.is_fit is False


def test_medical_visit_has_restrictions_property(db, sample_employee):
    """Test the has_restrictions property."""
    from employee.models import MedicalVisit

    visit = MedicalVisit.create(
        employee=sample_employee,
        visit_type='periodic',
        visit_date=date(2023, 1, 1),
        result='fit_with_restrictions',
        document_path='/documents/medical/restrictions.pdf'
    )

    assert visit.has_restrictions is True
```

#### C. CASCADE Delete

```python
def test_deleting_employee_deletes_medical_visits(sample_employee, medical_visit, db):
    """Test that deleting employee CASCADE deletes their medical visits."""
    from employee.models import Employee, MedicalVisit

    employee_id = sample_employee.id
    visit_id = medical_visit.id

    sample_employee.delete_instance()

    assert Employee.get_or_none(Employee.id == employee_id) is None
    assert MedicalVisit.get_or_none(MedicalVisit.id == visit_id) is None
```

---

## 5. OnlineTraining Model Tests

### Test Categories

#### A. Model Creation

```python
def test_online_training_with_expiration(online_training, db):
    """Test creating training with validity period."""
    assert online_training.validity_months == 12
    assert online_training.expiration_date is not None


def test_online_training_permanent(permanent_training):
    """Test creating permanent (non-expiring) training."""
    assert permanent_training.validity_months is None
    assert permanent_training.expiration_date is None


def test_online_training_expiration_calculation(db, sample_employee):
    """Test that expiration is calculated correctly."""
    from employee.models import OnlineTraining

    training = OnlineTraining.create(
        employee=sample_employee,
        title='Test Training',
        completion_date=date(2023, 1, 15),
        validity_months=6,
        certificate_path='/documents/training/test.pdf'
    )

    # 6 months from Jan 15 = Jul 15
    assert training.expiration_date == date(2023, 7, 15)


def test_online_training_month_overflow(db, sample_employee):
    """Test month overflow in expiration calculation."""
    from employee.models import OnlineTraining

    # Completion in November, validity 3 months
    # Should correctly roll over to next year (February)
    training = OnlineTraining.create(
        employee=sample_employee,
        title='Year End Training',
        completion_date=date(2023, 11, 15),
        validity_months=3,
        certificate_path='/documents/training/year-end.pdf'
    )

    assert training.expiration_date == date(2024, 2, 15)
```

#### B. Computed Properties

```python
def test_online_training_expires_property(online_training):
    """Test the expires property."""
    assert online_training.expires is True


def test_online_training_does_not_expire(permanent_training):
    """Test the expires property for permanent training."""
    assert permanent_training.expires is False


def test_online_training_status_permanent(permanent_training):
    """Test status property for permanent training."""
    assert permanent_training.status == 'permanent'


def test_online_training_permanent_days_until_expiration(permanent_training):
    """Test days_until_expiration returns None for permanent."""
    assert permanent_training.days_until_expiration is None
```

#### C. CASCADE Delete

```python
def test_deleting_employee_deletes_trainings(sample_employee, online_training, db):
    """Test that deleting employee CASCADE deletes their trainings."""
    from employee.models import Employee, OnlineTraining

    employee_id = sample_employee.id
    training_id = online_training.id

    sample_employee.delete_instance()

    assert Employee.get_or_none(Employee.id == employee_id) is None
    assert OnlineTraining.get_or_none(OnlineTraining.id == training_id) is None
```

---

## 6. AppLock Model Tests

### File: `tests/test_lock/test_manager.py`

### Test Categories

#### A. Lock Acquisition

```python
def test_acquire_lock_when_none_exists(db):
    """Test acquiring a lock when no lock exists."""
    from lock.models import AppLock

    lock = AppLock.acquire(
        hostname='test-machine',
        username='testuser',
        pid=12345,
        app_version='1.0.0'
    )

    assert lock.hostname == 'test-machine'
    assert lock.username == 'testuser'
    assert lock.process_id == 12345
    assert lock.app_version == '1.0.0'
    assert lock.is_stale is False


def test_acquire_lock_fails_when_active_lock_exists(db):
    """Test that acquiring fails when an active lock exists."""
    from lock.models import AppLock

    # Create first lock
    AppLock.acquire(
        hostname='machine-1',
        username='user1',
        pid=1111
    )

    # Try to acquire with different machine
    with pytest.raises(RuntimeError, match="Lock is held by"):
        AppLock.acquire(
            hostname='machine-2',
            username='user2',
            pid=2222
        )


def test_acquire_lock_removes_stale_lock(db):
    """Test that acquiring a lock removes an existing stale lock."""
    from lock.models import AppLock
    from datetime import datetime, timedelta

    # Create an old lock
    lock = AppLock.create(
        hostname='old-machine',
        username='old-user',
        pid=9999,
        locked_at=datetime.now() - timedelta(minutes=10),
        last_heartbeat=datetime.now() - timedelta(minutes=10)
    )

    # Lock should be stale (> 2 minutes old)
    assert lock.is_stale is True

    # Should be able to acquire new lock
    new_lock = AppLock.acquire(
        hostname='new-machine',
        username='new-user',
        pid=1234
    )

    assert new_lock.hostname == 'new-machine'
```

#### B. Lock Release

```python
def test_release_lock_when_owner(db):
    """Test releasing a lock when caller is the owner."""
    from lock.models import AppLock

    lock = AppLock.acquire(
        hostname='my-machine',
        username='myuser',
        pid=12345
    )

    # Should succeed
    result = AppLock.release(
        hostname='my-machine',
        pid=12345
    )

    assert result is True
    assert AppLock.get_active_lock() is None


def test_release_lock_fails_when_not_owner(db):
    """Test that release fails when caller is not the owner."""
    from lock.models import AppLock

    AppLock.acquire(
        hostname='owner-machine',
        username='owner',
        pid=1111
    )

    # Try to release with different credentials
    result = AppLock.release(
        hostname='other-machine',
        pid=2222
    )

    assert result is False


def test_release_lock_when_no_lock_exists(db):
    """Test releasing when no lock exists."""
    from lock.models import AppLock

    result = AppLock.release(
        hostname='any-machine',
        pid=1234
    )

    assert result is False
```

#### C. Heartbeat Refresh

```python
def test_refresh_heartbeat_when_owner(db):
    """Test refreshing heartbeat when caller is the owner."""
    from lock.models import AppLock
    import time

    lock = AppLock.acquire(
        hostname='my-machine',
        username='myuser',
        pid=12345
    )

    original_heartbeat = lock.last_heartbeat

    # Wait a tiny bit
    time.sleep(0.01)

    # Refresh heartbeat
    result = AppLock.refresh_heartbeat(
        hostname='my-machine',
        pid=12345
    )

    assert result is True

    # Reload from DB
    lock = AppLock.get_by_id(lock.id)
    assert lock.last_heartbeat > original_heartbeat


def test_refresh_heartbeat_fails_when_not_owner(db):
    """Test that heartbeat refresh fails when caller is not the owner."""
    from lock.models import AppLock

    AppLock.acquire(
        hostname='owner-machine',
        username='owner',
        pid=1111
    )

    result = AppLock.refresh_heartbeat(
        hostname='other-machine',
        pid=2222
    )

    assert result is False
```

#### D. Stale Lock Detection

```python
def test_stale_lock_detection_old_lock(db):
    """Test that old locks are detected as stale."""
    from lock.models import AppLock
    from datetime import datetime, timedelta

    lock = AppLock.create(
        hostname='machine',
        username='user',
        pid=1234,
        locked_at=datetime.now() - timedelta(minutes=5),
        last_heartbeat=datetime.now() - timedelta(minutes=5)
    )

    assert lock.is_stale is True


def test_stale_lock_detection_fresh_lock(db):
    """Test that fresh locks are not stale."""
    from lock.models import AppLock

    lock = AppLock.acquire(
        hostname='machine',
        username='user',
        pid=1234
    )

    assert lock.is_stale is False


def test_get_active_lock_excludes_stale(db):
    """Test that get_active_lock excludes stale locks."""
    from lock.models import AppLock
    from datetime import datetime, timedelta

    # Create stale lock
    AppLock.create(
        hostname='stale-machine',
        username='stale-user',
        pid=9999,
        locked_at=datetime.now() - timedelta(minutes=10),
        last_heartbeat=datetime.now() - timedelta(minutes=10)
    )

    # Should return None (lock is stale)
    active = AppLock.get_active_lock()
    assert active is None


def test_get_active_lock_returns_fresh_lock(db):
    """Test that get_active_lock returns fresh locks."""
    from lock.models import AppLock

    lock = AppLock.acquire(
        hostname='fresh-machine',
        username='fresh-user',
        pid=1234
    )

    active = AppLock.get_active_lock()
    assert active is not None
    assert active.id == lock.id
```

#### E. Computed Properties

```python
def test_age_seconds_property(db):
    """Test the age_seconds computed property."""
    from lock.models import AppLock
    import time

    lock = AppLock.acquire(
        hostname='machine',
        username='user',
        pid=1234
    )

    time.sleep(0.1)  # Wait 100ms

    age = lock.age_seconds
    assert age >= 0
    assert age < 1  # Less than 1 second


def test_heartbeat_age_seconds_property(db):
    """Test the heartbeat_age_seconds computed property."""
    from lock.models import AppLock
    import time

    lock = AppLock.acquire(
        hostname='machine',
        username='user',
        pid=1234
    )

    time.sleep(0.1)  # Wait 100ms

    heartbeat_age = lock.heartbeat_age_seconds
    assert heartbeat_age >= 0
    assert heartbeat_age < 1
```

---

## 7. Integration Tests

### File: `tests/test_integration/test_relationships.py`

#### A. Back-Reference Queries

```python
def test_employee_caces_back_reference(sample_employee, sample_caces, db):
    """Test accessing CACES through employee back-reference."""
    from employee.models import Employee

    employee = Employee.get_by_id(sample_employee.id)
    caces_list = list(employee.caces)

    assert len(caces_list) == 1
    assert caces_list[0].kind == 'R489-1A'


def test_employee_medical_visits_back_reference(sample_employee, medical_visit, db):
    """Test accessing medical visits through employee back-reference."""
    from employee.models import Employee

    employee = Employee.get_by_id(sample_employee.id)
    visits = list(employee.medical_visits)

    assert len(visits) == 1
    assert visits[0].visit_type == 'periodic'


def test_employee_trainings_back_reference(sample_employee, online_training, db):
    """Test accessing trainings through employee back-reference."""
    from employee.models import Employee

    employee = Employee.get_by_id(sample_employee.id)
    trainings = list(employee.trainings)

    assert len(trainings) == 1
    assert trainings[0].title == 'Safety Training'


def test_multiple_caces_per_employee(sample_employee, db):
    """Test that an employee can have multiple CACES."""
    from employee.models import Caces

    Caces.create(
        employee=sample_employee,
        kind='R489-1A',
        completion_date=date(2023, 1, 1),
        document_path='/caces/1a.pdf'
    )

    Caces.create(
        employee=sample_employee,
        kind='R489-3',
        completion_date=date(2023, 6, 1),
        document_path='/caces/3.pdf'
    )

    assert len(list(sample_employee.caces)) == 2
```

#### B. Complex Queries (future)

```python
def test_employee_with_expiring_certifications(db):
    """Test complex query to find employees with expiring items."""
    from employee.models import Employee
    from employee.queries import get_employees_with_expiring_items

    # This will be implemented in employee/queries.py
    employees = get_employees_with_expiring_items(days=30)

    # Should return employees with at least one expiring item
    assert all(has_expiring_items(emp) for emp in employees)
```

---

## 8. N+1 Query Tests

### File: `tests/test_performance/test_queries.py`

#### A. Prefetch Tests

```python
def test_prefetch_caces_avoids_n_plus_1(db):
    """Test that prefetch() avoids N+1 query problem."""
    from employee.models import Employee
    from peewee import prefetch

    # Create 10 employees with 3 CACES each
    for i in range(10):
        emp = Employee.create(
            first_name=f'Employee{i}',
            last_name=f'Test{i}',
            current_status='active',
            workspace='Quai',
            role='Cariste',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )
        for j in range(3):
            Caces.create(
                employee=emp,
                kind='R489-1A',
                completion_date=date(2023, 1, 1),
                document_path=f'/caces/{i}_{j}.pdf'
            )

    # Query with prefetch (efficient)
    employees = Employee.select()
    employees_with_caces = prefetch(employees, Caces)

    # Access CACES - should not trigger additional queries
    for emp in employees_with_caces:
        _ = list(emp.caces)  # Should not trigger query

    # If this test passes without taking too long, prefetch works
    assert True


def test_query_without_prefetch_causes_n_plus_1(db):
    """Test that NOT using prefetch() causes N+1 queries."""
    from employee.models import Employee

    # Create 5 employees with 2 CACES each
    for i in range(5):
        emp = Employee.create(
            first_name=f'Emp{i}',
            last_name=f'Test{i}',
            current_status='active',
            workspace='Quai',
            role='Cariste',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )
        for j in range(2):
            Caces.create(
                employee=emp,
                kind='R489-1A',
                completion_date=date(2023, 1, 1),
                document_path=f'/caces/{i}_{j}.pdf'
            )

    # Query without prefetch (inefficient)
    employees = list(Employee.select())

    # This will trigger N+1 queries (5 employees + 5*2 CACES queries)
    query_count = 0
    original_execute = test_db.execute_sql

    def count_queries(sql, params=None):
        nonlocal query_count
        query_count += 1
        return original_execute(sql, params)

    test_db.execute_sql = count_queries

    for emp in employees:
        _ = list(emp.caces)  # Triggers query for each employee

    # Should have many queries (1 initial + 5 for CACES)
    assert query_count > 5
```

---

## 9. Time-Dependent Tests

### File: `tests/test_employee/test_time_dependent.py`

#### Using freezegun to Mock Time

```python
from freezegun import freeze_time

@freeze_time('2023-06-15')
def test_caces_expiration_with_frozen_time(sample_caces):
    """Test CACES expiration calculation with frozen time."""
    # With frozen time, date.today() always returns 2023-06-15
    from employee.models import Caces

    caces = Caces.create(
        employee=sample_caces.employee,
        kind='R489-1A',
        completion_date=date(2023, 1, 1),
        document_path='/test.pdf'
    )

    # Created 2023-01-01, expires 2028-01-01
    # Today is 2023-06-15
    # Days until expiration should be exactly calculable
    expected = (date(2028, 1, 1) - date(2023, 6, 15)).days
    assert caces.days_until_expiration == expected


@freeze_time('2025-01-01')
def test_medical_visit_expires_on_future_date(db):
    """Test that medical visit expiration is detected correctly in future."""
    from employee.models import MedicalVisit

    visit = MedicalVisit.create(
        employee=sample_employee,
        visit_type='periodic',
        visit_date=date(2023, 1, 1),
        result='fit',
        document_path='/test.pdf'
    )

    # Visit: 2023-01-01, Expiration: 2025-01-01
    # Today: 2025-01-01 (exactly expiration date!)
    assert visit.is_expired is True
    assert visit.days_until_expiration == 0
```

---

## 10. Running the Tests

### Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_employee/test_models.py

# Run specific test
pytest tests/test_employee/test_models.py::test_create_employee_minimal

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x

# Run with pdb debugger on failure
pytest --pdb
```

### Expected Coverage

```
Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
src/database/connection.py               12      0   100%
src/employee/constants.py                 28      0   100%
src/employee/models.py                   178      5    97%   87-91
src/lock/models.py                        67      0   100%
-------------------------------------------------------------------
TOTAL                                  285      5    98%
```

---

## 11. Test Organization

```
tests/
├── conftest.py                    # Fixtures and test configuration
├── test_employee/
│   ├── __init__.py
│   ├── test_models.py             # Employee model tests
│   ├── test_caces.py              # Caces model tests
│   ├── test_medical_visit.py      # MedicalVisit model tests
│   ├── test_online_training.py    # OnlineTraining model tests
│   ├── test_time_dependent.py     # Time-dependent tests with freezegun
│   └── test_queries.py            # Complex query tests (when queries.py is done)
├── test_lock/
│   ├── __init__.py
│   └── test_manager.py            # AppLock model tests
├── test_integration/
│   ├── __init__.py
│   └── test_relationships.py      # Model relationships and CASCADE tests
└── test_performance/
    ├── __init__.py
    └── test_queries.py            # N+1 query and prefetch tests
```

---

## 12. Next Steps After Model Tests

Once models are fully tested:

1. **Implement `src/employee/queries.py`**
   - Add complex multi-table queries
   - Test query results and performance

2. **Implement `src/lock/manager.py`**
   - Add heartbeat timer logic
   - Test lock lifecycle

3. **UI Tests** (much later)
   - Test Flet interface
   - Mock model calls

4. **End-to-End Tests**
   - Test complete workflows
   - Test with real SQLite file (not in-memory)
