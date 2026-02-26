"""Tests for business logic and validation using AAA pattern."""
import pytest


class TestParticipantValidation:
    """Test participant validation logic."""

    def test_valid_email_format_accepted(self, client, reset_activities, sample_activities):
        """Verify valid email formats are accepted."""
        # Arrange
        valid_emails = [
            "simple@mergington.edu",
            "with.dot@mergington.edu",
            "with+plus@mergington.edu",
            "underscore_test@mergington.edu",
        ]
        activity = sample_activities["programming"]

        # Act & Assert
        for email in valid_emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200

    def test_duplicate_signup_prevented(self, client, reset_activities, sample_emails, sample_activities):
        """Verify same email cannot sign up twice."""
        # Arrange
        email = sample_emails["valid"]
        activity = sample_activities["programming"]

        # Act (first signup)
        response1 = client.post(f"/activities/{activity}/signup?email={email}")

        # Act (second signup)
        response2 = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400


class TestActivityCapacity:
    """Test activity capacity management."""

    def test_participants_not_exceed_max(self, client, reset_activities, sample_activities):
        """Verify activity structure tracks max participants correctly."""
        # Arrange
        activity = sample_activities["chess"]
        max_participants = reset_activities[activity]["max_participants"]
        current_count = len(reset_activities[activity]["participants"])

        # Act & Assert
        assert isinstance(max_participants, int)
        assert max_participants > 0
        assert current_count <= max_participants

    def test_all_activities_have_capacity(self, client, reset_activities):
        """Verify all activities have max_participants defined."""
        # Arrange & Act
        activities_data = reset_activities

        # Assert
        for activity_name, activity_data in activities_data.items():
            assert "max_participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0


class TestDataIntegrity:
    """Test data integrity and consistency."""

    def test_signup_and_unregister_maintain_consistency(self, client, reset_activities, sample_emails, sample_activities):
        """Verify signup followed by unregister returns to original state."""
        # Arrange
        email = sample_emails["valid"]
        activity = sample_activities["chess"]
        original_participants = reset_activities[activity]["participants"].copy()

        # Act (signup)
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act (unregister)
        client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert reset_activities[activity]["participants"] == original_participants

    def test_unregister_does_not_affect_other_activities(self, client, reset_activities, sample_emails, sample_activities):
        """Verify unregistering from one activity doesn't affect others."""
        # Arrange
        email = sample_emails["existing_in_chess"]
        chess_activity = sample_activities["chess"]
        programming = sample_activities["programming"]
        prog_before = reset_activities[programming]["participants"].copy()

        # Act
        client.delete(f"/activities/{chess_activity}/unregister?email={email}")

        # Assert
        assert reset_activities[programming]["participants"] == prog_before

    def test_activities_endpoint_reflects_signup_changes(self, client, reset_activities, sample_emails, sample_activities):
        """Verify GET /activities reflects signup changes immediately."""
        # Arrange
        email = sample_emails["valid"]
        activity = sample_activities["chess"]

        # Act (signup)
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act (fetch activities)
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert email in data[activity]["participants"]
