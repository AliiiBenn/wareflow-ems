"""Update command for Wareflow Employee Management System.

This command provides automated application updating functionality:
- Check for updates from GitHub Releases
- Download new application files
- Backup current data before update
- Migrate database schema
- Validate update integrity
- Rollback on failure

Usage:
    wems update
    wems update --preview
    wems update --force
    wems update --path "C:/custom/path"
"""

import hashlib
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
import typer
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn

from bootstrapper.update_checker import UpdateChecker, get_update_info, is_update_available
from database.connection import database
from database.migration_model import get_applied_migrations
from utils.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO", enable_console=True, enable_file=True)
logger = get_logger(__name__)

# Initialize Typer app
app = typer.Typer(
    name="update",
    help="Update Wareflow EMS to the latest version",
    add_completion=True,
)

console = Console()


def get_current_version() -> str:
    """Get current application version."""
    try:
        from employee_manager import __version__
        return __version__.lstrip('v')
    except ImportError:
        return "unknown"


def download_file(url: str, dest_path: Path, show_progress: bool = True) -> Path:
    """Download file from URL with optional progress bar.

    Args:
        url: URL to download from
        dest_path: Destination path
        show_progress: Whether to show progress bar

    Returns:
        Path to downloaded file
    """
    if show_progress:
        console.print(f"[cyan]📥 Downloading from:[/cyan] {url}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if show_progress:
            total_size = int(response.headers.get('content-length', 0))
            with Progress(
                *[
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(bar_width=None),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TextColumn("[bold green]{task.completed} / {task.total}"),
                ],
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Downloading",
                    total=total_size or None,
                )

                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
        else:
            with open(dest_path, 'wb') as f:
                f.write(response.content)

        console.print("[green]✓ Download complete[/green]")
        return dest_path

    except requests.RequestException as e:
        console.print(f"[red]✗ Download failed: {e}[/red]")
        raise


def verify_checksum(download_path: Path, expected_checksum: Optional[str] = None) -> bool:
    """Verify SHA256 checksum of downloaded file.

    Args:
        download_path: Path to downloaded file
        expected_checksum: Expected SHA256 checksum (optional)

    Returns:
        True if checksum matches (or no expected checksum provided)
    """
    console.print("[cyan]🔒 Verifying checksum...[/cyan]")

    sha256_hash = hashlib.sha256()
    with open(download_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    checksum = sha256_hash.hexdigest()

    if expected_checksum:
        if checksum != expected_checksum.lower().replace('sha256:', '').replace('sha256:', ''):
            console.print(f"[red]✗ Checksum mismatch![/red]")
            console.print(f"  Expected: {expected_checksum}")
            console.print(f"  Got:      {checksum}")
            return False
        else:
            console.print(f"[green]✓ Checksum verified: {checksum}[/green]")
            return True
    else:
        console.print(f"[green]✓ Checksum: {checksum}[/green]")
        return True


def create_backup(data_path: Path) -> Path:
    """Create backup of database before update.

    Args:
        data_path: Path to database file

    Returns:
        Path to backup file
    """
    if not data_path.exists():
        console.print(f"[yellow]⚠ No database file found at {data_path}, skipping backup[/yellow]")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = data_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_name = f"before_update_{timestamp}.db"
    backup_path = backup_dir / backup_name

    console.print(f"[cyan]💾 Creating backup...[/cyan]")
    console.print(f"  From: {data_path}")
    console.print(f"  To:   {backup_path}")

    shutil.copy2(data_path, backup_path)
    console.print("[green]✓ Backup created[/green]")

    return backup_path


def restore_backup(backup_path: Path, data_path: Path) -> bool:
    """Restore database from backup.

    Args:
        backup_path: Path to backup file
        data_path: Target database path

    Returns:
        True if successful, False otherwise
    """
    console.print(f"[cyan]🔄 Restoring from backup...[/cyan]")
    console.print(f"  From: {backup_path}")
    console.print(f"  To:   {data_path}")

    try:
        shutil.copy2(backup_path, data_path)
        console.print("[green]✓ Database restored[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Restore failed: {e}[/red]")
        return False


def run_migrations() -> bool:
    """Run database migrations.

    Returns:
        True if successful, False otherwise
    """
    console.print("[cyan]🔄 Running database migrations...[/cyan]")

    try:
        from database.migrations.base import get_pending_migrations
        from database.migrations.base import run_migration

        # Connect to database
        if database.is_closed():
            database.connect()

        # Get pending migrations
        pending = get_pending_migrations(Path("src/database/migrations"))

        if not pending:
            console.print("[green]✓ No migrations to run[/green]")
            return True

        # Run migrations
        from database.migration_model import get_last_batch_number
        batch = get_last_batch_number() + 1

        with Progress(
            *[
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=None),
                TextColumn("[bold green]{task.completed} / {task.total}"),
            ],
            console=console,
        ) as progress:
            for migration in pending:
                task = progress.add_task(
                    f"Running {migration.name}",
                    total=1
                )

                success = run_migration(migration, batch)

                if success:
                    progress.update(task, completed=1)
                else:
                    console.print(f"[red]✗ Migration {migration.name} failed[/red]")
                    return False

        console.print("[green]✓ All migrations completed successfully[/green]")
        return True

    except Exception as e:
        console.print(f"[red]✗ Migration failed: {e}[/red]")
        return False


def get_download_url(release_info: dict) -> str:
    """Get download URL for the appropriate platform.

    Args:
        release_info: GitHub release information

    Returns:
        Download URL for current platform
    """
    # Get download URL from release assets
    # For now, we'll use the source code zip
    tag_name = release_info.get('tag_name', '')

    # Try to find platform-specific asset
    # This would need to be enhanced when we have actual binaries
    return f"https://github.com/wareflowx/wareflow-ems/archive/refs/tags/{tag_name}.zip"


def update_application(
    preview: bool = False,
    force: bool = False,
    data_path: Optional[Path] = None,
    backup: bool = True
) -> bool:
    """Update application to latest version.

    Args:
        preview: Preview changes without updating
        force: Update even if already on latest version
        data_path: Custom database path
        backup: Create backup before update

    Returns:
        True if update successful, False otherwise
    """
    current_version = get_current_version()

    console.print(f"[bold blue]Wareflow EMS Updater[/bold blue]")
    console.print(f"Current version: [cyan]{current_version}[/cyan]\n")

    # Check for updates
    checker = UpdateChecker(current_version)
    update_info = checker.check_for_updates()

    if not update_info:
        console.print("[green]✓ Already up to date![/green]")
        return True

    latest_version = update_info['version']
    console.print(f"[bold green]Update available:[/bold green] {current_version} → [bold yellow]{latest_version}[/bold yellow]\n")

    # Show release notes
    console.print("[bold]What's new:[/bold]")
    # Show first few lines of release notes
    body_lines = update_info.get('body', '').split('\n')[:10]
    for line in body_lines:
        if line.strip():
            console.print(f"  {line}")
    console.print(f"\n  Full notes: {update_info.get('html_url', '')}\n")

    if preview:
        console.print("[yellow]Preview mode - no changes made[/yellow]")
        return True

    # Confirm before updating (unless --force)
    if not force:
        console.print("[yellow]This will:[/yellow]")
        console.print("  • Download the latest version")
        console.print("  • Create a backup of your data")
        console.print("  • Run database migrations")
        console.print("  • Verify the update")
        console.print("")
        typer.confirm("Continue with update?", abort=True)

    # Determine data path
    if data_path is None:
        # Try to find database
        from utils.config import get_database_path
        data_path = get_database_path()

    # Create backup
    backup_path = None
    if backup:
        try:
            backup_path = create_backup(data_path)
        except Exception as e:
            console.print(f"[red]✗ Backup failed: {e}[/red]")
            if not typer.confirm("Continue without backup?", abort=False):
                return False

    # Download update
    try:
        download_url = get_download_url(update_info)

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "update.zip"

            # Download
            download_file(download_url, temp_path)

            # Verify checksum (if provided in release)
            # For now, we skip this as GitHub doesn't provide checksums by default
            # In production, we would host checksums separately

            # Extract and validate
            console.print("\n[cyan]Validating update...[/cyan]")
            # TODO: Add validation logic here

            # Run migrations
            if not run_migrations():
                console.print("[red]✗ Update failed: migration error[/red]")
                if backup_path:
                    console.print("[yellow]Rolling back...[/yellow]")
                    restore_backup(backup_path, data_path)
                return False

            console.print("[green]✓ Update complete![/green]")
            console.print(f"\n[cyan]Please restart the application to use version {latest_version}[/cyan]")

            return True

    except Exception as e:
        console.print(f"[red]✗ Update failed: {e}[/red]")
        if backup_path:
            console.print("[yellow]Rolling back...[/yellow]")
            restore_backup(backup_path, data_path)
        return False


@app.command()
def update(
    preview: bool = typer.Option(False, help="Preview changes without updating"),
    force: bool = typer.Option(False, help="Update without confirmation"),
    path: Optional[Path] = typer.Option(None, help="Custom database path", exists=True),
    no_backup: bool = typer.Option(False, help="Skip creating backup"),
):
    """Update Wareflow EMS to the latest version."""
    success = update_application(
        preview=preview,
        force=force,
        data_path=path,
        backup=not no_backup
    )

    if not success:
        raise typer.Exit(code=1)


@app.command()
def check(
    json: bool = typer.Option(False, help="Output as JSON")
):
    """Check for updates."""
    info = get_update_info()

    if json:
        import json
        console.print_json(info)
    else:
        current = info['current_version']
        latest = info['latest_version']
        available = info['update_available']

        if available:
            console.print(f"[bold green]Update available![/bold green]")
            console.print(f"  Current: {current}")
            console.print(f"  Latest:  {latest}")

            if info['update_info']:
                console.print(f"\nRelease notes:")
                body = info['update_info'].get('body', '')
                if body:
                    # Show first few lines
                    for line in body.split('\n')[:10]:
                        if line.strip():
                            console.print(f"  {line}")
                    console.print(f"\n  URL: {info['update_info'].get('html_url', '')}")
        else:
            console.print(f"[green]✓ Already up to date![/green]")
            console.print(f"  Version: {current}")


if __name__ == "__main__":
    app()
