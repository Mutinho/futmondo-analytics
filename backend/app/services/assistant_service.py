"""AI Assistant Service — Context builder + Gemini 2.0 Flash integration + usage tracking.

Key features:
- Always injects user identity (name, team, championship) into system prompt
- Answers factual questions directly from DB WITHOUT calling Gemini (saves tokens)
- Only calls Gemini for questions that require reasoning/recommendations
- Guardrails block off-topic questions without wasting tokens
"""

import logging
import re
from datetime import datetime, date
from typing import Optional

from google import genai

from app.core.config import GEMINI_API_KEY, GROQ_API_KEY
from app.services.db_connection import get_db

logger = logging.getLogger(__name__)

# --- Usage limits (free tier protection) ---
MONTHLY_TOKEN_LIMIT = 25_000_000  # 25M tokens/month (free tier gives ~30M)
DAILY_REQUEST_LIMIT = 50  # Max 50 questions per day

# --- System prompt ---
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


# ==============================================================================
# FACTUAL ANSWER PATTERNS — resolved directly from DB, no LLM call
# ==============================================================================

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


# ==============================================================================
# GUARDRAILS — block off-topic questions without wasting tokens
# ==============================================================================

ALLOWED_KEYWORDS = [
    # Game mechanics
    "jugador", "fichaj", "fich", "vend", "venta", "compr", "puja", "clausul",
    "mercado", "plantilla", "equipo", "presupuesto", "saldo", "dinero",
    "transacci", "valor", "media", "rendimiento", "puntos", "punt",
    # Strategy
    "estrategia", "recomend", "consejo", "mejor", "peor", "debería",
    "conviene", "merece", "rentable", "profit",
    # Game concepts
    "jornada", "campeonato", "liga", "clasificaci", "posici", "dream team",
    "sofascore", "rating", "tendencia", "evolución", "estadístic",
    "gol", "asistencia", "titular", "suplente", "lesion",
    # Players/teams
    "defensa", "portero", "delantero", "centrocampista", "lateral",
    "barça", "madrid", "atlético", "betis", "sevilla", "sociedad",
    "villarreal", "athletic", "valencia", "celta", "getafe", "osasuna",
    "rayo", "mallorca", "girona", "alavés", "valladolid", "espanyol",
    "leganés", "las palmas",
    # App-related
    "sync", "sincroniz", "app", "futmondo",
]

BLOCKED_PATTERNS = [
    r"(receta|cocin|ingrediente)",
    r"(programa|código|python|javascript|html|css)",
    r"(política|elecciones|gobierno|presidente)",
    r"(crypto|bitcoin|inversión financiera|bolsa|acciones)",
    r"(salud|médico|enfermedad|síntoma|medicamento)",
    r"(relación|amor|cita|novia|novio|pareja)",
    r"(chiste|broma|cuéntame algo gracioso)",
    r"(escribe|redacta|traduce).*(carta|email|ensayo|artículo)",
    r"(quién eres|qué eres|eres una ia|eres un bot)",
    r"(haz|genera|dibuja).*(imagen|foto|dibujo)",
    r"(viaje|hotel|vuelo|restaurante|turismo)",
]

GUARDRAIL_RESPONSE = (
    "🚫 Solo puedo ayudarte con temas relacionados con **Futmondo**: "
    "fichajes, ventas, cláusulas, presupuesto, mercado, estrategia, estadísticas, plantilla...\n\n"
    "Prueba con preguntas como:\n"
    "- ¿A quién debería vender?\n"
    "- ¿Qué jugador me recomiendas fichar?\n"
    "- ¿Cómo va mi clasificación?"
)


def _check_guardrails(message: str) -> Optional[str]:
    """Check if message is off-topic. Returns guardrail response or None if allowed."""
    msg_lower = message.lower().strip()

    # Short messages and follow-up questions are OK (likely in-context)
    if len(msg_lower) < 60:
        return None

    # Check explicit blocked patterns first
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, msg_lower):
            return GUARDRAIL_RESPONSE

    # Check if message contains at least one allowed keyword
    has_allowed = any(keyword in msg_lower for keyword in ALLOWED_KEYWORDS)
    if has_allowed:
        return None

    # If no allowed keyword found, it's likely off-topic
    return GUARDRAIL_RESPONSE


# ==============================================================================
# USAGE TRACKER
# ==============================================================================

class AssistantUsageTracker:
    """Tracks token/request usage to stay within free tier limits."""

    def __init__(self):
        self._ensure_table()

    def _ensure_table(self):
        """Create usage table if it doesn't exist."""
        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = """
                CREATE TABLE IF NOT EXISTS assistant_usage (
                    month TEXT PRIMARY KEY,
                    total_input_tokens INTEGER DEFAULT 0,
                    total_output_tokens INTEGER DEFAULT 0,
                    total_requests INTEGER DEFAULT 0,
                    updated_at TEXT
                )
            """
            cursor.execute(sql)
            conn.commit()

    def can_make_request(self) -> tuple[bool, str]:
        """Check if we're within budget."""
        current_month = datetime.now().strftime("%Y-%m")
        today = date.today().isoformat()

        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            sql = db.adapt_params("SELECT total_input_tokens, total_output_tokens FROM assistant_usage WHERE month = ?")
            cursor.execute(sql, (current_month,))
            row = cursor.fetchone()

            if row:
                total_tokens = (row[0] or 0) + (row[1] or 0)
                if total_tokens >= MONTHLY_TOKEN_LIMIT:
                    return False, "Has alcanzado el límite mensual gratuito del asistente. Se restablece el próximo mes."

            sql_daily = db.adapt_params("SELECT total_requests FROM assistant_usage WHERE month = ?")
            cursor.execute(sql_daily, (today,))
            daily_row = cursor.fetchone()

            if daily_row and (daily_row[0] or 0) >= DAILY_REQUEST_LIMIT:
                return False, f"Has alcanzado el límite diario ({DAILY_REQUEST_LIMIT} preguntas). Inténtalo mañana."

        return True, ""

    def record_usage(self, input_tokens: int, output_tokens: int):
        """Record token usage after each request."""
        current_month = datetime.now().strftime("%Y-%m")
        today = date.today().isoformat()
        now = datetime.now().isoformat()

        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            # Upsert monthly
            cursor.execute(db.adapt_params("SELECT 1 FROM assistant_usage WHERE month = ?"), (current_month,))
            if cursor.fetchone():
                cursor.execute(db.adapt_params(
                    "UPDATE assistant_usage SET total_input_tokens = total_input_tokens + ?, total_output_tokens = total_output_tokens + ?, total_requests = total_requests + 1, updated_at = ? WHERE month = ?"
                ), (input_tokens, output_tokens, now, current_month))
            else:
                cursor.execute(db.adapt_params(
                    "INSERT INTO assistant_usage (month, total_input_tokens, total_output_tokens, total_requests, updated_at) VALUES (?, ?, ?, 1, ?)"
                ), (current_month, input_tokens, output_tokens, now))

            # Upsert daily
            cursor.execute(db.adapt_params("SELECT 1 FROM assistant_usage WHERE month = ?"), (today,))
            if cursor.fetchone():
                cursor.execute(db.adapt_params(
                    "UPDATE assistant_usage SET total_requests = total_requests + 1, updated_at = ? WHERE month = ?"
                ), (now, today))
            else:
                cursor.execute(db.adapt_params(
                    "INSERT INTO assistant_usage (month, total_input_tokens, total_output_tokens, total_requests, updated_at) VALUES (?, 0, 0, 1, ?)"
                ), (today, now))

            conn.commit()

    def get_usage_summary(self) -> dict:
        """Return current month usage."""
        current_month = datetime.now().strftime("%Y-%m")
        today = date.today().isoformat()

        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            cursor.execute(db.adapt_params("SELECT total_input_tokens, total_output_tokens, total_requests FROM assistant_usage WHERE month = ?"), (current_month,))
            row = cursor.fetchone()
            tokens_used = ((row[0] or 0) + (row[1] or 0)) if row else 0
            monthly_requests = (row[2] or 0) if row else 0

            cursor.execute(db.adapt_params("SELECT total_requests FROM assistant_usage WHERE month = ?"), (today,))
            daily_row = cursor.fetchone()
            requests_today = (daily_row[0] or 0) if daily_row else 0

        return {
            "tokens_used": tokens_used,
            "tokens_limit": MONTHLY_TOKEN_LIMIT,
            "pct_used": round((tokens_used / MONTHLY_TOKEN_LIMIT) * 100, 1) if MONTHLY_TOKEN_LIMIT > 0 else 0,
            "requests_today": requests_today,
            "requests_daily_limit": DAILY_REQUEST_LIMIT,
            "monthly_requests": monthly_requests,
        }


# ==============================================================================
# MAIN SERVICE
# ==============================================================================

class AssistantService:
    """Main assistant service — builds context, calls Gemini, tracks usage."""

    def __init__(self):
        self.usage_tracker = AssistantUsageTracker()
        self._client: Optional[genai.Client] = None
        self._groq_client = None

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

    # ==========================================================================
    # USER IDENTITY
    # ==========================================================================

    def _get_user_identity(self, user_id: str, championship_id: str) -> dict:
        """Get user's identity from DB. Always called first."""
        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            # Get user display name from app_users
            cursor.execute(db.adapt_params(
                "SELECT display_name FROM app_users WHERE id = ?"
            ), (user_id,))
            user_row = cursor.fetchone()
            user_name = user_row[0] if user_row else "Usuario"

            # Get championship name and team_id from user_championships
            cursor.execute(db.adapt_params(
                "SELECT name, futmondo_team_id, is_pro FROM user_championships WHERE user_id = ? AND championship_id = ?"
            ), (user_id, championship_id))
            champ_row = cursor.fetchone()

            if champ_row:
                championship_name = champ_row[0] or "Campeonato"
                team_id = champ_row[1] or ""
                is_pro = bool(champ_row[2]) if champ_row[2] is not None else False
            else:
                championship_name = "Campeonato"
                team_id = ""
                is_pro = False

            # Get team name
            team_name = "Desconocido"
            if team_id:
                cursor.execute(db.adapt_params(
                    "SELECT team_name FROM teams WHERE team_id = ?"
                ), (team_id,))
                team_row = cursor.fetchone()
                if team_row:
                    team_name = team_row[0]

        return {
            "user_name": user_name,
            "team_name": team_name,
            "team_id": team_id,
            "championship_name": championship_name,
            "is_pro": is_pro,
        }

    # ==========================================================================
    # FACTUAL ANSWERS — direct from DB, no Gemini call
    # ==========================================================================

    def _try_factual_answer(self, user_id: str, championship_id: str, message: str, identity: dict) -> Optional[str]:
        """Try to answer factual questions directly from DB."""
        msg_lower = message.lower().strip()

        # Only match if it's clearly a factual/informational question, not strategy
        # Strategy indicators that should bypass factual answers
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

    def _factual_balance(self, user_id: str, championship_id: str, identity: dict) -> Optional[str]:
        """Direct answer: user's balance/budget."""
        team_id = identity["team_id"]
        if not team_id:
            return None

        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            cursor.execute(db.adapt_params(
                "SELECT COALESCE(SUM(price), 0) FROM transactions WHERE championship_id = ? AND buyer_team_id = ?"
            ), (championship_id, team_id))
            total_spent = cursor.fetchone()[0] or 0

            cursor.execute(db.adapt_params(
                "SELECT COALESCE(SUM(price), 0) FROM transactions WHERE championship_id = ? AND seller_team_id = ?"
            ), (championship_id, team_id))
            total_income = cursor.fetchone()[0] or 0

            cursor.execute(db.adapt_params(
                "SELECT initial_budget FROM user_championships WHERE user_id = ? AND championship_id = ?"
            ), (user_id, championship_id))
            config_row = cursor.fetchone()
            initial_budget = config_row[0] if config_row else 200_000_000

            # Prizes
            cursor.execute(db.adapt_params(
                "SELECT COALESCE(SUM(ranking_prize + mvp_prize + COALESCE(points_prize, 0) + COALESCE(dream_team_prize, 0)), 0) FROM team_prizes WHERE championship_id = ? AND team_id = ?"
            ), (championship_id, team_id))
            prizes = cursor.fetchone()[0] or 0

            balance = initial_budget - total_spent + total_income + prizes

            # Team value from players table via player_championship_stats
            cursor.execute(db.adapt_params(
                "SELECT COALESCE(SUM(p.value), 0) FROM player_championship_stats pcs JOIN players p ON pcs.player_id = p.player_id WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?"
            ), (championship_id, team_id))
            team_value = cursor.fetchone()[0] or 0

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
        """Direct answer: user's current roster."""
        team_id = identity["team_id"]
        if not team_id:
            return None

        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(db.adapt_params("""
                SELECT p.player_id, p.name, p.role, p.value, pcs.average_overall, pcs.average_last_five,
                       sc.rating
                FROM player_championship_stats pcs
                JOIN players p ON pcs.player_id = p.player_id
                LEFT JOIN sofascore_cache sc ON LOWER(p.name) = LOWER(sc.player_name)
                WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?
                ORDER BY p.value DESC
            """), (championship_id, team_id))
            rows = cursor.fetchall()

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
        lines = [f"📋 **Tu plantilla ({identity['team_name']}) — {len(unique_rows)} jugadores** (Valor total: {total_value / 1_000_000:.1f}M€)\n"]

        for pid, name, role, value, avg, avg5, sofascore in unique_rows:
            value_m = f"{(value or 0) / 1_000_000:.1f}M"
            avg_str = f"Media {avg:.1f}" if avg else "Sin media"
            avg5_str = f"Últ5: {avg5:.1f}" if avg5 else ""
            ss_str = f"SS {sofascore:.1f}" if sofascore else ""
            parts = [f"**{name}**", role or "", value_m, avg_str, avg5_str, ss_str]
            lines.append("- " + " | ".join(p for p in parts if p))

        return "\n".join(lines)

    def _factual_standings(self, user_id: str, championship_id: str, identity: dict) -> Optional[str]:
        """Direct answer: current standings."""
        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            # Get latest matchday
            cursor.execute(db.adapt_params(
                "SELECT MAX(matchday) FROM team_standings WHERE championship_id = ?"
            ), (championship_id,))
            max_md_row = cursor.fetchone()
            if not max_md_row or not max_md_row[0]:
                return None
            max_matchday = max_md_row[0]

            cursor.execute(db.adapt_params("""
                SELECT t.team_name, ts.points, ts.position
                FROM team_standings ts
                JOIN teams t ON ts.team_id = t.team_id
                WHERE ts.championship_id = ? AND ts.matchday = ?
                ORDER BY ts.position ASC
            """), (championship_id, max_matchday))
            rows = cursor.fetchall()

        if not rows:
            return None

        lines = [f"🏆 **Clasificación ({identity['championship_name']}) — Jornada {max_matchday}:**\n"]
        for name, points, pos in rows:
            marker = " ← **TÚ**" if name == identity["team_name"] else ""
            lines.append(f"**#{pos}** {name} — {points or 0} pts{marker}")

        return "\n".join(lines)

    def _factual_team_value(self, user_id: str, championship_id: str, identity: dict) -> Optional[str]:
        """Direct answer: team value."""
        team_id = identity["team_id"]
        if not team_id:
            return None

        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(db.adapt_params(
                "SELECT COALESCE(SUM(p.value), 0), COUNT(*) FROM player_championship_stats pcs JOIN players p ON pcs.player_id = p.player_id WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?"
            ), (championship_id, team_id))
            row = cursor.fetchone()
            team_value = row[0] or 0
            player_count = row[1] or 0

        if player_count == 0:
            return "No tienes jugadores en tu plantilla."

        avg_value = team_value / player_count
        return (
            f"📊 **Valor de tu plantilla ({identity['team_name']}):**\n\n"
            f"- **Valor total:** {team_value / 1_000_000:.1f}M€\n"
            f"- Jugadores: {player_count}\n"
            f"- Media por jugador: {avg_value / 1_000_000:.1f}M€"
        )

    # ==========================================================================
    # MAIN ASK METHOD
    # ==========================================================================

    async def ask(self, user_id: str, championship_id: str, message: str, history: list[dict], request=None) -> dict:
        """Process a user question and return AI response.

        Flow:
        1. Guardrails — reject off-topic (no tokens)
        2. Get user identity (always)
        3. Try factual answer from DB (no tokens)
        4. If not factual → call Gemini with context
        """
        # 1. Guardrails
        guardrail_response = _check_guardrails(message)
        if guardrail_response:
            return {"response": guardrail_response, "context_used": ["guardrail"]}

        # 2. User identity
        identity = self._get_user_identity(user_id, championship_id)

        # 3. Factual answer (FREE)
        factual_answer = self._try_factual_answer(user_id, championship_id, message, identity)
        if factual_answer:
            logger.info(f"Factual answer for user {user_id} — no Gemini call")
            return {"response": factual_answer, "context_used": ["direct_db"]}

        # 4. Needs Gemini reasoning
        allowed, reason = self.usage_tracker.can_make_request()
        if not allowed:
            return {"response": f"⚠️ {reason}", "context_used": []}

        # Build context — skip full re-injection on follow-ups to save tokens
        # But if the follow-up asks about a new topic (market, lineup, etc), inject that context
        is_followup = len(history) >= 2 and len(message) < 120
        needs_full_context_keywords = ["fich", "compr", "mercado", "once", "aline", "formaci",
                                        "jornada", "claus", "libre", "agente", "clasif"]
        needs_full = any(k in message.lower() for k in needs_full_context_keywords)

        if is_followup and not needs_full:
            # Simple follow-up: only budget context
            db = get_db()
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                context = self._ctx_budget(cursor, db, user_id, championship_id, identity["team_id"]) or ""
            context_types = ["budget_only"]
        else:
            context, context_types = self._build_context(user_id, championship_id, message, identity, request)

        # Build prompt
        system = SYSTEM_PROMPT.format(
            user_name=identity["user_name"],
            team_name=identity["team_name"],
            championship_name=identity["championship_name"],
            mode="PRO (formaciones extra disponibles)" if identity.get("is_pro") else "Clásico",
            context=context,
        )

        # Build Gemini messages
        contents = []
        contents.append({"role": "user", "parts": [{"text": system}]})
        contents.append({"role": "model", "parts": [{"text": "Listo, tengo el contexto. ¿En qué te ayudo?"}]})

        for msg in history[-4:]:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})

        contents.append({"role": "user", "parts": [{"text": message}]})

        # Call LLM with provider fallback: Groq (fast) → Gemini
        # 1. Try Groq first (faster, more reliable)
        if self.groq_client:
            try:
                # Build OpenAI-format messages for Groq
                messages = []
                messages.append({"role": "system", "content": system})
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
                answer = groq_response.choices[0].message.content or "No pude generar una respuesta."

                input_tokens = getattr(groq_response.usage, 'prompt_tokens', 0) or 0
                output_tokens = getattr(groq_response.usage, 'completion_tokens', 0) or 0
                self.usage_tracker.record_usage(input_tokens, output_tokens)

                logger.info(f"Response from Groq/gpt-oss-120b ({input_tokens}+{output_tokens} tokens)")
                return {"response": answer, "context_used": context_types}

            except Exception as e:
                logger.warning(f"Groq error: {str(e)[:80]}. Falling back to Gemini...")

        # 2. Fallback to Gemini
        gemini_models = ["gemini-3.6-flash", "gemini-3.5-flash"]

        for model_name in gemini_models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config={"max_output_tokens": 2048},
                )
                answer = response.text or "No pude generar una respuesta."

                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0) or 0
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0) or 0
                self.usage_tracker.record_usage(input_tokens, output_tokens)

                logger.info(f"Response from Gemini/{model_name} ({input_tokens}+{output_tokens} tokens)")
                return {"response": answer, "context_used": context_types}

            except Exception as e:
                error_msg = str(e)
                is_rate_limit = "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg
                is_not_found = "404" in error_msg or "NOT_FOUND" in error_msg
                is_server_error = "503" in error_msg or "504" in error_msg or "DEADLINE_EXCEEDED" in error_msg or "UNAVAILABLE" in error_msg

                if is_rate_limit or is_not_found or is_server_error:
                    logger.warning(f"Gemini/{model_name} unavailable: {error_msg[:80]}. Trying next...")
                    continue
                else:
                    logger.error(f"Gemini API error ({model_name}): {e}")
                    break  # Non-recoverable error, try Groq

        # All providers exhausted
        return {"response": "⚠️ Todos los modelos están saturados. Espera un momento e inténtalo de nuevo.", "context_used": []}

    # ==========================================================================
    # CONTEXT BUILDER (for Gemini calls)
    # ==========================================================================

    def _build_context(self, user_id: str, championship_id: str, message: str, identity: dict, request=None) -> tuple[str, list[str]]:
        """Build relevant context from DB based on the user's question."""
        context_parts = []
        context_types = []
        msg_lower = message.lower()
        team_id = identity["team_id"]

        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            # --- Always: user's roster ---
            roster_ctx = self._ctx_roster(cursor, db, championship_id, team_id, identity["team_name"])
            if roster_ctx:
                context_parts.append(roster_ctx)
                context_types.append("roster")

            # --- Always: budget ---
            budget_ctx = self._ctx_budget(cursor, db, user_id, championship_id, team_id)
            if budget_ctx:
                context_parts.append(budget_ctx)
                context_types.append("budget")

            # --- Market (if asking about signings) — fetches LIVE from Futmondo API ---
            market_keywords = ["fich", "compr", "mercado", "puj", "fichar", "comprar"]
            if any(k in msg_lower for k in market_keywords):
                market_ctx = self._ctx_market_live(request, championship_id)
                if market_ctx:
                    context_parts.append(market_ctx)
                    context_types.append("market")

            # --- Free agents (if asking about free agents specifically) ---
            free_keywords = ["libre", "agente", "free"]
            if any(k in msg_lower for k in free_keywords):
                free_ctx = self._ctx_free_agents(cursor, db, championship_id)
                if free_ctx:
                    context_parts.append(free_ctx)
                    context_types.append("free_agents")

            # --- Clausulables ---
            clause_keywords = ["claus", "clausul"]
            if any(k in msg_lower for k in clause_keywords):
                clause_ctx = self._ctx_clausulables(cursor, db, championship_id)
                if clause_ctx:
                    context_parts.append(clause_ctx)
                    context_types.append("clausulable")

            # --- Standings ---
            strategy_keywords = ["clasif", "posición", "puesto", "estrategia", "rival", "punt"]
            if any(k in msg_lower for k in strategy_keywords):
                standings_ctx = self._ctx_standings(cursor, db, championship_id)
                if standings_ctx:
                    context_parts.append(standings_ctx)
                    context_types.append("standings")

            # --- Transactions ---
            sell_keywords = ["vend", "venta", "transacc", "historial"]
            if any(k in msg_lower for k in sell_keywords):
                tx_ctx = self._ctx_transactions(cursor, db, championship_id, team_id)
                if tx_ctx:
                    context_parts.append(tx_ctx)
                    context_types.append("transactions")

            # --- Matches/Odds (if asking about lineup, next matchday, rivals) ---
            lineup_keywords = ["once", "aline", "formaci", "jornada", "rival", "partido", "cuota", "poner", "pongo"]
            if any(k in msg_lower for k in lineup_keywords):
                matches_ctx = self._ctx_next_matches(cursor, db, championship_id, team_id)
                if matches_ctx:
                    context_parts.append(matches_ctx)
                    context_types.append("matches")

        context = "\n\n".join(context_parts) if context_parts else "No hay datos disponibles para este campeonato."
        return context, context_types

    def _ctx_roster(self, cursor, db, championship_id: str, team_id: str, team_name: str) -> str:
        """Build roster context."""
        if not team_id:
            return ""

        cursor.execute(db.adapt_params("""
            SELECT p.player_id, p.name, p.role, p.value, pcs.average_overall, pcs.average_last_five,
                   sc.rating, sc.matches_started
            FROM player_championship_stats pcs
            JOIN players p ON pcs.player_id = p.player_id
            LEFT JOIN sofascore_cache sc ON LOWER(p.name) = LOWER(sc.player_name)
            WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?
            ORDER BY p.value DESC
        """), (championship_id, team_id))
        rows = cursor.fetchall()

        if not rows:
            return ""

        # Deduplicate: keep first row per player_id (highest sofascore rating)
        seen = {}
        for row in rows:
            pid = row[0]
            if pid not in seen or (row[6] or 0) > (seen[pid][6] or 0):
                seen[pid] = row
        unique_rows = list(seen.values())
        unique_rows.sort(key=lambda r: r[3] or 0, reverse=True)  # sort by value desc

        lines = [f"MI PLANTILLA ({team_name}) — {len(unique_rows)} jugadores:"]
        for pid, name, role, value, avg, avg5, rating, started in unique_rows:
            value_m = f"{(value or 0) / 1_000_000:.1f}M"
            avg_str = f"{avg:.1f}" if avg else "-"
            avg5_str = f"{avg5:.1f}" if avg5 else "-"
            ss_str = f"{rating:.1f}" if rating else "-"
            started_str = str(started or 0)
            lines.append(f"{name},{role or '-'},{value_m},avg:{avg_str},últ5:{avg5_str},ss:{ss_str},tit:{started_str}")

        return "\n".join(lines)

    def _ctx_budget(self, cursor, db, user_id: str, championship_id: str, team_id: str) -> str:
        """Build budget context."""
        if not team_id:
            return ""

        cursor.execute(db.adapt_params(
            "SELECT COALESCE(SUM(price), 0) FROM transactions WHERE championship_id = ? AND buyer_team_id = ?"
        ), (championship_id, team_id))
        total_spent = cursor.fetchone()[0] or 0

        cursor.execute(db.adapt_params(
            "SELECT COALESCE(SUM(price), 0) FROM transactions WHERE championship_id = ? AND seller_team_id = ?"
        ), (championship_id, team_id))
        total_income = cursor.fetchone()[0] or 0

        cursor.execute(db.adapt_params(
            "SELECT initial_budget FROM user_championships WHERE user_id = ? AND championship_id = ?"
        ), (user_id, championship_id))
        config_row = cursor.fetchone()
        initial_budget = config_row[0] if config_row else 200_000_000

        # Prizes
        cursor.execute(db.adapt_params(
            "SELECT COALESCE(SUM(ranking_prize + mvp_prize + COALESCE(points_prize, 0) + COALESCE(dream_team_prize, 0)), 0) FROM team_prizes WHERE championship_id = ? AND team_id = ?"
        ), (championship_id, team_id))
        prizes = cursor.fetchone()[0] or 0

        balance = initial_budget - total_spent + total_income + prizes

        cursor.execute(db.adapt_params(
            "SELECT COALESCE(SUM(p.value), 0) FROM player_championship_stats pcs JOIN players p ON pcs.player_id = p.player_id WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?"
        ), (championship_id, team_id))
        team_value = cursor.fetchone()[0] or 0

        return (
            f"PRESUPUESTO: saldo={balance / 1_000_000:.1f}M, gastado={total_spent / 1_000_000:.1f}M, "
            f"ingresado={total_income / 1_000_000:.1f}M, premios={prizes / 1_000_000:.1f}M, "
            f"valor_plantilla={team_value / 1_000_000:.1f}M, patrimonio={(balance + team_value) / 1_000_000:.1f}M"
        )

    def _ctx_market_live(self, request, championship_id: str) -> str:
        """Get TODAY's market from DB only. No live API calls."""
        return self._ctx_market_from_db(championship_id)
    def _ctx_market_from_db(self, championship_id: str) -> str:
        """Read today's market from market_today table (computer players only)."""
        today = date.today().isoformat()
        db = get_db()
        try:
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                cursor.execute(db.adapt_params(
                    "SELECT player_name, position, value, average, matches_played FROM market_today WHERE championship_id = ? AND market_date = ? AND is_computer = TRUE"
                ), (championship_id, today))
                rows = cursor.fetchall()

            if not rows:
                return ""

            lines = [f"MERCADO HOY ({len(rows)} del computer):"]
            for name, pos, value, avg, matches in rows:
                value_m = f"{(value or 0) / 1_000_000:.1f}M"
                avg_str = f"{avg:.1f}" if avg else "-"
                lines.append(f"{name},{pos or '-'},{value_m},avg:{avg_str},pj:{matches or 0}")

            return "\n".join(lines)
        except Exception:
            return ""  # Table might not exist yet

    def _save_market_to_db(self, championship_id: str, players: list):
        """Save today's market to DB for caching (used by both assistant and market page)."""
        today = date.today().isoformat()
        db = get_db()
        try:
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                # Create table if needed
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS market_today (
                        id SERIAL PRIMARY KEY,
                        championship_id TEXT NOT NULL,
                        market_date TEXT NOT NULL,
                        player_id TEXT,
                        player_name TEXT,
                        slug TEXT,
                        position TEXT,
                        position2 TEXT,
                        team TEXT,
                        team_logo TEXT,
                        value INTEGER,
                        market_price INTEGER,
                        change INTEGER DEFAULT 0,
                        average REAL,
                        home_average REAL,
                        away_average REAL,
                        matches_played INTEGER,
                        points INTEGER DEFAULT 0,
                        photo TEXT,
                        expiration TEXT,
                        is_computer BOOLEAN DEFAULT TRUE,
                        raw_json TEXT
                    )
                """)
                # Clear old data for this championship today
                cursor.execute(db.adapt_params(
                    "DELETE FROM market_today WHERE championship_id = ? AND market_date = ?"
                ), (championship_id, today))

                # Insert today's market
                import json as json_mod
                for p in players:
                    avg_data = p.get('average', {})
                    avg = avg_data.get('average', 0) if isinstance(avg_data, dict) else 0
                    home_avg = avg_data.get('homeAverage') if isinstance(avg_data, dict) else None
                    away_avg = avg_data.get('awayAverage') if isinstance(avg_data, dict) else None
                    matches = avg_data.get('matches', 0) if isinstance(avg_data, dict) else 0

                    # SECURITY: 'bid' is the requesting user's private bid. This cache
                    # is shared per (championship, date), so strip it before storing to
                    # avoid leaking one user's bids to another. Per-user bids are fetched
                    # live in the market endpoint.
                    p_cached = {k: v for k, v in p.items() if k != 'bid'}

                    cursor.execute(db.adapt_params("""
                        INSERT INTO market_today (championship_id, market_date, player_id, player_name, slug,
                            position, position2, team, team_logo, value, market_price, change,
                            average, home_average, away_average, matches_played, points, photo, expiration, is_computer, raw_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """), (
                        championship_id, today,
                        p.get('id', ''), p.get('name', ''), p.get('slug', ''),
                        p.get('role', ''), p.get('role2', ''),
                        p.get('team', ''), p.get('logo', ''),
                        p.get('value', 0), p.get('price', p.get('value', 0)),
                        p.get('change', 0),
                        avg,
                        float(home_avg) if home_avg and home_avg != 'NaN' else None,
                        float(away_avg) if away_avg and away_avg != 'NaN' else None,
                        matches, p.get('points', 0),
                        p.get('photo', ''), p.get('expirationDate', ''),
                        p.get('computer', False),
                        json_mod.dumps(p_cached, ensure_ascii=False),
                    ))

                conn.commit()
                logger.info(f"Saved {len(players)} market players to DB for {championship_id}")
        except Exception as e:
            logger.warning(f"Could not save market to DB: {e}")

    def _format_market_context(self, computer_players: list) -> str:
        """Format market players as context string."""
        lines = [f"MERCADO HOY ({len(computer_players)} del computer):"]
        for p in computer_players:
            name = p.get('name', '?')
            role = p.get('role', '-')
            value = p.get('value', 0)
            avg_data = p.get('average', {})
            avg = avg_data.get('average', 0) if isinstance(avg_data, dict) else 0
            matches = avg_data.get('matches', 0) if isinstance(avg_data, dict) else 0
            value_m = f"{value / 1_000_000:.1f}M"
            avg_str = f"{avg:.1f}" if avg else "-"
            lines.append(f"{name},{role},{value_m},avg:{avg_str},pj:{matches}")
        return "\n".join(lines)

    def _ctx_free_agents(self, cursor, db, championship_id: str) -> str:
        """Get top free agents from DB."""
        cursor.execute(db.adapt_params("""
            SELECT p.name, p.role, p.value, pcs.average_overall, pcs.average_last_five,
                   sc.rating
            FROM player_championship_stats pcs
            JOIN players p ON pcs.player_id = p.player_id
            LEFT JOIN sofascore_cache sc ON LOWER(p.name) = LOWER(sc.player_name)
            WHERE pcs.championship_id = ? AND (pcs.owner_team_id IS NULL OR pcs.owner_team_name = 'Free Agent')
            AND pcs.average_overall > 0
            ORDER BY pcs.average_overall DESC
            LIMIT 30
        """), (championship_id,))
        rows = cursor.fetchall()

        if not rows:
            return ""

        lines = ["AGENTES LIBRES (top 30):"]
        for name, role, value, avg, avg5, rating in rows:
            value_m = f"{(value or 0) / 1_000_000:.1f}M"
            avg_str = f"{avg:.1f}" if avg else "-"
            avg5_str = f"{avg5:.1f}" if avg5 else "-"
            ss_str = f"{rating:.1f}" if rating else "-"
            lines.append(f"{name},{role or '-'},{value_m},avg:{avg_str},últ5:{avg5_str},ss:{ss_str}")

        return "\n".join(lines)

    def _ctx_clausulables(self, cursor, db, championship_id: str) -> str:
        """Build clausulables context."""
        cursor.execute(db.adapt_params("""
            SELECT p.name, p.role, p.value, pcs.average_overall, pcs.clause_price,
                   pcs.owner_team_name, sc.rating
            FROM player_championship_stats pcs
            JOIN players p ON pcs.player_id = p.player_id
            LEFT JOIN sofascore_cache sc ON LOWER(p.name) = LOWER(sc.player_name)
            WHERE pcs.championship_id = ? AND pcs.clause_price > 0
            AND pcs.owner_team_id IS NOT NULL AND pcs.owner_team_name != 'Free Agent'
            AND pcs.average_overall > 0
            ORDER BY (pcs.average_overall / (CAST(pcs.clause_price AS FLOAT) / 1000000.0)) DESC
            LIMIT 15
        """), (championship_id,))
        rows = cursor.fetchall()

        if not rows:
            return ""

        lines = ["CLAUSULABLES (top 15 por ratio media/cláusula):"]
        for name, role, value, avg, clause, owner, rating in rows:
            clause_m = f"{(clause or 0) / 1_000_000:.1f}M"
            avg_str = f"{avg:.1f}" if avg else "-"
            ss_str = f"{rating:.1f}" if rating else "-"
            lines.append(f"{name},{role or '-'},dueño:{owner or '-'},avg:{avg_str},cláusula:{clause_m},ss:{ss_str}")

        return "\n".join(lines)

    def _ctx_standings(self, cursor, db, championship_id: str) -> str:
        """Build standings context."""
        cursor.execute(db.adapt_params(
            "SELECT MAX(matchday) FROM team_standings WHERE championship_id = ?"
        ), (championship_id,))
        max_row = cursor.fetchone()
        if not max_row or not max_row[0]:
            return ""
        max_matchday = max_row[0]

        cursor.execute(db.adapt_params("""
            SELECT t.team_name, ts.points, ts.position
            FROM team_standings ts
            JOIN teams t ON ts.team_id = t.team_id
            WHERE ts.championship_id = ? AND ts.matchday = ?
            ORDER BY ts.position ASC
        """), (championship_id, max_matchday))
        rows = cursor.fetchall()

        if not rows:
            return ""

        lines = [f"CLASIFICACIÓN (J{max_matchday}):"]
        for name, points, pos in rows:
            lines.append(f"#{pos} {name} {points or 0}pts")

        return "\n".join(lines)

    def _ctx_transactions(self, cursor, db, championship_id: str, team_id: str) -> str:
        """Build transactions context."""
        if not team_id:
            return ""

        cursor.execute(db.adapt_params("""
            SELECT p.name, t.price, t.transaction_date,
                   CASE WHEN t.buyer_team_id = ? THEN 'COMPRA' ELSE 'VENTA' END as type
            FROM transactions t
            JOIN players p ON t.player_id = p.player_id
            WHERE t.championship_id = ? AND (t.buyer_team_id = ? OR t.seller_team_id = ?)
            ORDER BY t.transaction_date DESC
            LIMIT 15
        """), (team_id, championship_id, team_id, team_id))
        rows = cursor.fetchall()

        if not rows:
            return ""

        lines = ["TRANSACCIONES RECIENTES:"]
        for name, price, tx_date, tx_type in rows:
            price_m = f"{(price or 0) / 1_000_000:.1f}M"
            lines.append(f"{tx_type}:{name or '?'},{price_m},{tx_date or '-'}")

        return "\n".join(lines)

    def _ctx_next_matches(self, cursor, db, championship_id: str, team_id: str) -> str:
        """Build next matchday context — matches with odds + which players play where + formations."""
        if not team_id:
            return ""

        parts = []

        # Get next matchday (highest matchday in match_odds)
        cursor.execute(db.adapt_params(
            "SELECT MAX(matchday) FROM match_odds WHERE championship_id = ?"
        ), (championship_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            return ""
        next_matchday = row[0]

        # Get all matches for next matchday
        cursor.execute(db.adapt_params("""
            SELECT home_team_id, home_team_name, away_team_id, away_team_name,
                   odds_home, odds_draw, odds_away, match_date
            FROM match_odds
            WHERE championship_id = ? AND matchday = ?
            ORDER BY match_date ASC
        """), (championship_id, next_matchday))
        matches = cursor.fetchall()

        if not matches:
            return ""

        # Get my players' real teams
        cursor.execute(db.adapt_params("""
            SELECT p.name, p.real_team_id, p.role
            FROM player_championship_stats pcs
            JOIN players p ON pcs.player_id = p.player_id
            WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?
        """), (championship_id, team_id))
        my_players = cursor.fetchall()

        # Map: real_team_id → list of my players
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

        # Get available formations from Futmondo API
        formations_ctx = self._ctx_formations(championship_id, team_id)
        if formations_ctx:
            parts.append(formations_ctx)

        return "\n\n".join(parts)

    def _ctx_formations(self, championship_id: str, team_id: str) -> str:
        """Get available formations — hardcoded since they never change."""
        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(db.adapt_params(
                "SELECT is_pro FROM user_championships WHERE championship_id = ? LIMIT 1"
            ), (championship_id,))
            row = cursor.fetchone()
            is_pro = bool(row[0]) if row and row[0] else False

        standard = ["4-4-2", "4-3-3", "4-5-1", "3-4-3", "3-5-2", "5-4-1", "5-3-2"]
        pro = ["3-6-1", "4-2-4", "3-3-4", "4-6-0", "5-2-3"]

        lines = ["📐 FORMACIONES DISPONIBLES:"]
        lines.append(f"Estándar: {', '.join(standard)}")
        if is_pro:
            lines.append(f"Pro (extra): {', '.join(pro)}")

        return "\n".join(lines)


# Singleton
_assistant_service: Optional[AssistantService] = None


def get_assistant_service() -> AssistantService:
    """Get or create singleton assistant service."""
    global _assistant_service
    if _assistant_service is None:
        _assistant_service = AssistantService()
    return _assistant_service
