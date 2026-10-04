# Architecture

## System Overview

Futmondo Analytics es un sistema **cliente-servidor de dos apps desplegables**
sobre un mono-repo: un frontend Angular (PWA, `angular-app/`) y un backend
FastAPI (Python 3.12, `backend/app/`), con Neon PostgreSQL como almacén y dos
integraciones externas (API Futmondo, API Sofascore). En producción nginx sirve
la SPA y hace de reverse proxy hacia el backend (ver `README.md`).

## Architectural Style

**Monolito modular por capas** en el backend, con **contextos acotados DDD** en
progresiva extracción (oleadas `prizes/`, `analytics/`, `assistant/`, y la raíz
`sync/` con DOS pilotos: `match_odds` y `clauses`). No es microservicios: un único
servicio FastAPI concentra routers + servicios + integraciones + acceso a datos.
Evidencia: capas `api/v1/endpoints/` → `services/` → acceso a datos
(`data_manager_v2.py`) dentro de un solo proceso (`backend/app/main.py`). El
estilo objetivo del refactor es **hexagonal por dominio** (domain `ports.py` /
application `orchestrator.py` / infrastructure `*_adapter.py` / facade fino), ya
demostrado end-to-end en `analytics/`, `assistant/` y, para sync, en
`sync/match_odds/` y `sync/clauses/`.

Trade-off asumido (decisión de arquitectura, Inception): la extracción se hace
**por dominio y envolviendo verbatim** `DataManagerV2` tras un adapter en lugar
de reescribir el acceso a datos. Pros: equivalencia funcional estricta (FR5),
riesgo bajo y rollback quirúrgico por dominio. Contras: `DataManagerV2` sigue
siendo un god-file (~166 KB) y el SQL crudo permanece, sólo cambia su punto de
invocación. Alternativa descartada: reescribir el acceso a datos a la vez —
rechazada por su blast radius y por el mandato afirmado de no ampliar/reescribir
los god-files.

## Component Relationships

```mermaid
graph TD
  Browser["Browser / iPhone PWA"] -->|HTTPS| Nginx["nginx reverse proxy"]
  Nginx -->|/| NG["Angular SPA (angular-app)"]
  Nginx -->|/api /auth| API["FastAPI (backend/app/main.py)"]

  API --> Auth["auth/ (JWT + session/token stores)"]
  API --> Routers["api/v1/endpoints/ (21 routers)"]

  Routers --> SyncRouter["endpoints/sync.py (sync router)"]
  Routers --> Services["services/ (business logic)"]
  SyncRouter --> DSS["DataSyncService (data_sync_service.py)"]
  Services --> DSS
  Services --> SyncPkg["sync/ (DDD por dominio; pilotos match_odds + clauses)"]
  Services --> Analytics["analytics/ (DDD Wave 1)"]
  Services --> Assistant["assistant/ (DDD Wave 2)"]
  Services --> Prizes["prizes/ (calculator + team_prizes_writer)"]

  DSS --> FClient["futmondo_client.py"]
  DSS --> SClient["sofascore_client.py"]
  DSS --> Prizes
  DSS -->|delegacion fina| SyncPkg
  DSS --> DM["data_manager_v2.py (DataManagerV2)"]
  SyncPkg -->|solo en el adapter| DM
  Analytics --> DM
  Assistant --> DM
  SyncRouter -->|SQL-en-router: deuda| DM

  DM --> Neon[("Neon PostgreSQL")]
  FClient -->|HTTP| Futmondo["API Futmondo"]
  SClient -->|curl_cffi| Sofascore["API Sofascore"]
```

<!-- Text fallback: El navegador/PWA habla HTTPS con nginx, que sirve la SPA Angular en / y hace proxy de /api y /auth al backend FastAPI. FastAPI expone 21 routers (api/v1/endpoints/) y las rutas de auth; el sync router (endpoints/sync.py) y el resto de routers llaman a services/. DataSyncService consume futmondo_client y sofascore_client, delega el calculo de premios a prizes/ y (para match_odds y clauses) delega de forma fina al paquete sync/; persiste via DataManagerV2 contra Neon. Los contextos DDD (sync/, analytics/, assistant/) tocan DataManagerV2 solo en su adapter de infraestructura. Existe deuda de SQL-en-router: casi todos los routers acceden a DataManagerV2 con SQL crudo inline. -->

## Data Flow

Ingreso de petición → router (`api/v1/endpoints/`) → servicio de aplicación
(`services/`) → acceso a datos (`DataManagerV2`) → Neon. Las lecturas de datos
externos entran por `futmondo_client` / `sofascore_client` durante el sync y se
materializan en Neon. Ver el flujo asíncrono de sync abajo.

## Interaction Diagrams

### 1. Login / Auth flow

```mermaid
sequenceDiagram
  participant U as Browser (Angular)
  participant A as FastAPI auth/routes.py
  participant F as futmondo_client
  participant S as SessionStore / TokenStore
  U->>A: POST /auth/login (email, password)
  A->>F: validar credenciales contra API Futmondo
  F-->>A: sesion Futmondo (12h TTL)
  A->>S: crear sesion + persistir refresh token
  A-->>U: JWT access (1h, en memoria) + refresh (cookie HttpOnly, 30d)
  Note over U,A: peticiones /api/v1/* llevan Bearer access token
  U->>A: POST /auth/refresh (cookie)
  A->>S: validar refresh token
  A-->>U: nuevo JWT access
```

<!-- Text fallback: El navegador hace POST /auth/login con las credenciales Futmondo; el backend las valida contra la API de Futmondo via futmondo_client, crea la sesion y persiste el refresh token en el store, y devuelve un JWT access (1h, en memoria) mas un refresh token (cookie HttpOnly, 30d). Las peticiones a /api/v1/* llevan Bearer; POST /auth/refresh renueva el access desde la cookie. -->

### 2. Async sync transaction flow (router → DataSyncService facade → per-domain orchestrator → port/adapter → DataManagerV2/SQL → Neon)

```mermaid
sequenceDiagram
  participant U as Browser (Angular)
  participant R as endpoints/sync.py (POST /trigger)
  participant W as _run_sync_in_background (thread)
  participant D as DataSyncService (facade)
  participant O as sync/<domain>/orchestrator (patron match_odds + clauses)
  participant F as futmondo_client
  participant P as prizes (calculator + team_prizes_writer)
  participant A as *_adapter (envuelve DataManagerV2 verbatim)
  participant M as DataManagerV2
  participant N as Neon PostgreSQL
  U->>R: POST /api/v1/sync/trigger
  R->>R: crear task_id, status 202
  R->>W: lanzar thread background (daemon)
  W->>D: sync_players_full (primero por FK), luego el resto en orden fijo
  loop por cada dominio sync_*
    alt dominio ya extraido (match_odds, clauses)
      D->>O: delegacion fina (import perezoso + data=Adapter(dm=self.dm))
      O->>F: ingesta (get_match_list / get_clauses ...) + time.sleep throttling
      F-->>O: datos crudos o Integration*Error
      O->>A: save_* / update_sync_metadata (via port Protocol)
      A->>M: delega verbatim (solo kwargs originales)
      M->>N: escritura
      O-->>D: SyncResult (forma por dominio, byte-a-byte)
    else dominio aun en el god-file
      D->>F: ingesta inline + time.sleep throttling
      D->>M: SQL/persistencia inline (incl. SQL crudo sobre self.dm.db)
      M->>N: escritura
      D-->>D: SyncResult inline (forma por dominio)
    end
    W->>W: tm.update_progress[clave literal] (incl. team_standings, dream_teams)
  end
  D->>P: sync_prizes: calculate_round_prizes + replace_team_prizes (tx atomica)
  P->>N: upsert conjunto + DELETE stale NOT IN (all-or-nothing)
  D-->>W: dict agregado por dominio (10 claves literales)
  W->>W: phantoms extra + manejo DEGRADED via record_degraded_step
  U->>R: GET /api/v1/sync/task/{task_id} (polling progreso)
```

<!-- Text fallback: POST /api/v1/sync/trigger crea un task_id, responde 202 y lanza _run_sync_in_background en un thread daemon. El worker invoca el surface publico de DataSyncService en orden fijo (players primero por dependencia FK) con las mismas 10 claves que sync_all, actualizando progress[clave literal] por paso (incluidas team_standings->sync_round_rankings y dream_teams->sync_dream_teams_mvps), mas phantoms (helper del router). Para un dominio ya extraido (match_odds, clauses) DataSyncService delega de forma fina al orchestrator del paquete sync/<domain>/ (import perezoso, data=Adapter(dm=self.dm)), que ingesta desde futmondo_client (excepciones tipadas Integration*Error) con time.sleep de throttling, persiste a traves de un port Protocol cuyo *_adapter envuelve DataManagerV2 verbatim contra Neon (reenviando solo los kwargs originales), y devuelve un SyncResult cuya forma depende del dominio. Para un dominio aun en el god-file, DataSyncService mezcla ingesta, time.sleep de throttling y SQL/persistencia inline (incluido SQL crudo sobre self.dm.db). sync_prizes orquesta la ingesta, delega el calculo puro en calculate_round_prizes y persiste el conjunto de forma atomica con replace_team_prizes (upsert + DELETE ... NOT IN en una sola transaccion, all-or-nothing). El manejo DEGRADED de prizes/phantoms vive en el router via record_degraded_step. El frontend hace polling con GET /api/v1/sync/task/{task_id}. -->

### 3. Target DDD layering per domain (match_odds / clauses como molde)

```mermaid
graph LR
  DSS["DataSyncService.sync_<domain> (delegacion fina)"] --> ORCH["<Domain>SyncOrchestrator (application)"]
  ORCH --> PORT["domain/ports.py (Protocol consumer-owned, sin SQL)"]
  ORCH --> CLIENT["FutmondoClient (ingesta inyectada)"]
  PORT -.implementado por.-> ADAPTER["infrastructure/<domain>_adapter.py (unico SQL)"]
  ADAPTER --> DMV2["DataManagerV2 (envuelto verbatim, skip_init=True)"]
```

<!-- Text fallback: El metodo publico sync_<domain> de DataSyncService es una delegacion fina al <Domain>SyncOrchestrator (capa application). El orchestrator depende de un Protocol consumer-owned en domain/ports.py (sin SQL, sin framework) y del FutmondoClient inyectado para la ingesta; el port lo implementa infrastructure/<domain>_adapter.py, unico punto con SQL, que envuelve DataManagerV2 verbatim (DataManagerV2(skip_init=True) por defecto, kwargs originales preservados). Este es el molde probado por match_odds y clauses, a replicar por los 8 dominios pendientes. -->

## Key Design Decisions

- **Superficie pública estable de sync**: `DataSyncService` con 10 `sync_*` +
  `sync_all()` (10 claves literales, orden fijo) es el contrato a preservar en el
  refactor (ver `api-documentation.md`). El worker `_run_sync_in_background` del
  router replica ese orden/claves y añade `phantoms`, por lo que cualquier cambio
  de firma rompería el worker.
- **Extracción DDD por dominio (patrón probado por 2 pilotos)**: `sync/match_odds/`
  y `sync/clauses/` son el patrón de referencia exacto (orchestrator + domain port
  `Protocol` + infrastructure adapter que envuelve `DataManagerV2` verbatim). El
  método público queda como delegación delgada: import perezoso del orquestador +
  del adapter, instancia con `client=self.client`,
  `championship_id=self.championship_id`, `data=DataManager<Domain>Adapter(dm=self.dm)`,
  y `return orchestrator.sync()`. `prizes/` aporta el cálculo puro y la escritura
  atómica pero aún le falta el facade/orchestrator uniforme.
- **Adapter con default de producción inyectable**: `__init__(self, dm=None)` con
  default `DataManagerV2(skip_init=True)`; en `update_sync_metadata` reenvía SÓLO
  los kwargs que la llamada inline original suministraba (fila persistida
  idéntica). NO se añade ningún método a `data_manager_v2.py`.
- **Escritura atómica set-replacement**: `replace_team_prizes` corrige el antiguo
  `try/except → logger.warning` que dejaba estado mixto; es el patrón de
  referencia para reemplazos de conjunto (upsert + `DELETE ... NOT IN` en una sola
  transacción, all-or-nothing, el fallo propaga). `_save_favorites`
  (DELETE+INSERT) es candidato a elevarse a este patrón o quedar como deuda
  registrada según el alcance refactor/Minimal.
- **Manejo de errores tipado**: fatal `IntegrationBanError` propaga; recoverable
  (`IntegrationTimeoutError` / `IntegrationUnparseableError` / `IntegrationRequestError`)
  degrada vía `record_degraded_step`. Ninguna credencial/token alcanza mensajes de
  excepción, `repr` ni logs (`_log_integration_failure`, NFR1/BR4.2). Implicación
  de seguridad: esta garantía debe preservarse en cada adapter extraído.
- **Auth JWT dual**: access en memoria + refresh en cookie HttpOnly (defensa
  contra XSS/robo de token).

## Improvement Opportunities

- Retirar el SQL-en-router llevándolo tras adaptadores de infraestructura.
- Completar la descomposición de `data_sync_service.py` (8 de 10 dominios aún
  mezclan ingesta/SQL/cálculo; `sync_match_odds` y `sync_clauses` delegan del todo
  y `sync_prizes` delega cálculo/escritura) sin ampliar `data_manager_v2.py`.
  El SQL crudo sobre `self.dm.db` (`sync_transactions` ALTER/UPDATE,
  `_enrich_market_values`, `_save_favorites`, `sync_prizes` vía `get_db()`) debe
  envolverse verbatim tras port+adapter. Detalle y medidas en
  `code-quality-assessment.md`.
