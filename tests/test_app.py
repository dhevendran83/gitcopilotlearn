"""
Comprehensive test suite for Mergington High School Activities API
Tests cover all endpoints: GET /activities, POST signup, and DELETE participant
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Outdoor soccer practices and weekend matches",
            "schedule": "Saturdays, 9:00 AM - 11:00 AM",
            "max_participants": 22,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team training and games",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "henry@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stagecraft, and production of school plays",
            "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["oliver@mergington.edu", "grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Prepare for competitive debates and public speaking",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "ethan@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design, build, and program robots for competitions",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 12,
            "participants": ["harper@mergington.edu", "mason@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Should have 9 activities
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activities_contain_required_fields(self, client, reset_activities):
        """Test that activity objects contain required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_participants_list_populated(self, client, reset_activities):
        """Test that participants are included in response"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for activity that doesn't exist"""
        response = client.post(
            "/activities/NonExistentClub/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_already_registered(self, client, reset_activities):
        """Test signup for already registered participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test same student can signup for different activities"""
        # Signup for Chess Club
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=testuser@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Signup for Programming Class
        response2 = client.post(
            "/activities/Programming%20Class/signup?email=testuser@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "testuser@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert "testuser@mergington.edu" in activities_data["Programming Class"]["participants"]
    
    def test_signup_at_capacity(self, client, reset_activities):
        """Test signup when activity is at max capacity"""
        # Get current state
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # Chess Club has max 12 participants, currently has 2
        # Add 10 more to reach capacity
        for i in range(10):
            email = f"student{i}@mergington.edu"
            response = client.post(
                f"/activities/Chess%20Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Try to signup beyond capacity - should still succeed
        # (no capacity check in current implementation)
        response = client.post(
            "/activities/Chess%20Club/signup?email=overcapacity@mergington.edu"
        )
        assert response.status_code == 200


class TestDeleteParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successful removal of participant"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from activity that doesn't exist"""
        response = client.delete(
            "/activities/NonExistentClub/participants?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_participant_not_enrolled(self, client, reset_activities):
        """Test unregister when participant is not enrolled"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=notstudent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]
    
    def test_unregister_all_participants(self, client, reset_activities):
        """Test removing all participants from an activity"""
        # Get initial participants
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"].copy()
        
        # Remove all participants
        for email in participants:
            response = client.delete(
                f"/activities/Chess%20Club/participants?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all removed
        activities_response = client.get("/activities")
        assert len(activities_response.json()["Chess Club"]["participants"]) == 0
    
    def test_unregister_then_re_signup(self, client, reset_activities):
        """Test that a participant can re-signup after being unregistered"""
        email = "testuser@mergington.edu"
        
        # Signup
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=testuser@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            "/activities/Chess%20Club/participants?email=testuser@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Re-signup
        response3 = client.post(
            "/activities/Chess%20Club/signup?email=testuser@mergington.edu"
        )
        assert response3.status_code == 200
        
        # Verify in participants
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root URL redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
