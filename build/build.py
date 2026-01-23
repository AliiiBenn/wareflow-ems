"""Build script for Wareflow Employee Management System.

This script provides automated build functionality for creating standalone
executables using PyInstaller. It supports both GUI and CLI builds.

Usage:
    python build/build.py              # Build GUI version
    python build/build.py --cli        # Build CLI version
    python build/build.py --all        # Build both versions
    python build/build.py --clean      # Clean before building
    python build/build.py --version 1.2.3
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_version():
    """Get version from git tags or employee_manager module."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            # Remove 'v' prefix if present
            return version.lstrip('v')
    except Exception:
        pass

    # Fallback to reading from employee_manager.py
    init_file = Path("src/employee_manager.py")
    if init_file.exists():
        content = init_file.read_text()
        for line in content.split("\n"):
            if "__version__" in line:
                return line.split("=")[1].strip().strip('"').strip("'")

    return "0.0.0"


def run_command(cmd, cwd=None, check=True):
    """Run a command and display output.

    Args:
        cmd: Command to run as list
        cwd: Working directory
        check: Whether to check return code

    Returns:
        Completed process object
    """
    print(f"\n> Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result


def clean_build():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    dirs_to_clean = ["build", "dist", "__pycache__", "*.spec"]

    for dir_name in dirs_to_clean:
        if dir_name.endswith("*"):
            # Clean spec files in root
            for spec_file in Path(".").glob("*.spec"):
                if spec_file.name not in ["wems.spec", "wems-cli.spec"]:
                    spec_file.unlink()
                    print(f"  Removed: {spec_file}")
        else:
            dir_path = Path(dir_name)
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  Removed: {dir_name}")

    # Clean Python cache
    for pycache in Path(".").rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)

    # Clean .pyc files
    for pyc_file in Path(".").rglob("*.pyc"):
        pyc_file.unlink()


def run_tests():
    """Run tests before building."""
    print("\nRunning tests...")
    run_command(["uv", "run", "pytest", "tests/", "-v", "--tb=short",
                 "--ignore=tests/test_ui", "--ignore=tests/test_main_window.py"])


def inject_version(version):
    """Inject version into the application before building.

    Args:
        version: Version string to inject
    """
    print(f"\nInjecting version: {version}")

    # Create version file
    version_file = Path("src/version_info.py")
    version_content = f'''"""Version information for Wareflow EMS.

This file is auto-generated during the build process.
"""

__version__ = "{version}"
__build_date__ = "{datetime.now(timezone.utc).isoformat()}"
__build_type__ = "standalone"
'''

    version_file.write_text(version_content)
    print(f"  Created: {version_file}")


def build_executable(build_type="gui", version=None, clean=False, skip_tests=False):
    """Build the executable using PyInstaller.

    Args:
        build_type: Either "gui" or "cli"
        version: Version string
        clean: Whether to clean before building
        skip_tests: Whether to skip tests

    Returns:
        List of (artifact_path, checksum) tuples
    """
    version = version or get_version()
    build_name = "wems" if build_type == "gui" else "wems-cli"
    spec_file = Path(f"build/{build_name}.spec")

    print(f"\nBuilding {build_name.upper()} version {version}...")

    if clean:
        clean_build()

    # Inject version
    inject_version(version)

    # Run tests first
    if not skip_tests:
        run_tests()

    # Check if spec file exists
    if not spec_file.exists():
        print(f"Error: Spec file not found: {spec_file}")
        sys.exit(1)

    # Build with PyInstaller
    run_command(["uv", "run", "pyinstaller", str(spec_file), "--clean", "--noconfirm"])

    # Generate checksums
    print("\nGenerating checksums...")
    dist_dir = Path("dist")
    artifacts = []

    # Find the built executable
    if os.name == "nt":  # Windows
        exe_pattern = f"{build_name}/*.exe"
    elif sys.platform == "darwin":  # macOS
        exe_pattern = f"{build_name}/{build_name}"
    else:  # Linux
        exe_pattern = f"{build_name}/{build_name}"

    exe_files = list(dist_dir.glob(exe_pattern))

    if not exe_files:
        print(f"Warning: No executable found matching pattern: {exe_pattern}")
        return []

    for exe_file in exe_files:
        # Calculate SHA256 checksum
        sha256_hash = hashlib.sha256()
        with open(exe_file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        checksum = sha256_hash.hexdigest()
        checksum_file = dist_dir / f"{exe_file.name}.sha256"

        with open(checksum_file, "w") as f:
            f.write(f"{checksum}  {exe_file.name}\n")

        # Get file size
        file_size = exe_file.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        print(f"  {exe_file.name}: {checksum}")
        print(f"    Size: {file_size_mb:.2f} MB")
        artifacts.append((exe_file, checksum))

    # Create version.txt file
    version_file = dist_dir / f"{build_name}-version.txt"
    with open(version_file, "w") as f:
        f.write(f"Wareflow Employee Management System\n")
        f.write(f"Version: {version}\n")
        f.write(f"Build Type: {build_type.upper()}\n")
        f.write(f"Build Date: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"Platform: {sys.platform}\n")
        f.write(f"Python: {sys.version.split()[0]}\n")

    artifacts.append((version_file, None))

    print(f"\n[OK] {build_name.upper()} build complete!")
    print(f"\nArtifacts created in dist/{build_name}/:")
    for artifact, checksum in artifacts:
        if checksum:
            print(f"  - {artifact.name}")
            print(f"    SHA256: {checksum}")
        else:
            print(f"  - {artifact.name}")

    return artifacts


def build_all(version=None, clean=False, skip_tests=False):
    """Build both GUI and CLI versions.

    Args:
        version: Version string
        clean: Whether to clean before building
        skip_tests: Whether to skip tests

    Returns:
        Combined list of artifacts from both builds
    """
    all_artifacts = []

    # Build GUI version
    gui_artifacts = build_executable("gui", version, clean, skip_tests)
    all_artifacts.extend(gui_artifacts)

    # Clean between builds
    print("\n" + "="*60)
    print("Switching to CLI build...")
    print("="*60 + "\n")

    # Build CLI version (don't clean again)
    cli_artifacts = build_executable("cli", version, False, True)  # Skip tests for second build
    all_artifacts.extend(cli_artifacts)

    return all_artifacts


def print_summary(artifacts):
    """Print build summary.

    Args:
        artifacts: List of (artifact_path, checksum) tuples
    """
    print("\n" + "="*60)
    print("BUILD SUMMARY")
    print("="*60)

    total_size = 0
    for artifact, checksum in artifacts:
        if artifact.is_file():
            size = artifact.stat().st_size
            total_size += size
            size_mb = size / (1024 * 1024)
            print(f"\n{artifact.name}")
            print(f"  Location: {artifact}")
            print(f"  Size: {size_mb:.2f} MB")
            if checksum:
                print(f"  SHA256: {checksum}")

    print(f"\nTotal size: {total_size / (1024 * 1024):.2f} MB")
    print("\n[OK] All builds completed successfully!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Wareflow Employee Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build/build.py              # Build GUI version only
  python build/build.py --cli        # Build CLI version only
  python build/build.py --all        # Build both versions
  python build/build.py --clean      # Clean before building
  python build/build.py --version 1.2.3
  python build/build.py --skip-tests # Skip running tests
        """
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Build CLI version instead of GUI"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build both GUI and CLI versions"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building"
    )
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        help="Override version (default: from git tags or __version__)"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests before building"
    )

    args = parser.parse_args()

    # Build
    if args.all:
        artifacts = build_all(args.version, args.clean, args.skip_tests)
    elif args.cli:
        artifacts = build_executable("cli", args.version, args.clean, args.skip_tests)
    else:
        artifacts = build_executable("gui", args.version, args.clean, args.skip_tests)

    # Print summary
    if artifacts:
        print_summary(artifacts)


if __name__ == "__main__":
    main()
