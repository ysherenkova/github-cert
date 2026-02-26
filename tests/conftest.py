"""Shared test fixtures for FastAPI app tests."""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a known state before each test."""
    # Store original state
    original = {
        key: {
            "description": val["description"],
            "schedule": val["schedule"],
            "max_participants": val["max_participants"],
            "participants": val["participants"].copy(),
        }
        for key, val in activities.items()
    }
    yield activities
    # Restore original state after test
    for key, val in original.items():
        activities[key]["participants"] = val["participants"].copy()


@pytest.fixture
def sample_emails():
    """Provide sample email addresses for testing."""
    return {
        "valid": "test@mergington.edu",
        "another_valid": "student@mergington.edu",
        "invalid": "not-an-email",
        "existing_in_chess": "michael@mergington.edu",
    }


@pytest.fixture
def sample_activities():
    """Provide sample activity names."""
    return {
        "chess": "Chess Club",
        "programming": "Programming Class",
        "nonexistent": "Nonexistent Activity",
    }
