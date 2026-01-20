# Test main_window.py
"""Test main window creation."""

import sys
import customtkinter as ctk
from pathlib import Path

sys.path.insert(0, 'src')

from ui_ctk.main_window import MainWindow
from ui_ctk.constants import (
    APP_TITLE,
    NAV_EMPLOYEES,
    NAV_ALERTS,
    NAV_IMPORT,
)


def test_main_window_creation():
    """Test main window can be created."""
    print("[TEST] Testing main window creation...")

    # Create root app
    app = ctk.CTk()
    app.title("Test App")
    app.geometry("800x600")

    # Create main window
    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    # Verify components exist
    assert hasattr(main_window, 'nav_bar'), "Missing nav_bar"
    assert hasattr(main_window, 'view_container'), "Missing view_container"
    assert hasattr(main_window, 'current_view'), "Missing current_view"

    print("[OK] Main window has all components")

    # Verify navigation buttons exist
    assert hasattr(main_window, 'btn_employees'), "Missing btn_employees"
    assert hasattr(main_window, 'btn_alerts'), "Missing btn_alerts"
    assert hasattr(main_window, 'btn_import'), "Missing btn_import"

    print("[OK] Main window has all navigation buttons")

    # Verify navigation methods exist
    assert hasattr(main_window, 'show_employee_list'), "Missing show_employee_list"
    assert hasattr(main_window, 'show_alerts'), "Missing show_alerts"
    assert hasattr(main_window, 'show_import'), "Missing show_import"
    assert hasattr(main_window, 'clear_view'), "Missing clear_view"
    assert hasattr(main_window, 'switch_view'), "Missing switch_view"

    print("[OK] Main window has all navigation methods")

    # Cleanup
    app.destroy()

    print("[OK] Main window creation test passed")


def test_navigation_bar():
    """Test navigation bar structure."""
    print("\n[TEST] Testing navigation bar structure...")

    # Create root app
    app = ctk.CTk()
    app.geometry("800x600")

    # Create main window
    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    # Verify navigation bar is created
    assert main_window.nav_bar is not None, "Navigation bar should exist"
    assert main_window.nav_bar.winfo_height() > 0, "Navigation bar should have height"

    print("[OK] Navigation bar structure test passed")

    # Cleanup
    app.destroy()


def test_view_container():
    """Test view container structure."""
    print("\n[TEST] Testing view container structure...")

    # Create root app
    app = ctk.CTk()
    app.geometry("800x600")

    # Create main window
    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    # Verify view container is created
    assert main_window.view_container is not None, "View container should exist"

    print("[OK] View container structure test passed")

    # Cleanup
    app.destroy()


def test_clear_view():
    """Test clear_view method."""
    print("\n[TEST] Testing clear_view method...")

    # Create root app
    app = ctk.CTk()
    app.geometry("800x600")

    # Create main window
    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    # Initially should have a view (placeholder for employee list)
    initial_view = main_window.current_view
    assert initial_view is not None, "Should have initial view"

    # Clear the view
    main_window.clear_view()

    # Verify view is cleared
    assert main_window.current_view is None, "View should be None after clear"

    print("[OK] Clear view test passed")

    # Cleanup
    app.destroy()


def test_switch_view():
    """Test switch_view method with placeholder."""
    print("\n[TEST] Testing switch_view method...")

    # Create root app
    app = ctk.CTk()
    app.geometry("800x600")

    # Create main window
    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    # Import PlaceholderView
    from ui_ctk.views.placeholder import PlaceholderView

    # Switch to placeholder view
    main_window.switch_view(PlaceholderView, title="Test View")

    # Verify new view is created
    assert main_window.current_view is not None, "Should have current view"
    assert isinstance(main_window.current_view, PlaceholderView), "Should be PlaceholderView"

    print("[OK] Switch view test passed")

    # Cleanup
    app.destroy()


def test_navigation_methods():
    """Test navigation methods work."""
    print("\n[TEST] Testing navigation methods...")

    # Create root app
    app = ctk.CTk()
    app.geometry("800x600")

    # Create main window
    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    # Test each navigation method (should show placeholders)
    try:
        main_window.show_employee_list()
        assert main_window.current_view is not None, "Should have view after show_employee_list"
        print("[OK] show_employee_list works")
    except Exception as e:
        print(f"[FAIL] show_employee_list failed: {e}")
        raise

    try:
        main_window.show_alerts()
        assert main_window.current_view is not None, "Should have view after show_alerts"
        print("[OK] show_alerts works")
    except Exception as e:
        print(f"[FAIL] show_alerts failed: {e}")
        raise

    try:
        main_window.show_import()
        assert main_window.current_view is not None, "Should have view after show_import"
        print("[OK] show_import works")
    except Exception as e:
        print(f"[FAIL] show_import failed: {e}")
        raise

    print("[OK] Navigation methods test passed")

    # Cleanup
    app.destroy()


def test_imports():
    """Test that all imports work correctly."""
    print("\n[TEST] Testing imports...")

    try:
        from ui_ctk.main_window import MainWindow
        from ui_ctk.views.base_view import BaseView
        print("[OK] All main_window.py imports successful")
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        raise


if __name__ == "__main__":
    print("=" * 50)
    print(" TESTING MAIN_WINDOW.PY")
    print("=" * 50)

    try:
        test_imports()
        test_main_window_creation()
        test_navigation_bar()
        test_view_container()
        test_clear_view()
        test_switch_view()
        test_navigation_methods()

        print("\n" + "=" * 50)
        print(" [OK] ALL MAIN_WINDOW.PY TESTS PASSED")
        print("=" * 50)
    except Exception as e:
        print(f"\n[FAIL] Tests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
