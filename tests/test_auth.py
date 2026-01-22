"""Tests for authentication and session management.

These tests ensure the authentication system works correctly:
- User creation and password hashing
- Login and logout
- Account lockout
- Session management
- Password verification
"""

import pytest
from datetime import datetime, timedelta

from auth.models import User, Role, create_tables
from auth.authentication import (
    AuthenticationService,
    AuthenticationError,
    AccountLockedError,
    InvalidCredentialsError,
    hash_password,
    verify_password,
    authenticate_user,
)
from auth.session import Session, SessionManager, login, logout, get_current_user


class TestUserModel:
    """Test suite for User model."""

    def test_create_user(self, db):
        """Test creating a new user."""
        user = User.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
            role=Role.EMPLOYEE,
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == Role.EMPLOYEE.value
        assert user.is_active is True
        assert user.password_hash is not None
        assert user.password_hash != "TestPassword123!"  # Should be hashed

    def test_create_admin_user(self, db):
        """Test creating an admin user."""
        admin = User.create_admin(
            username="admin",
            email="admin@example.com",
            password="AdminPassword123!",
        )

        assert admin.role == Role.ADMIN.value
        assert admin.is_admin() is True

    def test_password_hashing(self, db):
        """Test that passwords are hashed correctly."""
        user = User.create_user(
            username="hashuser",
            email="hash@example.com",
            password="MyPassword123!",
        )

        # Password should be hashed
        assert user.password_hash.startswith("$2b$")  # bcrypt prefix
        assert len(user.password_hash) == 60  # bcrypt hash length

        # Verify password works
        assert user.verify_password("MyPassword123!") is True
        assert user.verify_password("WrongPassword") is False

    def test_set_password(self, db):
        """Test changing user password."""
        user = User.create_user(
            username="changepwd",
            email="change@example.com",
            password="OldPassword123!",
        )

        # Change password
        user.set_password("NewPassword456!")
        user.save()

        # Old password doesn't work
        assert user.verify_password("OldPassword123!") is False

        # New password works
        assert user.verify_password("NewPassword456!") is True

    def test_get_by_username(self, db):
        """Test retrieving user by username."""
        User.create_user(
            username="findme",
            email="find@example.com",
            password="Password123!",
        )

        user = User.get_by_username("findme")
        assert user is not None
        assert user.username == "findme"

    def test_get_by_email(self, db):
        """Test retrieving user by email."""
        User.create_user(
            username="emailuser",
            email="emailuser@example.com",
            password="Password123!",
        )

        user = User.get_by_email("emailuser@example.com")
        assert user is not None
        assert user.email == "emailuser@example.com"

    def test_failed_login_attempts(self, db):
        """Test failed login attempt tracking."""
        user = User.create_user(
            username="lockme",
            email="lock@example.com",
            password="Password123!",
        )

        assert user.failed_login_attempts == 0

        # Record 3 failed attempts
        for _ in range(3):
            user.record_failed_login()

        assert user.failed_login_attempts == 3
        assert user.is_locked() is False

        # 2 more attempts should trigger lockout
        user.record_failed_login()
        user.record_failed_login()

        assert user.failed_login_attempts == 5
        assert user.is_locked() is True
        assert user.locked_until is not None

    def test_account_unlock(self, db):
        """Test automatic account unlock after timeout."""
        user = User.create_user(
            username="unlockme",
            email="unlock@example.com",
            password="Password123!",
        )

        # Lock account
        for _ in range(5):
            user.record_failed_login()

        assert user.is_locked() is True

        # Manually expire lock for testing
        user.locked_until = datetime.now() - timedelta(minutes=1)

        # Check if locked should auto-unlock
        assert user.is_locked() is False
        assert user.failed_login_attempts == 0

    def test_reset_failed_attempts(self, db):
        """Test resetting failed login attempts."""
        user = User.create_user(
            username="resetme",
            email="reset@example.com",
            password="Password123!",
        )

        # Record failed attempts
        user.record_failed_login()
        user.record_failed_login()
        assert user.failed_login_attempts == 2

        # Reset should clear them
        user.reset_failed_login_attempts()
        assert user.failed_login_attempts == 0
        assert user.locked_until is None

    def test_role_checks(self, db):
        """Test role checking methods."""
        admin = User.create_user("admin", "admin@test.com", "Pass123!", Role.ADMIN)
        hr = User.create_user("hr", "hr@test.com", "Pass123!", Role.HR_MANAGER)
        manager = User.create_user("mgr", "mgr@test.com", "Pass123!", Role.MANAGER)
        employee = User.create_user("emp", "emp@test.com", "Pass123!", Role.EMPLOYEE)

        # Admin checks
        assert admin.is_admin() is True
        assert admin.is_hr_manager() is False

        # HR checks
        assert hr.is_hr_manager() is True
        assert hr.is_admin() is False

        # Manager checks
        assert manager.is_manager() is True
        assert manager.is_admin() is False

        # Employee checks
        assert employee.is_admin() is False
        assert employee.is_hr_manager() is False
        assert employee.is_manager() is False

    def test_can_manage_employees(self, db):
        """Test employee management permissions."""
        admin = User.create_user("admin", "admin@test.com", "Pass123!", Role.ADMIN)
        hr = User.create_user("hr", "hr@test.com", "Pass123!", Role.HR_MANAGER)
        employee = User.create_user("emp", "emp@test.com", "Pass123!", Role.EMPLOYEE)

        assert admin.can_manage_employees() is True
        assert hr.can_manage_employees() is True
        assert employee.can_manage_employees() is False

    def test_can_delete_employees(self, db):
        """Test employee deletion permissions."""
        admin = User.create_user("admin", "admin@test.com", "Pass123!", Role.ADMIN)
        hr = User.create_user("hr", "hr@test.com", "Pass123!", Role.HR_MANAGER)

        assert admin.can_delete_employees() is True
        assert hr.can_delete_employees() is False


class TestAuthenticationService:
    """Test suite for AuthenticationService."""

    def test_successful_authentication(self, db):
        """Test successful user authentication."""
        user = User.create_user("authuser", "auth@test.com", "CorrectPassword123!")

        auth_service = AuthenticationService()
        success, error, authenticated_user = auth_service.authenticate("authuser", "CorrectPassword123!")

        assert success is True
        assert error is None
        assert authenticated_user is not None
        assert authenticated_user.username == "authuser"

    def test_authentication_with_wrong_password(self, db):
        """Test authentication with incorrect password."""
        user = User.create_user("wrongpwd", "wrong@test.com", "CorrectPassword123!")

        auth_service = AuthenticationService()
        success, error, authenticated_user = auth_service.authenticate("wrongpwd", "WrongPassword")

        assert success is False
        assert error is not None
        assert authenticated_user is None
        assert "Invalid username or password" in error

    def test_authentication_with_nonexistent_user(self, db):
        """Test authentication with nonexistent user."""
        auth_service = AuthenticationService()
        success, error, authenticated_user = auth_service.authenticate("nonexistent", "password")

        assert success is False
        assert error is not None
        assert authenticated_user is None

    def test_authentication_with_locked_account(self, db):
        """Test authentication with locked account."""
        user = User.create_user("locked", "locked@test.com", "Password123!")

        # Lock account
        for _ in range(5):
            user.record_failed_login()

        auth_service = AuthenticationService()
        success, error, authenticated_user = auth_service.authenticate("locked", "Password123!")

        assert success is False
        assert "locked" in error.lower()

    def test_login_method(self, db):
        """Test login method."""
        User.create_user("loginuser", "login@test.com", "Password123!")

        auth_service = AuthenticationService()

        # Successful login
        user = auth_service.login("loginuser", "Password123!")
        assert user.username == "loginuser"
        assert auth_service.is_authenticated() is True
        assert auth_service.get_current_user() is not None

    def test_login_with_invalid_credentials_raises_error(self, db):
        """Test that login raises error with invalid credentials."""
        User.create_user("raiseuser", "raise@test.com", "Password123!")

        auth_service = AuthenticationService()

        with pytest.raises(InvalidCredentialsError):
            auth_service.login("raiseuser", "WrongPassword")

    def test_logout(self, db):
        """Test logout functionality."""
        User.create_user("logoutuser", "logout@test.com", "Password123!")

        auth_service = AuthenticationService()
        auth_service.login("logoutuser", "Password123!")

        assert auth_service.is_authenticated() is True

        auth_service.logout()

        assert auth_service.is_authenticated() is False
        assert auth_service.get_current_user() is None


class TestPasswordHashing:
    """Test suite for password hashing functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "MyPassword123!"
        password_hash = hash_password(password)

        assert password_hash != password
        assert password_hash.startswith("$2b$")
        assert len(password_hash) == 60

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "CorrectPassword123!"
        password_hash = hash_password(password)

        assert verify_password(password, password_hash) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "CorrectPassword123!"
        password_hash = hash_password(password)

        assert verify_password("WrongPassword", password_hash) is False

    def test_hash_is_unique(self):
        """Test that hashing same password twice gives different hashes (due to salt)."""
        password = "SamePassword123!"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to unique salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestSessionManagement:
    """Test suite for session management."""

    def test_create_session(self, db):
        """Test creating a session."""
        user = User.create_user("sessionuser", "session@test.com", "Password123!")

        session = Session(user)

        assert session.user == user
        assert session.is_expired() is False
        assert session.get_remaining_minutes() > 0

    def test_session_expiration(self, db):
        """Test session expiration."""
        user = User.create_user("expireuser", "expire@test.com", "Password123!")

        # Create session with very short timeout
        session = Session(user, timeout_minutes=0)

        # Session should be immediately expired
        assert session.is_expired() is True
        assert session.get_remaining_minutes() == 0

    def test_session_refresh(self, db):
        """Test refreshing a session."""
        user = User.create_user("refreshuser", "refresh@test.com", "Password123!")

        session = Session(user, timeout_minutes=30)

        # Get initial remaining time
        initial_remaining = session.get_remaining_minutes()

        # Wait a bit and refresh
        import time

        time.sleep(0.1)
        session.refresh()

        # Remaining time should be back to near 30 minutes
        after_refresh = session.get_remaining_minutes()

        assert after_refresh > initial_remaining

    def test_session_manager(self, db):
        """Test SessionManager."""
        user = User.create_user("mgruser", "mgr@test.com", "Password123!")

        manager = SessionManager()

        # No user initially
        assert manager.get_current_user() is None
        assert manager.is_authenticated() is False

        # Create session
        session = manager.create_session(user)

        assert manager.get_current_user() == user
        assert manager.is_authenticated() is True

        # Logout
        manager.logout()

        assert manager.get_current_user() is None
        assert manager.is_authenticated() is False

    def test_get_session_info(self, db):
        """Test getting session information."""
        user = User.create_user("infouser", "info@test.com", "Password123!")

        manager = SessionManager()
        manager.create_session(user)

        info = manager.get_session_info()

        assert info is not None
        assert info["username"] == "infouser"
        assert info["role"] == Role.EMPLOYEE.value
        assert "created_at" in info
        assert "last_activity" in info
        assert "remaining_minutes" in info


class TestIntegration:
    """Integration tests for authentication flow."""

    def test_complete_login_flow(self, db):
        """Test complete login flow."""
        # Create user
        user = User.create_user("flowuser", "flow@test.com", "Password123!")

        # Authenticate
        success, error, authenticated_user = authenticate_user("flowuser", "Password123!")
        assert success is True

        # Create session
        from auth.session import login as session_login

        session = session_login(authenticated_user)
        assert session.user == authenticated_user

        # Check authenticated
        from auth.session import is_authenticated

        assert is_authenticated() is True

        # Logout
        from auth.session import logout as session_logout

        session_logout()
        assert is_authenticated() is False
