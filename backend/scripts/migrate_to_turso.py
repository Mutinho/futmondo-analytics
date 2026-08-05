#!/usr/bin/env python3
"""
Migrate schema to Turso — creates all tables in the remote database.

Usage:
  1. Set TURSO_DATABASE_URL and TURSO_AUTH_TOKEN in .env
  2. Run: python scripts/migrate_to_turso.py

This creates all tables (if not exist) without dropping existing data.
Safe to run multiple times.
"""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    from app.core.config import DATABASE_TYPE, TURSO_DATABASE_URL, TURSO_AUTH_TOKEN

    if DATABASE_TYPE != "turso":
        logger.error("❌ DATABASE_TYPE no es 'turso'. Revisa tu .env")
        logger.error(f"   Actual: DATABASE_TYPE={DATABASE_TYPE}")
        sys.exit(1)

    if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
        logger.error("❌ Falta TURSO_DATABASE_URL o TURSO_AUTH_TOKEN en .env")
        sys.exit(1)

    logger.info(f"🔗 Conectando a Turso: {TURSO_DATABASE_URL}")

    import turso_serverless
    conn = turso_serverless.connect(TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)

    # ============================================================
    # CREAR TABLAS (IF NOT EXISTS — seguro ejecutar múltiples veces)
    # ============================================================
    tables = [
        ("users", '''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''),
        ("teams", '''
            CREATE TABLE IF NOT EXISTS teams (
                team_id TEXT PRIMARY KEY,
                user_id TEXT,
                team_name TEXT NOT NULL,
                initial_budget INTEGER DEFAULT 270000000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        '''),
        ("players", '''
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                real_team_id TEXT,
                real_team_name TEXT,
                slug TEXT,
                photo_url TEXT,
                photo_local_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''),
        ("championships", '''
            CREATE TABLE IF NOT EXISTS championships (
                championship_id TEXT PRIMARY KEY,
                name TEXT,
                season_start DATE,
                season_end DATE,
                total_matchdays INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''),
        ("championships_config", '''
            CREATE TABLE IF NOT EXISTS championships_config (
                championship_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                has_clauses INTEGER DEFAULT 0,
                initial_budget INTEGER DEFAULT 200000000,
                excluded_teams TEXT DEFAULT ''
            )
        '''),
        ("team_standings", '''
            CREATE TABLE IF NOT EXISTS team_standings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                championship_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                matchday INTEGER NOT NULL,
                position INTEGER NOT NULL,
                points INTEGER NOT NULL,
                points_this_matchday INTEGER DEFAULT 0,
                team_value INTEGER,
                goals_for INTEGER DEFAULT 0,
                goals_against INTEGER DEFAULT 0,
                goal_difference INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(championship_id, team_id, matchday),
                FOREIGN KEY (team_id) REFERENCES teams (team_id),
                FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
            )
        '''),
        ("player_performance", '''
            CREATE TABLE IF NOT EXISTS player_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                championship_id TEXT NOT NULL,
                player_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                matchday INTEGER NOT NULL,
                points INTEGER NOT NULL,
                value INTEGER,
                minutes_played INTEGER,
                goals INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                yellow_cards INTEGER DEFAULT 0,
                red_cards INTEGER DEFAULT 0,
                was_starter INTEGER DEFAULT 0,
                was_best_player INTEGER DEFAULT 0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(championship_id, player_id, team_id, matchday),
                FOREIGN KEY (player_id) REFERENCES players (player_id),
                FOREIGN KEY (team_id) REFERENCES teams (team_id),
                FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
            )
        '''),
        ("transactions", '''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                championship_id TEXT NOT NULL,
                api_transaction_id TEXT UNIQUE NOT NULL,
                player_id TEXT NOT NULL,
                seller_user_id TEXT,
                buyer_user_id TEXT NOT NULL,
                seller_team_id TEXT,
                buyer_team_id TEXT,
                price INTEGER NOT NULL,
                transaction_date TIMESTAMP NOT NULL,
                matchday INTEGER,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (player_id),
                FOREIGN KEY (seller_user_id) REFERENCES users (user_id),
                FOREIGN KEY (buyer_user_id) REFERENCES users (user_id),
                FOREIGN KEY (seller_team_id) REFERENCES teams (team_id),
                FOREIGN KEY (buyer_team_id) REFERENCES teams (team_id)
            )
        '''),
        ("punishments_bonuses", '''
            CREATE TABLE IF NOT EXISTS punishments_bonuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                championship_id TEXT NOT NULL,
                news_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                team_id TEXT,
                user_name TEXT NOT NULL,
                type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                admin_name TEXT,
                created_date TIMESTAMP NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        '''),
        ("clauses", '''
            CREATE TABLE IF NOT EXISTS clauses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                championship_id TEXT NOT NULL,
                news_id TEXT UNIQUE NOT NULL,
                payer_user_id TEXT NOT NULL,
                payer_team_id TEXT,
                payer_name TEXT NOT NULL,
                receiver_user_id TEXT NOT NULL,
                receiver_team_id TEXT,
                receiver_name TEXT NOT NULL,
                player_name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                created_date TIMESTAMP NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (payer_user_id) REFERENCES users (user_id),
                FOREIGN KEY (receiver_user_id) REFERENCES users (user_id),
                FOREIGN KEY (payer_team_id) REFERENCES teams (team_id),
                FOREIGN KEY (receiver_team_id) REFERENCES teams (team_id)
            )
        '''),
        ("team_rosters", '''
            CREATE TABLE IF NOT EXISTS team_rosters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                championship_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                player_id TEXT NOT NULL,
                matchday INTEGER NOT NULL,
                formation_position TEXT,
                is_starter INTEGER DEFAULT 0,
                lineup_order INTEGER,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(championship_id, team_id, player_id, matchday),
                FOREIGN KEY (team_id) REFERENCES teams (team_id),
                FOREIGN KEY (player_id) REFERENCES players (player_id),
                FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
            )
        '''),
        ("dream_teams_mvps", '''
            CREATE TABLE IF NOT EXISTS dream_teams_mvps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                championship_id TEXT NOT NULL,
                round_id TEXT NOT NULL,
                matchday INTEGER NOT NULL,
                player_id TEXT NOT NULL,
                is_mvp INTEGER DEFAULT 0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(championship_id, round_id, player_id, is_mvp),
                FOREIGN KEY (player_id) REFERENCES players (player_id),
                FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
            )
        '''),
        ("sync_metadata", '''
            CREATE TABLE IF NOT EXISTS sync_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                championship_id TEXT NOT NULL,
                data_type TEXT NOT NULL,
                last_sync_id TEXT,
                last_sync_date TIMESTAMP,
                last_sync_matchday INTEGER,
                records_synced INTEGER DEFAULT 0,
                sync_duration_seconds REAL,
                sync_status TEXT DEFAULT 'success',
                error_message TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(championship_id, data_type),
                FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
            )
        '''),
        ("sofascore_cache", '''
            CREATE TABLE IF NOT EXISTS sofascore_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                player_id_sofascore INTEGER,
                rating REAL,
                matches_played INTEGER,
                goals INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                minutes_played INTEGER DEFAULT 0,
                sofascore_url TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_name)
            )
        '''),
    ]

    created = 0
    for name, sql in tables:
        try:
            conn.execute(sql)
            conn.commit()
            logger.info(f"  ✅ {name}")
            created += 1
        except Exception as e:
            logger.error(f"  ❌ {name}: {e}")

    # ============================================================
    # INDEXES
    # ============================================================
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_team_standings_championship_matchday ON team_standings(championship_id, matchday)",
        "CREATE INDEX IF NOT EXISTS idx_team_standings_team ON team_standings(team_id)",
        "CREATE INDEX IF NOT EXISTS idx_player_performance_championship ON player_performance(championship_id, matchday)",
        "CREATE INDEX IF NOT EXISTS idx_player_performance_player ON player_performance(player_id)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_championship ON transactions(championship_id)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_player ON transactions(player_id)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_buyer ON transactions(buyer_user_id)",
        "CREATE INDEX IF NOT EXISTS idx_team_rosters_championship ON team_rosters(championship_id, matchday)",
        "CREATE INDEX IF NOT EXISTS idx_sofascore_cache_player ON sofascore_cache(player_name)",
    ]

    for idx_sql in indexes:
        try:
            conn.execute(idx_sql)
            conn.commit()
        except Exception as e:
            logger.warning(f"  ⚠️ Index: {e}")

    logger.info(f"\n🎉 Migración completada: {created}/{len(tables)} tablas creadas en Turso")

    # ============================================================
    # INSERTAR CONFIGURACIÓN DE CAMPEONATOS
    # ============================================================
    logger.info("\n📋 Insertando configuración de campeonatos...")
    configs = [
        ("592416daa3a2dd871a7a9956", "Ivan el flautista de Futmondin", 0, 200000000, "javier.ortega"),
        ("6a5f82a09c06c8d0ceaa40ee", "Infantino es español", 1, 300000000, ""),
    ]
    for champ_id, name, has_clauses, budget, excluded in configs:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO championships_config (championship_id, name, has_clauses, initial_budget, excluded_teams) VALUES (?, ?, ?, ?, ?)",
                (champ_id, name, has_clauses, budget, excluded)
            )
            conn.commit()
            logger.info(f"  ✅ {name}")
        except Exception as e:
            logger.warning(f"  ⚠️ {name}: {e}")

    conn.close()
    logger.info("\n✅ ¡Base de datos Turso lista!")


if __name__ == "__main__":
    main()
