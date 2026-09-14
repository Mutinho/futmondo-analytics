# Arquitectura del Sistema — Futmondo Analytics

> Reverse-engineering. Escaneo previo FULL preservado; rerun FOCUSED sobre
> `backend/app/services/` y `backend/tests/`. Diagramas Mermaid validados; cada
> diagrama incluye un fallback de texto inmediatamente debajo.

## Visión general del sistema

Futmondo Analytics es una arquitectura de **tres componentes desplegables** más un
proceso cron one-shot:

- **angular-app/** — frontend Angular 22 (PWA/SPA + service worker). En producción
  la propia imagen del frontend incluye un nginx (`angular-app/nginx.prod.conf`)
  que proxya `/api` y `/auth` al backend.
- **backend/** — API FastAPI (Python 3.12) con arquitectura por capas
  (api → services → auth → core → models). Concentra la lógica de negocio, la
  sincronización y los clientes de integración externa.
- **proxy/** — nginx reverse proxy, **solo local** (`docker-compose.yml`). En
  producción su rol lo cumple el nginx embebido en el frontend.
- **cron/** — app Fly.io `futmondo-cron` que reutiliza `backend/Dockerfile` y
  ejecuta `python scripts/sync_data.py`.

La persistencia productiva es **Neon PostgreSQL** (Frankfurt), a través de una capa
de abstracción (`db_connection.py`) que soporta además SQLite y Turso/libSQL
(ramas heredadas, ver deuda técnica). Las integraciones externas son la API
oficial de Futmondo (`requests`) y la API no oficial de Sofascore (`curl_cffi`
con `impersonate="chrome"`).

## Estilo arquitectónico

**Monolito modular desplegado como servicios separados** (híbrido). El backend es
un monolito FastAPI por capas (no microservicios: un único proceso, una única
base de código, routers montados en `main.py`). El frontend es una SPA
independiente. La separación en apps Fly.io responde a la topología de despliegue
y coste, no a límites de dominio microservicio. Evidencia: `backend/app/main.py`
monta 23 routers en un solo proceso; no hay comunicación inter-servicio backend
salvo el proxy HTTP frontend→backend.

## Relaciones entre componentes

```mermaid
graph TD
    Browser["iPhone / Browser (PWA)"]
    FE["angular-app (Angular 22 + nginx.prod.conf)"]
    BE["backend (FastAPI, 23 routers)"]
    DB[("Neon PostgreSQL")]
    FM["API Futmondo (oficial)"]
    SS["API Sofascore (no oficial)"]
    CRON["cron (futmondo-cron, sync_data.py)"]
    AI["Gemini / Groq (asistente IA)"]

    Browser -->|HTTPS| FE
    FE -->|/api/*, /auth/* proxy| BE
    BE -->|SQL, pool 5-20| DB
    BE -->|requests| FM
    BE -->|curl_cffi impersonate| SS
    BE -->|chat| AI
    CRON -->|reutiliza imagen backend| DB
    CRON --> FM
```

Fallback de texto: el navegador habla por HTTPS con `angular-app`; el nginx del
frontend proxya `/api/*` y `/auth/*` hacia `backend`. El `backend` accede a Neon
PostgreSQL mediante un pool de conexiones (5-20), consume la API Futmondo con
`requests`, la API Sofascore con `curl_cffi`, y el asistente IA (Gemini/Groq). El
proceso `cron` reutiliza la imagen del backend y escribe en la misma base de datos
consumiendo Futmondo directamente.

## Flujo de datos

```mermaid
flowchart LR
    U["Usuario"] --> L["POST /auth/login"]
    L --> V["Valida credenciales contra Futmondo"]
    V --> J["Emite JWT access + refresh"]
    U --> T["POST /api/v1/sync/trigger"]
    T --> TH["threading.Thread daemon (background)"]
    TH --> SVC["DataSyncService (11 pasos)"]
    SVC --> DB[("PostgreSQL")]
    U --> P["GET /api/v1/sync/task/{id} (polling)"]
    P --> TM["TaskManager (estado in-memory)"]
```

Fallback de texto: el usuario hace login, el backend valida contra Futmondo y
emite JWT; el usuario dispara `sync/trigger`, que arranca un hilo daemon en
background ejecutando `DataSyncService` (11 pasos) que escribe en PostgreSQL; el
usuario consulta el progreso por polling contra el `TaskManager`, cuyo estado vive
solo en memoria del proceso.

## Diagramas de Interacción (transacciones de negocio clave)

### Login (autenticación)

```mermaid
sequenceDiagram
    participant U as Usuario/PWA
    participant BE as backend /auth/login
    participant FM as API Futmondo
    participant SS as SessionStore (in-memory)
    participant DB as PostgreSQL

    U->>BE: POST /auth/login (email, password)
    BE->>FM: FutmondoClient.login()
    FM-->>BE: ok / 401
    alt credenciales válidas
        BE->>DB: upsert_user + save_refresh_token
        BE->>SS: store_session(user_id, client, email, password)
        BE-->>U: 200 access_token + Set-Cookie refresh (HttpOnly)
    else inválidas
        BE-->>U: 401 credenciales incorrectas
    end
```

Fallback de texto: el usuario envía email/password a `/auth/login`; el backend
crea un `FutmondoClient` y valida contra Futmondo. Si es válido, hace upsert del
usuario y guarda el hash del refresh token en BD, almacena la sesión Futmondo en
el `SessionStore` en memoria (incluidas las credenciales), devuelve el access
token en el cuerpo y el refresh token como cookie HttpOnly (`path=/auth`,
`samesite=lax`, `secure` según `COOKIE_SECURE`). Si es inválido, responde 401.

### Sincronización asíncrona (11 pasos)

```mermaid
sequenceDiagram
    participant U as Usuario/PWA
    participant BE as backend /api/v1/sync
    participant TM as TaskManager (in-memory)
    participant TH as Thread daemon
    participant SVC as DataSyncService
    participant DB as PostgreSQL

    U->>BE: POST /sync/trigger
    BE->>TM: get_active_task (dedupe)
    alt ya hay sync activo
        BE-->>U: 409 sync en curso
    else libre
        BE->>TM: create_task
        BE->>TH: threading.Thread(daemon).start()
        BE-->>U: 202 task_id
        loop 11 pasos
            TH->>SVC: sync_<paso>()
            SVC->>DB: upsert datos
            TH->>TM: update_progress
        end
        TH->>TM: mark_completed / mark_failed
    end
    loop polling
        U->>BE: GET /sync/task/{id}
        BE->>TM: get_task
        BE-->>U: status + progress
    end
```

Fallback de texto: `sync/trigger` comprueba si ya hay un sync activo para el
campeonato (dedupe → 409); si no, crea la tarea, lanza un hilo daemon y responde
202 con `task_id`. El hilo ejecuta los 11 pasos secuenciales de
`DataSyncService`, actualizando el progreso en el `TaskManager` tras cada paso;
los pasos `prizes` y `phantoms` degradan sus excepciones a "non-critical". El
usuario consulta el progreso por polling contra `/sync/task/{task_id}`. Punto
frágil: el estado del `TaskManager` y la sesión (`SessionStore`) viven solo en
memoria; un reinicio de la máquina Fly pierde la tarea y la sesión.

### Puja / Mercado

```mermaid
sequenceDiagram
    participant U as Usuario/PWA
    participant BE as backend /api/v1/market
    participant DB as PostgreSQL
    participant FM as API Futmondo

    U->>BE: GET /market/today
    BE->>DB: histórico transacciones (market_value_at_purchase)
    BE-->>U: jugadores + puja sugerida + rating Sofascore
    U->>BE: POST /market/bid (player, price)
    BE->>FM: proxy /1/market/bid (price query param)
    FM-->>BE: resultado puja
    BE-->>U: confirmación / error
```

Fallback de texto: el usuario pide el mercado del día; el backend calcula la puja
sugerida a partir del histórico real de sobrepago (`_calculate_suggested_bid`,
margen ±25%) y adjunta el rating Sofascore. Al pujar, el backend proxya la puja a
`/1/market/bid` de Futmondo con `price` como query param entero. Riesgo: el
backend NO valida rango/positividad de `price` (solo el frontend valida min/max).

### Analítica bajo test — `AnalyticsService` con `StubDM` (foco del rerun)

```mermaid
sequenceDiagram
    participant T as pytest fixture
    participant AS as AnalyticsService
    participant CACHE as _team_cache / _player_cache (in-memory)
    participant DM as StubDM (fake DataManager)

    T->>AS: monkeypatch __init__ -> fake_init(self) { self.dm = stub_dm }
    Note over AS,CACHE: fake_init NO inicializa _team_cache ni _player_cache
    T->>AS: get_championship_trends / get_clause_network / get_player_value_trend
    AS->>CACHE: lee/escribe _team_cache / _player_cache
    CACHE-->>AS: AttributeError (atributos ausentes)
    AS->>DM: get_* (datos fake)
    DM-->>AS: dicts sin player_name / con price
    Note over AS: get_player_value_trend emite last_transaction_price (el test exige latest_price)
```

Fallback de texto: la fixture de `test_analytics_service.py` sustituye el
`__init__` de `AnalyticsService` por un `fake_init` que solo asigna `self.dm =
stub_dm` y NO inicializa `_team_cache` ni `_player_cache`. Los métodos públicos
`get_championship_trends` (vía `_safe_team_info`), `get_clause_network` (vía
`_resolve_team`/`_build_team_lookup`) y `get_player_value_trend` (vía
`_safe_player_info`) leen/escriben esos atributos y lanzan `AttributeError`.
Además, `get_player_value_trend` emite la clave `last_transaction_price` mientras
el test espera `latest_price`, produciendo un `KeyError` independiente. Detalle y
punto de arreglo en `code-quality-assessment.md`.

## Decisiones de diseño destacables

- **JWT en dos tokens**: access (60 min, en memoria del navegador) + refresh (30
  días, cookie HttpOnly) — reduce superficie XSS. Fail-fast del secreto JWT en
  arranque (`config.py::resolve_jwt_secret`).
- **Sync desacoplada por hilo + polling**: evita timeouts HTTP en operaciones
  largas, a costa de estado no durable.
- **Middleware de auth central** (`AuthMiddleware`): protege todo `/api/v1/*`
  salvo `AUTH_EXCLUDED_PATHS`.
- **Capa de abstracción de BD multi-backend**: flexibilidad histórica
  (SQLite/Turso/PostgreSQL) hoy con ramas muertas.
- **Caché de instancia en `AnalyticsService`**: `_team_cache` y `_player_cache`
  se inicializan en el `__init__` real (analytics_service.py:16-17) y actúan como
  memoización por instancia; los métodos públicos asumen su presencia. Es un
  acoplamiento a estado de instancia que la caracterización debe respetar.

## ADR — Registro de decisión (síntesis del rerun)

### ADR-RE-001: Punto de arreglo de la suite de `AnalyticsService`

- **Status**: Proposed (decisión final del stage code-generation).
- **Context**: Tres tests de caracterización (`test_championship_trends`,
  `test_clause_network`, `test_player_value_trend`) fallan. Dos raíces: (a) la
  fixture `fake_init` omite `_team_cache`/`_player_cache` presentes en el
  `__init__` real; (b) divergencia de nombre de clave `last_transaction_price`
  (servicio) vs `latest_price` (test). Restricción dura: no romper los otros
  tests del fichero ni el resto de la suite; regla coste 0€; scope `bugfix`.
- **Decision**: preferir el arreglo en el **test** (Alternativa A): inicializar
  `_team_cache`/`_player_cache` en `fake_init` y alinear la aserción de clave con
  la salida real del servicio. Es el cambio de menor blast radius: no toca el
  contrato de salida consumido por `/api/v1/analytics/*` (skimmed only).
- **Consequences**:
  - Positivo: cero riesgo para consumidores del servicio; la caracterización
    congela el comportamiento real actual, que es el objetivo de una suite de
    caracterización.
  - Negativo: mantiene la deuda de naming (`last_transaction_price` vs
    `latest_price`) y el acoplamiento de la fixture a atributos privados.
  - Neutral: si el negocio decidiera que la clave pública debe llamarse
    `latest_price`, ese es un cambio de contrato separado (Alternativa B) que
    exige revisar los endpoints `/api/v1/analytics/*` antes de renombrar.
- **Alternatives Considered**:
  - **Alternativa B — tocar el servicio** (renombrar/duplicar clave a
    `latest_price` y endurecer los métodos ante caches ausentes): riesgo de
    romper el contrato consumido por endpoints no leídos en profundidad;
    rechazada para un scope `bugfix` sin verificación de esos consumidores.
  - **Alternativa C — no monkeypatchear `__init__`** y usar el `__init__` real
    con un DM fake inyectado: cambio mayor de la estrategia de test; rechazada
    por blast radius en toda la fixture del fichero.

## Oportunidades de mejora arquitectónica

- Persistir el estado de sync y las sesiones (durabilidad frente a reinicios Fly).
- Podar el multi-backend de BD hacia Neon único.
- Romper los "god files" (`data_manager_v2.py`, `data_sync_service.py`,
  `analytics_service.py`).
- Unificar el contrato del dict de salida de `AnalyticsService` (fuente única de
  verdad para nombres de clave como `latest_price`/`last_transaction_price`).
- Hacer transaccional el reemplazo de la caché Sofascore (hoy DELETE antes de
  repoblar).
