#!/usr/bin/env python3
"""
Migrate all data from local SQLite to Turso.
Tables are inserted in dependency order to respect foreign keys.
Reads schema directly from local DB to avoid mismatches.

Usage:
  TURSO_DATABASE_URL=... TURSO_AUTH_TOKEN=... python scripts/migrate_data_to_turso.py
"""

import sys
import os
import sqlite3
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

LOCAL_DB = os.path.join(os.path.dirname(__file__), "..", "futmondo_data.db")

# Orden de inserción respetando foreign keys (padres antes que hijas)
MIGRATION_ORDER = [
    # 1. Sin dependencias
    "users",
    "championships",
    "championships_config",
    "players",
    # 2. Dependen de users/championships
    "teams",
    "sync_metadata",
    "sofascore_cache",
    # 3. Dependen de players/teams/users
    "transactions",
    "punishments_bonuses",
    "clauses",
    "team_standings",
    "player_performance",
    "team_rosters",
    "dream_teams_mvps",
    # 4. Tablas extra
    "match_odds",
    "matchday_articles",
    "player_championship_stats",
]


def main():
    import turso_serverless

    turso_url = os.environ.get("TURSO_DATABASE_URL")
    turso_token = os.environ.get("TURSO_AUTH_TOKEN")

    if not turso_url or not turso_token:
        logger.error("❌ Falta TURSO_DATABASE_URL o TURSO_AUTH_TOKEN")
        sys.exit(1)

    # Conectar a SQLite local
    local_conn = sqlite3.connect(LOCAL_DB)
    local_cursor = local_conn.cursor()

    # Conectar a Turso
    logger.info(f"🔗 Conectando a Turso: {turso_url}")
    remote_conn = turso_serverless.connect(turso_url, auth_token=turso_token)

    # Obtener tablas locales existentes
    local_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    local_tables = {r[0] for r in local_cursor.fetchall()}

    # Para cada tabla: recrear en Turso usando el CREATE TABLE real de la DB local
    logger.info("\n📋 Asegurando que las tablas existen en Turso con el schema correcto...")
    for table in MIGRATION_ORDER:
        if table not in local_tables:
            continue
        local_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        row = local_cursor.fetchone()
        if not row:
            continue
        create_sql = row[0]
        # Convertir CREATE TABLE a CREATE TABLE IF NOT EXISTS
        create_sql_safe = create_sql.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1)
        try:
            remote_conn.execute(create_sql_safe)
            remote_conn.commit()
        except Exception as e:
            # Si ya existe con schema diferente, drop y recrear
            if "already exists" in str(e).lower() or "has no column" in str(e).lower():
                logger.info(f"  🔄 Recreando {table} (schema mismatch)...")
                remote_conn.execute(f"DROP TABLE IF EXISTS {table}")
                remote_conn.commit()
                remote_conn.execute(create_sql)
                remote_conn.commit()
            else:
                logger.warning(f"  ⚠️ {table}: {e}")

    # Migrar datos en orden
    logger.info("\n📦 Migrando datos...")
    total_rows = 0
    for table in MIGRATION_ORDER:
        if table not in local_tables:
            continue

        local_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = local_cursor.fetchone()[0]

        if count == 0:
            logger.info(f"  ⏭️  {table}: vacía")
            continue

        # Obtener columnas
        local_cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in local_cursor.fetchall()]
        cols_str = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))

        # Leer datos locales
        local_cursor.execute(f"SELECT {cols_str} FROM {table}")
        rows = local_cursor.fetchall()

        # Insertar en Turso
        inserted = 0
        errors = 0
        for row in rows:
            try:
                remote_conn.execute(
                    f"INSERT OR REPLACE INTO {table} ({cols_str}) VALUES ({placeholders})",
                    tuple(row)
                )
                inserted += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    logger.warning(f"    ⚠️ {table}: {e}")

            # Commit cada 50 filas
            if inserted % 50 == 0 and inserted > 0:
                remote_conn.commit()

        remote_conn.commit()
        total_rows += inserted

        status = f"✅ {table}: {inserted}/{count} rows"
        if errors > 0:
            status += f" ({errors} errores)"
        logger.info(f"  {status}")

    local_conn.close()
    remote_conn.close()

    logger.info(f"\n🎉 Migración completada: {total_rows} registros migrados a Turso")


if __name__ == "__main__":
    main()
