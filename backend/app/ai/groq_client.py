import os
import json
from typing import Dict, Any, Optional, List
from groq import Groq
from app.config import settings
from app.core.logging import logger
from app.utils.json_utils import extract_json_from_llm_response
from app.core.security import sanitize_for_prompt

class GroqClient:
    """
    Wrapper for Groq LLM API.
    Follows project rule: Groq is the ONLY LLM provider.
    Includes deterministic fallback engine for when GROQ_API_KEY is not yet supplied.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.client = None
        
        if self.api_key and not self.api_key.startswith("gsk_YOUR_GROQ"):
            try:
                self.client = Groq(api_key=self.api_key, max_retries=0)
                logger.info(f"Initialized Groq client with model {self.model}")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
                self.client = None
        else:
            logger.info("No active GROQ_API_KEY detected. Using deterministic fallback engine.")

    def is_available(self) -> bool:
        return self.client is not None

    def call_structured(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        """
        Calls Groq Chat Completion with json response format.
        Restricted to 900 max_tokens to remain strictly within Groq free-tier 1000 OTPM limits.
        """
        if not self.is_available():
            logger.info("Groq API not active, routing to fallback response generator.")
            return {}

        sanitized_user = sanitize_for_prompt(user_prompt)
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": sanitized_user}
                ],
                model=self.model,
                temperature=temperature,
                max_tokens=900,
                timeout=8.0,
                response_format={"type": "json_object"}
            )
            raw_content = chat_completion.choices[0].message.content
            return extract_json_from_llm_response(raw_content)
        except Exception as e:
            logger.error(f"Groq API call error: {e}. Attempting fallback model...")
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": sanitized_user}
                    ],
                    model=settings.GROQ_FALLBACK_MODEL,
                    temperature=temperature,
                    max_tokens=900,
                    timeout=8.0,
                    response_format={"type": "json_object"}
                )
                return extract_json_from_llm_response(chat_completion.choices[0].message.content)
            except Exception as e2:
                logger.error(f"Groq fallback model also failed: {e2}")
                return {}

groq_client = GroqClient()
