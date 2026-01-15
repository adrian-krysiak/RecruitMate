import logging

from django.conf import settings
from semantic_kernel.functions import kernel_function
from advisor.services.ml_client import MLServiceClient
from advisor.data_models import MatchRequestMLService

logger = logging.getLogger(__name__)


class MlServicePlugin:
    """
    Semantic Kernel Plugin that exposes ML Service to LLM agents.
    
    This allows agents (CV Writer, Career Advisor) to call the ML service
    for match analysis during their reasoning process.
    
    Note: Each call takes ~10 seconds. Agents are prompted to use sparingly.
    """

    def __init__(self):
        self.ml_client = MLServiceClient()
        self.timeout = getattr(settings, 'ML_SERVICE_TIMEOUT', 20.0)

    @kernel_function(
        description=(
            "Analyze CV-job match using the ML service. Returns similarity scores "
            "and keywords (present or missing). EXPENSIVE: takes ~10 seconds. Use sparingly - "
            "only when you need precise match data, not for every iteration."
        ),
        name="GetMatchAnalysis"
    )
    async def analyze_match(
        self,
        job_description: str,
        cv_text: str,
        alpha: float = 0.5,
    ) -> str:
        """
        Call this function when you need semantic similarity scores or
        keywords (present or missing) analysis for a candidate's CV against a job description.
        
        Args:
            job_description: The target job posting text
            cv_text: The candidate's CV/resume text
            alpha: Weight for semantic vs keyword matching (0.5 = balanced)
        
        Returns:
            JSON string with match scores and keyword analysis
        """
        try:
            match_request = MatchRequestMLService(
                job_description=job_description,
                cv_text=cv_text,
                alpha=alpha,
            )

            logger.info("ML Plugin: Calling ML service for match analysis")
            match_response = await self.ml_client.analyze_match(match_request)
            logger.info("ML Plugin: Successfully received ML response")

            return match_response.model_dump_json()

        except TimeoutError:
            logger.warning("ML Plugin: Service timeout")
            return '{"error": "ML service timeout. Try again or proceed without match data."}'
        except Exception as e:
            logger.error(f"ML Plugin error: {e}")
            return '{"error": "Unable to analyze match. Proceed with your best judgment."}'
