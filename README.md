# Wareflow EMS

**Warehouse Employee Management System** - Desktop application for warehouse employee management, CACES safety certification tracking, and medical compliance monitoring.

![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-40%25%20min-brightgreen.svg)

---

## 📖 Table of Contents

1. [Description](#-description)
2. [Features](#-features)
3. [Screenshots](#-screenshots)
4. [Prerequisites](#-prerequisites)
5. [Installation](#-installation)
6. [Usage](#-usage)
7. [Configuration](#-configuration)
8. [Project Structure](#-project-structure)
9. [Database](#-database)
10. [CLI Interface](#-cli-interface)
11. [Testing](#-testing)
12. [Development](#-development)
13. [Changelog](#-changelog)
14. [Roadmap](#-roadmap)
15. [Contributing](#-contributing)
16. [License](#-license)
17. [Contact](#-contact)

---

## 🎯 Description

Wareflow EMS is a modern Python desktop application designed for logistics and warehouse companies. It provides comprehensive management of:

- **Employee Management**: Complete administrative tracking (CDI, CDD, Temporary, Apprenticeship)
- **CACES Tracking**: French safety certifications (R489 categories: 1A, 1B, 3, 4, 5)
- **Medical Monitoring**: Compliance with French labor law medical examinations
- **Training Records**: Online training tracking with expiration monitoring
- **Smart Alerts**: Proactive notifications for upcoming expirations
- **Concurrent Access**: Multi-user support for network-shared deployments

**Technologies**: Python 3.14+, CustomTkinter, SQLite, Peewee ORM

---

## ✨ Features

### Employee Management
- ✅ Full CRUD (Create, Read, Update, Delete)
- ✅ Status tracking: Active/Inactive
- ✅ Contract types: CDI, CDD, Temporary, Apprenticeship, Internship
- ✅ Customizable workspaces and roles
- ✅ Automatic seniority calculation
- ✅ Contact information (email, phone)

### CACES Tracking
- ✅ 5 R489 categories (1A, 1B, 3, 4, 5)
- ✅ Automatic expiration calculation (5 or 10 years based on type)
- ✅ PDF document management
- ✅ Visual status (valid, warning, critical, expired)
- ✅ Proactive alerts before expiration

### Medical Visits
- ✅ 3 visit types: Initial, Periodic, Recovery
- ✅ Results: Fit, Unfit, Fit with restrictions
- ✅ Automatic expiration calculation (1-2 years)
- ✅ Business rules: Recovery visit requires restrictions
- ✅ Medical certificate storage

### Online Training
- ✅ Training tracking with optional validity
- ✅ Permanent training support
- ✅ Automatic expiration calculation
- ✅ Certificate secure storage

### Alert System
- ✅ 3 levels: Critical (< 7 days), Warning (< 30 days), Info (< 90 days)
- ✅ Filter by type (CACES, Medical, Training)
- ✅ Per-employee aggregation
- ✅ Excel alert export

### Excel Import/Export
- ✅ Batch import with validation
- ✅ Excel template generation
- ✅ Export with conditional formatting
- ✅ Multiple sheets (Summary, Employees, CACES, Visits, Training)

### Automatic Backups
- ✅ Startup backup
- ✅ Configurable retention (default: 30)
- ✅ Automatic old backup cleanup
- ✅ One-click restore

### Concurrent Access Control
- ✅ Database-backed locking
- ✅ Heartbeat every 30 seconds
- ✅ Stale lock detection (2 minutes)
- ✅ Read-only mode when locked by others

---

## 🖼️ Screenshots

*(Add 3-4 screenshots here)*

- Employee list with filters
- Employee detail view
- Alert dashboard
- CACES addition form

---

## 📦 Prerequisites

### Requirements

- **Python 3.14 or higher** (strict requirement)
- **Windows 10/11** (primary), macOS, Linux compatible
- **200 MB disk space**

### Optional

- **Network access** (for network share deployment)
- **PDF reader** (to view stored certificates)

---

## 🚀 Installation

### Method 1: uv (Recommended)

```bash
# Clone repository
git clone https://github.com/wareflowx/wareflow-ems.git
cd wareflow-ems

# Install dependencies
uv sync

# Launch application
uv run python -m src.main
```

### Method 2: pip

```bash
# Clone repository
git clone https://github.com/wareflowx/wareflow-ems.git
cd wareflow-ems

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Launch application
python -m src.main
```

### First Run

On first launch, the application will:
1. ✅ Automatically create `data/` directory
2. ✅ Initialize SQLite database
3. ✅ Create necessary tables
4. ✅ Create startup backup
5. ✅ Display main interface

**No configuration required!**

---

## 🎮 Usage

### Graphical Interface (GUI)

```bash
uv run python -m src.main
```

**Navigation**:
- **Employees**: Employee list and search
- **Alerts**: Upcoming expirations view
- **Excel Import**: Batch employee import
- **Backups**: Backup management

### Command Line Interface (CLI)

```bash
# Show help
uv run python src/cli_main.py --help

# List employees
uv run python src/cli_main.py employee list

# Add employee (interactive)
uv run python src/cli_main.py employee add

# Show employee details
uv run python src/cli_main.py employee show <employee-id>

# Add CACES
uv run python src/cli_main.py caces add <employee-id>

# Show alerts
uv run python src/cli_main.py report alerts --days 30

# Export to Excel
uv run python src/cli_main.py report export employees.xlsx

# Lock management
uv run python src/cli_main.py lock status
uv run python src/cli_main.py lock release
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file at project root:

```bash
# Database
DATABASE_PATH=data/employee_manager.db

# Or separate folder and name
DATABASE_DIR=data
DATABASE_NAME=employee_manager.db

# Application
APP_ENV=production
LOG_LEVEL=INFO

# Interface
APP_THEME=blue      # blue, green, dark-blue
APP_MODE=system     # light, dark, system
DEFAULT_WIDTH=1200
DEFAULT_HEIGHT=800
```

### Configuration File `config.json` (Optional)

```json
{
  "alerts": {
    "critical_days": 7,
    "warning_days": 30,
    "info_days": 90
  },
  "lock": {
    "timeout_minutes": 2,
    "heartbeat_interval_seconds": 30
  },
  "backup": {
    "max_backups": 30,
    "auto_backup_on_startup": true
  },
  "organization": {
    "roles": ["Cariste", "Préparateur", "Magasinier", "Réceptionnaire"],
    "workspaces": ["Quai", "Zone A", "Zone B", "Bureau"]
  }
}
```

---

## 📁 Project Structure

```
wareflow-ems/
├── src/
│   ├── cli/                    # Command-line interface
│   │   ├── employee.py         # Employee commands
│   │   ├── caces.py            # CACES commands
│   │   ├── medical.py          # Medical visit commands
│   │   ├── training.py         # Training commands
│   │   └── report.py           # Reports and exports
│   ├── controllers/            # Business logic layer
│   │   ├── employee_controller.py
│   │   ├── dashboard_controller.py
│   │   └── alerts_controller.py
│   ├── database/               # Database layer
│   │   └── connection.py       # SQLite connection with Peewee
│   ├── employee/               # Employee module (Entity-Oriented)
│   │   ├── models.py           # ORM models (560 lines)
│   │   ├── queries.py          # Complex queries
│   │   ├── calculations.py     # Business calculations
│   │   ├── validators.py       # Data validation
│   │   ├── constants.py        # Constants and enums
│   │   └── alerts.py           # Alert generation
│   ├── excel_import/           # Excel import
│   ├── export/                 # Excel export
│   ├── lock/                   # Concurrent access control
│   │   ├── models.py           # AppLock model
│   │   └── manager.py          # Lock manager
│   ├── ui_ctk/                 # CustomTkinter GUI
│   │   ├── app.py              # GUI entry point
│   │   ├── main_window.py      # Main window
│   │   ├── forms/              # Input forms
│   │   ├── views/              # Data views
│   │   └── widgets/            # Reusable components
│   ├── utils/                  # Utility functions
│   │   ├── config.py           # Configuration management
│   │   ├── validation.py       # Validation framework
│   │   ├── logging_config.py   # Logging setup
│   │   ├── files.py            # File operations
│   │   └── backup_manager.py   # Backup management
│   └── main.py                 # Main entry point
├── tests/                      # Test suite
│   ├── test_employee/          # Employee model tests
│   ├── test_cli/               # CLI tests
│   ├── test_integration/       # Integration tests
│   └── conftest.py             # Shared fixtures
├── docs/                       # Documentation (30+ files)
├── data/                       # SQLite database
├── documents/                  # Stored certificates
│   ├── caces/
│   ├── medical/
│   └── training/
├── backups/                    # Automatic backups
├── logs/                       # Logs with rotation
├── pyproject.toml              # Project metadata
├── .env.example                # Configuration template
└── README.md                   # This file
```

---

## 🗄️ Database

### Schema

**5 SQLite Tables** with foreign key relationships:

1. **employees**: Employee data
   - Fields: external_id, first_name, last_name, email, phone, status, workspace, role, contract_type, entry_date
   - Indexes: external_id (unique), status, workspace, role, contract_type

2. **caces**: Safety certifications
   - Relation: employee_id → employees.id (CASCADE DELETE)
   - Fields: kind, completion_date, expiration_date, document_path
   - Index: (employee_id, expiration_date)

3. **medical_visits**: Medical visits
   - Relation: employee_id → employees.id (CASCADE DELETE)
   - Fields: visit_type, visit_date, expiration_date, result, document_path
   - Index: (employee_id, expiration_date)

4. **online_trainings**: Online training
   - Relation: employee_id → employees.id (CASCADE DELETE)
   - Fields: title, completion_date, validity_months, expiration_date, certificate_path
   - Index: (employee_id, expiration_date)

5. **app_locks**: Concurrent access locks
   - Fields: hostname, username, locked_at, last_heartbeat, process_id
   - Indexes: hostname, locked_at, last_heartbeat

### Location

**Default**: `data/employee_manager.db`

**Customizable** via environment variables.

### Concurrency

- **WAL mode** (Write-Ahead Logging) for concurrent reads
- **PRAGMA foreign_keys = 1** for referential integrity
- **CASCADE DELETE**: Deleting an employee deletes all related data

---

## 💻 CLI Interface

### Available Commands

#### Employees
```bash
employee-manager employee list                    # List all employees
employee-manager employee show <id>               # Employee details
employee-manager employee add                     # Add (interactive)
employee-manager employee update <id>             # Update
employee-manager employee delete <id>             # Delete
```

#### CACES
```bash
employee-manager caces list                       # List all CACES
employee-manager caces add <employee-id>          # Add CACES
employee-manager caces expiring --days 30         # Expiring within 30 days
employee-manager caces expired                    # Expired CACES
```

#### Medical Visits
```bash
employee-manager medical list                     # List all visits
employee-manager medical add <employee-id>        # Add visit
employee-manager medical unfit                    # Unfit employees
employee-manager medical expiring --days 30       # Expiring within 30 days
```

#### Training
```bash
employee-manager training list                    # List all training
employee-manager training add <employee-id>       # Add training
employee-manager training expiring --days 60      # Expiring within 60 days
```

#### Reports
```bash
employee-manager report dashboard                 # Dashboard statistics
employee-manager report alerts --type caces       # CACES alerts
employee-manager report export output.xlsx       # Export to Excel
employee-manager report stats                     # Global statistics
```

#### Locks
```bash
employee-manager lock status                      # Lock status
employee-manager lock acquire                    # Acquire lock
employee-manager lock release                    # Release lock
employee-manager lock refresh                    # Refresh lock
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test
uv run pytest tests/test_employee/test_models.py

# Verbose mode
uv run pytest -v

# Stop on first error
uv run pytest -x
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_employee/           # Employee model tests
├── test_cli/                # CLI tests
├── test_export/             # Excel export tests
├── test_integration/        # Integration tests
├── test_lock/               # Lock mechanism tests
├── test_utils/              # Utility tests
└── test_ui/                 # GUI tests (excluded from CI)
```

### Coverage

**Minimum required**: 40%

**HTML report**: `htmlcov/index.html`

---

## 🔧 Development

### Code Style

**Linter**: Ruff
**Formatter**: Ruff

```bash
# Check style
uv run ruff check src/

# Auto-fix
uv run ruff check --fix src/

# Format code
uv run ruff format src/
```

### Contribution Workflow

1. Fork the project
2. Create a feature branch `feature/my-feature`
3. Make changes
4. Add tests
5. Run tests: `uv run pytest`
6. Check style: `uv run ruff check src/`
7. Commit with conventional message
8. Push and create Pull Request

### Commit Messages

Conventional commits recommended:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Refactoring
- `chore:` - Maintenance

### Build Executable

```bash
# Install PyInstaller
uv pip install pyinstaller

# Build
python build/build.py

# Output: dist/employee_manager.exe
```

---

## 📝 Changelog

### Version 1.0.0 (2025-01-22)

#### Added
- ✅ Complete employee management system
- ✅ CACES tracking with automatic expiration calculation
- ✅ Medical visit tracking
- ✅ Online training management
- ✅ Smart alert system
- ✅ Excel import/export
- ✅ Automatic backups
- ✅ Full CLI interface (30+ commands)
- ✅ Modern CustomTkinter GUI
- ✅ Concurrent access control
- ✅ Authentication system removed (OS-level access)

#### Fixed
- 🐛 Fixed datetime/date comparisons in computed properties
- 🐛 Fixed EmployeeController import path
- 🐛 Fixed validate_date to return date objects

#### Technical
- 📦 11,000+ lines of Python code
- 📦 80+ test files
- 📦 30+ documentation files
- 📦 Python 3.14+ required
- 📦 Test coverage: 40% minimum

---

## 🗺️ Roadmap

### Phase 1: Core Features ✅ (Complete)
- [x] Employee management
- [x] CACES tracking
- [x] Medical visits
- [x] Training
- [x] Alerts
- [x] CustomTkinter GUI
- [x] Complete CLI

### Phase 2: Advanced Features (In Progress)
- [ ] Undo/Redo functionality
- [ ] Soft delete with trash
- [ ] Optimistic locking
- [ ] Internationalization (i18n)
- [ ] Advanced theming

### Phase 3: Integration (Planned)
- [ ] REST API for remote access
- [ ] Web dashboard
- [ ] Mobile app (React Native)
- [ ] ERP/WMS integration

### Phase 4: Enterprise (Future)
- [ ] Multi-company support
- [ ] Advanced permissions
- [ ] Complete audit trail
- [ ] SSO integration
- [ ] High availability setup

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure tests pass
6. Submit a Pull Request

### Guidelines

- Follow existing code style (ruff)
- Write tests for new features
- Update documentation
- Atomic commits with clear messages

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Wareflow

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📧 Contact

- **Project**: https://github.com/wareflowx/wareflow-ems
- **Issues**: https://github.com/wareflowx/wareflow-ems/issues
- **Documentation**: https://github.com/wareflowx/wareflow-ems/tree/main/docs

---

## 🙏 Acknowledgments

- **Peewee ORM**: For the elegant and simple ORM
- **CustomTkinter**: For the modern UI framework
- **Typer**: For the beautiful CLI framework
- **uv**: For the ultra-fast package manager

---

**Built with ❤️ by Wareflow**
