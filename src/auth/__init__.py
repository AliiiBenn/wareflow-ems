"""Authentication and authorization module.

This module provides user authentication, session management,
and role-based access control for the application.
"""

from auth.models import User, Role
from auth.authentication import AuthenticationService, authenticate_user, hash_password, verify_password
from auth.session import SessionManager, get_current_user, login, logout

__all__ = [
    "User",
    "Role",
    "AuthenticationService",
    "authenticate_user",
    "hash_password",
    "verify_password",
    "SessionManager",
    "get_current_user",
    "login",
    "logout",
]
