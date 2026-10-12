import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Mondays",
            "max_participants": 12,
            "participants": ["student@example.com"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Tuesdays",
            "max_participants": 10,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == ["student@example.com"]
    assert response.json()["Art Club"]["participants"] == []


def test_signup_adds_student_to_activity(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new-student@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new-student@example.com for Chess Club"
    }
    assert "new-student@example.com" in client.get("/activities").json()["Chess Club"]["participants"]


def test_duplicate_signup_is_rejected(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_unknown_activity_is_rejected(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new-student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
