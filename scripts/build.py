#!/usr/bin/env python
"""Build script for Wareflow EMS.

This script provides a convenient way to build the Windows executable
locally for testing before creating a release.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd: list, cwd: Path = None) -> int:
    """Run a command and return exit code.

    Args:
        cmd: Command list to execute
        cwd: Working directory

    Returns:
        Exit code from command
    """
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def build_executable(clean: bool = True) -> int:
    """Build Windows executable using PyInstaller.

    Args:
        clean: Clean build directory before building

    Returns:
        Exit code (0 for success)
    """
    # Get project root
    project_root = Path(__file__).parent.parent
    spec_file = project_root / "wareflow-ems.spec"

    if not spec_file.exists():
        print(f"Error: Spec file not found: {spec_file}")
        return 1

    # Check PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("Error: PyInstaller not installed")
        print("Install with: uv sync --extra build")
        return 1

    # Build command
    cmd = ["pyinstaller", str(spec_file)]

    if clean:
        cmd.extend(["--clean", "--noconfirm"])

    print("\n" + "=" * 60)
    print("Building Wareflow EMS Windows executable")
    print("=" * 60 + "\n")

    exit_code = run_command(cmd, cwd=project_root)

    if exit_code == 0:
        print("\n" + "=" * 60)
        print("Build successful!")
        print("=" * 60)
        print(f"\nExecutable location: {project_root / 'dist' / 'Wareflow EMS.exe'}")

        # Show file size
        exe_path = project_root / "dist" / "Wareflow EMS.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"File size: {size_mb:.2f} MB")
    else:
        print("\n" + "=" * 60)
        print("Build failed!")
        print("=" * 60)

    return exit_code


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Build Wareflow EMS Windows executable"
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Don't clean build directory before building"
    )

    args = parser.parse_args()

    exit_code = build_executable(clean=not args.no_clean)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
