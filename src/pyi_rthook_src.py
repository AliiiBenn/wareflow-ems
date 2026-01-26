"""PyInstaller runtime hook to fix sys.path for src imports.

This hook is executed by PyInstaller before any application code,
allowing 'from src.xxx' imports to work correctly in the bundled executable.
"""
import sys
import os
from pathlib import Path

# When running from PyInstaller bundle, src is not in path by default
# We need to add it early, before any imports happen
if getattr(sys, 'frozen', False):
    # Get the temporary extraction directory
    # PyInstaller extracts to a temp folder when running
    # We need to find src/ within the extraction
    if '_MEIPASS' in os.environ:
        # PyInstaller has extracted to temp dir
        extraction_dir = Path(os.environ['_MEIPASS'])
        src_dir = extraction_dir / "src"
    else:
        # Development mode or testing - should not happen in frozen app
        exe_dir = Path(sys.executable).parent.resolve()
        src_dir = exe_dir / "src"

    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
        # Also add parent dir in case we need other top-level modules
        sys.path.insert(1, str(src_dir.parent))
    else:
        # Fallback: try to find src directory by searching upward
        # This handles cases where the structure is different
        if '_MEIPASS' in os.environ:
            current = Path(os.environ['_MEIPASS'])
        else:
            current = Path(sys.executable).parent.resolve()

        for _ in range(3):  # Search up to 3 levels
            if (current / "src").exists():
                sys.path.insert(0, str(current / "src"))
                break
            current = current.parent if current.parent != current else current
