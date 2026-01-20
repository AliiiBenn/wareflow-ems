#!/usr/bin/env python
"""
Integration tests for Phase 4 - Alerts View.

Tests the complete alerts functionality.
"""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

import customtkinter as ctk
from employee.alerts import AlertQuery, AlertType, UrgencyLevel
from ui_ctk.views.alerts_view import AlertsView
from database.connection import database, init_database
from datetime import date, timedelta


def test_urgency_calculation():
    """Test urgency level calculation."""
    print("[TEST 1] Testing urgency calculation...")

    today = date.today()

    # Test critical (< 30 days)
    critical_date = today + timedelta(days=15)
    urgency = AlertQuery.calculate_urgency(critical_date)
    assert urgency == UrgencyLevel.CRITICAL, "15 days should be critical"
    print("  [OK] Critical urgency calculated correctly")

    # Test warning (30-60 days)
    warning_date = today + timedelta(days=45)
    urgency = AlertQuery.calculate_urgency(warning_date)
    assert urgency == UrgencyLevel.WARNING, "45 days should be warning"
    print("  [OK] Warning urgency calculated correctly")

    # Test info (60-90 days)
    info_date = today + timedelta(days=75)
    urgency = AlertQuery.calculate_urgency(info_date)
    assert urgency == UrgencyLevel.INFO, "75 days should be info"
    print("  [OK] Info urgency calculated correctly")

    # Test ok (> 90 days)
    ok_date = today + timedelta(days=120)
    urgency = AlertQuery.calculate_urgency(ok_date)
    assert urgency == UrgencyLevel.OK, "120 days should be ok"
    print("  [OK] OK urgency calculated correctly")

    # Test expired
    expired_date = today - timedelta(days=10)
    urgency = AlertQuery.calculate_urgency(expired_date)
    assert urgency == UrgencyLevel.CRITICAL, "Expired should be critical"
    print("  [OK] Expired urgency calculated correctly")

    return True


def test_alert_structure():
    """Test alert data structure."""
    print("\n[TEST 2] Testing alert data structure...")

    try:
        from employee.alerts import Alert, AlertType

        # Create test alert
        alert = Alert(
            alert_type=AlertType.CACES,
            employee=None,  # Not checking employee
            description="CACES R489-1A",
            expiration_date=date.today(),
            days_until=45,
            urgency=UrgencyLevel.WARNING
        )

        # Verify properties
        assert hasattr(alert, 'urgency_text'), "Should have urgency_text"
        assert hasattr(alert, 'urgency_color'), "Should have urgency_color"
        assert alert.urgency_text == "Bientôt (45 jours restants)", "Wrong urgency text"
        assert alert.urgency_color == "#FFC107", "Wrong urgency color"

        print("  [OK] Alert structure is correct")

        return True

    except Exception as e:
        print(f"  [FAIL] Alert structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_alert_queries():
    """Test alert query methods."""
    print("\n[TEST 3] Testing alert queries...")

    try:
        # Initialize database
        init_database(Path("employee_manager.db"))
        if database.is_closed():
            database.connect()

        # Test get_caces_alerts
        caces_alerts = AlertQuery.get_caces_alerts(days_threshold=90)
        assert isinstance(caces_alerts, list), "Should return list"
        print(f"  [OK] Found {len(caces_alerts)} CACES alerts")

        # Test get_medical_alerts
        medical_alerts = AlertQuery.get_medical_alerts(days_threshold=90)
        assert isinstance(medical_alerts, list), "Should return list"
        print(f"  [OK] Found {len(medical_alerts)} medical alerts")

        # Test get_all_alerts
        all_alerts = AlertQuery.get_all_alerts(days_threshold=90)
        assert isinstance(all_alerts, list), "Should return list"
        print(f"  [OK] Found {len(all_alerts)} total alerts")

        # Verify sorting
        for i in range(len(all_alerts) - 1):
            assert all_alerts[i].days_until <= all_alerts[i+1].days_until, \
                "Should be sorted by days_until"
        print("  [OK] Alerts sorted correctly")

        return True

    except Exception as e:
        print(f"  [FAIL] Alert queries test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_alerts_view():
    """Test alerts view creation."""
    print("\n[TEST 4] Testing alerts view creation...")

    try:
        # Create test app
        app = ctk.CTk()
        app.geometry("1000x700")

        # Create alerts view
        alerts_view = AlertsView(app, title="Alertes")

        # Verify components exist
        assert hasattr(alerts_view, 'type_filter_var'), "Missing type_filter_var"
        assert hasattr(alerts_view, 'days_filter_var'), "Missing days_filter_var"
        assert hasattr(alerts_view, 'alerts_frame'), "Missing alerts_frame"
        assert hasattr(alerts_view, 'alerts'), "Missing alerts list"

        print("  [OK] Alerts view has all components")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Alerts view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_filter_functionality():
    """Test filter controls."""
    print("\n[TEST 5] Testing filter functionality...")

    try:
        # Create test app
        app = ctk.CTk()
        app.geometry("1000x700")

        # Create alerts view
        alerts_view = AlertsView(app, title="Alertes")

        # Test type filter
        alerts_view.type_filter_var.set("CACES")
        alert_types = alerts_view._parse_type_filter()
        assert alert_types == [AlertType.CACES], "Should parse CACES filter"
        print("  [OK] Type filter parsing works")

        # Test days filter
        alerts_view.days_filter_var.set("30 jours")
        days_threshold = alerts_view._parse_days_filter()
        assert days_threshold == 30, "Should parse 30 days filter"
        print("  [OK] Days filter parsing works")

        # Test "all" filter
        alerts_view.type_filter_var.set("Tous")
        alert_types = alerts_view._parse_type_filter()
        assert alert_types is None, "Should parse 'All' as None"
        print("  [OK] 'All' type filter works")

        alerts_view.days_filter_var.set("Toutes")
        days_threshold = alerts_view._parse_days_filter()
        assert days_threshold == 9999, "Should parse 'All' as 9999"
        print("  [OK] 'All' days filter works")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Filter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_alert_summary():
    """Test alert summary calculation."""
    print("\n[TEST 6] Testing alert summary...")

    try:
        summary = AlertQuery.get_alerts_summary()

        # Verify summary structure
        assert "critical" in summary, "Should have critical count"
        assert "warning" in summary, "Should have warning count"
        assert "info" in summary, "Should have info count"
        assert "ok" in summary, "Should have ok count"
        assert "total" in summary, "Should have total count"

        # Verify total matches sum
        total_manual = summary["critical"] + summary["warning"] + summary["info"] + summary["ok"]
        assert total_manual == summary["total"], "Total should match sum"

        print(f"  [OK] Summary: {summary}")

        return True

    except Exception as e:
        print(f"  [FAIL] Alert summary test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 4 integration tests."""
    print("=" * 70)
    print(" PHASE 4 INTEGRATION TESTS")
    print(" Testing Alerts View")
    print("=" * 70)

    # Initialize database
    init_database(Path("employee_manager.db"))
    if database.is_closed():
        database.connect()

    tests = [
        ("Urgency Calculation", test_urgency_calculation),
        ("Alert Data Structure", test_alert_structure),
        ("Alert Queries", test_alert_queries),
        ("Alerts View Creation", test_alerts_view),
        ("Filter Functionality", test_filter_functionality),
        ("Alert Summary", test_alert_summary),
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
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")

    print("\n" + "=" * 70)
    if passed == total:
        print(f" [OK] ALL {total} TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print(f" [FAIL] {passed}/{total} tests passed")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
