"""Backward-compatible re-export shim for the assistant service.

The assistant god-file was decomposed into the ``app.services.assistant`` bounded
context (Wave 2, FR13). This module is kept only so the historical import path
``from app.services.assistant_service import get_assistant_service`` — used by the
assistant and market endpoints — keeps working unchanged. The implementation now
lives across ``app.services.assistant`` (facade + domain + application +
infrastructure).

Every name the rest of the codebase and the existing tests import from here is
re-exported below with its original identity:

- ``get_assistant_service`` / ``AssistantService`` / ``AssistantUsageTracker`` —
  the public surface and the singleton (``facade``).
- ``SYSTEM_PROMPT`` — the prompt template (``facade``).
- ``_check_guardrails`` / ``ALLOWED_KEYWORDS`` / ``BLOCKED_PATTERNS`` /
  ``GUARDRAIL_RESPONSE`` — the guardrail seam (``domain.guardrails``).
- ``FACTUAL_PATTERNS`` — the factual patterns (``application.factual``).
- ``MONTHLY_TOKEN_LIMIT`` / ``DAILY_REQUEST_LIMIT`` — the free-tier limits
  (``infrastructure.usage_adapter``).
- ``get_db`` — re-exported so tests that patch ``assistant_service.get_db`` (the
  DB seam used by the characterization suite) keep working.
"""

from app.core.config import GEMINI_API_KEY, GROQ_API_KEY
from app.services.assistant.application.factual import FACTUAL_PATTERNS
from app.services.assistant.domain.guardrails import (
    ALLOWED_KEYWORDS,
    BLOCKED_PATTERNS,
    GUARDRAIL_RESPONSE,
)
from app.services.assistant.domain.guardrails import check_guardrails as _check_guardrails
from app.services.assistant.facade import (
    SYSTEM_PROMPT,
    AssistantService,
    AssistantUsageTracker,
    get_assistant_service,
)
from app.services.assistant.infrastructure.usage_adapter import (
    DAILY_REQUEST_LIMIT,
    MONTHLY_TOKEN_LIMIT,
)
from app.services.db_connection import get_db

__all__ = [
    "AssistantService",
    "AssistantUsageTracker",
    "get_assistant_service",
    "SYSTEM_PROMPT",
    "FACTUAL_PATTERNS",
    "ALLOWED_KEYWORDS",
    "BLOCKED_PATTERNS",
    "GUARDRAIL_RESPONSE",
    "_check_guardrails",
    "MONTHLY_TOKEN_LIMIT",
    "DAILY_REQUEST_LIMIT",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "get_db",
]
