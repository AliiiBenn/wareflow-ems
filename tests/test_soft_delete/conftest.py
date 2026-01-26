"""Pytest configuration and fixtures for soft delete tests."""

import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

import customtkinter as ctk
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import database
from employee.models import Caces, Employee, MedicalVisit, OnlineTraining


@pytest.fixture(scope="function")
def db_connection():
    """Create a test database connection."""
    # Connect to test database
    db_path = ":memory:"  # Use in-memory database for tests

    # Initialize database connection
    database.init(db_path)

    # Connect
    database.connect()

    # Create tables
    database.create_tables(
        [Employee, Caces, MedicalVisit, OnlineTraining], safe=True
    )

    yield database

    # Cleanup: close connection
    database.close()
    # Reinitialize to default for next test
    database.init(":memory:")


@pytest.fixture(scope="function")
def sample_employee(db_connection):
    """Create a sample employee for testing."""
    employee = Employee.create(
        external_id=str(uuid4()),
        first_name="John",
        last_name="Doe",
        email="john.doe@test.com",
        phone="1234567890",
        workspace="Zone A",
        role="Operator",
        contract_type="CDI",
        entry_date=date(2023, 1, 1),
        current_status="active",
    )
    return employee


@pytest.fixture(scope="function")
def sample_caces(db_connection, sample_employee):
    """Create a sample CACES certification for testing."""
    caces = Caces.create(
        employee=sample_employee,
        kind="R489-1A",
        completion_date=date(2023, 1, 1),
        expiration_date=date(2024, 1, 1),
    )
    return caces


@pytest.fixture(scope="function")
def sample_medical_visit(db_connection, sample_employee):
    """Create a sample medical visit for testing."""
    visit = MedicalVisit.create(
        employee=sample_employee,
        visit_type="periodic",
        visit_date=date(2023, 6, 1),
        expiration_date=date(2024, 6, 1),
        result="fit",
    )
    return visit


@pytest.fixture(scope="function")
def sample_training(db_connection, sample_employee):
    """Create a sample online training for testing."""
    training = OnlineTraining.create(
        employee=sample_employee,
        title="Safety Training",
        completion_date=date(2023, 6, 1),
        expiration_date=date(2024, 6, 1),
        validity_months=12,
    )
    return training


@pytest.fixture(scope="session")
def ctk_app():
    """Create a CustomTkinter application for GUI tests."""
    app = ctk.CTk()
    app.geometry("800x600")
    yield app
    app.destroy()
