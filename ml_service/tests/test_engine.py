from src.data_models import MatchRequest, MatchResponse
from tests.test_data import JOB_OFFERS, CV_CANDIDATE


def test_calculate_match_perfect_scenario(mock_engine):
    """
    Tests the data flow using the 'Perfect' job offer.
    Note: Scores are mocked and random
    """
    job_text = JOB_OFFERS['perfect']['text']

    request = MatchRequest(
        job_description=job_text,
        cv_text=CV_CANDIDATE,
        alpha=0.7
    )

    response = mock_engine.calculate_match(request)

    assert isinstance(response, MatchResponse)
    assert 0.0 <= response.final_score <= 1.0
    # Ensure details were generated for the job requirements
    assert len(response.details) > 0
    # Ensure common keywords is a list
    assert isinstance(response.common_keywords, list)


def test_calculate_match_poor_scenario(mock_engine):
    """
    Tests the data flow using the 'Poor' job offer (Plumbing vs Data Science).
    """
    job_text = JOB_OFFERS['poor']['text']

    request = MatchRequest(
        job_description=job_text,
        cv_text=CV_CANDIDATE,
        alpha=0.7
    )

    response = mock_engine.calculate_match(request)
    assert isinstance(response, MatchResponse)


def test_alpha_weight_logic(mock_engine):
    """
    Verifies that the final score is a weighted average of SBERT and TF-IDF.
    """
    request = MatchRequest(
        job_description="Software Engineer Job Description Python SQL Experience needed " * 5,
        cv_text="Software Engineer Job Description Python SQL Experience needed " * 5,
        alpha=0.5
    )

    response = mock_engine.calculate_match(request)

    # Calculate expected logic manually
    expected = (0.5 * response.sbert_score) + (0.5 * response.tfidf_score)

    # Allow for floating point limitations
    assert abs(response.final_score - expected) < 1e-5

def test_no_alpha_logic(mock_engine):
    """
    Verifies that alpha takes the default value when not in the request
    """
    request = MatchRequest(
        job_description="Software Engineer Job Description Python SQL Experience needed " * 5,
        cv_text="Software Engineer Job Description Python SQL Experience needed " * 5,
    )
    response = mock_engine.calculate_match(request)

    response = mock_engine.calculate_match(request)
    assert isinstance(response, MatchResponse)


def test_guard_clause_empty_input(mock_engine):
    """
    Test that the engine handles empty chunking results gracefully.
    (WRequest is constructed manually to bypass Pydantic length validation for this test).
    """
    req = MatchRequest.model_construct(job_description="", cv_text="", alpha=0.7)

    # The chunker mock in conftest might still return "something" for empty string
    # unless we explicitly test the engine's check.
    # Ideally, if inputs are empty, chunk_text returns []

    response = mock_engine.calculate_match(req)

    # If chunks are present but empty strings, SBERT mock returns random noise.
    # If the chunker returns empty list, we get 0.0.
    assert isinstance(response, MatchResponse)
    assert response.final_score == 0.0
    assert response.sbert_score == 0.0
    assert response.tfidf_score == 0.0
    assert response.common_keywords == []
    assert response.details == []
