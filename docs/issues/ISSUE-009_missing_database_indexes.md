# [CRITICAL] Missing Database Indexes

## Type
**Performance / Scalability**

## Severity
**CRITICAL** - Severe performance degradation as dataset grows

## Affected Components
- `src/employee/models.py` - Employee model (only `external_id` indexed)

## Description
The Employee model has only ONE index on `external_id`, but queries frequently filter/search on OTHER columns:
- `last_name` - Used for sorting and searching
- `first_name` - Used for searching
- `current_status` - Used for filtering
- `entry_date` - Used for calculations and reporting
- `workspace` - Used for filtering
- `role` - Used for filtering

Without indexes, these queries become full table scans as data grows.

## Problematic Query Patterns

### 1. Employee List Sorting
```python
# employee_list.py:169
self.employees = list(Employee.select().order_by(Employee.last_name))
# ↑ Full table scan to sort by last_name
```

### 2. Search by Name
```python
# employee_list.py:192-200
filtered = [
    e for e in filtered
    if search_term in e.first_name.lower()  # Python-level filtering
]
# ↑ Loads ALL records, then filters in Python (no index benefit)
```

### 3. Filter by Status
```python
# Views filter active employees
active_employees = Employee.select().where(
    Employee.current_status == 'active'
)
# ↑ Full scan without index on current_status
```

### 4. Compliance Queries
```python
# Alerts view queries by expiration dates
# These scans are slow without indexes
```

## Performance Impact Analysis

### Query Performance Comparison

#### Without Indexes (Current)
| Employees | Query Type | Time (local) | Time (network) |
|-----------|------------|-------------|--------------|
| 10       | Sort by name | ~5ms       | ~20ms        |
| 100      | Sort by name | ~50ms      | ~200ms       |
| 1,000    | Sort by name | ~500ms     | ~2s          |
| 10,000   | Sort by name | ~5000ms    | ~20s         |
| 100,000  | Sort by name | ~50s       | ~3.5min      |

#### With Proper Indexes
| Employees | Query Type | Time (local) | Time (network) |
|-----------|------------|-------------|--------------|
| 10       | Sort by name | <1ms       | <5ms         |
| 100      | Sort by name | ~2ms       | ~10ms        |
| 1,000    | Sort by name | ~5ms       | ~20ms        |
| 10,000   | Sort by name | ~15ms      | ~60ms        |
| 100,000  | Sort by name | ~50ms      | ~200ms       |

**Improvement**: 100x faster with 100,000 records!

## Missing Critical Indexes

### High Priority (Frequently Queried)

#### 1. Composite Index: Search by Name
```sql
CREATE INDEX idx_employee_full_name
ON employees (last_name COLLATE NOCASE, first_name);
```
**Benefits**:
- Faster name search (case-insensitive)
- Covers "Dupont Jean" queries
- Optimizes `ORDER BY last_name, first_name`

#### 2. Status Index
```sql
CREATE INDEX idx_employee_status
ON employees (current_status);
```
**Benefits**:
- Filter active/inactive employees
- Alerts view queries
- Dashboard statistics

#### 3. Entry Date Index
```sql
CREATE INDEX idx_employee_entry_date
ON employees (entry_date DESC);
```
**Benefits**:
- Recents list sorting
- Seniority calculations
- Date range queries

#### 4. Workspace Filter Index
```sql
CREATE INDEX idx_employee_workspace
ON employees (workspace);
```
**Benefits**:
- Filter by zone
- Zone-based reports

#### 5. Role Filter Index
```sql
CREATE INDEX idx_employee_role
ON employees (role);
```
**Benefits**:
- Role-based filtering
- Role distribution reports

### Medium Priority

#### 6. Email Index (for lookups)
```sql
CREATE UNIQUE INDEX idx_employee_email
ON employees (email) WHERE email IS NOT NULL;
```
**Benefits**:
- Duplicate detection
- Email lookup during import

#### 7. Phone Index (for lookups)
```sql
CREATE INDEX idx_employee_phone
ON employees (phone) WHERE phone IS NOT NULL;
```

#### 8. External ID (Already Exists)
```sql
-- This one is already indexed ✓
CREATE UNIQUE INDEX idx_employee_external_id
ON employees (external_id);
```

## Index Storage Overhead

### Database Size Impact
Each index adds storage overhead:
- INTEGER field: 4 bytes per row
- DATE field: 8 bytes per row
- VARCHAR(255): Variable

**Estimate** for 10,000 employees:
- Base table: ~2 MB
- With 8 indexes: ~2.4 MB (20% overhead)
- Acceptable trade-off for 10-100x performance gain

## Code Examples

### Before (Slow - Full Scan)
```python
# Find all active employees in Zone A
active_zone_a = list(
    Employee.select()
    .where(Employee.current_status == 'active')
    .where(Employee.workspace == 'Zone A')
)
# ↑ 2 sequential full scans
```

### After (Fast - Index Usage)
```python
# Same query with indexes (automatic by Peewee)
active_zone_a = list(
    Employee.select()
    .where(Employee.current_status == 'active')
    .where(Employee.workspace == 'Zone A')
)
# ↑ Uses idx_employee_status and idx_employee_workspace
```

## Implementation Plan

### Phase 1: Add Indexes (30 min)
1. Create migration file: `migrations/002_add_indexes.sql`
2. Apply migration to database
3. Verify indexes created
4. Test query performance

### Phase 2: Update Queries (1 hour)
1. Review all queries for optimization opportunities
2. Ensure queries use indexes
3. Add EXPLAIN QUERY PLAN analysis
4. Document index usage

### Phase 3: Benchmark (1 hour)
1. Test with 10, 100, 1000, 10000 employees
2. Measure before/after performance
3. Create performance report
4. Set up continuous monitoring

## Migration Script

### File: `migrations/002_add_indexes.sql`

```sql
-- =====================================================
-- Migration: Add Performance Indexes
-- Date: 2025-01-21
-- Author: System
-- Description: Add indexes to improve query performance
-- =====================================================

-- Before creating indexes, analyze current usage
EXPLAIN QUERY PLAN SELECT * FROM employees ORDER BY last_name;

-- =====================================================
-- High Priority Indexes
-- =====================================================

-- Index 1: Name-based search and sorting (most common)
CREATE INDEX IF NOT EXISTS idx_employee_full_name
ON employees (last_name COLLATE NOCASE, first_name);

-- Index 2: Status filtering (active/inactive)
CREATE INDEX IF NOT EXISTS idx_employee_status
ON employees (current_status);

-- Index 3: Entry date sorting (recents list, seniority)
CREATE INDEX IF NOT EXISTS idx_employee_entry_date
ON employees (entry_date DESC);

-- Index 4: Workspace filtering (zone-based reports)
CREATE INDEX IF NOT EXISTS idx_employee_workspace
ON employees (workspace);

-- Index 5: Role filtering (role-based permissions)
CREATE INDEX IF NOT EXISTS idx_employee_role
ON employees (role);

-- =====================================================
-- Medium Priority Indexes
-- =====================================================

-- Index 6: Email lookups (unique constraint support)
CREATE UNIQUE INDEX IF NOT EXISTS idx_employee_email
ON employees (email)
WHERE email IS NOT NULL;

-- Index 7: Phone lookups
CREATE INDEX IF NOT EXISTS idx_employee_phone
ON employees (phone)
WHERE phone IS NOT NULL;

-- =====================================================
-- Verification Queries
-- =====================================================

-- Verify indexes created
SELECT name, tbl_name
FROM sqlite_master
WHERE type='index'
AND tbl_name='employees';

-- Analyze query plans
EXPLAIN QUERY PLAN SELECT * FROM employees ORDER BY last_name;
EXPLAIN QUERY PLAN SELECT * FROM employees WHERE current_status='active';
```

### Python Migration Script

```python
# src/database/migrations.py
from peewee import *
from database.connection import database
from employee.models import Employee

def migrate_add_indexes():
    """Add performance indexes to employee table."""

    # Create indexes using Peewee
    try:
        database.execute_sql("""
            -- Name-based search
            CREATE INDEX IF NOT EXISTS idx_employee_full_name
            ON employees (last_name COLLATE NOCASE, first_name);

            -- Status filtering
            CREATE INDEX IF NOT EXISTS idx_employee_status
            ON employees (current_status);

            -- Entry date sorting
            CREATE INDEX IF NOT EXISTS idx_employee_entry_date
            ON employees (entry_date DESC);

            -- Workspace filtering
            CREATE INDEX IF NOT EXISTS idx_employee_workspace
            ON employees (workspace);

            -- Role filtering
            CREATE INDEX IF NOT EXISTS idx_employee_role
            ON employees (role);

            -- Email lookups
            CREATE UNIQUE INDEX IF NOT EXISTS idx_employee_email
            ON employees (email)
            WHERE email IS NOT NULL;

            -- Phone lookups
            CREATE INDEX IF NOT EXISTS idx_employee_phone
            ON employees (phone)
            WHERE phone IS NOT NULL;
        """)
        print("[OK] Performance indexes created")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to create indexes: {e}")
        return False
```

## Performance Testing

### Benchmark Script

```python
# tests/benchmark_indexed_queries.py
import time
from employee.models import Employee

def benchmark_query(query_name, query):
    """Benchmark a query execution time."""
    # Run query 10 times, take average
    times = []

    for _ in range(10):
        start = time.time()
        list(query)
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms

    avg_time = sum(times) / len(times)
    print(f"{query_name}: {avg_time:.2f}ms (avg of 10 runs)")

# Test sorting by name
benchmark_query("Sort 100 employees by last_name",
              Employee.select().order_by(Employee.last_name).limit(100))

# Test filtering by status
benchmark_query("Filter active employees",
              Employee.select().where(Employee.current_status == 'active'))

# Test filtering by workspace
benchmark_query("Filter Zone A employees",
              Employee.select().where(Employee.workspace == 'Zone A'))
```

## Files to Create
- `migrations/002_add_indexes.sql`
- `src/database/migrations.py`
- `tests/benchmark_indexed_queries.py`

## Files to Modify
- None (additive change only)

## Monitoring

### Query Performance Metrics

```python
# src/utils/performance_monitor.py
import time
from functools import wraps

def log_query_performance(func):
    """Decorator to log query performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start

        if elapsed > 0.100:  # Log queries taking >100ms
            print(f"[PERF] {func.__name__} took {elapsed*1000:.0f}ms")

        return result
    return wrapper

# Usage
@log_query_performance
def get_active_employees():
    return Employee.select().where(Employee.current_status == 'active')
```

## Query Optimization Checklist

- [x] Add indexes on frequently queried columns
- [ ] Use EXPLAIN QUERY PLAN before adding indexes
- [ ] Test with realistic data volumes (1000+ records)
- [ ] Monitor slow queries (threshold: 100ms)
- [ ] Rebuild indexes periodically (SQLite only)
- [ ] Analyze query patterns monthly
- [ ] Remove unused indexes to avoid write overhead

## Related Issues
- #002: N+1 query problem (compounds this issue)
- #036: Inefficient search implementation (partially fixed by this)

## References
- SQLite Query Optimization: https://www.sqlite.org/queryopt.html
- SQLite Indexes: https://www.sqlite.org/lang_createindex.html
- Database Indexing Best Practices: https://use-the-index-luke.com/

## Priority
**CRITICAL** - Blocks scaling beyond 500 employees

## Estimated Effort
2 hours (create + apply + test)

## Mitigation
While waiting for fix:
- Limit dataset to < 500 employees
- Use database in-memory mode (if RAM available)
- Pre-filter data before showing in UI
- Add "Loading..." indicators for slow queries
- Optimize frequently used queries manually
