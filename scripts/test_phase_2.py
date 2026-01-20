#!/usr/bin/env python
"""
Integration test for Phase 2 - UI Structure

Tests the complete application startup, navigation, and view switching.
"""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

import customtkinter as ctk


def test_imports():
    """Test that all Phase 2 modules can be imported."""
    print("[TEST 1] Testing imports...")

    try:
        # Test app.py imports
        from ui_ctk.app import (
            setup_customtkinter,
            setup_database,
            create_main_window,
            main
        )
        print("  [OK] app.py imports successful")

        # Test main_window.py imports
        from ui_ctk.main_window import MainWindow
        print("  [OK] main_window.py imports successful")

        # Test placeholder view imports
        from ui_ctk.views.placeholder import PlaceholderView
        print("  [OK] placeholder.py imports successful")

        # Test base view imports
        from ui_ctk.views.base_view import BaseView
        print("  [OK] base_view.py imports successful")

        return True

    except ImportError as e:
        print(f"  [FAIL] Import failed: {e}")
        return False


def test_customtkinter_setup():
    """Test CustomTkinter configuration."""
    print("\n[TEST 2] Testing CustomTkinter setup...")

    try:
        from ui_ctk.app import setup_customtkinter

        # Call setup function
        setup_customtkinter()

        print("  [OK] CustomTkinter configured successfully")
        return True

    except Exception as e:
        print(f"  [FAIL] CustomTkinter setup failed: {e}")
        return False


def test_database_setup():
    """Test database initialization."""
    print("\n[TEST 3] Testing database setup...")

    test_db = "test_phase_2.db"

    try:
        from ui_ctk.app import setup_database
        from database.connection import database

        # Setup test database
        setup_database(test_db)

        # Verify database is connected
        assert not database.is_closed(), "Database should be connected"

        print("  [OK] Database setup successful")

        # Cleanup
        if not database.is_closed():
            database.close()

        # Remove test database
        if Path(test_db).exists():
            Path(test_db).unlink()

        return True

    except Exception as e:
        print(f"  [FAIL] Database setup failed: {e}")
        # Cleanup
        if Path(test_db).exists():
            Path(test_db).unlink()
        return False


def test_main_window_creation():
    """Test main window can be created."""
    print("\n[TEST 4] Testing main window creation...")

    try:
        from ui_ctk.main_window import MainWindow

        # Create test app
        app = ctk.CTk()
        app.geometry("800x600")

        # Create main window
        main_window = MainWindow(app)
        main_window.pack(fill="both", expand=True)

        # Verify all components exist
        assert hasattr(main_window, 'nav_bar'), "Missing nav_bar"
        assert hasattr(main_window, 'view_container'), "Missing view_container"
        assert hasattr(main_window, 'current_view'), "Missing current_view"
        assert hasattr(main_window, 'btn_employees'), "Missing btn_employees"
        assert hasattr(main_window, 'btn_alerts'), "Missing btn_alerts"
        assert hasattr(main_window, 'btn_import'), "Missing btn_import"

        print("  [OK] Main window has all components")

        # Verify navigation methods exist
        assert hasattr(main_window, 'show_employee_list'), "Missing show_employee_list"
        assert hasattr(main_window, 'show_alerts'), "Missing show_alerts"
        assert hasattr(main_window, 'show_import'), "Missing show_import"
        assert hasattr(main_window, 'clear_view'), "Missing clear_view"
        assert hasattr(main_window, 'switch_view'), "Missing switch_view"

        print("  [OK] Main window has all navigation methods")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Main window creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_placeholder_view():
    """Test placeholder view works."""
    print("\n[TEST 5] Testing placeholder view...")

    try:
        from ui_ctk.views.placeholder import PlaceholderView

        # Create test app
        app = ctk.CTk()
        app.geometry("800x600")

        # Create main window
        from ui_ctk.main_window import MainWindow
        main_window = MainWindow(app)
        main_window.pack(fill="both", expand=True)

        # Switch to placeholder view
        main_window.switch_view(PlaceholderView, title="Test Placeholder")

        # Verify view is created
        assert main_window.current_view is not None, "Should have current view"
        assert isinstance(main_window.current_view, PlaceholderView), "Should be PlaceholderView"

        print("  [OK] Placeholder view works correctly")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Placeholder view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_view_switching():
    """Test view switching mechanism."""
    print("\n[TEST 6] Testing view switching...")

    try:
        from ui_ctk.views.placeholder import PlaceholderView
        from ui_ctk.main_window import MainWindow

        # Create test app
        app = ctk.CTk()
        app.geometry("800x600")

        # Create main window
        main_window = MainWindow(app)
        main_window.pack(fill="both", expand=True)

        # Test switching to placeholder view
        main_window.switch_view(PlaceholderView, title="View 1")
        view1 = main_window.current_view
        assert view1 is not None, "Should have view after first switch"

        # Test switching to another placeholder
        main_window.switch_view(PlaceholderView, title="View 2")
        view2 = main_window.current_view
        assert view2 is not None, "Should have view after second switch"
        assert view1 != view2, "Should be different view instances"

        print("  [OK] View switching works correctly")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] View switching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_clear_view():
    """Test clear_view method."""
    print("\n[TEST 7] Testing clear_view...")

    try:
        from ui_ctk.views.placeholder import PlaceholderView
        from ui_ctk.main_window import MainWindow

        # Create test app
        app = ctk.CTk()
        app.geometry("800x600")

        # Create main window
        main_window = MainWindow(app)
        main_window.pack(fill="both", expand=True)

        # Create a view
        main_window.switch_view(PlaceholderView, title="Test")
        assert main_window.current_view is not None, "Should have view"

        # Clear the view
        main_window.clear_view()
        assert main_window.current_view is None, "View should be None after clear"

        print("  [OK] Clear view works correctly")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Clear view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_navigation_buttons():
    """Test navigation button handlers."""
    print("\n[TEST 8] Testing navigation button handlers...")

    try:
        from ui_ctk.main_window import MainWindow

        # Create test app
        app = ctk.CTk()
        app.geometry("800x600")

        # Create main window
        main_window = MainWindow(app)
        main_window.pack(fill="both", expand=True)

        # Test each navigation method (should show placeholders)
        main_window.show_employee_list()
        assert main_window.current_view is not None, "Should have view after show_employee_list"
        print("  [OK] show_employee_list works")

        main_window.show_alerts()
        assert main_window.current_view is not None, "Should have view after show_alerts"
        print("  [OK] show_alerts works")

        main_window.show_import()
        assert main_window.current_view is not None, "Should have view after show_import"
        print("  [OK] show_import works")

        print("  [OK] All navigation button handlers work")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Navigation button handlers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """Test that all Phase 2 files exist."""
    print("\n[TEST 9] Testing file structure...")

    files_to_check = [
        ("src/ui_ctk/app.py", "Main entry point"),
        ("src/ui_ctk/main_window.py", "Main window"),
        ("src/ui_ctk/views/placeholder.py", "Placeholder view"),
        ("src/ui_ctk/constants.py", "Constants"),
        ("src/ui_ctk/views/base_view.py", "Base view"),
        ("src/ui_ctk/forms/base_form.py", "Base form"),
    ]

    all_exist = True
    for file_path, description in files_to_check:
        if Path(file_path).exists():
            print(f"  [OK] {description}: {file_path}")
        else:
            print(f"  [FAIL] {description} missing: {file_path}")
            all_exist = False

    return all_exist


def main():
    """Run all Phase 2 integration tests."""
    print("=" * 60)
    print(" PHASE 2 INTEGRATION TESTS")
    print(" Testing UI Structure")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("CustomTkinter Setup", test_customtkinter_setup),
        ("Database Setup", test_database_setup),
        ("Main Window Creation", test_main_window_creation),
        ("Placeholder View", test_placeholder_view),
        ("View Switching", test_view_switching),
        ("Clear View", test_clear_view),
        ("Navigation Buttons", test_navigation_buttons),
        ("File Structure", test_file_structure),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n[ERROR] {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")

    print("\n" + "=" * 60)
    if passed == total:
        print(f" [OK] ALL {total} TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print(f" [FAIL] {passed}/{total} tests passed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
