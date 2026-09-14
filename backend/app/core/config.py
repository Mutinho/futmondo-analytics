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
CHAMPIONSHIP_ID = os.getenv("CHAMPIONSHIP_ID", "599b0e413f8a751620554699")
LEAGUE_ID = os.getenv("LEAGUE_ID", "504e4f584d8bec9a67000079")

# Analysis Settings
MAX_PLAYERS_TO_ANALYZE = int(os.getenv("MAX_PLAYERS_TO_ANALYZE", "600"))
MIN_TRANSACTIONS_FOR_ANALYSIS = int(os.getenv("MIN_TRANSACTIONS_FOR_ANALYSIS", "1"))
REQUEST_DELAY_SECONDS = float(os.getenv("REQUEST_DELAY_SECONDS", "0.1"))

# Output Settings
TOP_PROFITABLE_PLAYERS = int(os.getenv("TOP_PROFITABLE_PLAYERS", "20"))
SHOW_DETAILED_ANALYSIS = os.getenv("SHOW_DETAILED_ANALYSIS", "True").lower() == "true"

# Database and Caching Settings
CACHE_DURATION_HOURS = int(os.getenv("CACHE_DURATION_HOURS", "24"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "futmondo_data.db")

# Database type: "sqlite", "turso", or "postgresql"
DATABASE_URL = os.getenv("DATABASE_URL", "")  # Railway provides this automatically

# Turso (LibSQL) Settings
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

if DATABASE_URL:
    # Railway: PostgreSQL via DATABASE_URL
    DATABASE_TYPE = "postgresql"
    POSTGRES_HOST = None
    POSTGRES_PORT = None
    POSTGRES_DB = None
    POSTGRES_USER = None
    POSTGRES_PASSWORD = None
elif TURSO_DATABASE_URL:
    # Turso: LibSQL remoto (detectar automáticamente si hay URL de Turso)
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "turso")
    POSTGRES_HOST = None
    POSTGRES_PORT = None
    POSTGRES_DB = None
    POSTGRES_USER = None
    POSTGRES_PASSWORD = None
else:
    # Fallback: SQLite local o PostgreSQL manual
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "futmondo")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "futmondo")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "futmondo123")

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

# Gemini AI Assistant
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Groq AI (fallback)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
