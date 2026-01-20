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

    with patch('customtkinter.set_appearance_mode') as mock_mode:
        with patch('customtkinter.set_default_color_theme') as mock_theme:
            from ui_ctk.app import setup_customtkinter

            # Assert configuration was called
            assert mock_mode.called, "set_appearance_mode should be called"
            assert mock_theme.called, "set_default_color_theme should be called"

            print("[OK] CustomTkinter setup test passed")


def test_database_initialization():
    """Test database initialization function."""
    print("\n[TEST] Testing database initialization...")

    with patch('ui_ctk.app.init_database') as mock_init:
        with patch('database.connection.database') as mock_db:
            # Mock database methods
            mock_db.connect = MagicMock()
            mock_db.create_tables = MagicMock()
            mock_db.is_closed = MagicMock(return_value=False)
            mock_db.close = MagicMock()

            from ui_ctk.app import setup_database

            # Call with test database
            setup_database("test_employee.db")

            # Verify initialization was called
            assert mock_init.called, "init_database should be called"
            assert mock_db.connect.called, "database.connect should be called"
            assert mock_db.create_tables.called, "database.create_tables should be called"

            # Cleanup test database
            if Path("test_employee.db").exists():
                Path("test_employee.db").unlink()

            print("[OK] Database initialization test passed")


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
