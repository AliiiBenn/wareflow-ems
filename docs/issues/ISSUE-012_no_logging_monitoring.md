# [CRITICAL] No Logging or Monitoring System

## Type
**Observability / Debugging / Security Auditing**

## Severity
**CRITICAL** - No visibility into application behavior, security events, or errors

## Affected Components
- **ENTIRE APPLICATION** - No structured logging exists

## Description
The application has NO structured logging system. All output uses `print()` statements, which creates critical problems:

### Operational Issues
1. **No error tracking** - Cannot diagnose production issues
2. **No audit trail** - Cannot track who did what
3. **No security monitoring** - Cannot detect suspicious activity
4. **No performance metrics** - Cannot identify bottlenecks
5. **No usage analytics** - Cannot understand user behavior
6. **No crash diagnostics** - Cannot debug after crashes

### Development Issues
1. **Debugging impossible** - No logs to review
2. **Error messages lost** - Console output not captured
3. **Cannot reproduce bugs** - No context when issues occur
4. **No test coverage data** - Cannot see what code runs

### Security Issues
1. **No authentication logging** - Cannot detect unauthorized access
2. **No data modification tracking** - Cannot trace changes
3. **No failed operation logging** - Cannot detect attacks
4. **No exception tracking** - Cannot see security vulnerabilities

### Compliance Issues
1. **GDPR Article 30** - Requires record of processing activities
2. **ISO 27001** - Requires logging and monitoring
3. **SOC 2** - Requires audit trails
4. **No forensic evidence** - Cannot investigate incidents

## Current Code Analysis

### Print Statements Everywhere

```python
# Example 1: Employee creation
# src/controllers/employee_controller.py:85-87
def create_employee(**kwargs) -> Employee:
    employee = Employee.create(**kwargs)
    print(f"[OK] Employee created: {employee.full_name}")  # ← Lost if console closed!
    return employee

# Problems:
# - Log level not specified (is this info? debug? warning?)
# - No timestamp
# - No context (who created? when? from where?)
# - Not captured to file
# - Lost on application restart
```

```python
# Example 2: Error handling
# src/ui_ctk/forms/employee_form.py:514-517
try:
    # ... code ...
except:
    print(f"[ERROR] {message}")  # ← What error? When? Context?
    # ↑ Stack trace lost
    # ↑ No error details
    # ↑ No context

# Problems:
# - Stack trace not logged
# - Exception type unknown
# - No line numbers
# - No call stack
# - Cannot reproduce or debug
```

```python
# Example 3: Database operations
# src/database/connection.py:28-35
def init_database(db_path):
    # ... create tables ...
    database.connect()
    print("[OK] Database connected")  # ← Connection details lost

    # ... create tables ...
    print(f"[OK] Created {len(tables)} tables")  # ← Which tables?

# Problems:
# - No database path logged
# - No connection parameters
# - No table names
# - No timing information
# - Cannot diagnose connection issues
```

## What's Missing

### 1. Structured Logging
```python
# Current (BAD)
print(f"[OK] Employee created: {employee.full_name}")

# Should be (GOOD)
logger.info(
    "Employee created",
    extra={
        'employee_id': employee.id,
        'employee_name': employee.full_name,
        'user': current_user.id if current_user else None,
        'ip_address': request.remote_addr if web else None,
        'timestamp': datetime.now().isoformat(),
    }
)
```

### 2. Log Levels
Currently, all output uses same level (everything printed):

```python
# No distinction between:
print("[INFO] Application starting")     # Information
print("[WARN] Database slow")            # Warning
print("[ERROR] Failed to load")          # Error
print("[CRITICAL] Database corrupted")   # Critical

# ↑ All treated the same! No filtering!
```

### 3. Log Destinations
```python
# Current: Only prints to console
print("[INFO] Something happened")

# Missing:
# - File logging (persistent)
# - Rotating logs (manage disk space)
# - Remote logging (centralized monitoring)
# - Error tracking services (Sentry, Rollbar)
```

### 4. Contextual Information
```python
# Current: No context
print("[ERROR] Failed to delete employee")

# Should include:
# - Who: user_id, username, role
# - What: employee_id, operation
# - When: timestamp
# - Where: function, file, line_number
# - Why: error_message, stack_trace
# - Related data: request_id, session_id
```

### 5. Performance Logging
```python
# Current: No timing information
employees = list(Employee.select())
print(f"[OK] Loaded {len(employees)} employees")
# ↑ How long did it take? Was it slow?

# Should log:
# - Query duration
# - Memory usage
# - Database query count
# - API response times
```

### 6. Security Event Logging
```python
# Security events that SHOULD be logged but aren't:
# - Failed login attempts
# - Permission denied
# - Data export (GDPR)
# - Employee deletion
# - Bulk operations
# - Database connection failures
# - File access violations
```

## Real-World Scenarios

### Scenario 1: Production Issue
```
Day 1: Application deployed to production
Day 15: User reports "Can't add employees"
IT: Checks logs → No logs exist!
Developer: "What error do you see?"
User: "Just says 'Failed'"
Developer: Cannot diagnose without logs
Result: Days of debugging, production downtime
```

### Scenario 2: Security Incident
```
Incident: Someone deleted all employees
Security: "When did this happen?"
IT: "We don't have logs"
Security: "Who did it?"
IT: "We don't track user actions"
Security: "Can we trace the changes?"
IT: "No audit trail exists"
Result: Cannot investigate, cannot prevent recurrence
```

### Scenario 3: Performance Degradation
```
User: "Application is slow"
Developer: "What's slow?"
User: "Everything"
Developer: Checks code → No timing logs
Developer: "I don't know where to optimize"
Result: Performance issues remain unresolved
```

### Scenario 4: Compliance Audit
```
Auditor: "Show me your processing activity logs"
IT: "We don't have logging"
Auditor: "How do you track data access?"
IT: "We don't"
Auditor: "GDPR Article 30 requires records of processing activities"
IT: "..."
Result: Non-compliance, potential fines
```

### Scenario 5: Bug Report
```
User: "Application crashed when I added an employee"
Developer: "What was the error?"
User: "I don't remember, it closed too fast"
Developer: Checks logs → No logs
Developer: "I can't reproduce without error details"
Result: Bug cannot be fixed, user frustration
```

## Proposed Solution

### Part 1: Structured Logging Setup

```python
# src/utils/logging_config.py
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import json

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured log output."""

    def format(self, record):
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info),
            }

        # Add extra context
        if hasattr(record, 'employee_id'):
            log_entry['employee_id'] = record.employee_id
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address

        return json.dumps(log_entry, ensure_ascii=False)

class ColoredConsoleFormatter(logging.Formatter):
    """Colored formatter for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = record.levelname
        logger = record.name
        message = record.getMessage()

        return f"{color}[{timestamp}] {level:8} {logger}: {message}{self.RESET}"

def setup_logging(
    log_level: str = "INFO",
    log_dir: Path = Path("logs"),
    enable_console: bool = True,
    enable_file: bool = True,
    max_file_size_mb: int = 10,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_console: Enable console output
        enable_file: Enable file output
        max_file_size_mb: Maximum log file size before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured root logger
    """
    # Create log directory
    log_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredConsoleFormatter())
        root_logger.addHandler(console_handler)

    # File handler (structured JSON)
    if enable_file:
        log_file = log_dir / f"wareflow_ems_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8',
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)

    # Error file handler (separate file for errors)
    if enable_file:
        error_file = log_dir / f"wareflow_ems_errors_{datetime.now().strftime('%Y%m%d')}.log"

        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8',
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(error_handler)

    return root_logger

# Create logger for application
logger = logging.getLogger('wareflow_ems')
```

### Part 2: Logging in Application Code

```python
# src/controllers/employee_controller.py
import logging

logger = logging.getLogger('wareflow_ems.controllers.employee')

def create_employee(**kwargs) -> Employee:
    """Create employee with logging."""
    try:
        logger.info(
            "Creating employee",
            extra={
                'operation': 'create_employee',
                'employee_data': {
                    'first_name': kwargs.get('first_name'),
                    'last_name': kwargs.get('last_name'),
                    'email': kwargs.get('email'),
                }
            }
        )

        employee = Employee.create(**kwargs)

        logger.info(
            "Employee created successfully",
            extra={
                'operation': 'create_employee',
                'employee_id': str(employee.id),
                'employee_name': employee.full_name,
            }
        )

        return employee

    except Exception as e:
        logger.error(
            "Failed to create employee",
            extra={
                'operation': 'create_employee',
                'employee_data': kwargs,
                'error_type': type(e).__name__,
                'error_message': str(e),
            },
            exc_info=True  # Include stack trace
        )
        raise

def delete_employee(employee: Employee):
    """Delete employee with audit logging."""
    logger.info(
        "Deleting employee",
        extra={
            'operation': 'delete_employee',
            'employee_id': str(employee.id),
            'employee_name': employee.full_name,
            'caces_count': employee.caces.count(),
            'visits_count': employee.medical_visits.count(),
        }
    )

    try:
        employee.delete_instance()

        logger.warning(
            "Employee deleted",
            extra={
                'operation': 'delete_employee',
                'employee_id': str(employee.id),
                'employee_name': employee.full_name,
            }
        )

    except Exception as e:
        logger.error(
            "Failed to delete employee",
            extra={
                'operation': 'delete_employee',
                'employee_id': str(employee.id),
                'error_type': type(e).__name__,
                'error_message': str(e),
            },
            exc_info=True
        )
        raise
```

### Part 3: Performance Logging

```python
# src/utils/performance_logger.py
import logging
import time
from functools import wraps
from typing import Callable

logger = logging.getLogger('wareflow_ems.performance')

def log_performance(operation_name: str):
    """Decorator to log function execution time."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                elapsed_ms = (time.time() - start_time) * 1000

                # Log performance
                if elapsed_ms > 1000:  # Slow operation
                    logger.warning(
                        f"Slow operation: {operation_name}",
                        extra={
                            'operation': operation_name,
                            'duration_ms': round(elapsed_ms, 2),
                            'slow': True,
                        }
                    )
                else:
                    logger.debug(
                        f"Operation: {operation_name}",
                        extra={
                            'operation': operation_name,
                            'duration_ms': round(elapsed_ms, 2),
                        }
                    )

                return result

            except Exception as e:
                elapsed_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Operation failed: {operation_name}",
                    extra={
                        'operation': operation_name,
                        'duration_ms': round(elapsed_ms, 2),
                        'error': str(e),
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator

# Usage
@log_performance("load_employee_list")
def get_all_employees():
    return list(Employee.select())

@log_performance("import_excel")
def import_from_excel(file_path: str):
    # ... import logic
    pass
```

### Part 4: Security Event Logging

```python
# src/utils/security_logger.py
import logging
from typing import Optional

logger = logging.getLogger('wareflow_ems.security')

def log_security_event(
    event_type: str,
    description: str,
    severity: str = "info",
    **context
):
    """
    Log security-related events.

    Args:
        event_type: Type of security event (login, access_denied, data_export, etc.)
        description: Human-readable description
        severity: info, warning, critical
        **context: Additional context (user_id, ip_address, etc.)
    """
    log_func = {
        'info': logger.info,
        'warning': logger.warning,
        'critical': logger.critical,
    }.get(severity, logger.info)

    log_func(
        f"Security: {description}",
        extra={
            'security_event': True,
            'event_type': event_type,
            'severity': severity,
            **context
        }
    )

# Usage examples
def log_failed_login(username: str, reason: str):
    log_security_event(
        event_type='failed_login',
        description=f"Failed login attempt for user: {username}",
        severity='warning',
        username=username,
        reason=reason,
    )

def log_data_export(employee_id: str, export_type: str):
    log_security_event(
        event_type='data_export',
        description=f"Employee data exported: {employee_id}",
        severity='info',
        employee_id=employee_id,
        export_type=export_type,
    )

def log_bulk_operation(operation: str, count: int, user_id: Optional[str] = None):
    log_security_event(
        event_type='bulk_operation',
        description=f"Bulk {operation} affecting {count} records",
        severity='warning',
        operation=operation,
        record_count=count,
        user_id=user_id,
    )

def log_permission_denied(resource: str, action: str, user_id: Optional[str] = None):
    log_security_event(
        event_type='permission_denied',
        description=f"Permission denied: {action} on {resource}",
        severity='warning',
        resource=resource,
        action=action,
        user_id=user_id,
    )
```

### Part 5: Application Initialization

```python
# src/ui_ctk/app.py
from src.utils.logging_config import setup_logging

def main():
    """Application entry point with logging."""
    # Setup logging FIRST
    logger = setup_logging(
        log_level="INFO",
        log_dir=Path("logs"),
        enable_console=True,
        enable_file=True,
    )

    logger.info("Application starting")

    try:
        # Initialize database
        setup_database()

        # Create and run application
        app = WareflowEMS()
        logger.info("Application initialized successfully")

        app.mainloop()

    except Exception as e:
        logger.critical(
            "Application crashed",
            exc_info=True,
            extra={'error_type': type(e).__name__, 'error_message': str(e)}
        )
        raise

    finally:
        logger.info("Application shutting down")
```

## Implementation Plan

### Phase 1: Logging Infrastructure (2 hours)
1. Create `src/utils/logging_config.py`
2. Create `src/utils/performance_logger.py`
3. Create `src/utils/security_logger.py`
4. Setup log rotation
5. Write tests

### Phase 2: Replace Print Statements (3 hours)
1. Find all `print()` statements
2. Replace with proper logging
3. Add context to logs
4. Update error handling
5. Test log output

### Phase 3: Add Performance Logging (1 hour)
1. Add decorators to slow operations
2. Log database query times
3. Log import/export times
4. Monitor application startup

### Phase 4: Add Security Logging (1 hour)
1. Log all data modifications
2. Log destructive operations
3. Log bulk operations
4. Log failed operations

## Files to Create
- `src/utils/logging_config.py`
- `src/utils/performance_logger.py`
- `src/utils/security_logger.py`
- `tests/test_logging_config.py`
- `logs/.gitignore` (add: `*.log`)

## Files to Modify
- Replace `print()` in ~50 files
- `src/ui_ctk/app.py` - Setup logging
- `src/controllers/*.py` - Add operation logging
- `src/ui_ctk/forms/*.py` - Add form logging

## Log Files Structure

```
logs/
├── wareflow_ems_20250121.log          # All logs (JSON)
├── wareflow_ems_errors_20250121.log   # Errors only (JSON)
├── wareflow_ems_20250120.log.1        # Rotated logs
├── wareflow_ems_20250120.log.2
└── wareflow_ems_20250120.log.3
```

## Log Entry Examples

### Information Log
```json
{
  "timestamp": "2025-01-21T14:30:45.123456",
  "level": "INFO",
  "logger": "wareflow_ems.controllers.employee",
  "message": "Employee created successfully",
  "module": "employee_controller",
  "function": "create_employee",
  "line": 95,
  "employee_id": "wms-001",
  "employee_name": "Dupont Jean",
  "operation": "create_employee"
}
```

### Error Log
```json
{
  "timestamp": "2025-01-21T14:35:12.789012",
  "level": "ERROR",
  "logger": "wareflow_ems.controllers.employee",
  "message": "Failed to create employee",
  "module": "employee_controller",
  "function": "create_employee",
  "line": 105,
  "operation": "create_employee",
  "error_type": "IntegrityError",
  "error_message": "UNIQUE constraint failed: employees.external_id",
  "exception": {
    "type": "IntegrityError",
    "message": "UNIQUE constraint failed: employees.external_id",
    "traceback": "Traceback (most recent call last):\n  File ..."
  }
}
```

### Security Log
```json
{
  "timestamp": "2025-01-21T14:40:00.000000",
  "level": "WARNING",
  "logger": "wareflow_ems.security",
  "message": "Security: Employee deleted",
  "module": "security_logger",
  "function": "log_security_event",
  "line": 42,
  "security_event": true,
  "event_type": "employee_deletion",
  "severity": "warning",
  "employee_id": "wms-001",
  "employee_name": "Dupont Jean",
  "caces_count": 3,
  "visits_count": 2,
  "user_id": "admin"
}
```

## Log Analysis Tools

### Search Logs
```bash
# Find all errors
grep '"level": "ERROR"' logs/wareflow_ems_*.log

# Find operations for specific employee
grep '"employee_id": "wms-001"' logs/wareflow_ems_*.log

# Find security events
grep '"security_event": true' logs/wareflow_ems_*.log

# Find slow operations
grep '"slow": true' logs/wareflow_ems_*.log
```

### Monitoring Dashboard
```python
# src/utils/log_analyzer.py
import json
from pathlib import Path
from collections import Counter

def analyze_logs(log_dir: Path):
    """Analyze log files for insights."""
    log_files = sorted(log_dir.glob("wareflow_ems_*.log"))

    error_counts = Counter()
    operation_counts = Counter()
    security_events = []

    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)

                    # Count errors
                    if entry.get('level') == 'ERROR':
                        error_type = entry.get('error_type', 'Unknown')
                        error_counts[error_type] += 1

                    # Count operations
                    if 'operation' in entry:
                        operation_counts[entry['operation']] += 1

                    # Track security events
                    if entry.get('security_event'):
                        security_events.append(entry)

                except json.JSONDecodeError:
                    continue

    return {
        'error_counts': dict(error_counts.most_common(10)),
        'operation_counts': dict(operation_counts.most_common(10)),
        'security_event_count': len(security_events),
    }
```

## Related Issues
- #010: Broad exception handling (logging provides stack traces)
- #007: No undo/redo (logging provides audit trail)
- #003: No authentication (logging tracks access)
- #011: No backups (logging monitors backup operations)

## References
- Python Logging Documentation: https://docs.python.org/3/library/logging.html
- Logging Best Practices: https://docs.python.org/3/howto/logging.html
- GDPR Article 30: https://gdpr-info.eu/art-30-gdpr/
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

## Priority
**CRITICAL** - No visibility into application behavior

## Estimated Effort
7-8 hours (setup + replace prints + tests)

## Mitigation
While waiting for full implementation:
1. **Redirect stdout to file**:
   ```bash
   python -m src.main > logs/app.log 2>&1
   ```

2. **Use script command** (Linux/Mac):
   ```bash
   script logs/session.log
   python -m src.main
   exit
   ```

3. **Use PowerShell logging** (Windows):
   ```powershell
   Start-Transcript -Path logs\session.log
   python -m src.main
   Stop-Transcript
   ```

4. **Add basic logging** to critical operations:
   - Database initialization
   - Import/export operations
   - Employee creation/deletion
   - Error conditions

5. **Document troubleshooting procedures** without logs
6. **Enable debug mode** when issues occur
