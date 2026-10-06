# Component Inventory — futmondo-analytics

Lista completa de componentes con responsabilidad y dependencias. Los encabezados
`###` son los nombres de componente usados verbatim en el bloque Scope of Analysis
de `reverse-engineering-timestamp.md`.

### angular-app (frontend SPA/PWA)

- **Responsabilidad**: SPA/PWA Angular 22; pantallas de usuario, servicios HTTP,
  interceptor de auth, service worker.
- **Dependencias**: Angular Material/CDK, Chart.js + ng2-charts, rxjs, marked;
  consume `backend` vía `/api/v1/*` y `/auth/*` a través de nginx.

### calculator-component

- **Responsabilidad**: pantalla `/calculator` (`calculator.component.ts/.html`),
  planificador de ventas/proyección de balance. `loadData()` lee en paralelo
  `rosterService.getMyRoster()`, `GET /api/v1/market/today`,
  `rosterService.getOnSale()`; `computed()` calcula `selectedTotal`, `onSaleTotal`,
  `futureBalance`; acciones `sellPlayers()` → `POST /api/v1/roster/sell`,
  `cancelSale()`. Proyección temporal lineal (`getProjectedValue`).
- **Dependencias**: `rosterService`, `/api/v1/market/today`, `authGuard`. **Sin
  spec** hoy (characterization-first pendiente). Foco del intent.

### backend (FastAPI app)

- **Responsabilidad**: app FastAPI (`main.py`), montaje de routers, `AuthMiddleware`,
  mount público de fotos, configuración fail-fast (`config.py`).
- **Dependencias**: servicios de dominio, sync, auth; Neon PostgreSQL.

### prizes-domain

- **Responsabilidad**: cálculo de dinero de premio. `calculator.py:calculate_round_prizes()`
  (función pura, reglas BR1.1-BR3.2) y `team_prizes_writer.py:replace_team_prizes()`
  (reemplazo transaccional atómico sobre `team_prizes`).
- **Dependencias**: consumido por `DataSyncService.sync_prizes()`; `team_prizes`
  leída por `player-finances`. Patrón de referencia para lógica nueva testeable.

### player-finances-endpoint

- **Responsabilidad**: `GET /api/v1/player-finances/` (`player_finances.py`); agrega
  finanzas por usuario leyendo `team_prizes` como única fuente de verdad.
- **Dependencias**: `prizes-domain` (vía `team_prizes`), Neon. Contiene SQL inline
  (`_get_finance_config`) — deuda registrada (ver `code-quality-assessment.md`).

### data-sync-service

- **Responsabilidad**: orquestación del sync asíncrono de 11 pasos
  (`data_sync_service.py` + `sync/**`); llama a `sync_prizes()`. Reporta `StepStatus`
  (OK/DEGRADED).
- **Dependencias**: `prizes-domain`, clientes Futmondo/Sofascore, Neon. God-file en
  descomposición DDD.

### data-manager

- **Responsabilidad**: gestión de datos del dominio; `data_manager_v2.py` (fachada
  delgada) delega a 12 submódulos DDD `data_manager/<responsabilidad>/{application,
  infrastructure,domain}`.
- **Dependencias**: Neon, puertos de dominio. God-file en descomposición.

### analytics-and-assistant

- **Responsabilidad**: analítica (`analytics/**`) y asistente IA (`assistant/**`,
  `assistant_service.py` fachada fina) con fachadas + puertos + adaptadores.
- **Dependencias**: Neon; proveedores IA Gemini/Groq (asistente).

### auth-and-security

- **Responsabilidad**: autenticación JWT y `AuthMiddleware` (`auth/**`), almacenes de
  sesión/estado (`stores/**`), cifrado de credenciales (`security/**`,
  `FUTMONDO_CRED_KEY`).
- **Dependencias**: API Futmondo (validación de login), Neon. `config.py` fuerza
  `JWT_SECRET` no-default.

### external-clients

- **Responsabilidad**: clientes de integración saliente — `futmondo_client.py`
  (auth por usuario), `sofascore_client.py` (`curl_cffi`).
- **Dependencias**: APIs externas Futmondo y Sofascore.

### proxy-nginx

- **Responsabilidad**: reverse proxy nginx (local `proxy/` y prod
  `angular-app/nginx*.conf`); sirve SPA y hace proxy de `/api/*` y `/auth/*`.
- **Dependencias**: `backend`.

### cron-jobs

- **Responsabilidad**: máquinas Fly one-shot para sync programado
  (`daily-sync.yml`, `sofascore-sync.yml`, `cron/`).
- **Dependencias**: `backend` / `data-sync-service`.

## Sources

- `developer-scan.md`: Packages Found, APIs Discovered, Handoff Summary, Technical
  Debt Signals.
- Responsabilidades cruzadas en `architecture.md`, `code-structure.md`,
  `api-documentation.md`.
