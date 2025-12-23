from typing import List, Annotated, Optional, Dict

from pydantic import BaseModel, Field
# from enum import Enum

from src.config import DEFAULT_ALPHA


# Should be handel by frontend or backend
# class MatchStatus(str, Enum):
#     """Defines the quality status of a match based on its score."""
#     GOOD = "Good Match ✅"
#     MEDIUM = "Medium Match ⚠️"
#     WEAK = "Weak Match 🔸"
#     NONE = "No Match ❌"


class MatchDetail(BaseModel):
    """
    Detailed scoring for a specific sentence/chunk comparison.
    Used to generate the "Best matches" and "Worst matches" report.
    """
    job_requirement: str        # Sentence/chunk from the job posting
    best_cv_match: str          # Best matching sentence from the CV
    # CV section where the match originates (e.g., experience, projects)
    cv_section: str
    # Similarity score (accounting for section weight)
    score: float
    # Raw semantic score without weight, for debugging purposes
    raw_semantic_score: Optional[float] = None


class MatchRequest(BaseModel):
    """Input validation for the matching engine."""
    job_description: Annotated[str, Field(..., min_length=50,
                                          description="Full text of the job offer.")]
    cv_text: Annotated[str, Field(..., min_length=50,
                                  description="Full text of the candidate's CV.")]
    alpha: Annotated[float, Field(DEFAULT_ALPHA, ge=0.0, le=1.0,
                                  description="Weight for Semantic Score (0.0-1.0).")]


class MatchResponse(BaseModel):
    """Output structure returned by the engine."""

    # 1. Main Scores
    final_score: Annotated[float, Field(..., ge=0.0, le=1.0,
                                        description="Aggregated final match score.")]
    
    semantic_score: Annotated[float, Field(...,
                                           description="Weighted semantic similarity score.")]
    
    keyword_score: Annotated[float, Field(...,
                                          description="Score based on NER gap analysis.")]
    
    action_verb_score: Annotated[float, Field(...,
                                              description="Bonus score for active voice usage.")]

    # 2. Keyword Analysis (Gap Analysis)
    common_keywords: Annotated[List[str], Field(...,
                                                description="Keywords found in BOTH Job and CV.")]
    
    missing_keywords: Annotated[List[str], Field(...,
                                                 description="Keywords found in Job but MISSING in CV.")]

    # 3. Section Breakdown
    # e.g., {'experience': 0.85, 'skills': 0.90, 'education': 0.50}
    section_scores: Annotated[Dict[str, float], Field(...,
                                                      description="Average semantic match per CV section.")]

    # 4. Granular Details
    # List of all processed chunks with their individual matches
    details: Annotated[List[MatchDetail], Field(...,
                                                description="Detailed scoring for each sentence/chunk comparison.")]
