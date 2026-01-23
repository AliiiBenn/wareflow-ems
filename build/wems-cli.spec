# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Wareflow Employee Management System (CLI version).

This spec file defines how to bundle the CLI application into a standalone
executable. It includes all necessary dependencies, data files, and configuration.

Usage:
    pyinstaller build/wems-cli.spec

Or via build script:
    python build/build.py --cli
    uv run pyinstaller build/wems-cli.spec
"""

import os
import sys
from pathlib import Path

# Get the root directory of the project
block_cipher = None
ROOT_DIR = Path(SPECPATH).parent
SRC_DIR = ROOT_DIR / "src"

# Collect all hidden imports for CLI and dependencies
hiddenimports = [
    # CLI Framework
    "typer",
    "rich",
    "rich.console",
    "rich.progress",
    "rich.table",
    "tabulate",

    # Database
    "peewee",
    "playhouse.sqliteq",

    # Excel handling
    "openpyxl",
    "openpyxl.cell._writer",
    "openpyxl.styles",

    # Date utilities
    "dateutil",
    "dateutil.parser",

    # Application modules
    "excel_import.template_generator",
    "utils.config",
    "utils.logging_config",
    "database.connection",
    "database.migration_model",
    "employee.models",
    "employee.calculations",
    "employee.validators",
    "employee.queries",
    "employee.alerts",
    "lock.manager",
    "lock.models",
    "state.app_state",

    # Bootstrapper
    "bootstrapper.update_checker",

    # All CLI modules
    "cli.employee",
    "cli.caces",
    "cli.medical",
    "cli.training",
    "cli.report",
    "cli.lock",
    "cli.update",
    "cli.upgrade",
    "cli.rollback",

    # Update system
    "requests",
    "packaging",
    "packaging.version",

    # Questionary for interactive prompts
    "questionary",
]

# Data files to include
datas = [
    # Include all source modules (except GUI)
    (str(SRC_DIR / "utils"), "utils"),
    (str(SRC_DIR / "state"), "state"),
    (str(SRC_DIR / "controllers"), "controllers"),
]

# Binary excludes (exclude unnecessary files)
binaries_excludes = []

# Import exclusions (reduce file size)
excludes = [
    # GUI frameworks (not needed for CLI)
    "customtkinter",
    "tkinter",
    "PIL",
    "PIL._tkinter_finder",
    "PIL._imaging",

    # GUI modules
    "ui_ctk",

    # Scientific computing
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "IPython",

    # Testing frameworks
    "pytest",
    "unittest",
    "mock",

    # Development tools
    "black",
    "ruff",
    "mypy",
]

# Analysis
a = Analysis(
    [str(SRC_DIR / "cli_main.py")],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary files from the executable
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="wems-cli",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # CLI application - show console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT_DIR / "build" / "assets" / "icon.ico") if (ROOT_DIR / "build" / "assets" / "icon.ico").exists() else None,
)

# Collect all binaries and Python files
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="wems-cli",
)
