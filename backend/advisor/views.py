import logging

from adrf.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pydantic import ValidationError

from .data_models import MatchRequestMLService, MatchRequestBackend
from .services.ml_client import MLServiceClient
from .services.response_curator import curate_response
from .services.llm_agent import AdvisorLLMAgent

logger = logging.getLogger(__name__)

# Singleton agent instance (reuses Kernel across requests)
_advisor_agent: AdvisorLLMAgent | None = None


def get_advisor_agent() -> AdvisorLLMAgent:
    """Get or create the singleton AdvisorLLMAgent instance."""
    global _advisor_agent
    if _advisor_agent is None:
        _advisor_agent = AdvisorLLMAgent()
    return _advisor_agent


class AnalyzeMatchView(APIView):
    """
    Analyze CV-job offer match using external ML service.

    Premium users can get AI-generated insights explaining the match results.
    Free users get raw curated scores only.
    """
    permission_classes = [permissions.AllowAny]

    async def post(self, request):
        try:
            match_req = MatchRequestBackend(**request.data)
        except ValidationError as e:
            return Response(
                {"error": "Validation failed", "details": e.errors()},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = MLServiceClient()
        try:
            match_req_ml = MatchRequestMLService(
                job_description=match_req.job_description,
                cv_text=match_req.cv_text,
                alpha=match_req.alpha,
            )
            result = await service.analyze_match(match_req_ml)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except Exception:
            # Infrastructure errors
            logger.exception("Critical error in AnalyzeMatchView")
            return Response(
                {"error": "Service temporarily unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        user_is_premium = (
            request.user.is_authenticated and request.user.is_premium
        )
        ai_report_text = None

        # Premium users get AI analysis of the results
        if user_is_premium and match_req.ai_deep_analysis:
            try:
                agent = get_advisor_agent()
                ai_report_text = await agent.analyze_match(
                    ml_json_data=result.model_dump_json()
                )
            except Exception as e:
                logger.warning(f"AI analysis failed, returning without: {e}")
                ai_report_text = None

        curated = curate_response(
            raw_data=result,
            is_premium=user_is_premium,
            ai_report_text=ai_report_text
        )

        return Response(curated.model_dump(), status=status.HTTP_200_OK)


class GenerateCvView(APIView):
    """
    Generate an ATS-optimized CV based on job description.

    Uses GPT-4o to rewrite CV sections with relevant keywords.
    """
    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request, *args, **kwargs):
        # Check premium access
        if not request.user.is_premium:
            return Response(
                {"error": "Premium subscription required"},
                status=status.HTTP_403_FORBIDDEN
            )

        job_description = request.data.get("job_description")
        section_data = request.data.get("section_data")

        if not job_description or not section_data:
            return Response(
                {"error": "job_description and section_data are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            agent = get_advisor_agent()
            # TODO: Fetch user_experiences from user profile DB
            result = await agent.write_cv_content(
                section_data=section_data,
                job_description=job_description,
                user_experiences=None,
            )
            return Response({"cv_content": result}, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("CV generation failed")
            return Response(
                {"error": "CV generation service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class AdviceCareerView(APIView):
    """
    Provide personalized career advice and development roadmap.
    Analyzes user's profile, experience gaps, and market trends to suggest
    next steps, skill improvements, and career paths.
    Uses o1 models for deep reasoning about career progression.
    """
    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request, *args, **kwargs):
        # Check premium access
        if not request.user.is_premium:
            return Response(
                {"error": "Premium subscription required"},
                status=status.HTTP_403_FORBIDDEN
            )

        user_profile = request.data.get("user_profile")
        job_description = request.data.get("job_description")

        if not user_profile or not job_description:
            return Response(
                {"error": "user_profile and job_description are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            agent = get_advisor_agent()
            result = await agent.advise_career(
                user_profile=user_profile,
                job_description=job_description,
            )
            return Response({"advice": result}, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("Career advice generation failed")
            return Response(
                {"error": "Career advice service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
