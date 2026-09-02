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
JWT_SECRET = os.getenv("JWT_SECRET", "")
if not JWT_SECRET:
    _fly_app = os.getenv("FLY_APP_NAME", "")
    _is_web_service = _fly_app and "cron" not in _fly_app  # api = web; cron = worker
    if _is_web_service:
        raise RuntimeError("FATAL: JWT_SECRET must be set in the web API service!")
    JWT_SECRET = "futmondo-dev-secret-change-in-prod"

# Gemini AI Assistant
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Groq AI (fallback)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
