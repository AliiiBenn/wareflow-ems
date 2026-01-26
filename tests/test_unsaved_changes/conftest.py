"""Pytest configuration for unsaved changes tests."""

import sys
from pathlib import Path

import customtkinter as ctk
import pytest


# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture(scope="session", autouse=True)
def setup_ctk():
    """Setup CustomTkinter for all tests."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create a root window that will persist for the session
    root = ctk.CTk()
    root.withdraw()  # Hide it

    yield root

    # Cleanup
    root.destroy()
