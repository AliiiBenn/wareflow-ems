# BOOTSTRAPPER & TOOLKIT ANALYSIS

## 🎯 PROJECT NATURE REVELATION

**This is NOT just a desktop application - it's a DEPLOYMENT TOOLKIT.**

The real product is a **complete system** that can generate standalone, deployable employee management instances with a single command.

---

## 📊 WHAT THIS PROJECT ACTUALLY IS

### **My Previous Understanding (WRONG):**
- A simple desktop app to manage employees
- One database, one installation
- CustomTkinter UI is just for this one app

### **The Actual Reality (CORRECT):**
- A **bootstrapper/toolkit** that creates NEW project instances
- Each instance is a **complete standalone deployment**
- Like a "franchise" system - one template, many independent instances

---

## 🏗️ THE COMPLETE SYSTEM ARCHITECTURE

### **1. Development Repository (THIS CODEBASE)**

```
wareflow-ems/                    # Git repository
├── src/                         # Source code (the "product")
│   ├── ui_ctk/                  # CustomTkinter UI app
│   ├── employee/                # Business logic
│   ├── controllers/             # Data access
│   ├── state/                   # Global state
│   ├── database/                # DB setup
│   ├── lock/                    # Locking system
│   └── utils/                   # Helpers
│
├── bootstrapper/                # 🆕 PROJECT GENERATOR
│   ├── main.py                  # CLI entry point
│   ├── creator.py               # Instance creation logic
│   └── templates/               # File templates
│       ├── config.json.template
│       └── README.md.template
│
├── build/                       # 🆕 BUILD SYSTEM
│   ├── build.py                 # PyInstaller script
│   └── build.spec               # PyInstaller config
│
├── tests/                       # Test suite
├── docs/                        # Documentation
└── pyproject.toml              # Dependencies
```

---

### **2. Deployed Instance (WHAT THE BOOTSTRAPPER CREATES)**

Every time someone runs the bootstrapper, they get:

```
[Gestion_Salaries_SiteA]/         # Instance name
├── data/
│   └── employee_manager.db      # SQLite DB (local to this instance)
│
├── documents/                    # All uploaded files
│   ├── caces/                   # CACES certificates
│   ├── medical/                 # Medical visit reports
│   ├── training/                # Training certificates
│   └── avatars/                 # Employee photos
│
├── exports/                      # Generated Excel files
│
├── logs/                         # Application logs
│
├── src/
│   └── employee_manager.exe     # Compiled CustomTkinter app
│
├── config.json                   # Instance configuration
└── README.md                     # User documentation
```

**This is a COMPLETE, INDEPENDENT application instance.**

---

## 🔄 THE COMPLETE WORKFLOW

### **Phase 1: Development (Our Current State)**

```bash
# Developer works in this repo
cd wareflow-ems/

# 1. Write CustomTkinter UI code
#    src/ui_ctk/app.py
#    src/ui_ctk/views.py
#    src/ui_ctk/dialogs.py

# 2. Write bootstrapper logic
#    bootstrapper/creator.py

# 3. Write build script
#    build/build.py

# 4. Test everything
uv run pytest

# 5. Build executable
python build/build.py
# → Generates: build/dist/employee_manager.exe
```

---

### **Phase 2: Instance Creation (Admin/User)**

```bash
# Administrator runs bootstrapper
python bootstrapper/main.py create "Gestion_Salaries_SiteA"

# Bootstrapper does:
✅ Create folder structure
✅ Initialize database
✅ Copy config.json template
✅ Copy README.md
✅ Prepare src/ folder for .exe
```

---

### **Phase 3: Build & Deploy**

```bash
# Developer builds the executable
python build/build.py --output build/dist/employee_manager.exe

# Administrator copies to network share
cp build/dist/employee_manager.exe /path/to/Gestion_Salaries_SiteA/src/

# OR: Build directly into the instance
python build/build.py --target Gestion_Salaries_SiteA/src/
```

---

### **Phase 4: End User Usage**

```bash
# End user on network drive
cd Z:/Gestion_Salaries_SiteA/

# Double-click employee_manager.exe
# → App starts
# → Connects to data/employee_manager.db
# → Manages employees
# → Uploads documents to documents/
# → Exports to exports/
```

---

## 🎨 THE CUSTOMTKINTER UI'S ROLE

### **Critical Design Requirements:**

#### **1. PORTABILITY**
The .exe must work **anywhere** without installation:
- On network drives (Z:, \\server\share)
- On local drives (C:)
- On different computers
- **NO hardcoded paths**

**Solution:** Use relative paths from executable location
```python
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    BASE_DIR = Path(sys.executable).parent
else:
    # Running in development
    BASE_DIR = Path(__file__).parent.parent

DB_PATH = BASE_DIR / "data" / "employee_manager.db"
DOCUMENTS_DIR = BASE_DIR / "documents"
```

---

#### **2. CONFIGURATION DRIVEN**
The app reads `config.json` at startup:

```python
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

# Use config values
ALERT_THRESHOLDS = CONFIG.get("alert_thresholds_days", [30, 60, 90])
ROLES = CONFIG.get("roles", ["Préparateur", "Cariste"])
WORKSPACES = CONFIG.get("workspaces", ["Quai", "Zone A"])
```

**This allows customization WITHOUT recompiling!**

---

#### **3. DOCUMENTS MANAGEMENT**
When users upload files:

```python
def handle_caces_upload(employee_id, file_path):
    """Handle CACES certificate upload."""
    # Get documents directory
    documents_dir = BASE_DIR / "documents" / "caces"
    documents_dir.mkdir(parents=True, exist_ok=True)

    # Copy and rename file
    dest = documents_dir / f"CACES_{employee_id}_{date.today()}.pdf"
    shutil.copy2(file_path, dest)

    # Store RELATIVE path in DB
    relative_path = dest.relative_to(BASE_DIR)
    caces.document_path = str(relative_path)
    caces.save()
```

**Why copy?**
- Centralized document storage
- Standardized naming
- Portable (relative paths)
- Backup-friendly

---

#### **4. LOCKING SYSTEM**
Multi-user safety (mentioned in PROJECT.md):

```python
# On app startup
lock_manager = LockManager()
if not lock_manager.acquire_lock():
    show_readonly_mode()  # Or show error
    return

# Every 30 seconds
lock_manager.update_heartbeat()

# On app close
lock_manager.release_lock()
```

This prevents DB corruption when multiple users access the network share.

---

## 📦 THE BOOTSTRAPPER: WHAT IT MUST DO

### **bootstrapper/main.py**

```python
"""Bootstrapper entry point."""

import click
from .creator import ProjectCreator

@click.group()
def cli():
    """Wareflow EMS Bootstrapper."""
    pass

@cli.command()
@click.argument('project_name')
@click.option('--path', default='.', help='Parent directory')
def create(project_name, path):
    """Create a new Wareflow EMS instance."""
    creator = ProjectCreator(project_name, path)
    creator.create_instance()
    click.echo(f"✅ Instance created: {project_name}")

@cli.command()
@click.argument('exe_path')
@click.argument('target_instance')
def deploy(exe_path, target_instance):
    """Deploy compiled .exe to an instance."""
    creator = ProjectCreator(target_instance)
    creator.deploy_executable(exe_path)
    click.echo(f"✅ Deployed to {target_instance}")

if __name__ == '__main__':
    cli()
```

---

### **bootstrapper/creator.py**

```python
"""Project instance creator."""

import shutil
from pathlib import Path

class ProjectCreator:
    def __init__(self, project_name: str, parent_path: str = '.'):
        self.project_name = project_name
        self.project_path = Path(parent_path) / project_name
        self.templates_dir = Path(__file__).parent / 'templates'

    def create_instance(self):
        """Create a complete project instance."""
        # 1. Create directory structure
        self._create_directories()

        # 2. Copy templates
        self._copy_templates()

        # 3. Initialize database
        self._init_database()

        # 4. Create placeholder for .exe
        self._create_exe_placeholder()

        print(f"✅ Instance '{self.project_name}' created at {self.project_path}")

    def _create_directories(self):
        """Create required directory structure."""
        dirs = [
            'data',
            'documents/caces',
            'documents/medical',
            'documents/training',
            'documents/avatars',
            'exports',
            'logs',
            'src',
        ]

        for dir_path in dirs:
            (self.project_path / dir_path).mkdir(parents=True, exist_ok=True)
            print(f"  Created: {dir_path}/")

    def _copy_templates(self):
        """Copy configuration templates."""
        # Copy config.json
        shutil.copy(
            self.templates_dir / 'config.json.template',
            self.project_path / 'config.json'
        )

        # Copy README.md
        shutil.copy(
            self.templates_dir / 'README.md.template',
            self.project_path / 'README.md'
        )

    def _init_database(self):
        """Initialize SQLite database."""
        from database.connection import init_database

        db_path = self.project_path / 'data' / 'employee_manager.db'
        init_database(db_path)

        print(f"  Database: {db_path}")

    def _create_exe_placeholder(self):
        """Create placeholder for executable."""
        placeholder = self.project_path / 'src' / 'employee_manager.exe'
        placeholder.write_text('# PLACEHOLDER\n# Build with: python build/build.py\n')
        print(f"  EXE placeholder: {placeholder}")

    def deploy_executable(self, exe_path: str):
        """Deploy compiled .exe to instance."""
        exe = Path(exe_path)
        target = self.project_path / 'src' / 'employee_manager.exe'

        shutil.copy2(exe, target)
        print(f"✅ Deployed: {exe} → {target}")
```

---

## 🔨 THE BUILD SYSTEM: WHAT IT MUST DO

### **build/build.py**

```python
"""PyInstaller build script."""

import PyInstaller.__main__
import sys
from pathlib import Path

def build():
    """Build CustomTkinter executable."""

    # PyInstaller arguments
    args = [
        # Source
        'src/ui_ctk/app.py',  # Entry point

        # Output
        '--name=employee_manager',
        '--onefile',              # Single .exe
        '--windowed',             # No console
        '--distpath=build/dist',
        '--workpath=build/build',

        # Include data
        '--add-data=config.json;.',  # Include default config

        # Hidden imports (CustomTkinter, etc.)
        '--hidden-import=customtkinter',
        '--hidden-import=tkinter',
        '--hidden-import=peewee',

        # Icon (if exists)
        '--icon=assets/icon.ico' if Path('assets/icon.ico').exists() else '',

        # Clean
        '--clean',
    ]

    # Run PyInstaller
    PyInstaller.__main__.run(args)

    print("\n✅ Build complete!")
    print(f"   Executable: {Path('build/dist/employee_manager.exe').absolute()}")
    print("\n   Deploy with:")
    print(f"   python bootstrapper/main.py deploy build/dist/employee_manager.exe <instance_path>")

if __name__ == '__main__':
    build()
```

---

## 🎯 CRITICAL REALIZATION: IMPLICATIONS FOR CUSTOMTKINTER UI

### **What Changes in My Understanding:**

#### **BEFORE (My Wrong Understanding):**
- UI just needs to work on my machine
- Hardcode paths if needed
- One database, one location
- Simple deployment

#### **AFTER (Correct Understanding):**
- UI must be **FREAKING PORTABLE**
- **ZERO hardcoded paths** - everything relative
- Must work from **ANY location**
- Must read `config.json` at runtime
- Must handle documents carefully (copy, rename, relative paths)
- Must integrate with lock system
- Must be **COMPILE-READY** from day 1

---

## 🚨 CRITICAL REQUIREMENTS FOR UI IMPLEMENTATION

### **1. Path Management (CRITICAL)**

```python
# WRONG ❌
DB_PATH = "employee_manager.db"
DOCUMENTS_DIR = "C:/Users/me/Documents"

# CORRECT ✅
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

DB_PATH = BASE_DIR / "data" / "employee_manager.db"
DOCUMENTS_DIR = BASE_DIR / "documents"
```

---

### **2. Configuration Loading (CRITICAL)**

```python
# Must load at startup, NOT hardcode
import json

config_path = BASE_DIR / "config.json"

try:
    with open(config_path) as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    # Use defaults if config missing
    CONFIG = {
        "alert_thresholds_days": [30, 60, 90],
        "roles": ["Préparateur", "Cariste"],
        "workspaces": ["Quai", "Zone A"],
    }

# Use throughout app
ROLES = CONFIG.get("roles", [])
ALERT_THRESHOLDS = CONFIG.get("alert_thresholds_days", [30, 60, 90])
```

---

### **3. Database Initialization (CRITICAL)**

```python
def init_database():
    """Initialize database if needed."""
    db_path = BASE_DIR / "data" / "employee_manager.db"

    # Create data directory if not exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize if DB doesn't exist
    if not db_path.exists():
        from database.connection import init_database
        init_database(db_path)
```

---

### **4. Document Uploads (CRITICAL)**

```python
def handle_document_upload(file_path, doc_type, employee_id):
    """Handle document upload - copy to managed location."""
    documents_dir = BASE_DIR / "documents" / doc_type
    documents_dir.mkdir(parents=True, exist_ok=True)

    # Generate standardized filename
    from datetime import date
    filename = f"{doc_type}_{employee_id}_{date.today()}.pdf"

    dest = documents_dir / filename

    # Copy file
    shutil.copy2(file_path, dest)

    # Return RELATIVE path for DB storage
    return str(dest.relative_to(BASE_DIR))
```

---

### **5. Lock Integration (CRITICAL)**

```python
# On app startup
from lock.manager import LockManager, get_process_info

lock_manager = LockManager(*get_process_info())

if not lock_manager.acquire_lock():
    show_error("Application is already in use by another user")
    sys.exit(1)

# Start heartbeat timer
import threading
def heartbeat():
    while True:
        time.sleep(30)
        lock_manager.update_heartbeat()

threading.Thread(target=heartbeat, daemon=True).start()

# On app close
def on_closing():
    lock_manager.release_lock()
    app.destroy()
```

---

### **6. Logging (IMPORTANT)**

```python
import logging
from pathlib import Path

logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    filename=logs_dir / "app.log",
    level=logging.INFO,
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 📋 UPDATED IMPLEMENTATION PLAN

### **Phase 1: Foundation (UPDATED)**

**Step 1.1: CustomTkinter App Skeleton**
- [ ] Create `src/ui_ctk/app.py`
- [ ] Implement path management (portable)
- [ ] Load config.json
- [ ] Initialize database
- [ ] Integrate lock manager

**Step 1.2: Bootstrapper Implementation**
- [ ] Create `bootstrapper/creator.py`
- [ ] Implement directory creation
- [ ] Implement template copying
- [ ] Implement DB initialization
- [ ] Create CLI entry point

---

### **Phase 2: Views Implementation**

**Same as before**, but with awareness of:
- All paths must be relative
- All config must come from config.json
- All uploads go to documents/ folder

---

### **Phase 3: Build System**

**Step 3.1: PyInstaller Script**
- [ ] Create `build/build.py`
- [ ] Configure PyInstaller for CustomTkinter
- [ ] Test executable
- [ ] Deploy to test instance

---

### **Phase 4: Integration Testing**

**Test on:**
- [ ] Local drive (C:)
- [ ] Network drive (Z:)
- [ ] Different computers
- [ ] Fresh instance (bootstrapped)
- [ ] Existing instance (with data)

---

## 🎯 NEW SUCCESS CRITERIA

The system is successful when:

### **Bootstrapper:**
- ✅ Creates complete instance with one command
- ✅ Generates proper folder structure
- ✅ Initializes database
- ✅ Copies config templates

### **Build System:**
- ✅ Compiles to standalone .exe
- ✅ .exe works without Python installed
- ✅ .exe works from network drive
- ✅ No hardcoded paths

### **CustomTkinter UI:**
- ✅ Works from any location
- ✅ Reads config.json
- ✅ Manages documents correctly
- ✅ Implements locking system
- ✅ Logs to logs/ folder

### **Deployment:**
- ✅ Can create new instance in 5 minutes
- ✅ Can deploy .exe to existing instance
- ✅ End users just double-click .exe
- ✅ Multiple instances can coexist (different DBs)

---

## 📊 REVISED ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────┐
│              DEVELOPMENT REPOSITORY                       │
│  wareflow-ems/ (Git repo)                               │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Source     │  │Bootstrapper  │  │    Build     │   │
│  │  Code       │  │              │  │    System    │   │
│  │             │  │              │  │              │   │
│  │ src/ui_ctk/ │  │creator.py    │  │build.py      │   │
│  │ src/employee│  │main.py       │  │build.spec    │   │
│  │ src/db/     │  │templates/    │  │              │   │
│  └─────────────┘  └──────────────┘  └──────────────┘   │
│         │                  │                  │          │
│         └──────────────────┴──────────────────┘          │
│                            │                             │
│                            ▼                             │
│                    python build/build.py                   │
│                            │                             │
│                            ▼                             │
│                   employee_manager.exe                    │
└─────────────────────────────────────────────────────────┘
                            │
                            │ Deploy
                            ▼
┌─────────────────────────────────────────────────────────┐
│          BOOTSTRAPPED INSTANCE (Network Share)             │
│  Gestion_Salaries_SiteA/                                  │
│                                                           │
│  data/employee_manager.db  ← Local DB                    │
│  documents/ ← Uploaded files                              │
│  src/employee_manager.exe  ← Compiled app                 │
│  config.json  ← Instance config                           │
│  exports/  ← Generated Excel files                        │
│  logs/  ← Application logs                                │
│                                                           │
│  End users double-click .exe → App runs!                  │
└─────────────────────────────────────────────────────────┘

ANOTHER INSTANCE:
┌─────────────────────────────────────────────────────────┐
│       Gestion_Salaries_SiteB/ (Different DB!)             │
│  Same structure, different data                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 NEXT STEPS

### **Immediate Actions:**

1. **Update Migration Plan**
   - Add portability requirements
   - Add config.json loading
   - Add document management
   - Add lock integration

2. **Implement Bootstrapper**
   - Create `bootstrapper/creator.py`
   - Implement `bootstrapper/main.py` CLI
   - Test instance creation

3. **Update CustomTkinter Plan**
   - All paths relative
   - Config-driven
   - Document-aware

4. **Implement Build System**
   - PyInstaller script
   - Test executable
   - Test deployment

---

## ❓ QUESTIONS FOR YOU

1. **Bootstrapper Priority:** Implement bootstrapper FIRST or UI FIRST?
   - Option A: Bootstrapper first (can create test instances)
   - Option B: UI first (bootstrapper can be manual initially)

2. **Config.json Complexity:** What should be configurable?
   - Alert thresholds? (30/60/90 days)
   - Roles list?
   - Workspaces list?
   - Lock timeout?
   - All of the above?

3. **Document Management:**
   - Should the app validate file types (PDF only)?
   - Should it scan for viruses?
   - Should it compress files?

4. **Build Frequency:**
   - Rebuild for every instance?
   - One build, deploy to many instances?

5. **Multi-Instance:**
   - Can one bootstrapper create multiple instances?
   - Yes (franchise model) or No (one-time setup)?

---

**This is the COMPLETE picture. Now I understand this is a TOOLKIT/BOOTSTRAPPER system, not just an app! 🎯**
