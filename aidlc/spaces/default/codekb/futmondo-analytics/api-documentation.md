# Documentación de APIs — Futmondo Analytics

> Reverse-engineering. Escaneo previo FULL preservado; rerun FOCUSED sobre
> `backend/app/services/` y `backend/tests/`. APIs internas expuestas por el
> backend y APIs externas consumidas. Los nombres de ruta y parámetros se
> mantienen literales.

## API interna (REST — FastAPI)

El backend expone una API REST en `backend/app/main.py`: 23 routers montados bajo
`/api/v1/*` más el router de auth bajo `/auth/*`. Autenticación por Bearer JWT
para todo `/api/v1/*` salvo `AUTH_EXCLUDED_PATHS`
(`/auth/login`, `/auth/refresh`, `/auth/logout`, `/health`, `/`, `/docs`,
`/openapi.json`, `/redoc`).

### Autenticación (`/auth/*`, `backend/app/auth/routes.py`)

| Endpoint | Método | Contrato |
|----------|--------|----------|
| `/auth/login` | POST | Body `LoginRequest` (email, password). Valida contra Futmondo; devuelve `access_token` (60 min) en cuerpo + refresh (30 días) en cookie HttpOnly `futmondo_refresh_token` (`path=/auth`, `samesite=lax`, `secure` por `COOKIE_SECURE`). 401 si credenciales inválidas. |
| `/auth/refresh` | POST | Renueva el access token leyendo el refresh de la cookie. |
| `/auth/logout` | POST | Revoca la sesión y limpia la cookie de refresh. |

### Endpoints de dominio (`/api/v1/*`)

Notables (evidencia en `main.py` y endpoints leídos en profundidad):

| Endpoint | Método | Descripción / contrato |
|----------|--------|------------------------|
| `/api/v1/sync/trigger` | POST | Dispara sync asíncrona. Query `sync_type` (`all`/`transactions`/`clauses`/`dream_teams`/`rosters`/`players`), `championship_id`. Devuelve **202** con `task_id`; **409** si ya hay sync activo. |
| `/api/v1/sync/task/{task_id}` | GET | Polling de progreso: `status` (pending/running/completed/failed), `current_step`, `progress`, `result`, `error`. 404 si no existe la tarea. |
| `/api/v1/sync/status` | GET | Última metadata de sync por tipo de dato. |
| `/api/v1/sync/last-sync` | GET | Fecha de la última sync completa (`MAX(last_sync_date)`). |
| `/api/v1/sync/sofascore` | POST | `DELETE FROM sofascore_cache` seguido de re-poblado jugador a jugador (no transaccional respecto al fetch externo). |
| `/api/v1/market/today` | GET | Mercado del día: jugadores + puja sugerida (histórico real de sobrepago, margen ±25%) + rating Sofascore. |
| `/api/v1/market/bid` | POST | Proxy de puja a `/1/market/bid` de Futmondo; `price` como query param entero (sin validación de rango en backend). |
| `/api/v1/market/cancelbid` | POST | Cancela la puja en Futmondo. |
| `/api/v1/database/reset` | POST | Destructivo; protegido tras `ENABLE_DB_ADMIN` (404 por defecto). |
| `/api/v1/database/populate` | POST | Destructivo; mismo guard `ENABLE_DB_ADMIN`. |
| `/api/v1/photos/{player_id}` | GET | Sirve foto local (redirect 302 a `/static/photos/...`) o descarga de Futmondo; placeholder SVG por defecto. NO figura en `AUTH_EXCLUDED_PATHS` (revisar exposición). |
| `/api/v1/assistant/*` | POST | Chat IA (Gemini/Groq), persistencia en `assistant_conversations`. |
| `/api/v1/analytics/balances` | GET | Presupuestos por equipo. |
| `/api/v1/player-finances/` | GET | Finanzas por usuario. |
| `/api/v1/user/me`, `/api/v1/user/championships` | GET/POST/DELETE | Info y CRUD de campeonatos del usuario. |
| `/api/v1/championships` | GET | Lista campeonatos del usuario. |
| `/health`, `/` | GET | Health check y raíz (públicos). |

Routers adicionales montados (dominio): `matchdays` (doble montaje en
`/api/v1/matchdays` y `/v1/matchdays`), `initialize`, `statistics`,
`user-stats`, `clausulable-players`, `roster`, `favorites`, `transactions`,
`sofascore` (detail), `phantoms`.

### Contrato interno de `AnalyticsService` (consumido por `/api/v1/analytics/*`, `statistics`, `clausulable-players`)

`AnalyticsService` no es una API HTTP en sí, pero sus dicts de salida forman el
contrato de datos que los routers de analítica serializan. Puntos observados en
el rerun (evidencia en `analytics_service.py`):

- `get_player_value_trend` (l.437) emite la clave `last_transaction_price`
  (l.474), NO `latest_price`. La cadena `latest_price` no aparece en
  `backend/app/`. La suite de caracterización espera `latest_price`, lo que
  revela una divergencia de contrato (detalle en `code-quality-assessment.md`).
- **Advertencia de contrato**: renombrar la clave de salida en el servicio a
  `latest_price` afectaría a los consumidores `/api/v1/analytics/*` (skimmed
  only en este rerun); debe verificarse antes de cualquier renombrado del lado
  del servicio.

## APIs externas consumidas

### API Futmondo (oficial) — `backend/app/services/futmondo_client.py`

- Cliente `requests.Session`. Endpoints versionados heterogéneos:
  `/5/login/with_mail`, `/2/user/activechampionships`, `/1/market/players`,
  `/1/player/summary`, `/1/market/bid`, etc.
- Patrón de payload: `{header:{token,userid}, query:{...}, answer:{}}`.
- Timeouts 10-15 s. Token de sesión Futmondo en memoria por usuario.

### API Sofascore (no oficial) — `backend/app/services/sofascore_client.py`

- `curl_cffi` con `impersonate="chrome"` para evadir el fingerprinting TLS.
- Throttle de 750 ms entre llamadas; `BASE_URL` hardcodeado; sin API key.
- Riesgo de baneo de IP (tratado como exit code 2 en `sofascore-sync.yml`).

### Servicios IA — `backend/app/services/assistant_service.py`

- Gemini (`google-genai`) con fallback a Groq (`groq`) para el chat del asistente.

## Notas de contrato

- Todos los `/api/v1/*` requieren `Authorization: Bearer <access_token>`.
- Los datos del campeonato se consultan con la sesión Futmondo del usuario
  logado (`_helpers.get_user_futmondo_client`); un reinicio que pierda la sesión
  in-memory devuelve 403 "sesión expirada".
