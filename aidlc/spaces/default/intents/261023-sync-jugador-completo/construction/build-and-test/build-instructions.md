# Build Instructions — Backend (enriquecimiento del sync)

## Prerequisitos

- Python 3.12 (CI) / venv efímero sin `libsql-experimental` si el Python local es
  más nuevo (learning 2026-09-16); en el repo existe `backend/.venv-verify`.
- `export JWT_SECRET=<efímero-no-default>` (arranque del servicio).
- Sin servicios externos: tests con el fake in-memory de `conftest.py`.

## Instalación

```bash
pip install -r requirements.txt   # o el venv .venv-verify
```
Sin dependencias nuevas en este intent.

## Build / verificación

Backend Python sin compilación. La "build" es:

1. Importabilidad:
   ```bash
   python -c "import app.services.sync.players_full.orchestrator, app.services.sync_read.favorites_read, app.services.data_manager.players.infrastructure.players_adapter, app.services.data_manager.schema_lifecycle.infrastructure.schema_lifecycle_adapter"
   ```
2. Lint (gate CI, quirúrgico sobre ficheros tocados):
   ```bash
   ruff check app/services/sync/players_full/orchestrator.py app/services/sync_read/favorites_read.py app/services/data_manager/players/infrastructure/players_adapter.py app/services/data_manager/schema_lifecycle/infrastructure/schema_lifecycle_adapter.py tests/test_sync_players_enrichment.py tests/test_schema_players_columns.py tests/test_players_adapter_enrichment.py tests/test_favorites_read_enriched.py
   ```
   (NUNCA `ruff format` masivo ni `--fix` de repo entero.)

## Nota de migración

El `ALTER TABLE players ADD COLUMN` nuevo es **idempotente y engine-aware**
(PostgreSQL `IF NOT EXISTS`; SQLite introspecta `PRAGMA table_info`). Corre en
`ensure_schema_updates` en el arranque; no requiere paso manual ni backfill.

## Troubleshooting

- `psycopg2.OperationalError` en tests → el autouse de `conftest.py` ya evita la
  conexión real; ejecutar desde `backend/`.
- Columnas nuevas vacías tras desplegar → se pueblan en el primer sync de
  jugadores; `favorites/my` degrada con los defaults hasta entonces (por diseño).
