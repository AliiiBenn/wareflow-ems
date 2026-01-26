"""PyInstaller entry point for Windows executable.

This module serves as the entry point for the PyInstaller-built executable.
It correctly sets up sys.path before importing the application.
"""

import sys
import os
from pathlib import Path

# Get the directory where the executable is located
if getattr(sys, 'frozen', False):
    # Running from PyInstaller bundle
    # The executable is in dist/, and src/ should be next to it
    # But in one-file mode, we need to find the original script location
    application_path = Path(sys.executable).parent
else:
    # Running from Python normally
    application_path = Path(__file__).parent

# Add src directory to Python path
src_path = application_path / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))
else:
    # Fallback: try parent directory (for development)
    parent_path = application_path.parent
    if (parent_path / "src").exists():
        sys.path.insert(0, str(parent_path / "src"))
    else:
        # Last resort: current directory
        sys.path.insert(0, str(Path.cwd()))

# Now import and run the application
if __name__ == "__main__":
    from ui_ctk.app import main

    main()
