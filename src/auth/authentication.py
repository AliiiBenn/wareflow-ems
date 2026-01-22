"""Authentication service for user login and password management.

This module provides authentication functions including password hashing,
user authentication, and credential validation.
"""

import getpass
from typing import Optional, Tuple

from auth.models import User, Role


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class AccountLockedError(AuthenticationError):
    """Raised when attempting to authenticate with a locked account."""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid."""

    pass


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt password hash

    Security:
        - Uses bcrypt with salt
        - Work factor: 12 rounds
    """
    import bcrypt

    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password
        password_hash: Bcrypt hash to verify against

    Returns:
        True if password matches, False otherwise
    """
    import bcrypt

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except Exception:
        return False


class AuthenticationService:
    """
    Service for handling user authentication.

    Features:
    - User login/logout
    - Credential validation
    - Account lockout handling
    - Password management
    """

    def __init__(self):
        """Initialize authentication service."""
        self.current_user: Optional[User] = None

    def authenticate(
        self, username: str, password: str
    ) -> Tuple[bool, Optional[str], Optional[User]]:
        """
        Authenticate a user with username and password.

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            Tuple of (success, error_message, user)

        Examples:
            >>> auth = AuthenticationService()
            >>> success, error, user = auth.authenticate("admin", "password")
            >>> if success:
            ...     print(f"Logged in as {user.username}")
            ... else:
            ...     print(f"Login failed: {error}")
        """
        # Find user by username or email
        user = User.get_by_username(username)
        if not user:
            user = User.get_by_email(username)

        if not user:
            return False, "Invalid username or password", None

        # Check if account is active
        if not user.is_active:
            return False, "Account is disabled. Please contact administrator.", None

        # Check if account is locked
        if user.is_locked():
            return (
                False,
                f"Account is locked. Try again after {user.locked_until.strftime('%H:%M')}",
                None,
            )

        # Verify password
        if not user.verify_password(password):
            # Record failed attempt
            user.record_failed_login()
            return False, "Invalid username or password", None

        # Successful login - reset failed attempts
        user.reset_failed_login_attempts()

        return True, None, user

    def login(self, username: str, password: str) -> User:
        """
        Authenticate and log in a user.

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            Authenticated User object

        Raises:
            AuthenticationError: If authentication fails
            AccountLockedError: If account is locked
            InvalidCredentialsError: If credentials are invalid
        """
        success, error, user = self.authenticate(username, password)

        if not success:
            if user and user.is_locked():
                raise AccountLockedError(error)
            raise InvalidCredentialsError(error)

        # Set as current user
        self.current_user = user
        return user

    def logout(self):
        """Log out the current user."""
        self.current_user = None

    def get_current_user(self) -> Optional[User]:
        """
        Get the currently authenticated user.

        Returns:
            User object or None if not authenticated
        """
        return self.current_user

    def is_authenticated(self) -> bool:
        """
        Check if a user is currently authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self.current_user is not None

    def require_authentication(self):
        """
        Require user to be authenticated.

        Raises:
            AuthenticationError: If no user is authenticated
        """
        if not self.is_authenticated():
            raise AuthenticationError("Authentication required")

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: Role = Role.EMPLOYEE,
    ) -> User:
        """
        Create a new user.

        Args:
            username: Unique username
            email: Unique email
            password: Plain text password
            role: User role

        Returns:
            Created User object

        Raises:
            IntegrityError: If username/email already exists
        """
        return User.create_user(username, email, password, role)

    def change_password(self, user: User, new_password: str):
        """
        Change user password.

        Args:
            user: User object
            new_password: New plain text password
        """
        user.set_password(new_password)
        user.save()


# Global authentication service instance
_auth_service = AuthenticationService()


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[str], Optional[User]]:
    """
    Authenticate a user (convenience function).

    Args:
        username: Username or email
        password: Plain text password

    Returns:
        Tuple of (success, error_message, user)
    """
    return _auth_service.authenticate(username, password)


def login(username: str, password: str) -> User:
    """
    Log in a user (convenience function).

    Args:
        username: Username or email
        password: Plain text password

    Returns:
        Authenticated User object

    Raises:
        AuthenticationError: If authentication fails
    """
    return _auth_service.login(username, password)


def logout():
    """Log out the current user (convenience function)."""
    _auth_service.logout()


def get_current_user() -> Optional[User]:
    """
    Get the currently authenticated user.

    Returns:
        User object or None if not authenticated
    """
    return _auth_service.get_current_user()


def is_authenticated() -> bool:
    """
    Check if a user is currently authenticated.

    Returns:
        True if authenticated, False otherwise
    """
    return _auth_service.is_authenticated()


def require_authentication():
    """
    Require user to be authenticated.

    Raises:
        AuthenticationError: If no user is authenticated
    """
    _auth_service.require_authentication()
