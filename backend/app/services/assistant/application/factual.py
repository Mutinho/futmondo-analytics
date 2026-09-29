"""Factual answers over :class:`AssistantReadPort` (BR2.1, BR2.2).

Application layer: it decides whether a message is a factual question and, if so,
formats the answer from data the read port returns. It contains NO SQL and never
touches the LLM — every read goes through the injected port. The formatting is a
verbatim relocation of the former ``_try_factual_answer`` and ``_factual_*``
handlers, so the produced answer strings are identical.
"""

import re
from typing import Dict, Optional

from app.services.assistant.domain.ports import AssistantReadPort

# Factual patterns resolved directly from DB, no LLM call (relocated verbatim).
FACTUAL_PATTERNS = [
    # Budget/balance questions
    (r"(cu[áa]nto|qu[ée]).*(saldo|dinero|presupuesto)\b", "balance"),
    (r"^mi saldo", "balance"),
    (r"^saldo\s*(actual|disponible)?$", "balance"),
    # Roster questions — only when asking TO SEE the roster, not strategy about it
    (r"^(mi|mis)\s*(plantilla|jugador)", "roster"),
    (r"^(muestra|enseña|lista|dame).*plantilla", "roster"),
    (r"(cu[áa]ntos|n[úu]mero).*(jugador)", "roster"),
    # Classification questions
    (r"^(clasificaci[óo]n|ranking|tabla)$", "standings"),
    (r"(qu[ée]|en qu[ée])\s*puesto", "standings"),
    (r"(c[óo]mo|cu[áa]l).*(clasificaci[óo]n)", "standings"),
    # Team value
    (r"(cu[áa]nto|qu[ée]).*(vale|valor).*(plantilla|equipo)", "team_value"),
]


class FactualAnswers:
    """Answer factual questions directly from data, without the LLM."""

    def __init__(self, data: AssistantReadPort) -> None:
        self._data = data

    def try_answer(
        self, user_id: str, championship_id: str, message: str, identity: dict
    ) -> Optional[str]:
        """Try to answer factual questions directly from DB (BR2.1)."""
        msg_lower = message.lower().strip()

        # Strategy indicators bypass factual answers (they need LLM reasoning).
        strategy_words = ["debería", "recomiend", "consejo", "mejor", "peor", "conviene", "merece"]
        if any(w in msg_lower for w in strategy_words):
            return None

        for pattern, handler_name in FACTUAL_PATTERNS:
            if re.search(pattern, msg_lower):
                handler = getattr(self, f"_factual_{handler_name}", None)
                if handler:
                    result = handler(user_id, championship_id, identity)
                    if result:
                        return result
        return None

    # --- Handlers (formatting over the read port; verbatim output) --------
    def _factual_balance(self, user_id: str, championship_id: str, identity: dict) -> Optional[str]:
        team_id = identity["team_id"]
        if not team_id:
            return None

        d: Dict = self._data.get_balance_data(user_id, championship_id, team_id)
        total_spent = d["total_spent"]
        total_income = d["total_income"]
        initial_budget = d["initial_budget"]
        prizes = d["prizes"]
        team_value = d["team_value"]

        balance = initial_budget - total_spent + total_income + prizes

        return (
            f"💰 **Tu presupuesto ({identity['team_name']}):**\n\n"
            f"- **Saldo disponible:** {balance / 1_000_000:.1f}M€\n"
            f"- Presupuesto inicial: {initial_budget / 1_000_000:.0f}M€\n"
            f"- Total gastado: {total_spent / 1_000_000:.1f}M€\n"
            f"- Total ingresado: {total_income / 1_000_000:.1f}M€\n"
            f"- Premios acumulados: {prizes / 1_000_000:.1f}M€\n"
            f"- Valor plantilla: {team_value / 1_000_000:.1f}M€\n"
            f"- **Patrimonio total:** {(balance + team_value) / 1_000_000:.1f}M€"
        )

    def _factual_roster(self, user_id: str, championship_id: str, identity: dict) -> Optional[str]:
        team_id = identity["team_id"]
        if not team_id:
            return None

        rows = self._data.get_roster_rows(championship_id, team_id)
        if not rows:
            return "No tienes jugadores en tu plantilla para este campeonato."

        # Deduplicate: keep first row per player_id (highest sofascore rating)
        seen = {}
        for row in rows:
            pid = row[0]
            if pid not in seen or (row[6] or 0) > (seen[pid][6] or 0):
                seen[pid] = row
        unique_rows = list(seen.values())
        unique_rows.sort(key=lambda r: r[3] or 0, reverse=True)  # sort by value desc

        total_value = sum(r[3] or 0 for r in unique_rows)
        lines = [
            f"📋 **Tu plantilla ({identity['team_name']}) — {len(unique_rows)} jugadores** "
            f"(Valor total: {total_value / 1_000_000:.1f}M€)\n"
        ]

        for pid, name, role, value, avg, avg5, sofascore in unique_rows:
            value_m = f"{(value or 0) / 1_000_000:.1f}M"
            avg_str = f"Media {avg:.1f}" if avg else "Sin media"
            avg5_str = f"Últ5: {avg5:.1f}" if avg5 else ""
            ss_str = f"SS {sofascore:.1f}" if sofascore else ""
            parts = [f"**{name}**", role or "", value_m, avg_str, avg5_str, ss_str]
            lines.append("- " + " | ".join(p for p in parts if p))

        return "\n".join(lines)

    def _factual_standings(
        self, user_id: str, championship_id: str, identity: dict
    ) -> Optional[str]:
        max_matchday, rows = self._data.get_standings(championship_id)
        if max_matchday is None or not rows:
            return None

        lines = [
            f"🏆 **Clasificación ({identity['championship_name']}) — Jornada {max_matchday}:**\n"
        ]
        for name, points, pos in rows:
            marker = " ← **TÚ**" if name == identity["team_name"] else ""
            lines.append(f"**#{pos}** {name} — {points or 0} pts{marker}")

        return "\n".join(lines)

    def _factual_team_value(
        self, user_id: str, championship_id: str, identity: dict
    ) -> Optional[str]:
        team_id = identity["team_id"]
        if not team_id:
            return None

        team_value, player_count = self._data.get_team_value(championship_id, team_id)
        if player_count == 0:
            return "No tienes jugadores en tu plantilla."

        avg_value = team_value / player_count
        return (
            f"📊 **Valor de tu plantilla ({identity['team_name']}):**\n\n"
            f"- **Valor total:** {team_value / 1_000_000:.1f}M€\n"
            f"- Jugadores: {player_count}\n"
            f"- Media por jugador: {avg_value / 1_000_000:.1f}M€"
        )
