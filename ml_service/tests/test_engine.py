from src.data_models import MatchRequest, MatchResponse
from tests.test_data import JOB_OFFERS, CV_CANDIDATE


def test_calculate_match_perfect_scenario(mock_engine):
    """Tests data flow with valid inputs."""
    request = MatchRequest(
        job_description=JOB_OFFERS['perfect']['text'],
        cv_text=CV_CANDIDATE,
        alpha=0.7
    )

    response = mock_engine.calculate_match(request)

    assert isinstance(response, MatchResponse)
    assert 0.0 <= response.final_score <= 1.0
    assert 0.0 <= response.semantic_score <= 1.0
    assert 0.0 <= response.keyword_score <= 1.0
    assert isinstance(response.details, list)
    assert isinstance(response.common_keywords, list)


def test_scoring_logic_aggregation(mock_engine):
    """Verifies the final score formula: Base * 0.95 + Bonus."""
    alpha = 0.6
    long_job = "Python SQL Developer requirement needed for this position. " * 3
    long_cv = "Python SQL Developer with management skills and experience. " * 3

    request = MatchRequest(
        job_description=long_job,
        cv_text=long_cv,
        alpha=alpha
    )

    response = mock_engine.calculate_match(request)

    # Reconstruct score from parts
    base_score = (alpha * response.semantic_score) + \
        ((1.0 - alpha) * response.keyword_score)
    style_bonus = response.action_verb_score * 0.05

    expected_final = (base_score * 0.95) + style_bonus
    expected_final = max(0.0, min(expected_final, 1.0))

    assert abs(response.final_score - expected_final) < 1e-4


def test_guard_clause_empty_input(mock_engine):
    """Ensures empty inputs return zeroed response."""
    req = MatchRequest.model_construct(
        job_description="", cv_text="", alpha=0.7)
    response = mock_engine.calculate_match(req)

    assert response.final_score == 0.0
    assert response.semantic_score == 0.0
    assert response.details == []
    assert response.common_keywords == []
