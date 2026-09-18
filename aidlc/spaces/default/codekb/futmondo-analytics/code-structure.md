# Estructura del Código — futmondo-analytics

## Organización de Paquetes/Módulos

Monorepo con dos aplicaciones desplegables y utilidades de soporte. El catálogo con
responsabilidades y dependencias está en `component-inventory.md`; aquí se describe la
organización física y los patrones de código.

```
futmondo-analytics/
├── backend/                    # Servicio web FastAPI (Python 3.12)
│   ├── app/
│   │   ├── main.py             # App FastAPI, AuthMiddleware, montaje de routers, /photos, /health
│   │   ├── api/v1/endpoints/   # Routers HTTP (market, reset_db, analytics, balances, matchdays,
│   │   │                       #   player_finances, sync, _helpers, ...)
│   │   ├── auth/               # JWT + sesión: routes.py, token_store.py, session_store.py
│   │   ├── core/               # config.py (entorno, JWT guard NFR1.1), constants.py
│   │   ├── services/           # Lógica de negocio + clientes externos (god-files, ver más abajo);
│   │   │                       #   data_sync_service.sync_prizes() = fórmula de premios
│   │   ├── stores/             # Repositorios de durabilidad (intent previo)
│   │   ├── security/           # Protección de credenciales
│   │   └── models/             # Modelos de dominio/datos (DTOs Pydantic; sin modelo de premios)
│   ├── scripts/                # Scripts one-shot (sync, migraciones, exportaciones) — no web
│   ├── tests/                  # pytest (test_db_admin_guard, test_jwt_startup,
│   │                           #   test_auth_characterization, test_finance_characterization,
│   │                           #   test_analytics_service)
│   ├── requirements.txt, pytest.ini, ruff.toml, fly.toml, Dockerfile, nixpacks.toml
├── angular-app/                # Frontend Angular 22 (PWA); features/{market,finances,budget,
│                               #   calculator,analytics}
├── proxy/, angular-app/nginx*.conf   # Reverse proxy nginx (local y prod)
├── cron/                       # Config Fly.io del worker cron (sync; nunca emite JWT)
├── docker-compose.yml          # Orquestación local (SSL_VERIFY=0 aquí)
└── .github/workflows/          # ci.yml (gate PR), fly-deploy.yml, daily-sync.yml, sofascore-sync.yml
```

## Clasificación de Archivos

- **Punto de entrada / composición**: `backend/app/main.py`, `run.py`/`entrypoint.sh`.
- **Configuración**: `backend/app/core/config.py`, `constants.py`, `.env.example`,
  `fly.toml`, `docker-compose.yml`.
- **Superficie HTTP**: `backend/app/api/v1/endpoints/*` (incl. `player_finances.py`,
  `balances.py`, `matchdays.py`, `analytics.py`), `backend/app/auth/routes.py`.
- **Lógica de premios (fórmula)**: `backend/app/services/data_sync_service.py::sync_prizes`
  (~líneas 1577-1885) — productor de la tabla `team_prizes`. Los routers de finanzas/saldos
  sólo leen/suman.
- **Persistencia**: `backend/app/stores/*` (capa nueva estrecha) y SQL crudo en
  `auth/token_store.py`, `_helpers.py`, `balances.py`, `analytics.py`,
  `routes._auto_detect_championships`.
- **Integración externa**: `services/futmondo_client.py`, `sofascore_client.py`,
  `photo_service.py`.
- **Tests**: `backend/tests/*.py`, `angular-app/**/*.spec.ts`.
- **Datos estáticos (no código)**: `backend/static/photos/players/**` (~800 PNG).

## Patrones de Código Observados

- **Middleware de autenticación global** con lista de exclusión (`AUTH_EXCLUDED_PATHS`) en
  vez de dependencias por endpoint; ver `api-documentation.md`.
- **Proxy a APIs externas** desde `services/`, con cliente por usuario resuelto en
  `_helpers.get_user_futmondo_client`.
- **Precálculo batch + lectura barata**: la fórmula de premios se ejecuta una vez en
  `sync_prizes` y persiste en `team_prizes`; los endpoints sólo hacen `SELECT`/suma. UPSERT
  con `ON CONFLICT (championship_id, team_id, matchday)` y limpieza defensiva
  `DELETE ... WHERE matchday NOT IN (...)`.
- **Matchday sintético negativo** para las pseudo-jornadas adelantadas de Futmondo (número
  no entero, p. ej. `0.5 -> -5`), evitando colisión con jornadas reales 1..38 en una columna
  entera.
- **Persistencia mixta**: capa `stores/` estrecha (patrón recomendado) conviviendo con SQL
  crudo disperso (anti-patrón a no ampliar; detalle en `code-quality-assessment.md`).
- **God-files en `services/`**: `data_manager_v2.py` (~166 KB), `data_sync_service.py`
  (~84 KB, aloja la fórmula de premios), `assistant_service.py` (~51 KB); no deben crecer.
- **Analítica derivada** en `analytics_service.py` con `statistics` (media, pstdev),
  ejercitada por `test_analytics_service.py` con `StubDM`.
- **Imports dinámicos dentro de funciones** (p. ej. `import requests` en `get_player_photo`);
  `refresh` ya migró a import estático. Convención del equipo: preferir import estático.
- **Idioma en el código**: identificadores, docstrings y comentarios en inglés; texto de
  usuario (`HTTPException.detail`) en castellano.
