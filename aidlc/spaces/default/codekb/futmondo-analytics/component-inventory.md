# Inventario de Componentes — Futmondo Analytics

> Reverse-engineering. Escaneo previo FULL preservado; rerun FOCUSED sobre
> `backend/app/services/` y `backend/tests/`. Lista completa de componentes con
> responsabilidades y dependencias. Los headings H2 de componente se comparan
> literalmente por el rerun guard y deben coincidir verbatim con la lista
> `components` del bloque Scope of Analysis en `reverse-engineering-timestamp.md`.

## Resumen del inventario

El sistema se descompone en componentes desplegables (frontend, backend, proxy,
cron) y, dentro del backend, en subsistemas lógicos (auth, servicios de datos,
clientes de integración, endpoints, gestor de tareas). A continuación cada
componente con su responsabilidad y dependencias. En este rerun solo `data
services` se re-verificó en profundidad; el resto se conserva del escaneo FULL
previo y aparece degradado a `shallow` en el bloque Scope of Analysis.

## angular-app

- **Tipo**: aplicación (frontend PWA, TypeScript/Angular 22).
- **Responsabilidad**: SPA instalable (service worker + manifest) con 17 features
  standalone (presupuesto, mercado, finanzas, evolución, estadísticas,
  clausulables, analytics, asistente, etc.), core transversal (auth interceptor,
  guards) y shared. En producción incluye nginx (`nginx.prod.conf`) que proxya
  `/api` y `/auth` al backend.
- **Dependencias**: `backend` (en runtime vía proxy HTTP); Material 22, Chart.js +
  ng2-charts, marked, rxjs.

## backend

- **Tipo**: aplicación (API FastAPI, Python 3.12).
- **Responsabilidad**: exponer la API REST (`/api/v1/*` + `/auth/*`), orquestar la
  sincronización, la analítica financiera, el mercado y el asistente IA. Monta 23
  routers en `main.py` con `AuthMiddleware` central.
- **Dependencias**: `PostgreSQL` (Neon) vía `db_connection`; `API Futmondo`,
  `API Sofascore`, Gemini/Groq; subsistemas internos (auth, services, endpoints,
  task_manager).

## auth

- **Tipo**: subsistema del backend (`backend/app/auth/`).
- **Responsabilidad**: login contra Futmondo, emisión/verificación de JWT (HS256,
  access 60 min + refresh 30 días HttpOnly), persistencia de refresh tokens
  (`token_store`), sesiones Futmondo por usuario (`session_store`), middleware y
  dependencias de auth.
- **Dependencias**: `futmondo_client` (validación de credenciales), `PostgreSQL`
  (tabla de usuarios/tokens), `SessionStore` in-memory. Deuda: contraseñas en
  claro en memoria; posible bug de expiración en `is_refresh_token_valid`.

## data services

- **Tipo**: subsistema del backend (`backend/app/services/`).
- **Responsabilidad**: acceso y transformación de datos y lógica de negocio pesada:
  `data_manager_v2.py` (acceso a datos, 166 KB), `data_sync_service.py`
  (orquestación de sync, 84 KB), `analytics_service.py` (34 KB),
  `assistant_service.py` (asistente IA, 51 KB), `photo_service.py` (23 KB).
- **`analytics_service.py` (re-verificado en profundidad, foco del rerun)**: clase
  `AnalyticsService` con estado de instancia `_team_cache`/`_player_cache`
  (memoización, inicializados en `__init__` l.16-17) y métodos públicos
  `get_championship_trends` (l.124), `get_player_value_trend` (l.437),
  `get_clause_network` (l.668), `get_player_form`, `get_opportunity_streaks`,
  `get_matchday_projections`. Helpers privados `_safe_team_info`,
  `_safe_player_info`, `_build_team_lookup`, `_resolve_team` dependen del estado
  de instancia. Emite `last_transaction_price` (no `latest_price`).
- **Dependencias**: `PostgreSQL` (`db_connection`), `futmondo_client`,
  `sofascore_client`, servicios IA. Deuda: "god files" intestables sin fakes;
  acoplamiento de la caracterización de `AnalyticsService` a atributos privados de
  instancia y divergencia de nombre de clave de salida (ver
  `code-quality-assessment.md`).

## integration clients

- **Tipo**: subsistema del backend (`backend/app/services/`).
- **Responsabilidad**: clientes de integración externa: `futmondo_client.py`
  (`requests.Session`, endpoints versionados heterogéneos, payload
  `{header, query, answer}`) y `sofascore_client.py` (`curl_cffi`
  `impersonate="chrome"`, throttle 750 ms, sin API key).
- **Dependencias**: `API Futmondo`, `API Sofascore`. Riesgo: baneo de IP en
  Sofascore.

## api endpoints

- **Tipo**: subsistema del backend (`backend/app/api/v1/endpoints/`).
- **Responsabilidad**: 23 routers por dominio (sync, sofascore_sync, market,
  reset_db, analytics, balances, championships, roster, favorites, transactions,
  player-finances, statistics, user-stats, clausulable-players, phantoms,
  matchdays, initialize, user, assistant, sofascore_detail, `_helpers`).
- **Dependencias**: `data services`, `integration clients`, `task manager`,
  `auth` (`request.state.user`). Nota: los routers de analítica serializan los
  dicts de `AnalyticsService`; sensibles a un renombrado de clave de salida.

## task manager

- **Tipo**: subsistema del backend (`backend/app/services/task_manager.py`).
- **Responsabilidad**: crear, seguir y cerrar tareas de sync en background
  (create/mark_running/update_progress/mark_completed/mark_failed), deduplicación
  por campeonato (`get_active_task`) y expiración de tareas >10 min.
- **Dependencias**: ninguna externa; **estado singleton in-memory** — se pierde en
  reinicios de la máquina Fly.

## backend/scripts

- **Tipo**: scripts (Python, jobs one-shot).
- **Responsabilidad**: `sync_data.py` (sync Futmondo multi-championship, entrypoint
  del cron), `sync_sofascore_local.py` (batch Sofascore), migraciones a Turso
  (`migrate_to_turso.py`, `migrate_data_to_turso.py`) y exportadores
  (`fetch_user_finances_data.py`, `export_user_transactions.py`).
- **Dependencias**: `data services`, `integration clients`, `PostgreSQL`.

## cron

- **Tipo**: desplegable (Fly.io app `futmondo-cron`).
- **Responsabilidad**: proceso one-shot que ejecuta `python scripts/sync_data.py`
  reutilizando `backend/Dockerfile`; refresco programado de datos sin usuario.
- **Dependencias**: imagen `backend`, `PostgreSQL`, `API Futmondo`.

## proxy

- **Tipo**: configuración (nginx, solo docker-compose local).
- **Responsabilidad**: reverse proxy local que enruta al frontend y al backend
  (`proxy/nginx.conf`). En producción su rol lo cumple el nginx embebido en el
  frontend.
- **Dependencias**: `backend` (healthy), `frontend` (compose).
