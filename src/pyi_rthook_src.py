"""PyInstaller runtime hook to fix sys.path for src imports.

This hook is executed by PyInstaller before any application code,
allowing 'from src.xxx' imports to work correctly in the bundled executable.
"""
import sys
import os
from pathlib import Path

# When running from PyInstaller bundle, src is not in path by default
# We need to add the parent directory to sys.path so 'from src.xxx' works
if getattr(sys, 'frozen', False):
    # Get the directory containing src (this should be added to sys.path)
    if '_MEIPASS' in os.environ:
        # PyInstaller has extracted to temp dir
        extraction_dir = Path(os.environ['_MEIPASS'])

        # The extraction_dir should already contain the src directory
        # We need to add extraction_dir itself to sys.path
        if (extraction_dir / "src").exists():
            sys.path.insert(0, str(extraction_dir))
        else:
            # Fallback: try finding src parent
            for _ in range(3):
                if (extraction_dir / "src").exists():
                    sys.path.insert(0, str(extraction_dir))
                    break
                extraction_dir = extraction_dir.parent
    else:
        # Development mode or testing
        exe_dir = Path(sys.executable).parent.resolve()

        # Look for src directory and add its parent to sys.path
        for check_dir in [exe_dir, exe_dir.parent, exe_dir.parent.parent]:
            if (check_dir / "src").exists():
                sys.path.insert(0, str(check_dir))
                break
