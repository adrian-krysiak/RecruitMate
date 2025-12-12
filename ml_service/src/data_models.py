from pydantic import BaseModel, Field
from typing import List
from enum import Enum

from src.config import DEFAULT_ALPHA


class MatchStatus(str, Enum):
    """Defines the quality status of a match based on its score."""
    GOOD = "Good Match ✅"
    MEDIUM = "Medium Match ⚠️"
    WEAK = "Weak Match 🔸"
    NONE = "No Match ❌"


class MatchDetail(BaseModel):
    """Detailed breakdown for a single job requirement."""
    requirement_chunk: str
    best_match_cv_chunk: str
    score: float
    status: MatchStatus


class MatchRequest(BaseModel):
    """Input validation for the matching API endpoint."""
    job_description: str = Field(..., min_length=50,
                                 description="Full text of the job offer.")
    cv_text: str = Field(..., min_length=50,
                         description="Full text of the candidate's CV.")
    alpha: float = Field(DEFAULT_ALPHA, ge=0.0, le=1.0,
                         description="Weight given to the SBERT score "
                         "(1-alpha is for TF-IDF).")


class MatchResponse(BaseModel):
    """Output structure returned by the API."""
    final_score: float
    sbert_score: float
    tfidf_score: float
    common_keywords: List[str]
    details: List[MatchDetail]
