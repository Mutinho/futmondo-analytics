"""
Configuration file for Futmondo API
Uses environment variables with fallback to default values
"""

import os

from dotenv import load_dotenv
load_dotenv()

# Futmondo API Credentials (optional — users authenticate individually via /auth/login)
FUTMONDO_EMAIL = os.getenv("FUTMONDO_EMAIL", "")
FUTMONDO_PASSWORD = os.getenv("FUTMONDO_PASSWORD", "")

# API Configuration
BASE_URL = os.getenv("BASE_URL", "https://api.futmondo.com")
# FR14.2: no hardcoded championship/league identifiers. The multi-user flow
# supplies the real championship_id per request from the logged-in user; these
# are env-provided fallbacks that default to empty (no legacy literal). An empty
# value means "not configured" — callers that rely on a default without env
# configuration get an explicit empty value, never a stale hardcoded ID.
CHAMPIONSHIP_ID = os.getenv("CHAMPIONSHIP_ID", "")
LEAGUE_ID = os.getenv("LEAGUE_ID", "")

# Analysis Settings
MAX_PLAYERS_TO_ANALYZE = int(os.getenv("MAX_PLAYERS_TO_ANALYZE", "600"))
MIN_TRANSACTIONS_FOR_ANALYSIS = int(os.getenv("MIN_TRANSACTIONS_FOR_ANALYSIS", "1"))
REQUEST_DELAY_SECONDS = float(os.getenv("REQUEST_DELAY_SECONDS", "0.1"))

# Output Settings
TOP_PROFITABLE_PLAYERS = int(os.getenv("TOP_PROFITABLE_PLAYERS", "20"))
SHOW_DETAILED_ANALYSIS = os.getenv("SHOW_DETAILED_ANALYSIS", "True").lower() == "true"

# Database and Caching Settings
CACHE_DURATION_HOURS = int(os.getenv("CACHE_DURATION_HOURS", "24"))
# Local cache file path (NOT a database engine selector). Consumed by
# photo_service and data_manager_v2 as a local cache location. Its full cleanup
# is registered debt tied to the god-file refactor intent.
DATABASE_PATH = os.getenv("DATABASE_PATH", "futmondo_data.db")

# Production database: PostgreSQL/Neon via DATABASE_URL (the only supported
# engine after FR14.1). Provisioned as a Fly.io/Neon secret in production.
DATABASE_URL = os.getenv("DATABASE_URL", "")

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))



# JWT Authentication
# Only the web API service issues/validates JWTs. The cron worker
# (futmondo-cron) imports this module too but never touches JWT, so we don't
# require the secret there — otherwise the whole sync would fail to start.
#
# NFR1.1 (endurecimiento afirmado): el servicio WEB debe fallar SIEMPRE en el
# arranque si JWT_SECRET falta O es igual al valor por defecto inseguro,
# independientemente de FLY_APP_NAME. El worker cron (identificado por "cron" en
# FLY_APP_NAME) sí puede arrancar sin secreto porque nunca emite/valida JWT.
JWT_DEFAULT_INSECURE_SECRET = "futmondo-dev-secret-change-in-prod"


def is_cron_worker() -> bool:
    """True solo para el worker cron (que legítimamente no necesita JWT_SECRET).

    El servicio web es el caso por defecto: cualquier proceso que NO sea el
    worker cron se trata como servicio web y exige un secreto válido. Así el
    guard deja de depender de que FLY_APP_NAME esté presente para el web.
    """
    fly_app = os.getenv("FLY_APP_NAME", "")
    return bool(fly_app) and "cron" in fly_app


def resolve_jwt_secret(secret, cron_worker):
    """Resuelve el JWT_SECRET aplicando el endurecimiento NFR1.1.

    Args:
        secret: valor de JWT_SECRET tal cual lo entrega el entorno ("" si falta).
        cron_worker: True si el proceso es el worker cron.

    Returns:
        El secreto validado (para el worker cron devuelve el valor tal cual,
        que puede ser el default o vacío porque nunca firma tokens).

    Raises:
        RuntimeError: si el servicio web arranca sin secreto o con el default
        inseguro.
    """
    if cron_worker:
        # El worker cron nunca toca JWT: no se le exige secreto.
        return secret

    # Servicio web: fallo de arranque duro (fail-fast) ante secreto ausente o
    # igual al default inseguro. No se degrada a un valor por defecto.
    if not secret:
        raise RuntimeError(
            "FATAL: JWT_SECRET must be set in the web API service "
            "(no puede estar vacío)."
        )
    if secret == JWT_DEFAULT_INSECURE_SECRET:
        raise RuntimeError(
            "FATAL: JWT_SECRET must not equal the insecure default value "
            f"'{JWT_DEFAULT_INSECURE_SECRET}' in the web API service."
        )
    return secret


JWT_SECRET = resolve_jwt_secret(os.getenv("JWT_SECRET", ""), is_cron_worker())

# Futmondo credential-protection key (u1-durable-session).
# Symmetric key used to encrypt the Futmondo re-auth handle at rest so a durable
# session can be rehydrated after a restart without ever persisting the password
# in cleartext (FR5.1/NFR1). MUST be provisioned as a Fly.io secret in
# production; never commit a real value to the repo. Empty when unset: the
# credential-protection layer treats an unset key as "protection unavailable"
# and degrades gracefully rather than crashing unrelated endpoints.
FUTMONDO_CRED_KEY = os.getenv("FUTMONDO_CRED_KEY", "")

# Gemini AI Assistant
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Groq AI (fallback)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
