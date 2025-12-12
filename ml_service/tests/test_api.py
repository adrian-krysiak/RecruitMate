from fastapi.testclient import TestClient
from main import app, get_engine
from tests.test_data import JOB_OFFERS, CV_CANDIDATE

client = TestClient(app)


def test_health_check():
    """Check if the health endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_match_endpoint_integration(mock_engine):
    """
    Integration test for the /match endpoint.
    Overrides the dependency to use the mocked engine.
    """
    # Dependency Override: Inject mock_engine instead of loading real models
    app.dependency_overrides[get_engine] = lambda: mock_engine

    payload = {
        "job_description": JOB_OFFERS['medium']['text'],
        "cv_text": CV_CANDIDATE,
        "alpha": 0.8
    }

    response = client.post("/match", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "final_score" in data
    assert "breakdown" not in data  # Pydantic alias check: model uses 'details'
    assert "details" in data
    assert len(data["details"]) > 0

    # Cleanup overrides
    app.dependency_overrides = {}

def test_match_endpoint_no_alpha(mock_engine):
    """
    Integration test for the /match endpoint, but without alpha in the payload
    """
    app.dependency_overrides[get_engine] = lambda: mock_engine

    payload = {
        "job_description": JOB_OFFERS['poor']['text'],
        "cv_text": CV_CANDIDATE,
    }
    response = client.post("/match", json=payload)
    assert response.status_code == 200


def test_match_endpoint_validation_error():
    """Test that short inputs are rejected by Pydantic."""
    payload = {
        "job_description": "Too short",
        "cv_text": "Also too short",
        "alpha": 1.5  # Invalid alpha (> 1.0)
    }

    response = client.post("/match", json=payload)
    assert response.status_code == 422  # Unprocessable Entity
