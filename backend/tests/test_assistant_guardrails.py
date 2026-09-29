"""Characterization tests for the assistant off-topic guardrail (BR1.1-BR1.3).

These freeze the CURRENT observable behavior of the guardrail seam BEFORE it is
extracted to ``assistant/domain/guardrails.py``. After extraction the exact same
tests must stay green against the extracted, pure module.

The guardrail is a pure function: given a user message it returns either
``None`` (the message is allowed / likely in-context) or the fixed
``GUARDRAIL_RESPONSE`` string (off-topic, blocked before any factual/LLM path).

BR1.1 — a blocked/off-topic message returns the guardrail response (no factual,
         no LLM).
BR1.2 — an allowed message returns ``None`` (the flow continues).
BR1.3 — the guardrail is pure: no DB, no network, no side effects.
"""

from app.services.assistant_service import (
    GUARDRAIL_RESPONSE,
    _check_guardrails,
)

# A long off-topic message (>= 60 chars) that matches no allowed keyword and no
# blocked pattern: it is rejected because no allowed keyword is present.
_LONG_OFFTOPIC = (
    "Necesito que me expliques con mucho detalle la historia completa del "
    "arte renacentista italiano durante todo el siglo quince por favor"
)

# A long message that hits an explicit BLOCKED_PATTERN (recipe/cooking).
_LONG_BLOCKED = (
    "Oye, dame por favor una receta completa con todos los ingredientes para "
    "cocinar una paella valenciana tradicional para ocho personas este domingo"
)

# A long ON-topic message (>= 60 chars) that contains an allowed keyword.
_LONG_ALLOWED = (
    "Estoy pensando en mi estrategia de mercado para la proxima jornada: "
    "necesito decidir a que jugador fichar y cual vender de mi plantilla"
)


# --- BR1.1: blocked / off-topic returns the guardrail response ---------------


def test_blocked_pattern_returns_guardrail_response():
    """A long message matching a blocked pattern returns GUARDRAIL_RESPONSE (BR1.1)."""
    assert _check_guardrails(_LONG_BLOCKED) == GUARDRAIL_RESPONSE


def test_long_offtopic_without_allowed_keyword_returns_guardrail_response():
    """A long message with no allowed keyword is treated as off-topic (BR1.1)."""
    assert _check_guardrails(_LONG_OFFTOPIC) == GUARDRAIL_RESPONSE


# --- BR1.2: allowed message returns None (flow continues) --------------------


def test_short_message_is_allowed():
    """Short messages (< 60 chars) are treated as in-context and allowed (BR1.2)."""
    assert _check_guardrails("¿A quién debería vender?") is None


def test_long_message_with_allowed_keyword_is_allowed():
    """A long on-topic message with an allowed keyword continues the flow (BR1.2)."""
    assert _check_guardrails(_LONG_ALLOWED) is None


# --- BR1.3: purity — no I/O, deterministic, side-effect free -----------------


def test_guardrail_is_pure_and_deterministic():
    """The guardrail returns the same result on repeated calls with no side effects (BR1.3).

    If the seam performed any DB/network I/O, importing and calling it here
    (with no ``fake_db`` and no network) would fail; a stable, repeatable result
    demonstrates the seam is pure.
    """
    first = _check_guardrails(_LONG_OFFTOPIC)
    second = _check_guardrails(_LONG_OFFTOPIC)
    assert first == second == GUARDRAIL_RESPONSE
    # Allowed path is equally stable.
    assert _check_guardrails(_LONG_ALLOWED) is None
