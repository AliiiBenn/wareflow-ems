# [CRITICAL] Hardcoded Database Path

## Type
**Configuration / Deployment**

## Severity
**CRITICAL** - Blocks deployment flexibility, environment separation

## Affected Components
- `src/ui_ctk/app.py` (lines 42, 111)
- `src/database/connection.py` (line 8)
- Potentially throughout codebase

## Description
The database file path is hardcoded to `"employee_manager.db"` in multiple places. This creates several critical problems:

### Deployment Issues
1. **Cannot have separate databases** for:
   - Development vs Production
   - Testing vs Staging vs Production
   - Different customers/installations

2. **No multi-tenancy support** - Cannot isolate data per client

3. **Cloud deployment blocked** - Database must be at specific relative path

4. **Installation conflicts** - Cannot install in non-writable directories

### Operational Issues
1. **No environment-specific configuration**
2. **Cannot change database location without code changes**
3. **Cannot use alternative databases (PostgreSQL, MySQL)**
4. **Database path conflicts with multiple instances**

## Problematic Code

### app.py:42
```python
def setup_database(db_path: str = "employee_manager.db"):
    # ↑ Hardcoded default path - should come from config
```

### app.py:111
```python
def main():
    # ...
    # Step 2: Setup database
    setup_database()  # ← Uses hardcoded path!
```

### connection.py:8
```python
database = SqliteDatabase(None, pragmas={'foreign_keys': 1})
# ↑ 'None' means current directory, path not configurable
```

## Current Behavior
```bash
$ cd /home/user/wareflow-ems
$ python -m src.main
# Creates employee_manager.db in current directory

$ cd /var/wareflow-ems
$ python -m src.main
# ALSO tries to create employee_manager.db in current directory
# But might not have write permissions!
```

## Deployment Scenarios Broken

### Scenario 1: Production Server
```
Server: /opt/wareflow-ems/
Database must be in: /var/lib/wareflow-ems/employee_manager.db
Problem: App tries to write to /opt/wareflow-ems/employee_manager.db
Result: Permission denied, application crashes
```

### Scenario 2: Development vs Production
```
Developer: ~/dev/wareflow-ems/ (uses employee_manager.db)
Production: /opt/wareflow-ems/ (needs employee_manager_prod.db)
Problem: Both apps would use same DB filename, causing confusion
Result: Could accidentally overwrite production DB during dev
```

### Scenario 3: Cloud Deployment
```
Container: Read-only filesystem (except /data)
Database must be: /data/employee_manager.db
Problem: Code doesn't support DATABASE_PATH env var
Result: Cannot deploy to cloud without code changes
```

## Proposed Solution

### Option 1: Environment Variables (Recommended)

#### Configuration File: `.env`
```bash
# Database configuration
DATABASE_PATH=employee_manager.db
DATABASE_DIR=./data

# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
```

#### Configuration Loader: `src/config.py`
```python
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    """Application configuration from environment variables."""

    # Database
    DATABASE_DIR: Path = Path(os.getenv('DATABASE_DIR', './data'))
    DATABASE_NAME: str = os.getenv('DATABASE_NAME', 'employee_manager.db')
    DATABASE_PATH: Path = DATABASE_DIR / DATABASE_NAME

    # Application
    APP_ENV: str = os.getenv('APP_ENV', 'development')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    # UI
    DEFAULT_WIDTH: int = 1200
    DEFAULT_HEIGHT: int = 800
    APP_THEME: str = os.getenv('APP_THEME', 'blue')
    APP_MODE: str = os.getenv('APP_MODE', 'dark')

    @classmethod
    def init_database_directory(cls) -> None:
        """Ensure database directory exists."""
        cls.DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_database_path(cls) -> Path:
        """Get full database path, ensuring directory exists."""
        cls.init_database_directory()
        return cls.DATABASE_PATH
```

#### Updated Application Code
```python
# src/ui_ctk/app.py
from src.config import Config

def setup_database():
    """Initialize database connection from configuration."""
    db_path = Config.get_database_path()

    if not db_path.exists():
        print(f"[WARN] Database not found: {db_path}")
        print(f"[INFO] Creating new database: {db_path}")

    try:
        init_database(db_path)
        # ... rest of setup
```

### Option 2: Configuration File

#### Config File: `config.yaml`
```yaml
database:
  path: data/employee_manager.db
  backup_enabled: true
  backup_schedule: daily

application:
  environment: production
  debug: false
  log_level: INFO

ui:
  theme: dark
  language: fr
```

### Option 3: Command-Line Arguments

```python
# src/ui_ctk/app.py
import argparse

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Wareflow EMS')
    parser.add_argument('--db-path', type=str,
                       default='data/employee_manager.db',
                       help='Path to SQLite database file')
    parser.add_argument('--config', type=str,
                       help='Path to configuration file')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    return parser.parse_args()

def main():
    args = parse_args()
    setup_database(args.db_path)
    # ...
```

## Implementation Plan

### Phase 1: Add Configuration Module (2 hours)
1. Create `src/config.py`
2. Add `python-dotenv` to dependencies
3. Create `.env.example` template
4. Update application to use Config

### Phase 2: Update Database Setup (1 hour)
1. Modify `setup_database()` to use Config
2. Update `connection.py` to use Config
3. Ensure database directory creation
4. Add path validation

### Phase 3: Add Environment Validation (1 hour)
1. Validate DATABASE_PATH is not in system directory
2. Check parent directory is writable
3. Create data directory if missing
4. Add helpful error messages

### Phase 4: Documentation (30 min)
1. Create `.env.example` with all options
2. Update README with configuration guide
3. Add deployment documentation

## Files to Create
- `src/config.py`
- `.env.example`
- `config.example.yaml` (if using YAML config)
- `tests/test_config.py`

## Files to Modify
- `src/ui_ctk/app.py`
- `src/database/connection.py`
- `src/employee/models.py` (uses database)

## Environment Variables

### Required
None (has sensible defaults)

### Optional
- `DATABASE_PATH` - Path to database file (default: `data/employee_manager.db`)
- `DATABASE_DIR` - Directory for databases (default: `data/`)
- `DATABASE_NAME` - Database filename (default: `employee_manager.db`)
- `APP_ENV` - Environment: development, staging, production (default: `development`)
- `DEBUG` - Enable debug mode (default: `false`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `APP_THEME` - UI theme: blue, green, dark-blue (default: `blue`)
- `APP_MODE` - UI mode: light, dark, system (default: `dark`)

## Deployment Examples

### Development
```bash
# Uses default: data/employee_manager.db
python -m src.main
```

### Production
```bash
# Custom database location
DATABASE_PATH=/var/lib/wareflow-ems/employee_manager.db \
APP_ENV=production \
DEBUG=false \
python -m src.main
```

### Docker
```dockerfile
ENV DATABASE_PATH=/data/employee_manager.db
ENV APP_ENV=production

VOLUME ["/data"]
```

### Windows Service
```ini
[Service]
Environment="DATABASE_PATH=C:\\ProgramData\\WareflowEMS\\employee_manager.db"
Environment="APP_ENV=production"
ExecStart=python -m src.main
```

## Configuration Validation

```python
def validate_config(config: Config) -> tuple[bool, str]:
    """Validate configuration before application starts."""
    errors = []

    # Check database path is not in system directory
    system_paths = ['/usr', '/bin', '/sbin', '/etc', '/var']
    if any(str(config.DATABASE_PATH).startswith(path) for path in system_paths):
        errors.append("Database path cannot be in system directory")

    # Check parent directory is writable
    if not config.DATABASE_DIR.exists():
        try:
            config.DATABASE_DIR.mkdir(parents=True)
        except Exception as e:
            errors.append(f"Cannot create database directory: {e}")
    else:
        if not os.access(config.DATABASE_DIR, os.W_OK):
            errors.append(f"Database directory not writable: {config.DATABASE_DIR}")

    if errors:
        return False, "; ".join(errors)

    return True, None
```

## Testing Requirements
- Test with custom DATABASE_PATH
- Test with non-existent directory (should create)
- Test with read-only directory (should fail gracefully)
- Test with relative path
- Test with absolute path
- Test environment variable overrides
- Test .env file loading

## Dependencies
```toml
# pyproject.toml
[project.optional-dependencies]
config = [
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",  # If using YAML config
]
```

## Related Issues
- #010: No secrets management (database credentials would go here too)
- #040: No configuration file support

## Priority
**CRITICAL** - Blocks flexible deployment

## Estimated Effort
4-5 hours (including tests and documentation)

## Mitigation
While waiting for fix:
- Document database location in README
- Ensure write permissions to application directory
- Use symbolic links for alternative locations
- Add setup script that creates directory before launching
