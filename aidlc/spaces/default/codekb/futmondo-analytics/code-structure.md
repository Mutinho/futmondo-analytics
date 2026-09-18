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
│   │   ├── api/v1/endpoints/   # Routers HTTP (market, reset_db, analytics, sync, _helpers, ...)
│   │   ├── auth/               # JWT + sesión: routes.py, token_store.py, session_store.py
│   │   ├── core/               # config.py (entorno, JWT guard NFR1.1), constants.py
│   │   ├── services/           # Lógica de negocio + clientes externos (god-files, ver más abajo)
│   │   ├── stores/             # Repositorios de durabilidad (intent previo)
│   │   ├── security/           # Protección de credenciales
│   │   └── models/             # Modelos de dominio/datos
│   ├── scripts/                # Scripts one-shot (sync, migraciones, exportaciones) — no web
│   ├── tests/                  # pytest (test_db_admin_guard, test_jwt_startup, test_auth_characterization)
│   ├── requirements.txt, pytest.ini, ruff.toml, fly.toml, Dockerfile, nixpacks.toml
├── angular-app/                # Frontend Angular 22 (PWA); features/market/bid-dialog.component.ts
├── proxy/, angular-app/nginx*.conf   # Reverse proxy nginx (local y prod)
├── cron/                       # Config Fly.io del worker cron (sync; nunca emite JWT)
├── docker-compose.yml          # Orquestación local (SSL_VERIFY=0 aquí)
└── .github/workflows/          # ci.yml (gate PR), fly-deploy.yml, daily-sync.yml, sofascore-sync.yml
```

## Clasificación de Archivos

- **Punto de entrada / composición**: `backend/app/main.py`, `run.py`/`entrypoint.sh`.
- **Configuración**: `backend/app/core/config.py`, `constants.py`, `.env.example`,
  `fly.toml`, `docker-compose.yml`.
- **Superficie HTTP**: `backend/app/api/v1/endpoints/*`, `backend/app/auth/routes.py`.
- **Persistencia**: `backend/app/stores/*` (capa nueva estrecha) y SQL crudo en
  `auth/token_store.py`, `_helpers.py`, `routes._auto_detect_championships`.
- **Integración externa**: `services/futmondo_client.py`, `sofascore_client.py`,
  `photo_service.py`.
- **Tests**: `backend/tests/*.py`, `angular-app/**/*.spec.ts`.
- **Datos estáticos (no código)**: `backend/static/photos/players/**` (~800 PNG).

## Patrones de Código Observados

- **Middleware de autenticación global** con lista de exclusión (`AUTH_EXCLUDED_PATHS`) en
  vez de dependencias por endpoint; ver `api-documentation.md`.
- **Proxy a APIs externas** desde `services/`, con cliente por usuario resuelto en
  `_helpers.get_user_futmondo_client`.
- **Persistencia mixta**: capa `stores/` estrecha (patrón recomendado) conviviendo con SQL
  crudo disperso (anti-patrón a no ampliar; detalle en `code-quality-assessment.md`).
- **God-files en `services/`**: `data_manager_v2.py` (~166 KB), `data_sync_service.py`
  (~84 KB), `assistant_service.py` (~51 KB); no deben crecer.
- **Imports dinámicos dentro de funciones** (p. ej. `import requests` en `get_player_photo`);
  `refresh` ya migró a import estático. Convención del equipo: preferir import estático.
- **Idioma en el código**: identificadores, docstrings y comentarios en inglés; texto de
  usuario (`HTTPException.detail`) en castellano.
