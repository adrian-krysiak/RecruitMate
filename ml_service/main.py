import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Depends

from src.orchestrator import HybridMatchEngine
from src.data_models import MatchRequest, MatchResponse


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Handles startup (loading models) and shutdown (clean up)"""
    ml_models['engine'] = HybridMatchEngine()

    global executor
    workers = max(os.cpu_count() - 1, 1)
    executor = ThreadPoolExecutor(max_workers=workers)

    yield
    ml_models.clear()
    if executor:
        executor.shutdown(wait=True)

# --- DEPENDENCY INJECTION ---
def get_engine():
    """Helper for FastAPI to inject the loaded engine."""
    if "engine" not in ml_models:
        raise HTTPException(status_code=503, detail="AI Engine is not ready.")
    return ml_models["engine"]


executor: Optional[ThreadPoolExecutor] = None
ml_models: Dict[str, HybridMatchEngine] = {}
app = FastAPI(title="RecruitMate ML Service",
              lifespan=lifespan)


# --- ENDPOINTS ---

@app.post("/match", response_model=MatchResponse)
async def match_cv_to_offer(
    request: MatchRequest,
    engine: HybridMatchEngine = Depends(get_engine)
):
    """
    Compares a job offer against a CV using the hybrid (SBERT + TF-IDF) engine.
    The 'alpha' parameter controls the weight given to the semantic score.
    """
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            executor,
            engine.calculate_match,
            request
        )
        return result
    except Exception as e:
        # Log error in production environment
        raise HTTPException(status_code=500, detail=f"Internal processing error: {str(e)}")

@app.get("/health")
async def health_check():
    """Basic health check to ensure the service is running and models are loaded."""
    return {"status": "ok", "models_loaded": "engine" in ml_models}
