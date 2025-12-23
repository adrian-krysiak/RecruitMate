import os
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.orchestrator import HybridMatchEngine
from src.data_models import MatchRequest, MatchResponse
from tests.test_data import JOB_OFFERS, CV_CANDIDATE
from main import app, get_engine


MAX_WORKERS = max(os.cpu_count() - 1, 1)
TEXT_MULTIPLIER = 4
TEST_URL = "http://test"

# --- FIXTURES ---


@pytest.fixture(scope="module")
def real_engine():
    """
    Initializes the REAL HybridMatchEngine.
    This will load SBERT and spaCy models into memory.
    """
    print("\n⏳ Loading REAL models for integration testing...")
    engine = HybridMatchEngine()
    print("✅ Models loaded.")
    return engine


@pytest_asyncio.fixture(scope="function")
async def async_client(real_engine):
    """
    Creates async client HTTP running the real app.
    """
    app.dependency_overrides[get_engine] = lambda: real_engine
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url=TEST_URL) as client:
        yield client
    app.dependency_overrides = {}


# --- TESTS ---

@pytest.mark.slow
def test_full_pipeline_sanity_check(real_engine):
    """
    Ensure the application works as a whole and returns a valid structure.
    """
    request = MatchRequest(
        job_description=JOB_OFFERS['perfect']['text'],
        cv_text=CV_CANDIDATE,
        alpha=0.7
    )

    result = real_engine.calculate_match(request)

    assert isinstance(result, MatchResponse)
    assert 0.0 <= result.final_score <= 1.0

    # Check new fields present in MatchResponse
    assert result.semantic_score >= 0.0
    assert result.keyword_score >= 0.0

    assert len(result.common_keywords) > 0
    assert len(result.details) > 0


@pytest.mark.slow
def test_ranking_logic_correctness(real_engine):
    """
    Verify that 'Perfect' match scores higher than 'Medium',
    and 'Medium' scores higher than 'Poor'.
    """
    # 1. Calculate Perfect Match
    req_perfect = MatchRequest(
        job_description=JOB_OFFERS['perfect']['text'],
        cv_text=CV_CANDIDATE
    )
    score_perfect = real_engine.calculate_match(req_perfect).final_score

    # 2. Calculate Medium Match
    req_medium = MatchRequest(
        job_description=JOB_OFFERS['medium']['text'],
        cv_text=CV_CANDIDATE
    )
    score_medium = real_engine.calculate_match(req_medium).final_score

    # 3. Calculate Poor Match
    req_poor = MatchRequest(
        job_description=JOB_OFFERS['poor']['text'],
        cv_text=CV_CANDIDATE
    )
    score_poor = real_engine.calculate_match(req_poor).final_score

    print(
        f"\n📊 SCORES -> Perfect: {score_perfect}, Medium: {score_medium}, Poor: {score_poor}")

    assert score_perfect > score_medium, "Perfect match should score higher than Medium"
    assert score_medium > score_poor, "Medium match should score higher than Poor"


@pytest.mark.slow
def test_parameter_impact_alpha(real_engine):
    """
    Verify that changing parameters (alpha) actually changes the result.
    """
    job_text = JOB_OFFERS['medium']['text']

    # Run with Alpha 1.0 (100% Semantic)
    res_semantic = real_engine.calculate_match(MatchRequest(
        job_description=job_text, cv_text=CV_CANDIDATE, alpha=1.0
    ))

    # Run with Alpha 0.0 (100% Keywords)
    res_keyword = real_engine.calculate_match(MatchRequest(
        job_description=job_text, cv_text=CV_CANDIDATE, alpha=0.0
    ))

    print(
        f"\n🎛️ ALPHA IMPACT -> Alpha 1.0 (Sem): {res_semantic.final_score}, Alpha 0.0 (Key): {res_keyword.final_score}")

    assert res_semantic.final_score != res_keyword.final_score

    assert res_semantic.semantic_score > 0
    assert res_keyword.keyword_score >= 0


@pytest.mark.slow
def test_engine_thread_safety(real_engine):
    """
    Verifies that the engine is thread-safe.
    """
    # 1. Setup payload
    payload = MatchRequest(
        job_description=JOB_OFFERS['perfect']['text'],
        cv_text=CV_CANDIDATE
    )
    n_threads = 4

    # 2. Run concurrently
    results = []
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = [executor.submit(
            real_engine.calculate_match, payload) for _ in range(n_threads)]
        results = [f.result() for f in as_completed(futures)]

    # 3. Assert consistency
    reference_score = results[0].final_score
    for res in results:
        assert res.final_score == reference_score, "Race condition detected! Results vary between threads."


@pytest.mark.slow
def test_engine_task_parallelism_performance(real_engine):
    """
    Verifies that the engine releases the GIL and scales on multiple cores.
    """
    # 1. Setup HEAVY payload
    payload = MatchRequest(
        job_description=JOB_OFFERS['perfect']['text'] * TEXT_MULTIPLIER,
        cv_text=CV_CANDIDATE * TEXT_MULTIPLIER,
        alpha=0.5
    )
    n_tasks = 4

    # 2. Measure Sequential Execution
    start_seq = time.time()
    for _ in range(n_tasks):
        real_engine.calculate_match(payload)
    duration_seq = time.time() - start_seq

    # 3. Measure Parallel Execution
    start_par = time.time()
    with ThreadPoolExecutor(max_workers=n_tasks) as executor:
        list(executor.map(real_engine.calculate_match, [payload] * n_tasks))
    duration_par = time.time() - start_par

    # 4. Assert Speedup
    print(f"\nSequential: {duration_seq:.4f}s | Parallel: {duration_par:.4f}s")
    assert duration_par < duration_seq * \
        1.1, "Parallelism check failed or overhead too high."


@pytest.mark.asyncio
@pytest.mark.slow
async def test_api_concurrency_benchmark(async_client):
    """Verify API concurrency: ensure non-blocking handling of requests."""
    payload = {
        "job_description": JOB_OFFERS['perfect']['text'] * TEXT_MULTIPLIER,
        "cv_text": CV_CANDIDATE * TEXT_MULTIPLIER,
    }
    n_req = 4

    # Sequential API calls
    start_seq = time.time()
    for _ in range(n_req):
        resp = await async_client.post(f"{TEST_URL}/match", json=payload)
        assert resp.status_code == 200
    dur_seq = time.time() - start_seq

    # Concurrent API calls
    start_conc = time.time()
    tasks = [async_client.post("/match", json=payload) for _ in range(n_req)]
    responses = await asyncio.gather(*tasks)
    dur_conc = time.time() - start_conc

    for r in responses:
        assert r.status_code == 200

    print(f"\nAPI Seq: {dur_seq:.4f}s | API Conc: {dur_conc:.4f}s")
    assert dur_conc < dur_seq, "API is blocking concurrent requests."
