"""
FastAPI endpoint tests using AAA (Arrange-Act-Assert) pattern.
"""
import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        assert "Chess Club" in data
        assert "Programming Class" in data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_valid_student_succeeds(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert email in data["message"]
    
    def test_signup_to_nonexistent_activity_fails(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Activity not found"
    
    def test_signup_filters_by_max_participants(self, client):
        # Arrange
        activity_name = "Tennis Club"  # max_participants: 10, currently has 2
        # Add 8 more students to reach capacity
        for i in range(8):
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
        
        # Act - Try to signup when activity is full
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overfull@mergington.edu"}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert data["detail"] == "Activity is full"


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_existing_participant_succeeds(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in data["message"]
        assert email in data["message"]
    
    def test_unregister_nonexistent_participant_fails(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Participant not found"
    
    def test_unregister_from_nonexistent_activity_fails(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Activity not found"


class TestRootEndpoint:
    """Tests for GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_redirect = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert expected_redirect in response.headers["location"]
