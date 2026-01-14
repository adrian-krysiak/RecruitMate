import logging

from adrf.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from pydantic import ValidationError

from .data_models import MatchRequest
from .services.ml_client import MLServiceClient
from .services.response_curator import curate_response

logger = logging.getLogger(__name__)


class AnalyzeMatchView(APIView):
    """
    View to analyze CV-job offer match using external ML service.
    """
    permission_classes = [permissions.AllowAny]

    async def post(self, request):
        # Pydantic + Async I/O + DRF = ADRF
        try:
            match_req = MatchRequest(**request.data)
        except ValidationError as e:
            return Response(
                {"error": "Validation failed", "details": e.errors()},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Call the ML service (Non-blocking I/O)
        service = MLServiceClient()
        try:
            # Thread is released for other users
            result = await service.analyze_match(match_req)
        except ValueError as e:
            # Business/logical errors from the service
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

        # AI Report logic
        user_is_premium = (request.user.is_authenticated
                           and request.user.is_premium)
        ai_report_text = None

        if user_is_premium and match_req.ai_deep_analysis:
            # TODO: Integrate with AI service for detailed report
            # ai_report_text = await llm_agent.generate_feedback(raw_result,
            #                                                    match_req)
            ai_report_text = "Detailed AI analysis report placeholder."

        # Curate the response
        result = curate_response(
            raw_data=result,
            is_premium=user_is_premium,
            ai_report_text=ai_report_text
        )

        return Response(result.model_dump(), status=status.HTTP_200_OK)


class GenerateCvView(APIView):
    """
    Generate an optimized CV based on job description and current CV.
    Leverages AI to rewrite CV sections with relevant keywords and
    action verbs. Premium feature - coming soon.
    """
    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request, *args, **kwargs):
        return Response({"status": "Coming soon"}, status=200)


class AdviceCareerView(APIView):
    """
    Provide personalized career advice and development roadmap.
    Analyzes user's profile, experience gaps, and market trends to suggest
    next steps, skill improvements, and career paths.
    Premium feature - coming soon.
    """
    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request, *args, **kwargs):
        return Response({"status": "Coming soon"}, status=200)
