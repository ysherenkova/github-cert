"""Tests for FastAPI endpoints using AAA pattern."""
import pytest


class TestGetActivities:
    """Test GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Verify all activities are returned with correct structure."""
        # Arrange: endpoint is ready

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "description" in data["Chess Club"]
        assert "schedule" in data["Chess Club"]
        assert "max_participants" in data["Chess Club"]
        assert "participants" in data["Chess Club"]

    def test_get_activities_has_participant_list(self, client):
        """Verify activities contain participant lists."""
        # Arrange: endpoint is ready

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        for activity in data.values():
            assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client, reset_activities, sample_emails, sample_activities):
        """Verify successful signup adds participant and returns confirmation."""
        # Arrange
        email = sample_emails["valid"]
        activity = sample_activities["chess"]
        initial_count = len(reset_activities[activity]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in reset_activities[activity]["participants"]
        assert len(reset_activities[activity]["participants"]) == initial_count + 1

    def test_signup_duplicate_fails(self, client, reset_activities, sample_emails, sample_activities):
        """Verify duplicate signup returns 400 error."""
        # Arrange
        email = sample_emails["existing_in_chess"]
        activity = sample_activities["chess"]

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities, sample_emails, sample_activities):
        """Verify signup for nonexistent activity returns 404."""
        # Arrange
        email = sample_emails["valid"]
        activity = sample_activities["nonexistent"]

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_with_special_characters_in_email(self, client, reset_activities, sample_activities):
        """Verify signup handles emails with special characters."""
        # Arrange
        email = "test+plus@mergington.edu"
        activity = sample_activities["programming"]

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in reset_activities[activity]["participants"]

    def test_signup_empty_email_fails(self, client, reset_activities, sample_activities):
        """Verify signup with empty email fails."""
        # Arrange
        email = ""
        activity = sample_activities["chess"]

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Email cannot be empty" in data["detail"]


class TestUnregisterFromActivity:
    """Test DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client, reset_activities, sample_emails, sample_activities):
        """Verify successful unregister removes participant."""
        # Arrange
        email = sample_emails["existing_in_chess"]
        activity = sample_activities["chess"]
        initial_count = len(reset_activities[activity]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email not in reset_activities[activity]["participants"]
        assert len(reset_activities[activity]["participants"]) == initial_count - 1

    def test_unregister_nonexistent_participant_fails(self, client, reset_activities, sample_emails, sample_activities):
        """Verify unregister of non-existent participant returns 400."""
        # Arrange
        email = sample_emails["valid"]
        activity = sample_activities["chess"]

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client, reset_activities, sample_emails, sample_activities):
        """Verify unregister from nonexistent activity returns 404."""
        # Arrange
        email = sample_emails["valid"]
        activity = sample_activities["nonexistent"]

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_twice_fails(self, client, reset_activities, sample_emails, sample_activities):
        """Verify unregistering twice fails on second attempt."""
        # Arrange
        email = sample_emails["existing_in_chess"]
        activity = sample_activities["chess"]

        # Act (first unregister)
        response1 = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Act (second unregister)
        response2 = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400


class TestRootRedirect:
    """Test GET / redirect endpoint."""

    def test_root_redirects_to_static(self, client):
        """Verify root path redirects to static/index.html."""
        # Arrange: client is ready

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
