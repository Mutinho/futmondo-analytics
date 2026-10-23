# Build Instructions — Backend (read-from-sync)

## Prerequisitos

- Python 3.12 (CI) / ejecutable local. Si el Python del sistema es más nuevo que
  el de CI, usar un venv efímero **excluyendo `libsql-experimental`** (no compila
  fuera de 3.12 y no lo ejercitan los tests, que usan el fake SQLite) y fijar un
  `JWT_SECRET` efímero (learning del proyecto 2026-09-16). En este repo existe ya
  `backend/.venv-verify`.
- Sin servicios externos: los tests usan el fake in-memory de `conftest.py` (sin
  Neon, sin red, sin credenciales).

## Instalación de dependencias

```bash
# Desde backend/, con el venv activo:
pip install -r requirements.txt   # (o el venv .venv-verify ya provisto)
```

No se añaden dependencias nuevas en este intent (stdlib suficiente).

## Entorno

```bash
export JWT_SECRET=<efímero-no-default>   # requerido por el arranque (NFR1.1 servicio)
```

## Build / verificación

Este es un backend Python (sin paso de compilación). La "build" es:

1. Importabilidad del paquete nuevo:
   ```bash
   python -c "import app.services.sync_read.favorites_read, app.services.sync_read.market_read"
   ```
2. Lint (gate de CI, quirúrgico sobre ficheros nuevos/tocados):
   ```bash
   ruff check app/services/sync_read/ app/api/v1/endpoints/favorites.py app/api/v1/endpoints/market.py tests/test_favorites_read_characterization.py tests/test_favorites_read.py tests/test_market_read.py tests/test_sync_read_endpoints.py
   ```
   (NUNCA `ruff format` masivo ni `--fix` de repo entero sobre brownfield.)

## Troubleshooting

- `psycopg2.OperationalError` en tests → el autouse de `conftest.py` ya evita la
  conexión real; asegúrate de ejecutar desde `backend/` (pytest.ini fija
  `pythonpath = .`).
- `libsql-experimental` falla al instalar fuera de 3.12 → exclúyelo del venv
  efímero (no lo usan los tests).
