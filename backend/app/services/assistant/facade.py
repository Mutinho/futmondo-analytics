"""Thin ``AssistantService`` application-service facade (BR6.1).

Preserves the exact public surface of the former ``assistant_service.py`` god-file
— ``get_assistant_service()``, the ``AssistantService`` attributes/methods the
endpoints rely on (``ask``, ``usage_tracker``, ``_save_market_to_db``, the
``client`` / ``groq_client`` properties) — and only orchestrates:
guardrails -> quota -> factual -> context -> LLM -> record -> response (BR6.1).

Constructor injection with defaults (OCP, like ``analytics/facade.py``):
``AssistantService()`` with no arguments builds the production adapters — the
read adapter over the global DB, the usage adapter, and the LLM provider adapter
— identical to the historical no-arg behavior the endpoints rely on. Tests inject
stub ports via ``AssistantService(read=..., usage=..., llm=...)`` (no
monkeypatching of SQL or the network).

The observable ``usage_tracker`` attribute and the ``client`` / ``groq_client``
properties remain for backward compatibility with the endpoints and the existing
characterization tests.
"""

import logging
from typing import Optional

from google import genai

from app.core.config import GEMINI_API_KEY, GROQ_API_KEY
from app.services.assistant.application.context import ContextBuilder
from app.services.assistant.application.factual import FactualAnswers
from app.services.assistant.domain.guardrails import check_guardrails
from app.services.assistant.domain.ports import (
    AssistantReadPort,
    AssistantUsagePort,
    LLMPort,
)
from app.services.assistant.infrastructure.llm_adapter import LLMProviderAdapter
from app.services.assistant.infrastructure.read_adapter import (
    DataManagerAssistantReadAdapter,
)
from app.services.assistant.infrastructure.usage_adapter import AssistantUsageAdapter
from app.services.db_connection import get_db

logger = logging.getLogger(__name__)

# --- System prompt (relocated verbatim from the god-file) --------------------
SYSTEM_PROMPT = """Eres el asistente de Futmondo Analytics. Ayudas al usuario a tomar decisiones \
en su liga de fantasy football (Futmondo - Liga española).

IDENTIDAD DEL USUARIO:
- Nombre: {user_name}
- Equipo: {team_name}
- Campeonato: {championship_name}
- Modo: {mode}

FORMATO OBLIGATORIO:
- Usa SOLO listas con viñetas (-) y negrita (**texto**)
- PROHIBIDO usar tablas (líneas con |). JAMÁS. Ni una sola tabla.
- Para cada jugador pon: **Nombre** (Pos) — Valor, Media Últ5, Titularidades → razón

REGLAS:
- Responde en español, natural y directo (como un colega que entiende de fantasy)
- Tutea al usuario. No repitas su nombre en cada frase
- Basa tus recomendaciones SOLO en los datos proporcionados
- Justifica con datos (media, tendencia, valor) cuando recomiendes vender/comprar
- No inventes datos ni jugadores
- Sé breve: máximo 350 palabras
- Mantén el hilo: si el usuario dice "no vendo a X", respétalo
- Solo respondes sobre Futmondo/fantasy football.

CONTEXTO DEL USUARIO:
{context}"""


class AssistantUsageTracker:
    """Tracks token/request usage to stay within free tier limits (BR4.1-BR4.3).

    Thin delegator over :class:`AssistantUsageAdapter` (the only place with the
    ``assistant_usage`` SQL). The DB boundary is threaded through the module-level
    ``get_db`` so existing behavior — and the injected in-memory fake used by the
    characterization tests — is unchanged.
    """

    def __init__(self, port: Optional[AssistantUsagePort] = None):
        self._adapter: AssistantUsagePort = (
            port if port is not None else AssistantUsageAdapter(db_factory=lambda: get_db())
        )

    def _ensure_table(self):
        """Create usage table if it doesn't exist (idempotent)."""
        # Only the concrete adapter exposes _ensure_table; injected stubs may not.
        ensure = getattr(self._adapter, "_ensure_table", None)
        if ensure is not None:
            ensure()

    def can_make_request(self) -> tuple[bool, str]:
        """Check if we're within budget."""
        return self._adapter.can_make_request()

    def record_usage(self, input_tokens: int, output_tokens: int):
        """Record token usage after each request."""
        self._adapter.record_usage(input_tokens, output_tokens)

    def get_usage_summary(self) -> dict:
        """Return current month usage."""
        return self._adapter.get_usage_summary()


class AssistantService:
    """Main assistant service — orchestrates guardrails, factual, context, LLM (BR6.1)."""

    def __init__(
        self,
        read: Optional[AssistantReadPort] = None,
        usage: Optional[AssistantUsagePort] = None,
        llm: Optional[LLMPort] = None,
    ) -> None:
        # Read port (default: production adapter over the global DB).
        self._read: AssistantReadPort = (
            read
            if read is not None
            else DataManagerAssistantReadAdapter(db_factory=lambda: get_db())
        )
        # Usage tracker (backward-compatible observable attribute).
        self.usage_tracker = AssistantUsageTracker(port=usage)
        # Application layers over the read port.
        self._factual = FactualAnswers(self._read)
        self._context = ContextBuilder(self._read)
        # LLM port: an injected stub short-circuits provider construction; the
        # lazily-built clients below remain for the historical property surface.
        self._llm = llm
        self._client: Optional[genai.Client] = None
        self._groq_client = None

    # --- Backward-compatible provider properties --------------------------
    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY no configurada")
            self._client = genai.Client(api_key=GEMINI_API_KEY)
        return self._client

    @property
    def groq_client(self):
        if self._groq_client is None:
            if not GROQ_API_KEY:
                return None
            from groq import Groq

            self._groq_client = Groq(api_key=GROQ_API_KEY)
        return self._groq_client

    def _make_llm(self) -> LLMPort:
        """Return the injected LLM port, or build the provider adapter from the facade's clients.

        Passing the facade's own ``_client`` / ``_groq_client`` keeps any caller-
        or test-injected client flowing through the port; when they are ``None``
        the adapter lazily builds each provider from its configured key, matching
        the historical property behavior.
        """
        if self._llm is not None:
            return self._llm
        return LLMProviderAdapter(gemini_client=self._client, groq_client=self._groq_client)

    # --- User identity ----------------------------------------------------
    def _get_user_identity(self, user_id: str, championship_id: str) -> dict:
        """Get user's identity from DB. Always called first."""
        return self._read.get_user_identity(user_id, championship_id)

    # --- Factual answers (delegators over the application layer) -----------
    def _try_factual_answer(
        self, user_id: str, championship_id: str, message: str, identity: dict
    ) -> Optional[str]:
        """Try to answer factual questions directly from DB."""
        return self._factual.try_answer(user_id, championship_id, message, identity)

    def _factual_balance(self, user_id: str, championship_id: str, identity: dict) -> Optional[str]:
        return self._factual._factual_balance(user_id, championship_id, identity)

    def _factual_roster(self, user_id: str, championship_id: str, identity: dict) -> Optional[str]:
        return self._factual._factual_roster(user_id, championship_id, identity)

    def _factual_standings(
        self, user_id: str, championship_id: str, identity: dict
    ) -> Optional[str]:
        return self._factual._factual_standings(user_id, championship_id, identity)

    def _factual_team_value(
        self, user_id: str, championship_id: str, identity: dict
    ) -> Optional[str]:
        return self._factual._factual_team_value(user_id, championship_id, identity)

    # --- Main orchestrator ------------------------------------------------
    async def ask(
        self, user_id: str, championship_id: str, message: str, history: list[dict], request=None
    ) -> dict:
        """Process a user question and return AI response (BR6.1).

        Flow:
        1. Guardrails — reject off-topic (no tokens)
        2. Get user identity (always)
        3. Try factual answer from DB (no tokens)
        4. If not factual → quota check → build context → call LLM → record → respond
        """
        # 1. Guardrails
        guardrail_response = check_guardrails(message)
        if guardrail_response:
            return {"response": guardrail_response, "context_used": ["guardrail"]}

        # 2. User identity
        identity = self._get_user_identity(user_id, championship_id)

        # 3. Factual answer (FREE) — short-circuits before the quota check (BR6.1).
        factual_answer = self._try_factual_answer(user_id, championship_id, message, identity)
        if factual_answer:
            logger.info(f"Factual answer for user {user_id} — no Gemini call")
            return {"response": factual_answer, "context_used": ["direct_db"]}

        # 4. Needs LLM reasoning — quota check first.
        allowed, reason = self.usage_tracker.can_make_request()
        if not allowed:
            return {"response": f"⚠️ {reason}", "context_used": []}

        # Build context — skip full re-injection on follow-ups to save tokens; but
        # if the follow-up asks about a new topic (market, lineup, etc), inject it.
        is_followup = len(history) >= 2 and len(message) < 120
        needs_full_context_keywords = [
            "fich",
            "compr",
            "mercado",
            "once",
            "aline",
            "formaci",
            "jornada",
            "claus",
            "libre",
            "agente",
            "clasif",
        ]
        needs_full = any(k in message.lower() for k in needs_full_context_keywords)

        if is_followup and not needs_full:
            # Simple follow-up: only budget context.
            context = (
                self._ctx_budget(None, None, user_id, championship_id, identity["team_id"]) or ""
            )
            context_types = ["budget_only"]
        else:
            context, context_types = self._build_context(
                user_id, championship_id, message, identity, request
            )

        system = SYSTEM_PROMPT.format(
            user_name=identity["user_name"],
            team_name=identity["team_name"],
            championship_name=identity["championship_name"],
            mode="PRO (formaciones extra disponibles)" if identity.get("is_pro") else "Clásico",
            context=context,
        )

        # Call LLM with provider fallback (Groq -> Gemini) behind the port (BR5.1-BR5.3).
        completion = self._make_llm().complete(system, history, message)
        if completion is not None:
            answer, input_tokens, output_tokens = completion
            self.usage_tracker.record_usage(input_tokens, output_tokens)
            return {"response": answer, "context_used": context_types}

        # All providers exhausted.
        return {
            "response": "⚠️ Todos los modelos están saturados. Espera un momento e inténtalo de nuevo.",
            "context_used": [],
        }

    # --- Context builder (delegators; historical (cursor, db) params kept) --
    def _build_context(
        self, user_id: str, championship_id: str, message: str, identity: dict, request=None
    ) -> tuple[str, list[str]]:
        return self._context.build_context(user_id, championship_id, message, identity, request)

    def _ctx_roster(self, cursor, db, championship_id: str, team_id: str, team_name: str) -> str:
        return self._context._ctx_roster(championship_id, team_id, team_name)

    def _ctx_budget(self, cursor, db, user_id: str, championship_id: str, team_id: str) -> str:
        return self._context._ctx_budget(user_id, championship_id, team_id)

    def _ctx_market_live(self, request, championship_id: str) -> str:
        return self._ctx_market_from_db(championship_id)

    def _ctx_market_from_db(self, championship_id: str) -> str:
        """Read today's market; degrades to '' on failure (BR3.3, degrading branch)."""
        return self._context.ctx_market_from_db(championship_id)

    def _save_market_to_db(self, championship_id: str, players: list):
        """Save today's market to DB for caching (used by both assistant and market page)."""
        self._read.save_market_today(championship_id, players)

    def _format_market_context(self, computer_players: list) -> str:
        return self._context.format_market_context(computer_players)

    def _ctx_free_agents(self, cursor, db, championship_id: str) -> str:
        return self._context._ctx_free_agents(championship_id)

    def _ctx_clausulables(self, cursor, db, championship_id: str) -> str:
        return self._context._ctx_clausulables(championship_id)

    def _ctx_standings(self, cursor, db, championship_id: str) -> str:
        return self._context._ctx_standings(championship_id)

    def _ctx_transactions(self, cursor, db, championship_id: str, team_id: str) -> str:
        return self._context._ctx_transactions(championship_id, team_id)

    def _ctx_next_matches(self, cursor, db, championship_id: str, team_id: str) -> str:
        return self._context._ctx_next_matches(championship_id, team_id)

    def _ctx_formations(self, championship_id: str, team_id: str) -> str:
        return self._context._ctx_formations(championship_id)


# Singleton
_assistant_service: Optional[AssistantService] = None


def get_assistant_service() -> AssistantService:
    """Get or create singleton assistant service."""
    global _assistant_service
    if _assistant_service is None:
        _assistant_service = AssistantService()
    return _assistant_service
