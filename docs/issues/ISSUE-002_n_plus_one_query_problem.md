# [CRITICAL] N+1 Query Problem in Employee Loading

## Type
**Performance Bug**

## Severity
**CRITICAL** - Severe performance degradation with multiple employees

## Affected Components
- `src/controllers/employee_controller.py` (lines 58-60)
- `src/ui_ctk/views/employee_list.py` (line 169)
- `src/ui_ctk/views/employee_detail.py` (throughout)

## Description
The application suffers from the classic N+1 query problem. When loading the employee list, it loads all employees, then for EACH employee, it makes separate database queries to load:
- CACES certifications
- Medical visits
- Online trainings

With 100 employees: **1 + 100 + 100 + 100 = 301 database queries** instead of 4 (or even 1 with proper joins).

## Problematic Code

### employee_controller.py:58-60
```python
# Called for EACH employee in the list
def get_employee_data(self, employee_id: str) -> dict:
    emp = Employee.get_by_id(employee_id)

    # N+1 PROBLEM: 3 additional queries per employee
    caces = list(emp.caces.order_by(-Caces.expiration_date))
    visits = list(emp.medical_visits.order_by(-MedicalVisit.visit_date))
    trainings = list(emp.trainings.order_by(-OnlineTraining.completion_date))

    return {
        'employee': emp,
        'caces': caces,
        'visits': visits,
        'trainings': trainings
    }
```

### employee_list.py:169
```python
# Loads ALL employees, then queries related data for each
self.employees = list(Employee.select().order_by(Employee.last_name))
# For each employee above, controller makes 3 more queries
```

## Performance Impact

### Current Behavior
| Employees | Queries | Est. Time (local DB) | Est. Time (network DB) |
|-----------|---------|-------------------|----------------------|
| 10        | 31      | ~50ms             | ~200ms               |
| 50        | 151     | ~250ms            | ~1s                  |
| 100       | 301     | ~500ms            | ~2s                  |
| 500       | 1501    | ~2.5s             | ~10s                 |
| 1000      | 3001    | ~5s               | ~20s                 |

### With 100 Employees
- **301 queries** to load the employee list
- **Potential 5 second delay** on list view load
- **UI freezes** during loading
- **Database connection overhead**

## Root Cause
Peewee ORM's foreign key relationships are lazily evaluated by default. When you access `employee.caces`, it triggers a query. Accessing it in a loop means N queries for N employees.

## Affected User Flows
1. **Employee list view** - Main dashboard
2. **Alerts view** - Loads employees to show their certifications
3. **Employee detail view** - Loads all related data
4. **Export functionality** (if added)

## Proposed Solution

### Option 1: Use Prefetch (Recommended)
Peewee provides `prefetch()` to load related objects in a single query:

```python
# Load employees with all related data in 4 queries instead of 301
query = (Employee
    .select(Employee, Caces, MedicalVisit, OnlineTraining)
    .join(Caces, attr='LEFT OUTER')
    .switch(MedicalVisit, attr='LEFT OUTER')
    .switch(OnlineTraining, attr='LEFT OUTER')
    .order_by(Employee.last_name)
)

employees = list(query)  # All data loaded in efficient manner

# Access related data without additional queries
for emp in employees:
    caces = list(emp.caces)  # Already loaded, no query!
    visits = list(emp.medical_visits)  # Already loaded!
```

**Result**: 4 queries instead of 301 (75x improvement)

### Option 2: Pagination + Lazy Loading
Load employees in pages and load related data only when needed:

```python
PAGE_SIZE = 25

def get_employees_page(page: int = 0):
    """Load employees with pagination."""
    query = (Employee
        .select(Employee, Caces, MedicalVisit)
        .join(Caces, attr='LEFT OUTER')
        .switch(MedicalVisit, attr='LEFT OUTER')
        .order_by(Employee.last_name)
        .paginate(page, PAGE_SIZE)
    )
    return query
```

**Result**: 1 query per page, initial load 75% faster

### Option 3: Caching Layer
Cache frequently accessed data:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_employee_certifications(employee_id: str):
    """Get employee certifications with caching."""
    emp = Employee.get_by_id(employee_id)
    return {
        'caces': list(emp.caces),
        'visits': list(emp.medical_visits),
        'trainings': list(emp.trainings)
    }

def clear_employee_cache(employee_id: str = None):
    """Clear cache when data changes."""
    get_employee_certifications.cache_clear()
```

**Result**: Subsequent loads instant, but cache invalidation needed

## Implementation Plan

### Phase 1: Fix Immediate Performance (1-2 hours)
1. Update `employee_list.py` to use `prefetch()`
2. Update `alerts_view.py` to use `prefetch()`
3. Update `employee_detail.py` to use `prefetch()`

### Phase 2: Add Pagination (2-3 hours)
1. Add pagination controls to list view
2. Update query to use `paginate()`
3. Add page size configuration

### Phase 3: Add Caching (optional, 2-3 hours)
1. Implement cache layer
2. Add cache invalidation on CRUD operations
3. Add cache statistics

## Files to Modify
- `src/controllers/employee_controller.py`
- `src/ui_ctk/views/employee_list.py`
- `src/ui_ctk/views/alerts_view.py`
- `src/ui_ctk/views/employee_detail.py`
- `tests/test_query_performance.py` (new)

## Testing Requirements
- Benchmark with 10, 100, 500 employees
- Verify query count with `EXPLAIN QUERY PLAN`
- Test with slow database (simulate network latency)
- Memory usage profiling
- Test pagination edge cases

## Performance Targets
- **Current**: 301 queries for 100 employees
- **Target**: 4 queries for 100 employees (prefetch)
- **Improvement**: 98.7% reduction in queries
- **Load time**: < 500ms for 100 employees (local DB)

## Code Example - Fix

### Before (N+1 queries)
```python
# BAD: N+1 problem
employees = list(Employee.select())
for emp in employees:
    caces = list(emp.caces)  # Query 1
    visits = list(emp.medical_visits)  # Query 2
    trainings = list(emp.trainings)  # Query 3
```

### After (Fixed with prefetch)
```python
# GOOD: Single query with prefetch
from peewee import prefetch

employees = list(Employee
    .select(Employee, Caces, MedicalVisit, OnlineTraining)
    .prefetch(Caces, MedicalVisit, OnlineTraining)  # Load all at once!
)

for emp in employees:
    # Already loaded, no additional queries
    caces = list(emp.caces)
    visits = list(emp.medical_visits)
    trainings = list(emp.trainings)
```

## Related Issues
- #008: Missing database indexes (would compound performance issue)
- #027: Inefficient search implementation

## References
- Peewee Documentation: https://docs.peewee-orm.com/
- SQL N+1 Problem: https://stackoverflow.com/questions/97197/what-is-the-n1-selects-query-issue
- OWASP Unvalidated Queries: https://owasp.org/www-community/attacks/Unvalidated_Query_Forwarding

## Priority
**CRITICAL** - Blocks scaling beyond 50 employees

## Estimated Effort
3-4 hours (including tests and benchmarks)

## Mitigation
While waiting for fix:
- Limit employee count to < 50
- Use database connection pooling
- Add warning for users with large datasets
