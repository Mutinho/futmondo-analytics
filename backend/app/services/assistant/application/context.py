"""Context builder over :class:`AssistantReadPort` (BR3.1-BR3.3).

Application layer: assembles the LLM context string from data the read port
returns. It contains NO SQL. The formatting and the per-branch degradation are a
verbatim relocation of the former ``_build_context`` and ``_ctx_*`` helpers, so
the produced context strings are identical (BR3.1, BR3.2) and the NON-uniform
degradation is preserved (BR3.3, reviewer note R-03): the market branch degrades
to ``""`` on a read failure while the others do not swallow.
"""

from typing import List, Tuple

from app.services.assistant.domain.ports import AssistantReadPort


class ContextBuilder:
    """Build the LLM context from the read port."""

    def __init__(self, data: AssistantReadPort) -> None:
        self._data = data

    def build_context(
        self, user_id: str, championship_id: str, message: str, identity: dict, request=None
    ) -> Tuple[str, List[str]]:
        """Build relevant context from DB based on the user's question (BR3.1)."""
        context_parts: List[str] = []
        context_types: List[str] = []
        msg_lower = message.lower()
        team_id = identity["team_id"]

        # --- Always: user's roster ---
        roster_ctx = self._ctx_roster(championship_id, team_id, identity["team_name"])
        if roster_ctx:
            context_parts.append(roster_ctx)
            context_types.append("roster")

        # --- Always: budget ---
        budget_ctx = self._ctx_budget(user_id, championship_id, team_id)
        if budget_ctx:
            context_parts.append(budget_ctx)
            context_types.append("budget")

        # --- Market (if asking about signings) ---
        market_keywords = ["fich", "compr", "mercado", "puj", "fichar", "comprar"]
        if any(k in msg_lower for k in market_keywords):
            market_ctx = self.ctx_market_from_db(championship_id)
            if market_ctx:
                context_parts.append(market_ctx)
                context_types.append("market")

        # --- Free agents ---
        free_keywords = ["libre", "agente", "free"]
        if any(k in msg_lower for k in free_keywords):
            free_ctx = self._ctx_free_agents(championship_id)
            if free_ctx:
                context_parts.append(free_ctx)
                context_types.append("free_agents")

        # --- Clausulables ---
        clause_keywords = ["claus", "clausul"]
        if any(k in msg_lower for k in clause_keywords):
            clause_ctx = self._ctx_clausulables(championship_id)
            if clause_ctx:
                context_parts.append(clause_ctx)
                context_types.append("clausulable")

        # --- Standings ---
        strategy_keywords = ["clasif", "posición", "puesto", "estrategia", "rival", "punt"]
        if any(k in msg_lower for k in strategy_keywords):
            standings_ctx = self._ctx_standings(championship_id)
            if standings_ctx:
                context_parts.append(standings_ctx)
                context_types.append("standings")

        # --- Transactions ---
        sell_keywords = ["vend", "venta", "transacc", "historial"]
        if any(k in msg_lower for k in sell_keywords):
            tx_ctx = self._ctx_transactions(championship_id, team_id)
            if tx_ctx:
                context_parts.append(tx_ctx)
                context_types.append("transactions")

        # --- Matches/Odds ---
        lineup_keywords = [
            "once",
            "aline",
            "formaci",
            "jornada",
            "rival",
            "partido",
            "cuota",
            "poner",
            "pongo",
        ]
        if any(k in msg_lower for k in lineup_keywords):
            matches_ctx = self._ctx_next_matches(championship_id, team_id)
            if matches_ctx:
                context_parts.append(matches_ctx)
                context_types.append("matches")

        context = (
            "\n\n".join(context_parts)
            if context_parts
            else "No hay datos disponibles para este campeonato."
        )
        return context, context_types

    # --- Simple budget-only context (used by the follow-up short path) --------
    def ctx_budget(self, user_id: str, championship_id: str, team_id: str) -> str:
        return self._ctx_budget(user_id, championship_id, team_id)

    # --- Per-branch builders (verbatim formatting over the port) -------------
    def _ctx_roster(self, championship_id: str, team_id: str, team_name: str) -> str:
        if not team_id:
            return ""
        rows = self._data.get_roster_rows_ctx(championship_id, team_id)
        if not rows:
            return ""

        seen = {}
        for row in rows:
            pid = row[0]
            if pid not in seen or (row[6] or 0) > (seen[pid][6] or 0):
                seen[pid] = row
        unique_rows = list(seen.values())
        unique_rows.sort(key=lambda r: r[3] or 0, reverse=True)

        lines = [f"MI PLANTILLA ({team_name}) — {len(unique_rows)} jugadores:"]
        for pid, name, role, value, avg, avg5, rating, started in unique_rows:
            value_m = f"{(value or 0) / 1_000_000:.1f}M"
            avg_str = f"{avg:.1f}" if avg else "-"
            avg5_str = f"{avg5:.1f}" if avg5 else "-"
            ss_str = f"{rating:.1f}" if rating else "-"
            started_str = str(started or 0)
            lines.append(
                f"{name},{role or '-'},{value_m},avg:{avg_str},últ5:{avg5_str},ss:{ss_str},tit:{started_str}"
            )

        return "\n".join(lines)

    def _ctx_budget(self, user_id: str, championship_id: str, team_id: str) -> str:
        if not team_id:
            return ""
        d = self._data.get_budget_data(user_id, championship_id, team_id)
        total_spent = d["total_spent"]
        total_income = d["total_income"]
        initial_budget = d["initial_budget"]
        prizes = d["prizes"]
        team_value = d["team_value"]
        balance = initial_budget - total_spent + total_income + prizes

        return (
            f"PRESUPUESTO: saldo={balance / 1_000_000:.1f}M, gastado={total_spent / 1_000_000:.1f}M, "
            f"ingresado={total_income / 1_000_000:.1f}M, premios={prizes / 1_000_000:.1f}M, "
            f"valor_plantilla={team_value / 1_000_000:.1f}M, patrimonio={(balance + team_value) / 1_000_000:.1f}M"
        )

    def ctx_market_from_db(self, championship_id: str) -> str:
        """Read today's market; degrades to '' on failure (BR3.3, degrading branch)."""
        rows = self._data.get_market_today(championship_id)
        if not rows:
            return ""
        lines = [f"MERCADO HOY ({len(rows)} del computer):"]
        for name, pos, value, avg, matches in rows:
            value_m = f"{(value or 0) / 1_000_000:.1f}M"
            avg_str = f"{avg:.1f}" if avg else "-"
            lines.append(f"{name},{pos or '-'},{value_m},avg:{avg_str},pj:{matches or 0}")
        return "\n".join(lines)

    def _ctx_free_agents(self, championship_id: str) -> str:
        rows = self._data.get_free_agents(championship_id)
        if not rows:
            return ""
        lines = ["AGENTES LIBRES (top 30):"]
        for name, role, value, avg, avg5, rating in rows:
            value_m = f"{(value or 0) / 1_000_000:.1f}M"
            avg_str = f"{avg:.1f}" if avg else "-"
            avg5_str = f"{avg5:.1f}" if avg5 else "-"
            ss_str = f"{rating:.1f}" if rating else "-"
            lines.append(
                f"{name},{role or '-'},{value_m},avg:{avg_str},últ5:{avg5_str},ss:{ss_str}"
            )
        return "\n".join(lines)

    def _ctx_clausulables(self, championship_id: str) -> str:
        rows = self._data.get_clausulables(championship_id)
        if not rows:
            return ""
        lines = ["CLAUSULABLES (top 15 por ratio media/cláusula):"]
        for name, role, value, avg, clause, owner, rating in rows:
            clause_m = f"{(clause or 0) / 1_000_000:.1f}M"
            avg_str = f"{avg:.1f}" if avg else "-"
            ss_str = f"{rating:.1f}" if rating else "-"
            lines.append(
                f"{name},{role or '-'},dueño:{owner or '-'},avg:{avg_str},cláusula:{clause_m},ss:{ss_str}"
            )
        return "\n".join(lines)

    def _ctx_standings(self, championship_id: str) -> str:
        max_matchday, rows = self._data.get_standings(championship_id)
        if max_matchday is None or not rows:
            return ""
        lines = [f"CLASIFICACIÓN (J{max_matchday}):"]
        for name, points, pos in rows:
            lines.append(f"#{pos} {name} {points or 0}pts")
        return "\n".join(lines)

    def _ctx_transactions(self, championship_id: str, team_id: str) -> str:
        if not team_id:
            return ""
        rows = self._data.get_transactions(championship_id, team_id)
        if not rows:
            return ""
        lines = ["TRANSACCIONES RECIENTES:"]
        for name, price, tx_date, tx_type in rows:
            price_m = f"{(price or 0) / 1_000_000:.1f}M"
            lines.append(f"{tx_type}:{name or '?'},{price_m},{tx_date or '-'}")
        return "\n".join(lines)

    def _ctx_next_matches(self, championship_id: str, team_id: str) -> str:
        if not team_id:
            return ""

        parts = []
        next_matchday, matches, my_players = self._data.get_next_matches(championship_id, team_id)
        if next_matchday is None or not matches:
            return ""

        team_players = {}
        for name, real_team_id, role in my_players:
            if real_team_id:
                team_players.setdefault(real_team_id, []).append(f"{name} ({role})")

        lines = [f"⚽ PARTIDOS JORNADA {next_matchday} (con cuotas y tus jugadores):"]
        for home_id, home_name, away_id, away_name, odds_h, odds_d, odds_a, match_date in matches:
            if odds_h and odds_a:
                odds_str = f"[{odds_h:.2f} / {odds_d:.2f} / {odds_a:.2f}]"
                if odds_h < odds_a:
                    fav = f"(favorito: {home_name})"
                elif odds_a < odds_h:
                    fav = f"(favorito: {away_name})"
                else:
                    fav = "(igualado)"
            else:
                odds_str = "[sin cuotas]"
                fav = ""

            line = f"{home_name} vs {away_name} {odds_str} {fav}"
            home_players = team_players.get(home_id, [])
            away_players = team_players.get(away_id, [])
            if home_players:
                line += f"\n  → Tus jugadores LOCAL: {', '.join(home_players)}"
            if away_players:
                line += f"\n  → Tus jugadores VISITANTE: {', '.join(away_players)}"
            lines.append(line)

        parts.append("\n".join(lines))

        formations_ctx = self._ctx_formations(championship_id)
        if formations_ctx:
            parts.append(formations_ctx)

        return "\n\n".join(parts)

    def _ctx_formations(self, championship_id: str) -> str:
        is_pro = self._data.get_is_pro(championship_id)
        standard = ["4-4-2", "4-3-3", "4-5-1", "3-4-3", "3-5-2", "5-4-1", "5-3-2"]
        pro = ["3-6-1", "4-2-4", "3-3-4", "4-6-0", "5-2-3"]
        lines = ["📐 FORMACIONES DISPONIBLES:"]
        lines.append(f"Estándar: {', '.join(standard)}")
        if is_pro:
            lines.append(f"Pro (extra): {', '.join(pro)}")
        return "\n".join(lines)

    @staticmethod
    def format_market_context(computer_players: list) -> str:
        """Format live market players as a context string. Verbatim from ``_format_market_context``."""
        lines = [f"MERCADO HOY ({len(computer_players)} del computer):"]
        for p in computer_players:
            name = p.get("name", "?")
            role = p.get("role", "-")
            value = p.get("value", 0)
            avg_data = p.get("average", {})
            avg = avg_data.get("average", 0) if isinstance(avg_data, dict) else 0
            matches = avg_data.get("matches", 0) if isinstance(avg_data, dict) else 0
            value_m = f"{value / 1_000_000:.1f}M"
            avg_str = f"{avg:.1f}" if avg else "-"
            lines.append(f"{name},{role},{value_m},avg:{avg_str},pj:{matches}")
        return "\n".join(lines)
