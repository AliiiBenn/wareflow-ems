# Test app.py unit tests
"""Test application entry point."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import customtkinter as ctk

sys.path.insert(0, 'src')


def test_customtkinter_setup():
    """Test CustomTkinter configuration."""
    print("[TEST] Testing CustomTkinter setup...")

    from ui_ctk.app import setup_customtkinter

    # Call the function to verify it works without errors
    setup_customtkinter()

    print("[OK] CustomTkinter setup test passed")


def test_database_initialization():
    """Test database initialization function."""
    print("\n[TEST] Testing database initialization...")

    from ui_ctk.app import setup_database
    from database.connection import database

    test_db = "test_employee_unit.db"

    try:
        # Call with test database
        setup_database(test_db)

        # Verify database is connected
        assert not database.is_closed(), "Database should be connected"

        print("[OK] Database initialization test passed")

    finally:
        # Cleanup
        if not database.is_closed():
            database.close()
        if Path(test_db).exists():
            Path(test_db).unlink()


def test_main_window_creation():
    """Test main window creation function."""
    print("\n[TEST] Testing main window creation...")

    # Create a mock app
    app = Mock()

    with patch('ui_ctk.app.MainWindow') as mock_main_window:
        # Create mock window instance
        mock_window_instance = Mock()
        mock_main_window.return_value = mock_window_instance

        from ui_ctk.app import create_main_window

        # Call function
        result = create_main_window(app)

        # Assert main window was created and packed
        assert mock_main_window.called, "MainWindow should be created"
        assert mock_window_instance.pack.called, "Main window should be packed"
        assert result == mock_window_instance, "Should return MainWindow instance"

        print("[OK] Main window creation test passed")


def test_imports():
    """Test that all imports work correctly."""
    print("\n[TEST] Testing imports...")

    try:
        from ui_ctk.app import (
            setup_customtkinter,
            setup_database,
            create_main_window,
            main
        )
        print("[OK] All app.py imports successful")
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        raise


if __name__ == "__main__":
    print("=" * 50)
    print(" TESTING APP.PY")
    print("=" * 50)

    try:
        test_imports()
        test_customtkinter_setup()
        test_database_initialization()
        test_main_window_creation()

        print("\n" + "=" * 50)
        print(" [OK] ALL APP.PY TESTS PASSED")
        print("=" * 50)
    except Exception as e:
        print(f"\n[FAIL] Tests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
