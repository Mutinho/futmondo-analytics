# Arquitectura — futmondo-analytics

## Visión General del Sistema

futmondo-analytics es un sistema de dos servicios desplegados por separado en Fly.io
(región `cdg`/París), respaldados por una base de datos Neon PostgreSQL (Frankfurt):

- **Backend** `futmondo-api`: aplicación FastAPI (Python 3.12), puerto 8000, healthcheck
  `/health`.
- **Frontend** `futmondo-app`: SPA/PWA Angular 22 servida por nginx (puerto 80), que además
  actúa como reverse proxy hacia el backend para `/api/*` y `/auth/*`.

Además del runtime, el repositorio incluye una **capa de entrega** (GitHub Actions +
Fly.io) que gobierna cómo el código llega a producción; su topología de verificación se
describe en las secciones de flujo de más abajo y su estado de calidad en
`code-quality-assessment.md`.

## Estilo Arquitectónico

**Monolito modular con frontend desacoplado.** El backend es un único despliegue FastAPI
con submódulos internos por responsabilidad (`api`, `auth`, `core`, `services`, `stores`,
`security`, `models`); no hay microservicios. La integración externa (Futmondo, Sofascore)
se hace vía clientes HTTP dentro de `services/`. El frontend es un despliegue independiente
que consume el backend por HTTP. Evidencia: routers montados en un solo `main.py`, un solo
`fly.toml` por servicio, sin buses de eventos ni colas.

El frontend Angular 22 es una **SPA/PWA de componentes standalone** (sin `NgModule` de
app; `bootstrapApplication`), con estado por signals, un `core/` transversal (servicios
HTTP, `auth.interceptor`, `auth.guard`, estrategia de precarga) y `features/` por pantalla.
El detalle físico está en `code-structure.md`.

El inventario completo de componentes y sus dependencias está en `component-inventory.md`;
aquí se describen relaciones y flujos, no el catálogo.

## Relaciones entre Componentes

```mermaid
graph TD
    Browser["Navegador / PWA (Angular 22)"]
    Nginx["nginx (futmondo-app)"]
    API["FastAPI (futmondo-api)"]
    MW["AuthMiddleware"]
    Auth["auth (JWT, token_store, session_store)"]
    Endpoints["api/v1/endpoints (routers)"]
    Services["services (clientes externos + lógica)"]
    Stores["stores (durabilidad)"]
    DB["Neon PostgreSQL"]
    Futmondo["API Futmondo"]
    Sofascore["API Sofascore"]

    Browser --> Nginx
    Nginx --> API
    API --> MW
    MW --> Endpoints
    MW --> Auth
    Endpoints --> Services
    Endpoints --> Auth
    Auth --> Stores
    Services --> Stores
    Stores --> DB
    Auth --> DB
    Services --> Futmondo
    Services --> Sofascore
```

<!-- Text fallback: el navegador (Angular PWA) habla con nginx, que hace reverse proxy a FastAPI. Toda petición pasa por AuthMiddleware, que enruta a los routers de api/v1/endpoints y consulta el módulo auth. Los routers usan services (clientes de Futmondo/Sofascore) y auth; ambos persisten vía stores hacia Neon PostgreSQL; auth también accede directamente a la BD para tablas de refresh tokens. -->

### Frontend (Angular 22) — relaciones internas

```mermaid
graph TD
    Bootstrap["main.ts (bootstrapApplication)"]
    AppCfg["app.config.ts (providers, router, http)"]
    Router["Angular Router (lazy features)"]
    Guard["core/guards/auth.guard.ts"]
    Interceptor["core/interceptors/auth.interceptor.ts"]
    Services["core/services/*.service.ts (11)"]
    Preload["core/preloading/idle-preloading-strategy.ts"]
    Features["features/* (standalone components)"]
    Shared["shared/* (UI reutilizable)"]
    Backend["backend HTTP /api/*, /auth/*"]

    Bootstrap --> AppCfg
    AppCfg --> Router
    AppCfg --> Interceptor
    AppCfg --> Preload
    Router --> Guard
    Router --> Features
    Features --> Services
    Features --> Shared
    Services --> Interceptor
    Interceptor --> Backend
```

<!-- Text fallback: main.ts arranca la app con bootstrapApplication y app.config.ts registra providers (router, HttpClient con el auth.interceptor y la estrategia de precarga idle). El router aplica auth.guard y carga las features (componentes standalone), que usan los servicios de core/services y componentes de shared/. Los servicios emiten HTTP a través del auth.interceptor, que añade Bearer y gestiona el refresh ante 401 contra el backend. -->

## Diagramas de Interacción

Cómo se implementan cuatro transacciones/flujos representativos a través de los
componentes.

### Transacción: cálculo y persistencia de premios de jornada

El cálculo de premios NO vive en los endpoints: vive por completo en
`data_sync_service.sync_prizes()` (un método dentro de un god-file de `services/`), que
consume la API de Futmondo, calcula todos los términos y UPSERTea la tabla `team_prizes`
(fuente de verdad). Los routers de finanzas/saldos sólo LEEN y SUMAN de esa tabla.

```mermaid
sequenceDiagram
    participant Cron as Cron / trigger de sync
    participant SP as data_sync_service.sync_prizes
    participant F as API Futmondo
    participant Cfg as user_championships (config)
    participant TP as tabla team_prizes
    participant EP as balances / player_finances
    participant U as Navegador

    Cron->>SP: ejecutar sincronización
    SP->>Cfg: leer money_per_point, money_per_ranking, ranking_mode, mvp_bonus, dream_team_bonus
    SP->>F: standings, rounds, round_ranking, dream_team, round_lineup, round_matches
    F-->>SP: datos de la ronda (con time.sleep entre llamadas)
    SP->>SP: points_prize = round(round_points * money_per_point)
    SP->>SP: award_round_prizes = is_closed AND round_fully_played AND NOT pseudo_ronda
    SP->>SP: ranking_prize / mvp_prize / dream_team_prize (solo si award_round_prizes)
    SP->>TP: UPSERT ON CONFLICT (championship_id, team_id, matchday)
    SP->>TP: DELETE ... WHERE matchday NOT IN (valid_matchdays) (limpieza defensiva)
    U->>EP: GET saldos / finanzas
    EP->>TP: SELECT premios por equipo/jornada
    EP-->>U: totales agregados (solo lectura + suma)
```

<!-- Text fallback: un cron o trigger de sync ejecuta data_sync_service.sync_prizes. El método lee la config de premios de user_championships (money_per_point, money_per_ranking, ranking_mode, mvp_bonus, dream_team_bonus) y consulta la API de Futmondo (standings, rounds, round_ranking, dream_team, round_lineup, round_matches) con time.sleep entre llamadas. Calcula points_prize (siempre), y solo si award_round_prizes = is_closed AND round_fully_played AND NOT pseudo-ronda calcula ranking_prize, mvp_prize y dream_team_prize. Hace UPSERT en team_prizes por (championship_id, team_id, matchday) y una limpieza defensiva DELETE de matchdays ya no válidos. Después, los endpoints balances y player_finances solo leen y suman esos premios para presentar los totales al navegador. -->

### Transacción: puja en el mercado (FR6)

```mermaid
sequenceDiagram
    participant U as Navegador
    participant N as nginx
    participant MW as AuthMiddleware
    participant M as market.place_bid
    participant H as _helpers.get_user_futmondo_client
    participant F as API Futmondo

    U->>N: POST /api/v1/market/bid (Bearer, price)
    N->>MW: reenvía petición
    MW->>MW: verify_token(expected_type="access")
    MW->>M: enruta si token válido
    M->>M: (FR6) NO valida price hoy
    M->>H: get_user_futmondo_client()
    H->>F: POST {base_url}/1/market/bid
    F-->>M: resultado de puja
    M-->>U: respuesta
```

<!-- Text fallback: el navegador envía POST /api/v1/market/bid con Bearer token y price. nginx lo reenvía; AuthMiddleware verifica el access token y enruta a place_bid. place_bid hoy NO valida price (hallazgo FR6), obtiene el cliente Futmondo del usuario vía _helpers y proxya la puja a POST /1/market/bid de Futmondo; la respuesta vuelve al navegador. -->

### Transacción: refresco de sesión (FR9)

```mermaid
sequenceDiagram
    participant U as Navegador
    participant R as auth.routes /auth/refresh
    participant T as token_store.is_refresh_token_valid
    participant DB as Neon PostgreSQL

    U->>R: POST /auth/refresh (cookie HttpOnly)
    R->>T: is_refresh_token_valid(token_hash)
    T->>DB: SELECT revoked, expires_at
    DB-->>T: fila (expires_at aware en PostgreSQL)
    T->>T: (FR9) ternario de precedencia ambigua
    T-->>R: False erróneo para tokens activos aware
    R-->>U: 401 pese a token válido
```

<!-- Text fallback: el navegador llama POST /auth/refresh con la cookie HttpOnly. auth.routes invoca is_refresh_token_valid, que consulta revoked y expires_at en PostgreSQL. Con expires_at aware, el ternario de precedencia ambigua (hallazgo FR9) devuelve False para tokens activos futuros, provocando un 401 indebido. -->

### Flujo: verificación de build/test del frontend y gate de CI/CD (intent activo)

El pipeline es la barrera que gobierna la llegada a producción. Hay **dos caminos** que
ejercitan los tests del frontend, ambos con `ng test --watch=false` BLOQUEANTE: el gate de
Pull Request (`ci.yml`) y el job `verify` del despliegue por push a `main`
(`fly-deploy.yml`). El intent activo interviene aquí: hoy `ng test` ejecuta specs pero NO
mide ni exige cobertura (no hay proveedor ni threshold instalado — ver
`code-quality-assessment.md`).

```mermaid
sequenceDiagram
    participant Dev as Desarrollador
    participant GH as GitHub
    participant CI as ci.yml (PR gate, job quality)
    participant FD as fly-deploy.yml (push a main)
    participant Fly as Fly.io

    Dev->>GH: abre PR a main
    GH->>CI: dispara pull_request
    CI->>CI: gitleaks (BLOQUEANTE)
    CI->>CI: pytest tests -q --cov=app (BLOQUEANTE)
    CI->>CI: ruff / pip-audit (advisory)
    CI->>CI: npm ci + ng test --watch=false (BLOQUEANTE)
    CI->>CI: ng lint / npm audit (advisory)
    CI-->>GH: verde/rojo del gate
    Dev->>GH: merge (squash) a main
    GH->>FD: dispara push a main
    FD->>FD: verify = gitleaks + pytest -q (SIN --cov) + npm ci + ng test --watch=false (BLOQUEANTE)
    FD->>Fly: deploy-backend
    FD->>Fly: deploy-frontend
    FD->>Fly: smoke-test GET /health (5 reintentos, HTTP 200)
```

<!-- Text fallback: al abrir un PR a main, ci.yml corre el job quality: gitleaks bloqueante, pytest con --cov=app bloqueante, ruff y pip-audit advisory, luego npm ci y ng test --watch=false bloqueante, y ng lint / npm audit advisory. Tras el merge squash a main, fly-deploy.yml corre el job verify (gitleaks + pytest sin --cov + npm ci + ng test --watch=false, todos bloqueantes salvo lo advisory), y si pasa despliega backend, luego frontend en Fly.io y ejecuta un smoke-test contra /health con 5 reintentos esperando HTTP 200. El hueco del intent (FR17.1) es de MEANINGFULNESS: ng test se ejecuta en ambos caminos pero sin threshold de cobertura que rompa el gate. -->

## Flujo de Datos

Toda petición autenticada entra por nginx → `AuthMiddleware` (que exige `Authorization:
Bearer <access>` salvo rutas en `AUTH_EXCLUDED_PATHS`) → router → `services`/`auth` →
persistencia (`stores` o SQL crudo) → Neon PostgreSQL o proxy a Futmondo/Sofascore. La
ruta `/static/photos/*` (StaticFiles) queda fuera del prefijo protegido y se sirve sin auth.

En el frontend, cada servicio de `core/services/*` emite HTTP a través del
`auth.interceptor`, que añade `Authorization: Bearer <access>` (salvo a `/auth/*`, donde usa
`withCredentials` para la cookie de refresh) y, ante un 401, encola las peticiones mientras
refresca el token; ante fallo de refresh o 403, fuerza logout.

Para los **premios**, el flujo tiene dos mitades desacopladas por la tabla `team_prizes`:
una **mitad de escritura** batch (`sync_prizes` → `team_prizes`) que sólo corre en la
sincronización, y una **mitad de lectura** en tiempo de petición (routers de saldos/finanzas
→ `SELECT` sobre `team_prizes`). No hay recálculo en la ruta de lectura.

## Decisiones de Diseño Clave

- **Access token en memoria + refresh token en cookie `HttpOnly`**: minimiza exposición del
  token a XSS a costa de un flujo de refresco (donde vive el bug FR9). Implementado en el
  frontend por `auth.interceptor` (ya caracterizado por spec).
- **Frontend standalone + Vitest vía `@angular/build:unit-test`**: el proyecto ya migró a
  Vitest + jsdom (sin restos Karma/Jasmine), pero la infraestructura de cobertura está
  ausente (decisión implícita a corregir por el intent activo).
- **Doble camino de verificación (`ci.yml` + `verify`)**: defensa en profundidad; un
  threshold de cobertura activado en `ng test` se propaga a AMBOS caminos automáticamente.
- **Proxy hacia Futmondo con credenciales por usuario**: el backend no guarda password en
  claro en sesión; usa la sesión Futmondo del usuario (12h TTL) — ver `NEVER almacenar la
  contraseña en claro` en las reglas del proyecto.
- **Persistencia mixta**: coexisten una capa `stores/` (durabilidad reciente) y SQL crudo
  disperso en `auth`/routers (deuda descrita en `code-quality-assessment.md`).
- **Precálculo de premios como fuente de verdad**: `team_prizes` desacopla el cálculo caro
  (dependiente de la API externa) de la lectura barata en las pantallas.

## Oportunidades de Mejora

- **Cobertura del frontend (intent activo)**: quitar `skipTests: true` de los schematics de
  `angular.json` (FR10.1) e introducir infraestructura de cobertura (`@vitest/coverage-v8`,
  `vitest.config` con `coverage.thresholds` bajo-y-trinquete) sembrando primero specs de
  servicios/guard/interceptores críticos (FR10.2); luego endurecer el job `verify` de
  `fly-deploy.yml` para que un cambio que rompa lógica cubierta no llegue a producción
  (FR17.1). Detalle y estado en `code-quality-assessment.md`.
- **Premios**: caracterizar `sync_prizes` (ratios flop/top, gating de ronda completa, MVP,
  dream-team, pseudo-jornada negativa, limpieza defensiva) ANTES de refactor, y extraer la
  fórmula a una función/módulo estrecho testeable con dobles de la API de Futmondo, sin
  ampliar el god-file `data_sync_service.py`. Detalle en `code-quality-assessment.md`.
- Introducir validación de entrada en el backend para pujas (FR6) tras una capa estrecha,
  sin ampliar el patrón SQL-en-router.
- Aislar de forma inequívoca `SSL_VERIFY` al entorno local (FR8).
- Consolidar el acceso a datos de auth en una capa repositorio para eliminar la clase de
  bugs naive/aware (FR9). El detalle de deuda vive en `code-quality-assessment.md`.
