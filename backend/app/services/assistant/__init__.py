"""Assistant bounded context (Wave 2 of the god-file decomposition, FR13).

This package extracts the former ``assistant_service.py`` god-file into a thin
DDD layering while preserving the exact public surface
(``get_assistant_service()`` + the ``AssistantService`` attributes/methods the
endpoints rely on) and observable behavior (BR6.1):

- ``domain/guardrails.py`` — the pure off-topic guardrail (regex/strings, no
                            I/O, BR1.1-BR1.3).
- ``domain/ports.py``      — the consumer-owned Protocols describing ONLY the
                            data/persistence/LLM operations the assistant needs
                            (no SQL, no framework): ``AssistantReadPort``,
                            ``AssistantUsagePort``, ``LLMPort``.
- ``application/`` — the factual answers and the context builder, operating over
                            the read port (dependency inversion).
- ``infrastructure/`` — the only place with raw SQL (usage persistence + read
                            adapter) and the only place that talks to the LLM
                            providers (Groq -> Gemini fallback, BR5.2).
- ``facade.py`` — ``AssistantService``, a thin application service that
                            orchestrates guardrails -> quota -> factual ->
                            context -> LLM -> record -> response (BR6.1) and
                            preserves the public surface.

``app.services.assistant_service`` remains importable as a re-export shim so the
historical import path used by the endpoints keeps working unchanged.
"""

from app.services.assistant.facade import (
    AssistantService,
    AssistantUsageTracker,
    get_assistant_service,
)

__all__ = ["AssistantService", "AssistantUsageTracker", "get_assistant_service"]
