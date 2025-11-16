"""
Configuration file for Futmondo API
Uses environment variables with fallback to default values
"""

import os

from dotenv import load_dotenv
load_dotenv()

# Futmondo API Credentials
# These MUST be provided via environment variables (.env); do not hardcode real credentials in code.
FUTMONDO_EMAIL = os.getenv("FUTMONDO_EMAIL")
FUTMONDO_PASSWORD = os.getenv("FUTMONDO_PASSWORD")

if not FUTMONDO_EMAIL or not FUTMONDO_PASSWORD:
    raise RuntimeError(
        "FUTMONDO_EMAIL and FUTMONDO_PASSWORD must be set in environment variables (e.g. in your .env file). "
        "Do NOT hardcode real credentials in config.py."
    )

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

# PostgreSQL Settings (default to postgresql for production, can use sqlite for local dev)
# Railway provides DATABASE_URL automatically, which takes precedence
DATABASE_URL = os.getenv("DATABASE_URL", "")  # Railway provides this automatically

# If DATABASE_URL is provided (Railway), parse it; otherwise use individual settings
if DATABASE_URL:
    # Parse DATABASE_URL (format: postgresql://user:password@host:port/dbname)
    DATABASE_TYPE = "postgresql"
    # Extract components from DATABASE_URL if needed (db_connection.py handles this)
    POSTGRES_HOST = None  # Will be parsed from DATABASE_URL
    POSTGRES_PORT = None
    POSTGRES_DB = None
    POSTGRES_USER = None
    POSTGRES_PASSWORD = None
else:
    # Fallback to individual settings (for local dev or manual config)
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "postgresql")  # "sqlite" or "postgresql"
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "futmondo")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "futmondo")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "futmondo123")

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# OpenAI Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY must be set in the environment (.env) and must NOT be hardcoded in config.py."
    )

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Use cheaper model by default

