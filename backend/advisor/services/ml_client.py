import logging
import json
import hashlib
from django.conf import settings
from django.core.cache import cache
import httpx
from pydantic import ValidationError

from advisor.data_models import MatchRequest, MatchResponse

logger = logging.getLogger(__name__)


class MLServiceClient:
    """Async client for communicating with the FastAPI ML service."""

    def __init__(self):
        self.base_url = settings.ML_SERVICE_URL
        self.timeout = settings.ML_SERVICE_TIMEOUT
        self.cache_ttl = 60 * 60  # Cache TTL in seconds (1 hour)

    def _get_cache_key(self, match_request: MatchRequest) -> str:
        """Generate a secure, unique cache key using MD5 hash."""
        payload_str = json.dumps(match_request.model_dump(), sort_keys=True)
        key_hash = hashlib.md5(payload_str.encode('utf-8')).hexdigest()
        return f"ml_analysis_{key_hash}"

    async def analyze_match(self,
                            match_request: MatchRequest
                            ) -> MatchResponse:
        """
        Analyze CV-job match with Django caching to reduce ML service calls.
        """
        cache_key = self._get_cache_key(match_request)

        # Check cache first
        cached_data = await cache.aget(cache_key)
        if cached_data:
            logger.info(f"Cache HIT for key: {cache_key}")
            return MatchResponse(**cached_data)

        # Cache miss - call ML service
        logger.info(f"Cache MISS for key: {cache_key}")
        endpoint = f"{self.base_url}/match"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Pydantic -> Dict -> JSON
                payload = match_request.model_dump()

                response = await client.post(endpoint, json=payload)
                response.raise_for_status()

                # JSON -> Pydantic
                result = MatchResponse(**response.json())

                # Store in Django cache
                await cache.aset(cache_key, result.model_dump(),
                                 timeout=self.cache_ttl)

                return result

            except httpx.HTTPStatusError as e:
                logger.error(
                    "ML Service error "
                    f"{e.response.status_code}: {e.response.text}")
                raise ValueError(f"ML Service error: {e.response.status_code}")
            except (httpx.RequestError, ValidationError) as e:
                logger.error(f"Connection/Validation error: {e}")
                raise
