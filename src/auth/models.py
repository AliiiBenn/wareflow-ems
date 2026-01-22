"""User and role models for authentication and authorization.

This module defines the User model with password hashing,
role-based access control, and audit fields.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum

import bcrypt
from peewee import (
    Model,
    UUIDField,
    CharField,
    BooleanField,
    DateTimeField,
    IntegerField,
    ForeignKeyField,
    DoesNotExist,
)

from database.connection import database


class Role(str, Enum):
    """User roles for access control."""

    ADMIN = "admin"
    HR_MANAGER = "hr_manager"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    VIEWER = "viewer"


class User(Model):
    """
    Application user with authentication and authorization.

    Features:
    - UUID primary key
    - Unique username and email
    - Bcrypt password hashing
    - Role-based access control
    - Account lockout after failed login attempts
    - Audit fields (created_at, last_login)
    - Account status (active/inactive)

    Security:
    - Passwords stored as bcrypt hashes (salt + hash)
    - Failed login attempt tracking
    - Automatic account lockout after 5 failed attempts
    - Session management support
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    username = CharField(unique=True, index=True, max_length=50)
    email = CharField(unique=True, index=True, max_length=255)
    password_hash = CharField(max_length=255)  # Bcrypt hash
    role = CharField(max_length=20)  # Role enum value

    # Account status
    is_active = BooleanField(default=True)
    failed_login_attempts = IntegerField(default=0)
    locked_until = DateTimeField(null=True)

    # Audit fields
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    last_login = DateTimeField(null=True)
    password_changed_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = "users"
        indexes = (
            (("username",), True),  # Unique index on username
            (("email",), True),  # Unique index on email
        )

    def __str__(self):
        return f"User({self.username}, role={self.role})"

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

    def set_password(self, password: str):
        """
        Hash and set user password using bcrypt.

        Args:
            password: Plain text password

        Security:
            - Uses bcrypt with salt
            - Work factor: 12 rounds (configurable)
            - Auto-generates unique salt per password
        """
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
        self.password_hash = password_hash.decode("utf-8")
        self.password_changed_at = datetime.now()

    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise

        Security:
            - Constant-time comparison (prevents timing attacks)
            - Handles bcrypt format correctly
        """
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                self.password_hash.encode("utf-8"),
            )
        except Exception:
            return False

    def check_password(self, password: str) -> bool:
        """
        Alias for verify_password() for compatibility.

        This method is provided for Django-style compatibility.
        """
        return self.verify_password(password)

    def is_locked(self) -> bool:
        """
        Check if user account is currently locked.

        Returns:
            True if account is locked, False otherwise
        """
        if not self.locked_until:
            return False

        # Check if lock has expired
        if datetime.now() >= self.locked_until:
            # Auto-unlock
            self.locked_until = None
            self.failed_login_attempts = 0
            self.save()
            return False

        return True

    def record_failed_login(self):
        """
        Record a failed login attempt and lock account if needed.

        Lock account after 5 failed attempts for 30 minutes.
        """
        self.failed_login_attempts += 1

        if self.failed_login_attempts >= 5:
            # Lock for 30 minutes
            from datetime import timedelta

            self.locked_until = datetime.now() + timedelta(minutes=30)

        self.save()

    def reset_failed_login_attempts(self):
        """Reset failed login attempts after successful login."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.now()
        self.save()

    def has_role(self, role: Role) -> bool:
        """
        Check if user has specific role.

        Args:
            role: Role to check

        Returns:
            True if user has the role, False otherwise
        """
        return self.role == role.value

    def is_admin(self) -> bool:
        """Check if user is an administrator."""
        return self.role == Role.ADMIN.value

    def is_hr_manager(self) -> bool:
        """Check if user is an HR manager."""
        return self.role == Role.HR_MANAGER.value

    def is_manager(self) -> bool:
        """Check if user is a manager."""
        return self.role == Role.MANAGER.value

    def can_manage_employees(self) -> bool:
        """
        Check if user can manage employee records.

        Returns:
            True if admin or HR manager, False otherwise
        """
        return self.role in {Role.ADMIN.value, Role.HR_MANAGER.value}

    def can_delete_employees(self) -> bool:
        """
        Check if user can delete employee records.

        Returns:
            True if admin only, False otherwise
        """
        return self.role == Role.ADMIN.value

    @classmethod
    def get_by_username(cls, username: str) -> Optional["User"]:
        """
        Get user by username.

        Args:
            username: Username to look up

        Returns:
            User object or None if not found
        """
        try:
            return cls.get(cls.username == username)
        except DoesNotExist:
            return None

    @classmethod
    def get_by_email(cls, email: str) -> Optional["User"]:
        """
        Get user by email.

        Args:
            email: Email to look up

        Returns:
            User object or None if not found
        """
        try:
            return cls.get(cls.email == email)
        except DoesNotExist:
            return None

    @classmethod
    def create_user(
        cls,
        username: str,
        email: str,
        password: str,
        role: Role = Role.EMPLOYEE,
    ) -> "User":
        """
        Create a new user with password hashing.

        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            role: User role (default: EMPLOYEE)

        Returns:
            Created User object

        Raises:
            IntegrityError: If username or email already exists
        """
        user = cls(username=username, email=email, role=role.value)
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def create_admin(cls, username: str, email: str, password: str) -> "User":
        """
        Create an admin user.

        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)

        Returns:
            Created admin User object
        """
        return cls.create_user(username, email, password, Role.ADMIN)

    def save(self, *args, **kwargs):
        """Save user and update updated_at timestamp."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)


# Create User table if it doesn't exist
def create_tables():
    """Create authentication tables if they don't exist."""
    database.create_tables([User], safe=True)
