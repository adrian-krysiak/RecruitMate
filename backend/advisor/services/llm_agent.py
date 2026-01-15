import os
import logging
from typing import List, Optional

import openai
from django.conf import settings

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.connectors.ai.google import GoogleAIChatCompletion

from .plugins.ml_plugin import MlServicePlugin
from .prompts import (
    CV_WRITER_SYSTEM,
    CV_WRITER_USER_TEMPLATE,
    ANALYST_SYSTEM,
    ANALYST_USER_TEMPLATE,
    CAREER_ADVISOR_SYSTEM,
    CAREER_ADVISOR_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class AdvisorLLMAgent:
    """
    Orchestrates 3 AI advisors using Semantic Kernel:
    - Analyst (Gemini): Explains ML match results
    - CV Writer (GPT-4o): Generates ATS-optimized CVs
    - Career Advisor (o1): Provides strategic career guidance

    Uses tiered fallback chains to handle rate limits:
    o1 -> o1-mini -> gpt-4o -> gpt-4o-mini (backup)
    """

    def __init__(self):
        self.kernel = Kernel()
        self._setup_services()
        self._register_plugins()

    def _setup_services(self):
        """
        Registers AI Services with tiered fallback hierarchy.

        Rate Limits (GitHub Models - Jan 2026):
        - o1: ~8/day (Tier 1 Strategist)
        - o1-mini: ~12/day (Tier 2 Strategist)
        - gpt-4o: ~50/day (Writer + Tier 3 fallback)
        - gpt-4o-mini: ~150/day (Backup for all)
        - gemini-3-flash: ~20/day (Analyst)
        """
        github_token = (
            getattr(settings, 'GITHUB_TOKEN', None)
            or os.getenv("GITHUB_TOKEN")
        )
        google_key = (
            getattr(settings, 'GOOGLE_API_KEY', None)
            or os.getenv("GOOGLE_API_KEY")
        )
        github_endpoint = getattr(
            settings,
            'GITHUB_MODELS_ENDPOINT',
            "https://models.inference.ai.azure.com"
        )

        if not github_token:
            logger.critical("GITHUB_TOKEN missing! AI advisors will fail.")
        else:
            # Create async client with GitHub Models endpoint
            github_client = openai.AsyncOpenAI(
                api_key=github_token,
                base_url=github_endpoint,
            )

            # 1. STRATEGIST TIER (Reasoning - for Career Advisor)
            self.kernel.add_service(
                OpenAIChatCompletion(
                    service_id="strategist-pro",
                    ai_model_id="o1",
                    async_client=github_client,
                )
            )
            self.kernel.add_service(
                OpenAIChatCompletion(
                    service_id="strategist-lite",
                    ai_model_id="o1-mini",
                    async_client=github_client,
                )
            )

            # 2. WRITER TIER (Creative - for CV Writer)
            self.kernel.add_service(
                OpenAIChatCompletion(
                    service_id="writer",
                    ai_model_id="gpt-4o",
                    async_client=github_client,
                )
            )

            # 3. BACKUP TIER (High Volume - fallback for all)
            self.kernel.add_service(
                OpenAIChatCompletion(
                    service_id="backup",
                    ai_model_id="gpt-4o-mini",
                    async_client=github_client,
                )
            )

        if not google_key:
            logger.warning("GOOGLE_API_KEY missing. Analyst uses backup.")
        else:
            # 4. ANALYST TIER (Context Processing - for Match Analysis)
            try:
                self.kernel.add_service(
                    GoogleAIChatCompletion(
                        service_id="analyst",
                        gemini_model_id="gemini-3-flash",
                        api_key=google_key,
                    )
                )
            except Exception as e:
                logger.error(f"Google AI Init Error: {e}")

    def _register_plugins(self):
        """Registers Semantic Kernel plugins (tools) for LLM agents."""
        self.kernel.add_plugin(
            plugin=MlServicePlugin(),
            plugin_name="MLService"
        )

    async def _try_service_chain(
        self,
        prompt: str,
        service_ids: List[str],
        system_prompt: Optional[str] = None,
        allow_tools: bool = False,
    ) -> str:
        """
        Attempts to invoke prompt across a chain of services with fallback.

        Args:
            prompt: The user prompt to send
            service_ids: Ordered list of service IDs to try (first = preferred)
            system_prompt: Optional system message to prepend
            allow_tools: Whether to enable function calling (tool use)

        Returns:
            Generated response string or error message
        """
        execution_settings = None
        if allow_tools:
            execution_settings = OpenAIChatPromptExecutionSettings(
                function_choice_behavior=FunctionChoiceBehavior.Auto()
            )

        for service_id in service_ids:
            try:
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"

                result = await self.kernel.invoke_prompt(
                    prompt=full_prompt,
                    service_id=service_id,
                    settings=execution_settings,
                )

                if result:
                    logger.info(f"Successfully used service: {service_id}")
                    return str(result)

            except Exception as e:
                logger.warning(
                    f"Service '{service_id}' failed: {e}. Trying next..."
                )
                continue

        logger.error("All services in chain failed.")
        return "AI Service Unavailable. Please try again later."

    # ========== PUBLIC ADVISOR METHODS ==========

    async def analyze_match(self, ml_json_data: str) -> str:
        """
        ANALYST: Explains ML match results in human-readable format.

        Uses: Gemini (fast context processing) -> GPT-4o-mini backup
        Tools: None (data already provided)
        """
        prompt = ANALYST_USER_TEMPLATE.format(ml_json=ml_json_data)
        chain = ["analyst", "backup"]
        return await self._try_service_chain(
            prompt,
            chain,
            system_prompt=ANALYST_SYSTEM,
            allow_tools=False,
        )

    async def write_cv_content(
        self,
        section_data: str,
        job_description: str,
        user_experiences: Optional[str] = None,
    ) -> str:
        """
        CV WRITER: Generates ATS-optimized CV content.

        Uses: GPT-4o (creative writing) -> GPT-4o-mini backup
        Tools: MLService (optional, for score verification)

        Note: ML tool calls are expensive (~10s). Prompt guides model to
        minimize usage and only verify final output if uncertain.
        """
        prompt = CV_WRITER_USER_TEMPLATE.format(
            job_description=job_description,
            section_data=section_data,
            user_experiences=user_experiences or "Not provided",
        )
        chain = ["writer", "backup"]
        return await self._try_service_chain(
            prompt,
            chain,
            system_prompt=CV_WRITER_SYSTEM,
            allow_tools=True,
        )

    async def advise_career(
        self,
        user_profile: str,
        job_description: str,
    ) -> str:
        """
        CAREER ADVISOR: Provides strategic career guidance.

        Uses: o1 (deep reasoning) -> o1-mini -> GPT-4o -> GPT-4o-mini backup
        Tools: MLService (optional, for skill gap analysis)

        Analyzes fit for target role, identifies gaps, suggests path.
        """
        prompt = CAREER_ADVISOR_USER_TEMPLATE.format(
            user_profile=user_profile,
            job_description=job_description,
        )
        # Full fallback chain: strategist -> writer tier -> backup
        chain = ["strategist-pro", "strategist-lite", "writer", "backup"]
        return await self._try_service_chain(
            prompt,
            chain,
            system_prompt=CAREER_ADVISOR_SYSTEM,
            allow_tools=True,
        )
