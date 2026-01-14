import random

from advisor.data_models import (
    MatchResponse,
    CuratedMatchResponse,
    CuratedMatchDetail,
    MatchStatus
)

LIMITS = {
    "FREE": {
        "KEYWORDS": 5,
        "TOP_MATCHES": 3,
        "UNADDRESSED": 3,
        "SHOW_SCORES": False
    },
    "PREMIUM": {
        "KEYWORDS": 50,
        "TOP_MATCHES": 10,
        "UNADDRESSED": 5,
        "SHOW_SCORES": True
    }
}


def get_status_from_score(score: float) -> MatchStatus:
    if score >= 0.65:
        return MatchStatus.GOOD
    elif score >= 0.45:
        return MatchStatus.MEDIUM
    else:
        return MatchStatus.WEAK


def curate_response(
                    raw_data: MatchResponse,
                    is_premium: bool, ai_report_text: str | None = None
                    ) -> CuratedMatchResponse:
    """Transforms raw ML data into a curated response based on user tier."""

    plan = LIMITS["PREMIUM"] if is_premium else LIMITS["FREE"]

    # Top matches with valid score threshold
    sorted_details = raw_data.details.copy()
    valid_matches = [d for d in sorted_details if d.score >= 0.45]

    curated_top_matches = []
    for item in valid_matches[:plan["TOP_MATCHES"]]:
        curated_top_matches.append(CuratedMatchDetail(
            status=get_status_from_score(item.score),
            job_requirement=item.job_requirement,
            cv_match=item.best_cv_match,
            cv_section=item.cv_section,
            score_percentage=(int(item.score * 100)
                              if plan["SHOW_SCORES"] else None)
        ))

    # Weak matches that weren't addressed
    weak_matches = [d for d in raw_data.details
                    if d.score < 0.45 and d.score >= 0.3]
    weak_matches.sort(key=lambda x: x.score)

    unaddressed_list = [
        item.job_requirement for item in weak_matches[:plan["UNADDRESSED"]]
    ]

    # Missing keywords with tier-based limit
    all_missing = raw_data.missing_keywords
    # Add randomness to avoid same keywords every time
    random.shuffle(all_missing)
    display_missing = all_missing[:plan["KEYWORDS"]]
    hidden_count = max(0, len(all_missing) - plan["KEYWORDS"])

    # Overall score visible only for premium users
    display_overall_score = int(
        raw_data.final_score * 100) if plan["SHOW_SCORES"] else None

    return CuratedMatchResponse(
        overall_status=get_status_from_score(raw_data.final_score),
        overall_score=display_overall_score,
        semantic_status=get_status_from_score(raw_data.semantic_score),
        keywords_status=get_status_from_score(raw_data.keyword_score),
        action_verbs_status=get_status_from_score(raw_data.action_verb_score),
        top_matches=curated_top_matches,
        missing_keywords=display_missing,
        unaddressed_requirements=unaddressed_list,
        hidden_keywords_count=hidden_count,
        ai_report=ai_report_text
    )
