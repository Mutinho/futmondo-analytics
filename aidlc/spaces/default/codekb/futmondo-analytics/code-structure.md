# Estructura del Código — Futmondo Analytics

## Organización de paquetes/módulos

```
futmondo-analytics/
├── backend/                # FastAPI (Python 3.12)
│   ├── app/
│   │   ├── core/           # config.py, constants.py
│   │   ├── services/       # lógica de negocio + integraciones
│   │   ├── api/v1/endpoints/  # 24 routers HTTP
│   │   ├── auth/           # JWT + token/session store
│   │   ├── stores/         # repositorios durables task/session
│   │   ├── security/       # protección de credenciales
│   │   ├── models/         # modelos de datos
│   │   └── main.py         # app, middleware, montaje de routers/estáticos
│   ├── scripts/            # utilidades one-shot (sync, export, migraciones, init_db)
│   ├── tests/              # ≈28 ficheros pytest (characterization-first)
│   └── conftest.py         # fixtures fake in-memory
├── angular-app/            # SPA Angular 22 (PWA)
├── proxy/                  # nginx reverse proxy (local)
├── cron/                   # app Fly.io de crons
└── docs/                   # documentación
```

> Inventario de responsabilidades por componente en `component-inventory.md`;
> versiones en `technology-stack.md`.

## Clasificación de ficheros

- **Configuración de negocio**: `backend/app/core/config.py` (resolución de
  BD y secretos; contiene los defaults hardcodeados `CHAMPIONSHIP_ID`/
  `LEAGUE_ID`), `backend/app/core/constants.py` (catálogo estático
  `LALIGA_TEAMS`, fallback legítimo).
- **Acceso a datos**: `backend/app/services/db_connection.py` (manager
  multi-backend PostgreSQL/SQLite/Turso).
- **Integraciones**: `futmondo_client.py`, `sofascore_client.py`,
  `assistant_service.py`; errores en `integration_errors.py`.
- **God-files (deuda, NO ampliar)**: `data_manager_v2.py` ~166 KB,
  `data_sync_service.py` ~84 KB, `assistant_service.py` ~51 KB.
- **Build/deploy**: `Dockerfile`, `fly.toml`, `requirements.txt`,
  `nixpacks.toml` (residuo Railway, ver deuda), `entrypoint.sh` (candidato a
  residuo), `docker-compose.yml`.
- **CI/CD**: `.github/workflows/ci.yml`, `fly-deploy.yml`, `daily-sync.yml`,
  `sofascore-sync.yml`.
- **Tests**: `backend/tests/` (pytest) y specs Angular en `angular-app/src/app/`.
- **Residuos versionados (basura)**: `*.jpg:Zone.Identifier`, imágenes
  sueltas (`42874.jpg`), `stitch_*/` (mockups), posibles `node_modules.old-*/`
  y `futmondo_data.db` (ver `code-quality-assessment.md`, FR15).

## Patrones de código observados

- **Router-por-recurso**: 24 routers montados en `main.py` bajo `/api/v1/*`.
- **Manager multi-backend** con adaptación de SQL/params por tipo de BD
  (`adapt_sql`/`adapt_params`/`get_last_insert_id`) — hoy solo la rama
  PostgreSQL está viva en producción.
- **Excepciones tipadas propagadas** para fallos de integración.
- **Estado de paso** para el sync (`sync_step_status.py`: `DEGRADED`/fatal).
- **Characterization-first** en tests (fixtures fake in-memory en `conftest.py`,
  sin red/BD real/credenciales).

## Idioma del código

Identificadores, docstrings y comentarios en inglés; texto de cara al usuario
(`HTTPException.detail`, UI) y mensajes de commit en castellano.
