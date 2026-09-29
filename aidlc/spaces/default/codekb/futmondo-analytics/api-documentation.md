# API Documentation — futmondo-analytics

## Superficies API

### 1. REST interno (FastAPI) — entrante

Evidencia: `backend/app/main.py` (montaje de routers) y
`backend/app/api/v1/endpoints/`. La API v1 monta ~20 routers de endpoints bajo
prefijos `/api/v1/*` (el handoff del developer lo enuncia como "22 routers"; el
recuento exacto de módulos-router de endpoints v1 mapeados en `main.py` es 20,
más el `auth` router fuera de `/api/v1`). Todos los routers `/api/v1/*` quedan
tras `AuthMiddleware`.

Routers montados (prefijo → módulo, verbatim de `main.py`):

- `/api/v1/matchdays` → `matchdays`
- `/api/v1/initialize` → `initialize`
- `/api/v1/database` → `reset_db`
- `/api/v1/statistics` → `statistics`
- `/api/v1/player-finances` → `player_finances`
- `/api/v1/user-stats` → `user_stats`
- `/api/v1/clausulable-players` → `clausulable_players`
- `/api/v1/sync` → `sync`, `phantoms`, `sofascore_sync` (tres routers, mismo prefijo)
- `/api/v1/analytics` → `analytics`, `balances` (dos routers, mismo prefijo)
- `/api/v1` → `championships`
- `/api/v1/market` → `market`
- `/api/v1/roster` → `roster`
- `/api/v1/favorites` → `favorites`
- `/api/v1/transactions` → `transactions`
- `/api/v1/sofascore` → `sofascore_detail`
- `/api/v1/user` → `user`
- `/api/v1/assistant` → `assistant`

Rutas fuera de `/api/v1` (no requieren Bearer salvo la de foto): `GET /`,
`GET /health`, `GET /api/v1/photos/{player_id}` (SÍ requiere Bearer; redirige a
`/static/photos/*`) y el mount estático **público intencional**
`/static/photos/*` (documentado como superficie pública en `main.py`, FR7/NFR1.6).

### 2. Auth — entrante

Evidencia: `backend/app/auth/routes.py` (montado sin prefijo `/api/v1`).
`/auth/login`, `/auth/refresh`, `/auth/logout`. Excluidas de `AuthMiddleware`.

### 3. Asistente IA — contrato interno + LLM saliente

Evidencia: `backend/app/api/v1/endpoints/assistant.py`. Endpoints:

- `POST /api/v1/assistant/ask` → `AskRequest{message, championship_id,
  conversation_id?, history?}` → `AskResponse{response, context_used[],
  conversation_id}`.
- `POST /api/v1/assistant/ask/stream` → SSE (`text/event-stream`): eventos
  `start` / `chunk` / `done` vía `service.ask_stream(...)`.
- `GET /api/v1/assistant/conversations` (opcional `championship_id`).
- `GET /api/v1/assistant/conversations/{id}`.
- `DELETE /api/v1/assistant/conversations/{id}`.
- `PUT /api/v1/assistant/conversations/{id}/title`.
- `GET /api/v1/assistant/usage` → `service.usage_tracker.get_usage_summary()`.

El endpoint consume la superficie pública `get_assistant_service()` +
`await service.ask(...)` de `assistant_service.py` (contrato a preservar por el
intent) y persiste conversaciones en `assistant_conversations` (tabla creada en
caliente).

## Contratos de autenticación/autorización

- **Esquema**: Bearer JWT (`Authorization: Bearer <access>`), validado por
  `verify_token(..., expected_type="access")`.
- **Rutas públicas** (`AUTH_EXCLUDED_PATHS`): `/auth/login`, `/auth/refresh`,
  `/auth/logout`, `/health`, `/`, `/docs`, `/openapi.json`, `/redoc`.
- **CORS**: allowlist explícita de orígenes (`futmondo-app.fly.dev`,
  `futmondo.localhost`, `localhost:4200/3000`) + `EXTRA_CORS_ORIGIN` opcional.
- **Seguridad**: `JWT_SECRET` no-default obligatorio en arranque (NFR1.1); nunca
  material de credencial en excepciones/logs (reglas afirmadas). Detalle de
  postura de seguridad en `code-quality-assessment.md`.

## Integraciones salientes (API consumidas)

Evidencia: `backend/app/services/`. Contratos externos consumidos:

- **API Futmondo** — `futmondo_client.py` — autenticación de usuario y datos de
  campeonato (transacciones, plantillas, cláusulas, etc.).
- **API Sofascore** — `sofascore_client.py` vía `curl_cffi` — ratings/odds; error
  tipado `SofascoreIPBanError` (`integration_errors.py`).
- **LLM externos** (solo asistente) — Groq (`openai/gpt-oss-120b`) con **fallback
  a Gemini** (`google-genai`).

Detalle de versiones de librería en `technology-stack.md`; grafo de dependencias
en `dependencies.md`.
