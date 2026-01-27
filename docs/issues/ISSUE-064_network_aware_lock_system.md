# ISSUE-064: Network-Aware Lock System for Shared Databases

## Description

The current lock system (`src/lock/manager.py`) works for single-user scenarios but doesn't properly handle multiple users accessing the same database file over a shared network folder. Need to implement proper network-aware file locking that prevents concurrent access and handles edge cases.

## Current State

- Lock mechanism exists but designed for local use
- No network folder support
- Race conditions possible when multiple users launch simultaneously
- Lock file not reliably detected over network (SMB/NFS)
- No user-friendly "database in use" messaging

## Problems

### Current Implementation Issues

```python
# src/lock/manager.py (current)
class LockManager:
    def acquire_lock(self):
        """Try to acquire lock."""
        if self.lock_file.exists():
            raise LockError("Database is locked")
        self.lock_file.write_text(getpid())
```

**Problems:**
1. **No atomic operations** - Check and write are not atomic
2. **No timeout handling** - Stale locks never released
3. **No network awareness** - SMB/NFS have different locking semantics
4. **No user identification** - Don't know who has the lock
5. **No heartbeat** - Can't detect if locking process crashed

## Expected Behavior

### Network-Aware Lock Manager

```python
# src/lock/network_lock_manager.py
import os
import socket
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
import fcntl  # Unix file locking
import msvcrt  # Windows file locking

class NetworkLockManager:
    """Manage database locks for network shared folders."""

    LOCK_TIMEOUT = timedelta(minutes=5)  # Auto-release stale locks
    HEARTBEAT_INTERVAL = 30  # Seconds

    def __init__(self, lock_file: Path):
        self.lock_file = lock_file
        self.lock_fd = None
        self.heartbeat_thread = None
        self.running = False

    def acquire_lock(
        self,
        timeout: int = 60,
        user: str = None,
        machine: str = None
    ) -> bool:
        """
        Try to acquire lock with network-aware behavior.

        Args:
            timeout: Max seconds to wait (0 = no wait)
            user: User name (from OS/environment)
            machine: Machine name

        Returns:
            True if lock acquired

        Raises:
            LockError: If lock cannot be acquired
        """
        if not user:
            user = os.getenv("USERNAME", os.getenv("USER", "unknown"))
        if not machine:
            machine = socket.gethostname()

        start_time = time.time()

        while True:
            # Try to acquire lock
            try:
                # Open/create lock file exclusively
                # Mode 'w' with exclusive access
                self.lock_fd = open(self.lock_file, 'w')

                # Platform-specific file locking
                if os.name == 'nt':
                    # Windows: Use msvcrt.locking
                    msvcrt.locking(
                        self.lock_fd.fileno(),
                        msvcrt.LK_NBLCK,  # Non-blocking lock
                        1
                    )
                else:
                    # Unix: Use fcntl flock
                    fcntl.flock(
                        self.lock_fd.fileno(),
                        fcntl.LOCK_EX | fcntl.LOCK_NB
                    )

                # Lock acquired! Write lock info
                lock_info = {
                    "pid": os.getpid(),
                    "user": user,
                    "machine": machine,
                    "acquired": datetime.now().isoformat(),
                    "heartbeat": datetime.now().isoformat()
                }

                self.lock_fd.write(json.dumps(lock_info))
                self.lock_fd.flush()

                # Start heartbeat thread
                self._start_heartbeat()

                return True

            except (IOError, OSError) as e:
                # Lock is held by another process
                if self.lock_fd:
                    self.lock_fd.close()
                    self.lock_fd = None

                # Check if lock is stale (timeout)
                if self._is_lock_stale():
                    print("Lock is stale, breaking...")
                    self._break_lock()
                    continue  # Retry acquiring

                # Check timeout
                if timeout == 0:
                    # No wait, fail immediately
                    raise LockError(
                        self._get_locked_message()
                    )
                elif time.time() - start_time >= timeout:
                    # Timeout exceeded
                    raise LockError(
                        f"Could not acquire lock after {timeout} seconds. "
                        f"{self._get_locked_message()}"
                    )

                # Wait before retry
                time.sleep(0.5)

    def _is_lock_stale(self) -> bool:
        """Check if lock is stale (older than timeout)."""
        try:
            with open(self.lock_file) as f:
                content = f.read().strip()
                if not content:
                    return True  # Empty lock file

                lock_info = json.loads(content)
                heartbeat = datetime.fromisoformat(lock_info["heartbeat"])
                return datetime.now() - heartbeat > self.LOCK_TIMEOUT

        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            # Invalid lock file, consider it stale
            return True

    def _get_locked_message(self) -> str:
        """Get user-friendly message about who holds the lock."""
        try:
            with open(self.lock_file) as f:
                content = f.read().strip()
                if content:
                    lock_info = json.loads(content)
                    return (
                        f"Database is locked by {lock_info['user']} "
                        f"on {lock_info['machine']} "
                        f"(since {lock_info['acquired']})"
                    )
        except:
            pass

        return "Database is locked by another user"

    def _break_lock(self):
        """Break a stale lock."""
        try:
            # On Windows, need to close file first
            if self.lock_fd:
                self.lock_fd.close()
                self.lock_fd = None

            # Delete lock file
            self.lock_file.unlink()
        except:
            pass

    def _start_heartbeat(self):
        """Start heartbeat thread to keep lock alive."""
        self.running = True
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True
        )
        self.heartbeat_thread.start()

    def _heartbeat_loop(self):
        """Update heartbeat timestamp periodically."""
        while self.running:
            try:
                time.sleep(self.HEARTBEAT_INTERVAL)

                if self.lock_fd:
                    # Update heartbeat timestamp
                    with open(self.lock_file, 'r+') as f:
                        lock_info = json.loads(f.read())
                        lock_info["heartbeat"] = datetime.now().isoformat()
                        f.seek(0)
                        f.write(json.dumps(lock_info))
                        f.truncate()

            except:
                # Lost lock, stop heartbeat
                self.running = False

    def release_lock(self):
        """Release the lock."""
        self.running = False

        if self.lock_fd:
            try:
                # Release file lock
                if os.name == 'nt':
                    msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)

                self.lock_fd.close()
            except:
                pass
            finally:
                self.lock_fd = None

        # Delete lock file
        try:
            self.lock_file.unlink()
        except:
            pass

    def __enter__(self):
        """Context manager entry."""
        self.acquire_lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release_lock()
```

### Usage in Application

```python
# src/main_exe.py
from lock.network_lock_manager import NetworkLockManager, LockError

def main():
    """Main entry point."""
    lock_file = Path("data/database.lock")

    try:
        with NetworkLockManager(lock_file) as lock:
            # Application main loop
            run_application()

    except LockError as e:
        # Show error dialog
        show_lock_error_dialog(str(e))
        sys.exit(1)

def show_lock_error_dialog(message: str):
    """Show user-friendly lock error dialog."""
    import customtkinter as ctk
    from tkinter import messagebox

    root = ctk.CTk()
    root.withdraw()  # Hide main window

    messagebox.showerror(
        "Database Unavailable",
        f"{message}\n\n"
        "Possible solutions:\n"
        "1. Wait for the other user to close the application\n"
        "2. If no one else is using it, delete 'data/database.lock' file\n"
        "3. Ensure all users have write access to the shared folder",
        icon="error"
    )

    sys.exit(1)
```

### Lock Status Indicator in UI

Add visual indicator when database is locked:

```python
# src/ui_ctk/main_window.py
class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.lock_manager = NetworkLockManager(Path("data/database.lock"))
        self.lock_indicator = None
        self.create_lock_indicator()

    def create_lock_indicator(self):
        """Create lock status indicator."""
        self.lock_indicator = ctk.CTkLabel(
            self,
            text="🔓 Database Unlocked",
            text_color="green",
            font=("Arial", 10)
        )
        self.lock_indicator.pack(side="bottom", anchor="e", padx=10, pady=5)

    def update_lock_indicator(self, locked: bool):
        """Update lock status indicator."""
        if locked:
            self.lock_indicator.configure(
                text="🔒 Database Locked",
                text_color="red"
            )
        else:
            self.lock_indicator.configure(
                text="🔓 Database Unlocked",
                text_color="green"
            )
```

## Affected Files

- `src/lock/network_lock_manager.py` - New network-aware lock manager
- `src/lock/manager.py` - Update to use network-aware implementation
- `src/main_exe.py` - Use new lock manager on startup
- `src/ui_ctk/main_window.py` - Add lock indicator
- Database migration to ensure lock file path is consistent

## Implementation Plan

### Phase 1: Network Lock Manager (2 days)
1. Implement NetworkLockManager class
2. Add platform-specific file locking (Windows/Unix)
3. Implement heartbeat mechanism
4. Add stale lock detection
5. Add lock breaking for stale locks

### Phase 2: Application Integration (1 day)
1. Update main_exe.py to use new lock manager
2. Add lock error dialog
3. Handle lock acquisition on startup
4. Ensure lock is released on exit

### Phase 3: UI Enhancements (1 day)
1. Add lock status indicator to main window
2. Add lock status to status bar
3. Show locked-by information
4. Add "Release Lock" button (admin only)

### Phase 4: Testing (2 days)
1. Test on local machine
2. Test on network share (SMB)
3. Test concurrent access scenarios
4. Test stale lock cleanup
5. Test crash recovery
6. Test on different platforms (Windows/Linux)

## Deployment Considerations

### Network Share Configuration

For proper operation, ensure:

1. **Folder permissions** - All users need:
   - Read/write access to database folder
   - Create/delete permissions for lock file
   - Write permissions to parent folder

2. **Lock file location** - Should be:
   - In same folder as database
   - Accessible to all users
   - On same network share as database

3. **Network protocol** - Tested with:
   - SMB/CIFS (Windows shares)
   - NFS (Unix shares)
   - Cloud storage (may not support file locking)

### Example Setup

**Windows Network Share:**

```
\\server\wareflow-ems\
├── data\
│   ├── wems.db
│   └── wems.db.lock  (created automatically)
├── documents\
└── config\
```

**Permissions Required:**
- Share permissions: Read/Write
- NTFS permissions: Modify (Read, Write, Delete, Create)

## Dependencies

- Standard library only (fcntl, msvcrt, socket, threading)

## Related Issues

- ISSUE-003: No Authentication (historical)
- ISSUE-063: Two-Way Excel Sync (concurrent access)

## Acceptance Criteria

- [ ] NetworkLockManager implemented
- [ ] Platform-specific file locking works (Windows/Linux)
- [ ] Heartbeat mechanism keeps lock alive
- [ ] Stale locks detected and broken automatically
- [ ] Lock acquisition shows who has the lock
- [ ] Lock error dialog is user-friendly
- [ ] Lock status indicator visible in UI
- [ ] Multiple users cannot open database simultaneously
- [ ] Lock released cleanly on application exit
- [ ] Lock recovered after crash (stale lock cleanup)
- [ ] Works on Windows network shares (SMB)
- [ ] Works on Linux network shares (NFS)
- [ ] All tests pass

## Estimated Effort

**Total:** 5-6 days
- Network lock manager: 2 days
- Application integration: 1 day
- UI enhancements: 1 day
- Testing: 2 days

## Notes

Network file locking is complex and platform-dependent. The implementation must handle:
- Different network protocols (SMB vs NFS)
- Platform differences (Windows vs Unix locking)
- Edge cases (crashes, network failures)
- Stale lock detection and cleanup

Test thoroughly on actual network shares before deploying to production.

## Troubleshooting

### Common Issues

**Issue:** Lock file created but not detected by other users
- **Cause:** Folder permissions or network protocol
- **Fix:** Ensure all users have write access to lock file location

**Issue:** Lock becomes stale frequently
- **Cause:** Heartbeat thread not running, network latency
- **Fix:** Increase heartbeat interval or lock timeout

**Issue:** Cannot break stale lock
- **Cause:** File still held by crashed process
- **Fix:** Manually delete lock file, check for open file handles

**Issue:** High latency on network share
- **Cause:** Frequent lock checks
- **Fix:** Reduce check frequency, increase lock timeout

## Future Enhancements

- Centralized lock server (for better multi-user support)
- Database-level locking (SQLite busy timeout)
- Request lock button (notify current user)
- Automatic lock release on inactivity
- Lock queue (wait in line for lock)
- Lock statistics and analytics
