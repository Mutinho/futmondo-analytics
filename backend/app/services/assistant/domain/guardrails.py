"""Pure off-topic guardrail for the assistant (BR1.1-BR1.3).

This is the domain layer: regex/strings only, no DB, no network, no framework.
The behavior is a verbatim relocation of the former ``_check_guardrails`` and its
``ALLOWED_KEYWORDS`` / ``BLOCKED_PATTERNS`` / ``GUARDRAIL_RESPONSE`` module
constants from ``assistant_service.py`` — it must return the exact same result
for every input so the characterization tests stay green (BR1.1, BR1.2).

``_check_guardrails`` returns ``None`` when the message may proceed (short,
likely in-context, or containing at least one allowed keyword) and the fixed
``GUARDRAIL_RESPONSE`` string when the message is off-topic and must be blocked
before any factual/LLM work (BR1.1).
"""

import re
from typing import Optional

# --- Allowed keywords: any presence marks the message as on-topic ------------
ALLOWED_KEYWORDS = [
    # Game mechanics
    "jugador",
    "fichaj",
    "fich",
    "vend",
    "venta",
    "compr",
    "puja",
    "clausul",
    "mercado",
    "plantilla",
    "equipo",
    "presupuesto",
    "saldo",
    "dinero",
    "transacci",
    "valor",
    "media",
    "rendimiento",
    "puntos",
    "punt",
    # Strategy
    "estrategia",
    "recomend",
    "consejo",
    "mejor",
    "peor",
    "debería",
    "conviene",
    "merece",
    "rentable",
    "profit",
    # Game concepts
    "jornada",
    "campeonato",
    "liga",
    "clasificaci",
    "posici",
    "dream team",
    "sofascore",
    "rating",
    "tendencia",
    "evolución",
    "estadístic",
    "gol",
    "asistencia",
    "titular",
    "suplente",
    "lesion",
    # Players/teams
    "defensa",
    "portero",
    "delantero",
    "centrocampista",
    "lateral",
    "barça",
    "madrid",
    "atlético",
    "betis",
    "sevilla",
    "sociedad",
    "villarreal",
    "athletic",
    "valencia",
    "celta",
    "getafe",
    "osasuna",
    "rayo",
    "mallorca",
    "girona",
    "alavés",
    "valladolid",
    "espanyol",
    "leganés",
    "las palmas",
    # App-related
    "sync",
    "sincroniz",
    "app",
    "futmondo",
]

# --- Blocked patterns: explicit off-topic categories -------------------------
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

# --- The fixed user-facing response for a blocked/off-topic message ----------
GUARDRAIL_RESPONSE = (
    "🚫 Solo puedo ayudarte con temas relacionados con **Futmondo**: "
    "fichajes, ventas, cláusulas, presupuesto, mercado, estrategia, estadísticas, plantilla...\n\n"
    "Prueba con preguntas como:\n"
    "- ¿A quién debería vender?\n"
    "- ¿Qué jugador me recomiendas fichar?\n"
    "- ¿Cómo va mi clasificación?"
)


def check_guardrails(message: str) -> Optional[str]:
    """Check if a message is off-topic.

    Returns the guardrail response string when the message must be blocked, or
    ``None`` when it may proceed. Behavior is preserved verbatim from the former
    god-file (BR1.1-BR1.3):

    - Messages shorter than 60 characters are treated as in-context follow-ups
      and allowed.
    - An explicit blocked pattern short-circuits to the guardrail response.
    - Otherwise, the presence of at least one allowed keyword permits the
      message; its absence blocks it.
    """
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
