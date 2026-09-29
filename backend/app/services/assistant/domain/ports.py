"""Consumer-owned ports for the assistant context (no SQL, no framework).

These structural :class:`typing.Protocol` types describe ONLY the operations the
assistant's application/facade layers consume. They live in the domain layer and
import neither ``infrastructure/`` nor any framework, and they contain no SQL
(dependency inversion). Concrete adapters in ``infrastructure/`` implement them.

- :class:`AssistantUsagePort` — quota check + usage recording for the free-tier
  budget (BR4.1, BR4.2), backed by the ``assistant_usage`` table in the adapter.
- :class:`AssistantReadPort` — the read-only data surface the factual answers and
  the context builder consume (BR2.2, BR3.2); every raw ``SELECT`` lives in the
  adapter behind this port.
- :class:`LLMPort` — the generative-completion surface (BR5.2); the Groq -> Gemini
  provider fallback lives entirely in the adapter behind this port.
"""

from typing import Dict, List, Optional, Protocol, Tuple


class AssistantUsagePort(Protocol):
    """Free-tier usage budget surface consumed by the facade (BR4.1, BR4.2)."""

    def can_make_request(self) -> Tuple[bool, str]:
        """Return ``(allowed, reason)``; reason is a user-facing message when blocked."""
        ...

    def record_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Accumulate token/request counters after a served request."""
        ...

    def get_usage_summary(self) -> Dict:
        """Return the current month's usage summary dict."""
        ...


class AssistantReadPort(Protocol):
    """Read-only data surface for factual answers and context building.

    Each method replaces a raw ``cursor.execute`` read that previously lived
    inline in ``assistant_service.py``. Implementations keep the SQL in the
    infrastructure adapter (BR2.2, BR3.2) and return plain rows/dicts.
    """

    # --- User identity ----------------------------------------------------
    def get_user_identity(self, user_id: str, championship_id: str) -> Dict:
        """Return the user's identity dict (name, team, championship, is_pro)."""
        ...

    # --- Factual reads ----------------------------------------------------
    def get_balance_data(self, user_id: str, championship_id: str, team_id: str) -> Dict:
        """Return the raw figures needed to compute the balance answer."""
        ...

    def get_roster_rows(self, championship_id: str, team_id: str) -> List[tuple]:
        """Return roster rows (player_id, name, role, value, avg, avg5, rating, started)."""
        ...

    def get_standings(self, championship_id: str) -> Tuple[Optional[int], List[tuple]]:
        """Return ``(max_matchday, rows)`` for the latest standings."""
        ...

    def get_team_value(self, championship_id: str, team_id: str) -> Tuple[int, int]:
        """Return ``(total_value, player_count)`` for the team."""
        ...

    # --- Context reads ----------------------------------------------------
    def get_free_agents(self, championship_id: str) -> List[tuple]:
        """Return top free-agent rows."""
        ...

    def get_clausulables(self, championship_id: str) -> List[tuple]:
        """Return top clausulable rows."""
        ...

    def get_transactions(self, championship_id: str, team_id: str) -> List[tuple]:
        """Return recent transaction rows for the team."""
        ...

    def get_next_matches(
        self, championship_id: str, team_id: str
    ) -> Tuple[Optional[int], List[tuple], List[tuple]]:
        """Return ``(next_matchday, match_rows, my_player_rows)``."""
        ...

    def get_is_pro(self, championship_id: str) -> bool:
        """Return whether the championship is in PRO mode."""
        ...

    def get_market_today(self, championship_id: str) -> List[tuple]:
        """Return today's cached computer-market rows (empty on any error)."""
        ...

    def save_market_today(self, championship_id: str, players: List[Dict]) -> None:
        """Persist today's market snapshot (used by the market page cache)."""
        ...


class LLMPort(Protocol):
    """Generative-completion surface with provider fallback (BR5.1, BR5.2)."""

    def complete(
        self,
        system: str,
        history: List[Dict],
        message: str,
    ) -> Optional[Tuple[str, int, int]]:
        """Return ``(answer, input_tokens, output_tokens)`` or ``None`` if unavailable.

        The Groq -> Gemini provider order and the degradation on failure live
        entirely behind this port. ``None`` signals every provider was exhausted
        (the facade then returns the fixed saturation message). No credential or
        token material is ever surfaced through this port (BR5.4).
        """
        ...
