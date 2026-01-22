"""Session management for authenticated users.

This module provides session tracking, timeout management,
and current user context for the application.
"""

import time
from typing import Optional
from datetime import datetime, timedelta

from auth.models import User


class Session:
    """
    User session with timeout tracking.

    Features:
    - Session timeout (default: 30 minutes)
    - Last activity tracking
    - User reference
    - Session metadata
    """

    DEFAULT_TIMEOUT_MINUTES = 30

    def __init__(self, user: User, timeout_minutes: int = DEFAULT_TIMEOUT_MINUTES):
        """
        Initialize a new session.

        Args:
            user: Authenticated user
            timeout_minutes: Session timeout in minutes (default: 30)
        """
        self.user = user
        self.timeout_minutes = timeout_minutes
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

    def is_expired(self) -> bool:
        """
        Check if session has expired due to inactivity.

        Returns:
            True if session expired, False otherwise
        """
        inactive_duration = datetime.now() - self.last_activity
        return inactive_duration >= timedelta(minutes=self.timeout_minutes)

    def refresh(self):
        """Update last activity time to prevent timeout."""
        self.last_activity = datetime.now()

    def get_remaining_minutes(self) -> float:
        """
        Get remaining time before session expires.

        Returns:
            Remaining minutes (0 if expired)
        """
        inactive_duration = datetime.now() - self.last_activity
        remaining = timedelta(minutes=self.timeout_minutes) - inactive_duration
        return max(0, remaining.total_seconds() / 60)


class SessionManager:
    """
    Manager for user sessions.

    Features:
    - Track current session
    - Automatic session timeout
    - Login/logout tracking
    - Session cleanup
    """

    def __init__(self, timeout_minutes: int = Session.DEFAULT_TIMEOUT_MINUTES):
        """
        Initialize session manager.

        Args:
            timeout_minutes: Session timeout in minutes
        """
        self.timeout_minutes = timeout_minutes
        self.current_session: Optional[Session] = None

    def create_session(self, user: User) -> Session:
        """
        Create a new session for authenticated user.

        Args:
            user: Authenticated user

        Returns:
            New Session object
        """
        self.current_session = Session(user, self.timeout_minutes)
        return self.current_session

    def get_current_user(self) -> Optional[User]:
        """
        Get current authenticated user.

        Returns:
            User object or None if no active session

        Note:
            This will return None if session has expired.
            Use is_authenticated() to check session status.
        """
        if self.current_session and not self.current_session.is_expired():
            return self.current_session.user
        return None

    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated with valid session.

        Returns:
            True if authenticated with valid session, False otherwise
        """
        return self.get_current_user() is not None

    def refresh_session(self):
        """
        Refresh current session activity time.

        Raises:
            AuthenticationError: If no valid session exists
        """
        if not self.current_session or self.current_session.is_expired():
            from auth.authentication import AuthenticationError

            raise AuthenticationError("No valid session")

        self.current_session.refresh()

    def logout(self):
        """End current session."""
        self.current_session = None

    def get_session_info(self) -> Optional[dict]:
        """
        Get information about current session.

        Returns:
            Dict with session info or None if no session
        """
        if not self.current_session:
            return None

        return {
            "username": self.current_session.user.username,
            "role": self.current_session.user.role,
            "created_at": self.current_session.created_at.isoformat(),
            "last_activity": self.current_session.last_activity.isoformat(),
            "remaining_minutes": self.current_session.get_remaining_minutes(),
        }

    def check_session_timeout(self) -> bool:
        """
        Check if session has timed out.

        Returns:
            True if session expired and was cleared, False otherwise
        """
        if self.current_session and self.current_session.is_expired():
            self.logout()
            return True
        return False


# Global session manager instance
_session_manager = SessionManager()


def login(user: User) -> Session:
    """
    Create a session for authenticated user.

    Args:
        user: Authenticated user

    Returns:
        New Session object
    """
    return _session_manager.create_session(user)


def logout():
    """End current session."""
    _session_manager.logout()


def get_current_user() -> Optional[User]:
    """
    Get current authenticated user.

    Returns:
        User object or None if not authenticated
    """
    return _session_manager.get_current_user()


def is_authenticated() -> bool:
    """
    Check if user is authenticated.

    Returns:
        True if authenticated, False otherwise
    """
    return _session_manager.is_authenticated()


def require_authentication():
    """
    Require user to be authenticated.

    Raises:
        AuthenticationError: If not authenticated
    """
    if not is_authenticated():
        from auth.authentication import AuthenticationError

        raise AuthenticationError("Authentication required")


def refresh_session():
    """Refresh current session activity."""
    _session_manager.refresh_session()


def get_session_info() -> Optional[dict]:
    """
    Get current session information.

    Returns:
        Dict with session info or None
    """
    return _session_manager.get_session_info()
