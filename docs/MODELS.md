# Data Models Design

This document details the design and implementation strategy for Peewee ORM models in the Warehouse Employee Management System.

## Overview

The models follow an **entity-oriented** approach where:
- Models contain their own business logic (classmethods, instance methods, properties)
- Relationships are defined with foreign keys and back-references
- Calculated properties are computed on-demand
- Class methods provide domain-specific queries

---

## 1. Database Configuration

### File: `src/database/connection.py`

### Purpose

Create a singleton Database instance configured for SQLite with Write-Ahead Logging (WAL) mode enabled for optimal network share performance.

### Implementation

```python
from peewee import SqliteDatabase
from pathlib import Path

database = SqliteDatabase(None)  # Path set at runtime

def init_database(db_path: Path) -> None:
    """
    Initialize database connection with WAL mode and optimal PRAGMAs.

    Args:
        db_path: Path to SQLite database file
    """
    database.init(db_path)

    # Enable WAL mode for better concurrent read performance
    database.execute_sql('PRAGMA journal_mode=WAL')
    database.execute_sql('PRAGMA foreign_keys=ON')
    database.execute_sql('PRAGMA synchronous=NORMAL')
    database.execute_sql('PRAGMA busy_timeout=5000')

    # Create all tables
    database.create_tables([
        Employee,
        Caces,
        MedicalVisit,
        OnlineTraining,
        AppLock,
    ], safe=True)

def get_database() -> SqliteDatabase:
    """Return the database instance."""
    return database
```

### Why WAL Mode?

| Feature | Without WAL | With WAL |
|---------|-------------|----------|
| Concurrent readers during write | No | Yes |
| File locking behavior | Aggressive | Less aggressive |
| Network share performance | Slower | Faster |
| Crash recovery | Manual | Automatic |

### PRAGMA Configuration Rationale

- **`journal_mode=WAL`**: Write-Ahead Logging for concurrent reads
- **`foreign_keys=ON`**: Enable referential integrity
- **`synchronous=NORMAL`**: Balance between safety and performance
- **`busy_timeout=5000`**: Wait 5 seconds before failing on lock

---

## 2. Employee Model

### File: `src/employee/models.py`

### Model Structure

```python
from peewee import *
from datetime import date, datetime
from utils.uuid import UUIDField  # Custom UUID field
from employee.constants import (
    EmployeeStatus,
    ContractType,
)

class Employee(Model):
    """Core employee entity with business logic."""

    # Primary Key
    id = UUIDField(primary=True)

    # Identification
    external_id = CharField(null=True, index=True)  # WMS reference (manual entry)
    first_name = CharField()
    last_name = CharField()

    # Employment Status
    current_status = CharField()  # Enum: 'active', 'inactive'
    workspace = CharField()
    role = CharField()
    contract_type = CharField()  # Enum: 'CDI', 'CDD', 'Interim', 'Alternance'

    # Employment Dates
    entry_date = DateField()

    # Optional
    avatar_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = 'employees'

    # ========== COMPUTED PROPERTIES ==========

    @property
    def full_name(self) -> str:
        """Complete employee name for display."""
        return f"{self.first_name} {self.last_name}"

    @property
    def seniority(self) -> int:
        """Complete years of service."""
        return (date.today() - self.entry_date).days // 365

    @property
    def is_active(self) -> bool:
        """Convenience boolean for active status."""
        return self.current_status == EmployeeStatus.ACTIVE

    # ========== CLASS METHODS (QUERIES) ==========

    @classmethod
    def active(cls):
        """Get all active employees."""
        return cls.select().where(cls.current_status == EmployeeStatus.ACTIVE)

    @classmethod
    def inactive(cls):
        """Get all inactive employees."""
        return cls.select().where(cls.current_status == EmployeeStatus.INACTIVE)

    @classmethod
    def by_workspace(cls, workspace: str):
        """Get employees by workspace assignment."""
        return cls.select().where(cls.workspace == workspace)

    @classmethod
    def by_role(cls, role: str):
        """Get employees by job role."""
        return cls.select().where(cls.role == role)

    @classmethod
    def by_contract_type(cls, contract_type: str):
        """Get employees by contract type."""
        return cls.select().where(cls.contract_type == contract_type)

    @classmethod
    def with_expiring_certifications(cls, days=30):
        """
        Complex query: employees with certifications expiring soon.

        Returns employees with at least one CACES, medical visit,
        or training expiring within the specified days.
        """
        from employee.queries import get_employees_with_expiring_items
        return get_employees_with_expiring_items(days)

    # ========== INSTANCE METHODS ==========

    def add_caces(self, kind: str, completion_date: date, document_path: str):
        """Create a CACES certification for this employee."""
        return Caces.create(
            employee=self,
            kind=kind,
            completion_date=completion_date,
            document_path=document_path
        )

    def add_medical_visit(self, visit_type: str, visit_date: date,
                         result: str, document_path: str):
        """Create a medical visit record for this employee."""
        return MedicalVisit.create(
            employee=self,
            visit_type=visit_type,
            visit_date=visit_date,
            result=result,
            document_path=document_path
        )

    def add_training(self, title: str, completion_date: date,
                    validity_months: int, certificate_path: str):
        """Create an online training record for this employee."""
        return OnlineTraining.create(
            employee=self,
            title=title,
            completion_date=completion_date,
            validity_months=validity_months,
            certificate_path=certificate_path
        )

    def get_alerts(self, thresholds_days=[30, 60, 90]):
        """
        Get all alerts for this employee.

        Returns list of dicts with alert information:
        - type: 'caces', 'medical', 'training'
        - item: the actual model instance
        - severity: 'critical', 'warning', 'info'
        - days_until: days until expiration
        """
        from employee.calculations import get_employee_alerts
        return get_employee_alerts(self, thresholds_days)

    # ========== VALIDATION ==========

    def validate(self):
        """Custom validation logic before save."""
        if self.entry_date > date.today():
            raise ValueError("Entry date cannot be in the future")

        if self.external_id:
            # Check uniqueness of external_id
            existing = Employee.select().where(
                (Employee.external_id == self.external_id) &
                (Employee.id != self.id)
            ).first()
            if existing:
                raise ValueError("External ID already exists")

    def save(self, force_insert=False, only=None):
        """Override save to update updated_at and validate."""
        self.updated_at = datetime.now()
        self.validate()
        return super().save(force_insert=force_insert, only=only)
```

### Relationships

```
Employee (1) ----< (N) Caces
Employee (1) ----< (N) MedicalVisit
Employee (1) ----< (N) OnlineTraining
```

---

## 3. Caces Model

### File: `src/employee/models.py` (continuing)

### Model Structure

```python
class Caces(Model):
    """
    CACES certification (Certificat d'Aptitude à la Conduite En Sécurité).

    French certification for operating heavy machinery and equipment.
    """

    id = UUIDField(primary=True)
    employee = ForeignKeyField(Employee, backref='caces', on_delete='CASCADE')

    # Certification Details
    kind = CharField()  # e.g., 'R489-1A', 'R489-1B', 'R489-3', 'R489-4'
    completion_date = DateField()

    # Calculated at creation time
    expiration_date = DateField(index=True)

    # Document
    document_path = CharField()

    # Metadata
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = 'caces'
        indexes = (
            (('employee', 'expiration_date'), False),  # Composite index
        )

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_expired(self) -> bool:
        """Check if certification is expired."""
        return date.today() > self.expiration_date

    @property
    def days_until_expiration(self) -> int:
        """Days until expiration (negative if already expired)."""
        return (self.expiration_date - date.today()).days

    @property
    def status(self) -> str:
        """
        Human-readable status.

        Returns:
            'expired': Already expired
            'critical': Expires within 30 days
            'warning': Expires within 60 days
            'valid': More than 60 days remaining
        """
        if self.is_expired:
            return "expired"
        elif self.days_until_expiration < 30:
            return "critical"
        elif self.days_until_expiration < 60:
            return "warning"
        else:
            return "valid"

    # ========== CLASS METHODS ==========

    @classmethod
    def calculate_expiration(cls, kind: str, completion_date: date) -> date:
        """
        Calculate expiration date based on CACES kind.

        Rules:
        - R489-1A, R489-1B, R489-3, R489-4: 5 years validity
        - Other certifications: 10 years validity

        Args:
            kind: CACES certification type
            completion_date: Date when certification was obtained

        Returns:
            Expiration date
        """
        if kind in ['R489-1A', 'R489-1B', 'R489-3', 'R489-4']:
            years = 5
        else:
            years = 10

        return completion_date + timedelta(days=years * 365)

    @classmethod
    def expiring_soon(cls, days=30):
        """Get all certifications expiring within X days."""
        threshold = date.today() + timedelta(days=days)
        return cls.select().where(
            (cls.expiration_date <= threshold) &
            (cls.expiration_date >= date.today())
        )

    @classmethod
    def expired(cls):
        """Get all expired certifications."""
        return cls.select().where(cls.expiration_date < date.today())

    @classmethod
    def by_kind(cls, kind: str):
        """Get certifications by type."""
        return cls.select().where(cls.kind == kind)

    # ========== HOOKS ==========

    def before_save(self):
        """Calculate expiration_date before saving if not set."""
        if not self.expiration_date:
            self.expiration_date = self.calculate_expiration(
                self.kind,
                self.completion_date
            )
```

### CACES Types

Standard French CACES certifications:
- **R489-1A**: Forklift truck with upright (porté-à-faux)
- **R489-1B**: Forklift truck with retractable mast (mât rétractable)
- **R489-3**: Heavy forklift ≥ 6 tons
- **R489-4**: Heavy retractable mast forklift ≥ 6 tons
- **R489-5**: Side-loading forklift

---

## 4. MedicalVisit Model

### File: `src/employee/models.py` (continuing)

### Model Structure

```python
class MedicalVisit(Model):
    """
    Occupational health visit record.

    French labor law requires periodic medical examinations for workers.
    """

    id = UUIDField(primary=True)
    employee = ForeignKeyField(Employee, backref='medical_visits', on_delete='CASCADE')

    # Visit Details
    visit_type = CharField()  # 'initial', 'periodic', 'recovery'
    visit_date = DateField()

    # Calculated expiration
    expiration_date = DateField(index=True)

    # Visit Result
    result = CharField()  # 'fit', 'unfit', 'fit_with_restrictions'

    # Document
    document_path = CharField()

    # Metadata
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = 'medical_visits'
        indexes = (
            (('employee', 'expiration_date'), False),
        )

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_expired(self) -> bool:
        """Check if medical clearance is expired."""
        return date.today() > self.expiration_date

    @property
    def days_until_expiration(self) -> int:
        """Days until expiration."""
        return (self.expiration_date - date.today()).days

    @property
    def is_fit(self) -> bool:
        """Convenience: is employee fit for work?"""
        return self.result == 'fit'

    @property
    def has_restrictions(self) -> bool:
        """Does this visit have work restrictions?"""
        return self.result == 'fit_with_restrictions'

    # ========== CLASS METHODS ==========

    @classmethod
    def calculate_expiration(cls, visit_type: str, visit_date: date) -> date:
        """
        Calculate medical visit expiration based on type.

        Rules:
        - Initial visit: 2 years
        - Periodic visit: 2 years
        - Recovery visit: 1 year

        Args:
            visit_type: Type of medical visit
            visit_date: Date when visit occurred

        Returns:
            Expiration date
        """
        if visit_type == 'recovery':
            years = 1
        else:  # initial or periodic
            years = 2

        return visit_date + timedelta(days=years * 365)

    @classmethod
    def expiring_soon(cls, days=30):
        """Get medical visits expiring within X days."""
        threshold = date.today() + timedelta(days=days)
        return cls.select().where(
            (cls.expiration_date <= threshold) &
            (cls.expiration_date >= date.today())
        )

    @classmethod
    def unfit_employees(cls):
        """Get employees with unfit medical visits."""
        return (Employee
                .select(Employee, cls)
                .join(cls)
                .where(cls.result == 'unfit'))

    # ========== HOOKS ==========

    def before_save(self):
        """Calculate expiration_date before saving if not set."""
        if not self.expiration_date:
            self.expiration_date = self.calculate_expiration(
                self.visit_type,
                self.visit_date
            )
```

---

## 5. OnlineTraining Model

### File: `src/employee/models.py` (continuing)

### Model Structure

```python
class OnlineTraining(Model):
    """
    Online training completion record.

    Some trainings have expiration dates, others are permanent.
    """

    id = UUIDField(primary=True)
    employee = ForeignKeyField(Employee, backref='trainings', on_delete='CASCADE')

    # Training Details
    title = CharField()
    completion_date = DateField()

    # Validity (NULL = permanent, no expiration)
    validity_months = IntegerField(null=True)

    # Calculated expiration (NULL if permanent)
    expiration_date = DateField(null=True, index=True)

    # Certificate (optional)
    certificate_path = CharField(null=True)

    # Metadata
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = 'online_trainings'
        indexes = (
            (('employee', 'expiration_date'), False),
        )

    # ========== COMPUTED PROPERTIES ==========

    @property
    def expires(self) -> bool:
        """Does this training expire?"""
        return self.validity_months is not None

    @property
    def is_expired(self) -> bool:
        """Check if training is expired (only if it expires)."""
        if not self.expires:
            return False
        return date.today() > self.expiration_date

    @property
    def days_until_expiration(self) -> int | None:
        """Days until expiration, or None if permanent."""
        if not self.expires:
            return None
        return (self.expiration_date - date.today()).days

    @property
    def status(self) -> str:
        """Human-readable status."""
        if not self.expires:
            return "permanent"
        elif self.is_expired:
            return "expired"
        elif self.days_until_expiration < 30:
            return "critical"
        elif self.days_until_expiration < 60:
            return "warning"
        else:
            return "valid"

    # ========== CLASS METHODS ==========

    @classmethod
    def calculate_expiration(cls, completion_date: date, validity_months: int | None) -> date | None:
        """
        Calculate training expiration date.

        If validity_months is None, training has no expiration (permanent).

        Args:
            completion_date: Date when training was completed
            validity_months: Number of months training is valid, or None for permanent

        Returns:
            Expiration date, or None for permanent trainings
        """
        if validity_months is None:
            return None

        # Add months to date
        year = completion_date.year
        month = completion_date.month + validity_months

        # Handle year overflow
        while month > 12:
            month -= 12
            year += 1

        # Keep same day of month
        return date(year, month, completion_date.day)

    @classmethod
    def expiring_soon(cls, days=30):
        """Get trainings expiring within X days."""
        threshold = date.today() + timedelta(days=days)
        return cls.select().where(
            (cls.expiration_date.is_null(False)) &
            (cls.expiration_date <= threshold) &
            (cls.expiration_date >= date.today())
        )

    @classmethod
    def permanent(cls):
        """Get all permanent (non-expiring) trainings."""
        return cls.select().where(cls.validity_months.is_null(True))

    # ========== HOOKS ==========

    def before_save(self):
        """Calculate expiration_date before saving if not set."""
        if self.expiration_date is None and self.validity_months is not None:
            self.expiration_date = self.calculate_expiration(
                self.completion_date,
                self.validity_months
            )
```

---

## 6. AppLock Model

### File: `src/lock/models.py`

### Model Structure

```python
class AppLock(Model):
    """
    Application lock for concurrent access control.

    Ensures only one user can edit data at a time on shared network drives.
    Uses heartbeat mechanism to detect stale locks from crashed applications.
    """

    id = UUIDField(primary=True)

    # Lock holder identification
    hostname = CharField(index=True)  # Machine name
    username = CharField(null=True)   # Optional: user name

    # Timestamps
    locked_at = DateTimeField(default=datetime.now, index=True)
    last_heartbeat = DateTimeField(default=datetime.now, index=True)

    # Process identification
    process_id = IntegerField()  # PID for debugging

    # Metadata
    app_version = CharField(null=True)  # For debugging/version tracking

    class Meta:
        database = database
        table_name = 'app_locks'

    # ========== COMPUTED PROPERTIES ==========

    @property
    def is_stale(self, timeout_minutes=15) -> bool:
        """
        Check if lock is stale (no recent heartbeat).

        Args:
            timeout_minutes: Minutes of inactivity before considering lock stale

        Returns:
            True if lock is stale and can be safely overridden
        """
        threshold = datetime.now() - timedelta(minutes=timeout_minutes)
        return self.last_heartbeat < threshold

    @property
    def age_seconds(self) -> int:
        """Age of lock in seconds since acquisition."""
        return (datetime.now() - self.locked_at).seconds

    @property
    def heartbeat_age_seconds(self) -> int:
        """Seconds since last heartbeat."""
        return (datetime.now() - self.last_heartbeat).seconds

    # ========== CLASS METHODS ==========

    @classmethod
    def acquire(cls, hostname: str, username: str | None, pid: int,
               app_version: str | None = None) -> 'AppLock':
        """
        Acquire application lock.

        Fails if an active lock already exists.

        Args:
            hostname: Machine name of lock holder
            username: Optional user name
            pid: Process ID
            app_version: Optional application version

        Returns:
            AppLock instance

        Raises:
            RuntimeError: If lock is already held by active host
        """
        # Check for existing active lock
        existing = cls.get_active_lock()
        if existing and not existing.is_stale:
            raise RuntimeError(
                f"Lock is held by {existing.hostname} "
                f"(since {existing.locked_at})"
            )

        # Remove stale lock if exists
        if existing:
            existing.delete_instance()

        # Create new lock
        return cls.create(
            hostname=hostname,
            username=username,
            process_id=pid,
            app_version=app_version
        )

    @classmethod
    def release(cls, hostname: str, pid: int) -> bool:
        """
        Release lock (only if owned by caller).

        Args:
            hostname: Must match lock holder's hostname
            pid: Must match lock holder's process ID

        Returns:
            True if lock was released, False if not owned by caller
        """
        lock = cls.get_active_lock()
        if not lock:
            return False

        if lock.hostname != hostname or lock.process_id != pid:
            return False

        lock.delete_instance()
        return True

    @classmethod
    def refresh_heartbeat(cls, hostname: str, pid: int) -> bool:
        """
        Update heartbeat timestamp to keep lock alive.

        Should be called every 30 seconds while holding lock.

        Args:
            hostname: Must match lock holder's hostname
            pid: Must match lock holder's process ID

        Returns:
            True if heartbeat updated, False if not lock owner
        """
        lock = cls.get_active_lock()
        if not lock:
            return False

        if lock.hostname != hostname or lock.process_id != pid:
            return False

        lock.last_heartbeat = datetime.now()
        lock.save()
        return True

    @classmethod
    def get_active_lock(cls) -> 'AppLock | None':
        """
        Get current active lock, or None if no active lock exists.

        Returns None if lock is stale (considered inactive).
        """
        lock = cls.select().order_by(cls.locked_at.desc()).first()
        if not lock:
            return None

        # Return None if lock is stale
        if lock.is_stale:
            return None

        return lock
```

### Heartbeat Mechanism

The locking system uses a heartbeat to detect crashed applications:

1. **Lock acquisition**: Create AppLock record with current timestamp
2. **Heartbeat**: Every 30 seconds, update `last_heartbeat` field
3. **Stale detection**: If `last_heartbeat` > 15 minutes ago, lock is considered stale
4. **Lock override**: Stale locks can be safely overridden by new users

---

## 7. Constants and Enums

### File: `src/employee/constants.py`

```python
"""Employee-related constants and enums."""

class EmployeeStatus:
    """Employee employment status."""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ALL = [ACTIVE, INACTIVE]

class ContractType:
    """Employment contract types."""
    CDI = 'CDI'
    CDD = 'CDD'
    INTERIM = 'Interim'
    ALTERNANCE = 'Alternance'
    ALL = [CDI, CDD, INTERIM, ALTERNANCE]

class VisitType:
    """Medical visit types."""
    INITIAL = 'initial'
    PERIODIC = 'periodic'
    RECOVERY = 'recovery'
    ALL = [INITIAL, PERIODIC, RECOVERY]

class VisitResult:
    """Medical visit results."""
    FIT = 'fit'
    UNFIT = 'unfit'
    FIT_WITH_RESTRICTIONS = 'fit_with_restrictions'
    ALL = [FIT, UNFIT, FIT_WITH_RESTRICTIONS]

# Standard French CACES certifications
CACES_TYPES = [
    'R489-1A',  # Forklift with upright (porté-à-faux)
    'R489-1B',  # Forklift with retractable mast (mât rétractable)
    'R489-3',   # Heavy forklift ≥ 6 tons
    'R489-4',   # Heavy retractable mast forklift ≥ 6 tons
    'R489-5',   # Side-loading forklift
]

# Default workspaces (configurable in config.json)
DEFAULT_WORKSPACES = [
    'Quai',
    'Zone A',
    'Zone B',
    'Bureau',
]

# Default roles (configurable in config.json)
DEFAULT_ROLES = [
    'Préparateur',
    'Réceptionnaire',
    'Cariste',
]
```

---

## 8. Model Relationships Diagram

```
┌─────────────┐
│   Employee  │
│             │
│ - id (UUID) │
│ - first_name│
│ - last_name │
│ - status    │
│ - workspace │
│ - role      │
│ - contract  │
│ - entry_date│
└──────┬──────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌──────────────┐                    ┌──────────────┐
│    Caces     │                    │ MedicalVisit │
│              │                    │              │
│ - id         │                    │ - id         │
│ - employee   │◄──────────────────│ - employee   │
│ - kind       │                    │ - visit_type │
│ - completion │                    │ - visit_date │
│ - expiration │                    │ - result     │
│ - document   │                    │ - document  │
└──────────────┘                    └──────────────┘

       │
       ▼
┌──────────────────┐
│ OnlineTraining   │
│                  │
│ - id             │
│ - employee       │◄──────────────────┐
│ - title          │                    │
│ - completion     │                    │
│ - validity_month │                    │
│ - expiration     │                    │
│ - certificate    │                    │
└──────────────────┘                    │
                                        │
┌──────────────────┐                    │
│     AppLock      │ (Independent)      │
│                  │                    │
│ - id             │                    │
│ - hostname       │                    │
│ - username       │                    │
│ - locked_at      │                    │
│ - heartbeat      │                    │
│ - process_id     │                    │
└──────────────────┘                    │
                                        │
          All models use:                │
          - UUIDField (primary key)      │
          - created_at timestamp         │
          - Foreign key CASCADE delete   │
```

---

## 9. Implementation Order

Models should be implemented in this order:

1. **`src/database/connection.py`**
   - Database singleton
   - `init_database()` function
   - PRAGMA configuration

2. **`src/employee/constants.py`**
   - All enum classes
   - CACES types
   - Default values

3. **`src/employee/models.py`**
   - Employee model (no dependencies)
   - Caces model (depends on Employee)
   - MedicalVisit model (depends on Employee)
   - OnlineTraining model (depends on Employee)

4. **`src/lock/models.py`**
   - AppLock model (independent)

5. **Tests**
   - Verify table creation
   - Test relationships
   - Test computed properties
   - Test class methods

---

## 10. Design Decisions

### Why UUID instead of Auto-increment?

- **Security**: UUIDs are not predictable, preventing enumeration attacks
- **Distribution**: Safe for distributed systems (future-proof)
- **Collision resistance**: Virtually impossible to collide
- **Standard**: Modern best practice for primary keys

### Why CASCADE delete?

- **Referential integrity**: Prevent orphaned records
- **Clean deletion**: Deleting employee removes all related data
- **Simplicity**: No need for manual cleanup
- **User expectation**: When deleting employee, expect all related data to disappear

### Why hard delete (not soft delete)?

- **Simplicity**: No need for additional `is_deleted` flag
- **Privacy**: GDPR compliance (actually remove data)
- **Performance**: Smaller tables, simpler queries
- **Use case**: Rarely need to "restore" deleted employees

### Why timezone-naive timestamps?

- **Desktop app**: Single timezone per deployment
- **Simplicity**: No timezone conversion complexity
- **SQLite**: Limited timezone support
- **Use case**: All users in same timezone (warehouse)

---

## 11. Next Steps After Models

Once models are implemented:

1. **`src/employee/queries.py`**
   - Complex multi-table queries
   - Optimized queries for UI
   - Join queries

2. **`src/employee/calculations.py`**
   - Alert calculation logic
   - Seniority calculations
   - Status determination

3. **`src/employee/validators.py`**
   - Custom Peewee validators
   - Business rule validation
   - Data integrity checks

4. **`src/lock/manager.py`**
   - Lock management logic
   - Heartbeat timer
   - Stale lock cleanup

5. **Tests**
   - Unit tests for all models
   - Integration tests for queries
   - Lock mechanism tests
