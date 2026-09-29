"""Infrastructure adapter implementing :class:`LLMPort` (BR5.1-BR5.4).

This is the ONLY place in the assistant context that talks to the LLM providers.
It encapsulates the Groq (fast) -> Gemini (fallback) provider order and the
``except Exception`` degradation moved verbatim from the former inline block in
``ask()``. The provider clients are lazily built from the configured API keys;
no credential or token material is ever placed into an exception message, repr,
or ``exc_info`` (BR5.4) — only bounded, non-sensitive substrings of a provider
error are logged.

``complete()`` returns ``(answer, input_tokens, output_tokens)`` on success, or
``None`` when every provider is exhausted (the facade then emits the fixed
saturation message). Recording usage is the facade's responsibility, keeping this
adapter a pure provider boundary.
"""

import logging
from typing import Dict, List, Optional, Tuple

from google import genai

from app.core.config import GEMINI_API_KEY, GROQ_API_KEY

logger = logging.getLogger(__name__)

# Gemini fallback models, in order (relocated verbatim).
GEMINI_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash"]


class LLMProviderAdapter:
    """Adapt the Groq -> Gemini provider fallback to :class:`LLMPort`."""

    def __init__(self, gemini_client=None, groq_client=None) -> None:
        """Create the adapter.

        Args:
            gemini_client: An optional pre-built Gemini client (injectable for
                tests). Defaults to lazy construction from ``GEMINI_API_KEY``.
            groq_client: An optional pre-built Groq client (injectable for
                tests). Defaults to lazy construction from ``GROQ_API_KEY``.
        """
        self._client = gemini_client
        self._groq_client = groq_client
        self._groq_resolved = groq_client is not None

    @property
    def client(self):
        """Lazily build the Gemini client (raises if no key, matching the former property)."""
        if self._client is None:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY no configurada")
            self._client = genai.Client(api_key=GEMINI_API_KEY)
        return self._client

    @property
    def groq_client(self):
        """Lazily build the Groq client; ``None`` when no key is configured."""
        if not self._groq_resolved:
            self._groq_resolved = True
            if not GROQ_API_KEY:
                self._groq_client = None
            else:
                from groq import Groq

                self._groq_client = Groq(api_key=GROQ_API_KEY)
        return self._groq_client

    def complete(
        self, system: str, history: List[Dict], message: str
    ) -> Optional[Tuple[str, int, int]]:
        """Run Groq -> Gemini and return ``(answer, in_tokens, out_tokens)`` or ``None`` (BR5.1-BR5.3)."""
        # 1. Try Groq first (faster, more reliable)
        if self.groq_client:
            try:
                messages = [{"role": "system", "content": system}]
                for msg in history[-4:]:
                    role = msg.get("role", "user")
                    if role == "model":
                        role = "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})
                messages.append({"role": "user", "content": message})

                groq_response = self.groq_client.chat.completions.create(
                    messages=messages,
                    model="openai/gpt-oss-120b",
                    max_tokens=2048,
                )
                answer = (
                    groq_response.choices[0].message.content or "No pude generar una respuesta."
                )

                input_tokens = getattr(groq_response.usage, "prompt_tokens", 0) or 0
                output_tokens = getattr(groq_response.usage, "completion_tokens", 0) or 0

                logger.info(
                    f"Response from Groq/gpt-oss-120b ({input_tokens}+{output_tokens} tokens)"
                )
                return answer, input_tokens, output_tokens

            except Exception as e:
                logger.warning(f"Groq error: {str(e)[:80]}. Falling back to Gemini...")

        # 2. Fallback to Gemini
        contents = [
            {"role": "user", "parts": [{"text": system}]},
            {"role": "model", "parts": [{"text": "Listo, tengo el contexto. ¿En qué te ayudo?"}]},
        ]
        for msg in history[-4:]:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
        contents.append({"role": "user", "parts": [{"text": message}]})

        for model_name in GEMINI_MODELS:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config={"max_output_tokens": 2048},
                )
                answer = response.text or "No pude generar una respuesta."

                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

                logger.info(
                    f"Response from Gemini/{model_name} ({input_tokens}+{output_tokens} tokens)"
                )
                return answer, input_tokens, output_tokens

            except Exception as e:
                error_msg = str(e)
                is_rate_limit = "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg
                is_not_found = "404" in error_msg or "NOT_FOUND" in error_msg
                is_server_error = (
                    "503" in error_msg
                    or "504" in error_msg
                    or "DEADLINE_EXCEEDED" in error_msg
                    or "UNAVAILABLE" in error_msg
                )

                if is_rate_limit or is_not_found or is_server_error:
                    logger.warning(
                        f"Gemini/{model_name} unavailable: {error_msg[:80]}. Trying next..."
                    )
                    continue
                else:
                    logger.error(f"Gemini API error ({model_name}): {e}")
                    break  # Non-recoverable error

        # All providers exhausted
        return None
