from fastapi.testclient import TestClient
from main import app, get_engine
from tests.test_data import JOB_OFFERS, CV_CANDIDATE

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_match_endpoint_integration(mock_engine):
    """Integration test for /match using mocked engine."""
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
    assert "semantic_score" in data
    assert "keyword_score" in data
    assert "section_scores" in data
    assert "common_keywords" in data
    assert "details" in data
    assert isinstance(data["details"], list)

    app.dependency_overrides = {}


def test_match_endpoint_validation_error(mock_engine):
    """Test rejection of invalid inputs."""
    app.dependency_overrides[get_engine] = lambda: mock_engine
    payload = {
        "job_description": "Short",
        "cv_text": "Short",
        "alpha": 1.5
    }
    response = client.post("/match", json=payload)
    app.dependency_overrides = {}
    assert response.status_code == 422
