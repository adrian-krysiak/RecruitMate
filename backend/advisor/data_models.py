from typing import List, Annotated, Optional, Dict

from pydantic import BaseModel, Field
from enum import Enum

from django.conf import settings


class MatchStatus(str, Enum):
    """Defines the quality status of a match based on its score."""

    GOOD = "Good"  # > 65%
    MEDIUM = "Medium"  # 45%-65%
    WEAK = "Weak"  # < 45%
    NONE = "None"


class MatchDetail(BaseModel):
    """
    Detailed scoring for a specific sentence/chunk comparison.
    Used to generate the "Best matches" and "Worst matches" report.
    """

    job_requirement: str  # Sentence/chunk from the job posting
    best_cv_match: str  # Best matching sentence from the CV
    # CV section where the match originates (e.g., experience, projects)
    cv_section: str
    # Similarity score (accounting for section weight)
    score: float
    # Raw semantic score without weight, for debugging purposes
    raw_semantic_score: Optional[float] = None


class CuratedMatchDetail(BaseModel):
    """
    Curated match detail for user-friendly reporting.
    Represents a specific pair of Job Requirement vs CV Snippet.
    """
    status: Annotated[
        MatchStatus,
        Field(..., description="Qualitative status of the match.")
    ]

    job_requirement: Annotated[
        str,
        Field(..., description="The specific requirement from the job posting.")
    ]

    cv_match: Annotated[
        str,
        Field(..., description="The most relevant snippet found in the CV.")
    ]

    cv_section: Annotated[
        str,
        Field(...,
              description="The section of the CV where the match was found.")
    ]

    score_percentage: Annotated[
        float | None,
        Field(
            default=None,
            ge=0.0,
            le=100.0,
            description="Exact match percentage (0-100). "
            "Visible only for Premium users."
        )
    ]


class MatchRequest(BaseModel):
    """Input validation for the matching engine."""
    job_description: Annotated[
        str, Field(..., min_length=50,
                   description="Full text of the job offer.")
    ]
    cv_text: Annotated[
        str, Field(..., min_length=50,
                   description="Full text of the candidate's CV.")
    ]
    alpha: Annotated[
        float,
        Field(
            settings.ML_DEFAULT_ALPHA,
            ge=0.0,
            le=1.0,
            description="Weight for Semantic Score (0.0-1.0).",
        ),
    ]
    ai_deep_analysis: Annotated[
        bool | None,
        Field(
            False,
            description="Whether to perform deep analysis using AI models. "
            "Only available for premium users.",
        ),
    ]


class MatchResponse(BaseModel):
    """
    Raw output structure returned by the ML engine (FastAPI).
    Internal use only - logic layer transforms this into CuratedMatchResponse.
    """

    # 1. Main Scores
    final_score: Annotated[
        float, Field(..., ge=0.0, le=1.0,
                     description="Aggregated final match score.")
    ]

    semantic_score: Annotated[
        float, Field(..., description="Weighted semantic similarity score.")
    ]

    keyword_score: Annotated[
        float, Field(..., description="Score based on NER gap analysis.")
    ]

    action_verb_score: Annotated[
        float, Field(..., description="Bonus score for active voice usage.")
    ]

    # 2. Keyword Analysis (Gap Analysis)
    common_keywords: Annotated[
        List[str], Field(..., description="Keywords found in BOTH Job and CV.")
    ]

    missing_keywords: Annotated[
        List[str], Field(...,
                         description="Keywords found in Job but"
                         " MISSING in CV.")
    ]

    # 3. Section Breakdown
    # e.g., {'experience': 0.85, 'skills': 0.90, 'education': 0.50}
    section_scores: Annotated[
        Dict[str, float],
        Field(..., description="Average semantic match per CV section."),
    ]

    # 4. Granular Details
    # List of all processed chunks with their individual matches
    details: Annotated[
        List[MatchDetail],
        Field(..., description="Detailed scoring for each sentence/chunk "
              "comparison."),
    ]


class CuratedMatchResponse(BaseModel):
    """
    Final, user-friendly output structure sent to the Frontend.
    """

    # 1. Overall Score - only place with a number for Premium users
    overall_score: Annotated[
        int | None,
        Field(
            None,
            description="Final score percentage (0-100). Null for free users."
        )
    ]

    overall_status: Annotated[
        MatchStatus,
        Field(..., description="General quality of the application.")
    ]

    # 2. Detailed Metrics - ONLY STATUS
    semantic_status: Annotated[
        MatchStatus, Field(..., description="Status of semantic relevance.")
    ]

    keywords_status: Annotated[
        MatchStatus, Field(..., description="Status of ATS keyword coverage.")
    ]

    action_verbs_status: Annotated[
        MatchStatus, Field(...,
                           description="Status of dynamic language usage.")
    ]

    # 3. Curated Lists
    top_matches: Annotated[
        List[CuratedMatchDetail],
        Field(..., description="Best matching sections (Top N).")
    ]

    missing_keywords: Annotated[
        List[str],
        Field(..., description="Keywords to add. Limited for free users.")
    ]

    unaddressed_requirements: Annotated[
        List[str],
        Field(..., description="Job requirements not found in CV.")
    ]

    # 4. Metadata / Upsell info
    hidden_keywords_count: Annotated[
        int,
        Field(0,
              description="Number of missing keywords hidden from the user.")
    ]

    # 5. AI Report (The Premium Value)
    ai_report: Annotated[
        str | None,
        Field(
            None,
            description="Deep analysis generated by LLM. "
            "Null if user is Free or didn't request analysis."
        )
    ]
