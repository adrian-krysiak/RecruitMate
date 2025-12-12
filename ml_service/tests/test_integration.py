import pytest

from src.matching_engine import HybridMatchEngine
from src.data_models import MatchRequest, MatchResponse
from tests.test_data import JOB_OFFERS, CV_CANDIDATE


# --- FIXTURES ---

@pytest.fixture(scope="module")
def real_engine():
    """
    Initializes the REAL HybridMatchEngine.
    This will load SBERT and spaCy models into memory (takes time).
    Scope='module' ensures it runs only once per test file.
    """
    print("\n⏳ Loading REAL models for integration testing... (this may take a while)")
    engine = HybridMatchEngine()
    print("✅ Models loaded.")
    return engine


# --- TESTS ---

@pytest.mark.slow
def test_full_pipeline_sanity_check(real_engine):
    """
    Goal 1: Ensure the application works as a whole and returns a valid structure.
    """
    request = MatchRequest(
        job_description=JOB_OFFERS['perfect']['text'],
        cv_text=CV_CANDIDATE,
        alpha=0.7
    )

    result = real_engine.calculate_match(request)

    assert isinstance(result, MatchResponse)
    assert 0.0 <= result.final_score <= 1.0
    # Common keywords should definitely exist for the perfect match
    assert len(result.common_keywords) > 0
    assert len(result.details) > 0


@pytest.mark.slow
def test_ranking_logic_correctness(real_engine):
    """
    Goal 2 (Validation): Verify that 'Perfect' match scores higher than 'Medium',
    and 'Medium' scores higher than 'Poor'. This proves the AI logic works.
    """
    # 1. Calculate Perfect Match
    req_perfect = MatchRequest(
        job_description=JOB_OFFERS['perfect']['text'],
        cv_text=CV_CANDIDATE,
        alpha=0.7
    )
    score_perfect = real_engine.calculate_match(req_perfect).final_score

    # 2. Calculate Medium Match
    req_medium = MatchRequest(
        job_description=JOB_OFFERS['medium']['text'],
        cv_text=CV_CANDIDATE,
        alpha=0.7
    )
    score_medium = real_engine.calculate_match(req_medium).final_score

    # 3. Calculate Poor Match
    req_poor = MatchRequest(
        job_description=JOB_OFFERS['poor']['text'],
        cv_text=CV_CANDIDATE,
        alpha=0.7
    )
    score_poor = real_engine.calculate_match(req_poor).final_score

    print(f"\n📊 SCORES -> Perfect: {score_perfect}, Medium: {score_medium}, Poor: {score_poor}")

    # Assert logic
    assert score_perfect > score_medium, "Perfect match should score higher than Medium"
    assert score_medium > score_poor, "Medium match should score higher than Poor"


@pytest.mark.slow
def test_parameter_impact_alpha(real_engine):
    """
    Goal 2 (Tuning): Verify that changing parameters (alpha) actually changes the result.
    We use the 'Medium' offer where keywords (TF-IDF) might differ from semantics (SBERT).
    """
    job_text = JOB_OFFERS['medium']['text']

    # Run with Alpha 1.0 (100% SBERT / Semantics)
    res_semantic = real_engine.calculate_match(MatchRequest(
        job_description=job_text, cv_text=CV_CANDIDATE, alpha=1.0
    ))

    # Run with Alpha 0.0 (100% TF-IDF / Keywords)
    res_keyword = real_engine.calculate_match(MatchRequest(
        job_description=job_text, cv_text=CV_CANDIDATE, alpha=0.0
    ))

    print(f"\n🎛️ ALPHA IMPACT -> Alpha 1.0: {res_semantic.final_score}, Alpha 0.0: {res_keyword.final_score}")

    # The scores should be different (unless by huge coincidence the models agree perfectly)
    assert res_semantic.final_score != res_keyword.final_score

    # For this specific data, expect semantics to find some connection
    # even if keywords are missing, or vice versa.
    assert res_semantic.sbert_score > 0
    assert res_keyword.tfidf_score > 0
