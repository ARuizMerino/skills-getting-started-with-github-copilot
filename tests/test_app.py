import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all():
    # Arrange
    expected_activities = ["Chess Club", "Programming Class"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    for expected in expected_activities:
        assert expected in data


def test_signup_new_participant():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    # Act (verify side effect)
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert email in response.json()[activity]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_participant():
    # Arrange
    activity = "Chess Club"
    email = "daniel@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]

    # Act (verify side effect)
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert email not in response.json()[activity]["participants"]


def test_unregister_nonexistent_participant_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "ghostuser@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_activity_not_found_returns_404():
    # Arrange
    missing_activity = "NoSuchClub"

    # Act
    signup_response = client.post(f"/activities/{missing_activity}/signup?email=test@mergington.edu")
    unregister_response = client.delete(f"/activities/{missing_activity}/unregister?email=test@mergington.edu")

    # Assert
    assert signup_response.status_code == 404
    assert unregister_response.status_code == 404
