# Code Structure — Futmondo Analytics

Monorepo con tres aplicaciones (`backend/` FastAPI, `angular-app/` Angular,
`ios/` cliente nativo Swift/SwiftUI) más `proxy/`, `cron/`, `docs/`, `scripts/`
y orquestación local (`docker-compose.yml`).

> Nota de cobertura (run 261019-presupuesto-selector-cam): refresco incremental
> enfocado en `ios/` (capa nativa añadida por F1) y en las áreas Budget/championship
> que F2 toca. El resto del backend y del frontend se **preserva** del store
> previo (shallow, no re-verificable en este run).

## backend/ (FastAPI, Python 3.12)

```
backend/
├── app/
│   ├── main.py                 # Entrypoint FastAPI: CORS, AuthMiddleware, routers, static photos, /health
│   ├── auth/                   # Autenticación (clave para F1)
│   │   ├── routes.py           # /auth/login, /auth/refresh, /auth/logout + auto-detección de campeonatos
│   │   ├── jwt_utils.py        # create/verify access & refresh tokens (PyJWT, HS256), hash_token
│   │   ├── dependencies.py     # get_current_user (Bearer -> payload)
│   │   ├── token_store.py      # Tablas auth (app_users, refresh_tokens, user_championships) + revocación
│   │   ├── session_store.py    # Caché en memoria de FutmondoClient por usuario (TTL 12h, sin password)
│   │   └── models.py           # LoginRequest / TokenResponse / Refresh* (pydantic)
│   ├── api/v1/endpoints/       # Routers REST (ver api-documentation.md)
│   │   ├── user.py             # /api/v1/user/me, /championships
│   │   ├── market.py, roster.py, sync.py, analytics.py, balances.py,
│   │   │   player_finances.py, transactions.py, favorites.py,
│   │   │   clausulable_players.py, statistics.py, user_stats.py,
│   │   │   championships.py, phantoms.py, matchdays.py, initialize.py,
│   │   │   reset_db.py, sofascore_sync.py, sofascore_detail.py, assistant.py
│   │   └── _helpers.py, _sofascore_helpers.py
│   ├── services/               # Lógica de negocio e integraciones
│   │   ├── futmondo_client.py  # Cliente API Futmondo (login, _make_request, errores tipados)
│   │   ├── sofascore_client.py # Cliente API Sofascore
│   │   ├── integration_errors.py  # Jerarquía de errores de integración tipados (FR4)
│   │   ├── session_service.py / session_repository (stores/) # Sesión durable + rehidratación
│   │   ├── task_service.py / task_repository (stores/)       # Tareas de sync durables
│   │   ├── sync/, prizes/, analytics/, assistant/            # Paquetes de dominio
│   │   ├── data_manager/        # Paquete DDD extraído del god-file (adapters de infraestructura)
│   │   ├── data_manager_v2.py   # God-file heredado (DEUDA CONOCIDA, NO ampliar) — ver abajo
│   │   ├── data_sync_service.py # God-file heredado (DEUDA CONOCIDA, NO ampliar) — ver abajo
│   │   ├── photo_service.py, futmondo_service.py, db_connection.py, sync_step_status.py
│   │   └── data_initializer*.py
│   ├── stores/                 # Repositorios de persistencia (session_repository, task_repository)
│   ├── security/               # credential_protection.py (cifrado del handle de re-auth)
│   ├── core/                   # config.py (env + JWT_SECRET), constants.py
│   └── models/                 # models.py (modelos de dominio)
├── tests/                      # Suite pytest (characterization-first) — ver code-quality-assessment.md
├── conftest.py                 # Fixtures fake in-memory (SQLite), sin red ni DB real
├── requirements.txt, pytest.ini, ruff.toml, .pip-audit-allowlist
├── Dockerfile, fly.toml, run.py
└── scripts/                    # Scripts de sync/exportación (fuera del servicio web)
```

> Nota de cobertura (este run): el subárbol `backend/` **no** se reanalizó en el
> escaneo enfocado del intent de diseño; su prosa se **preserva** del store
> previo y queda como cobertura shallow (no re-verificable en este run).

### God-files heredados (deuda conocida — NO ampliar)

Regla afirmada en `project.md`/`team.md`: NUNCA ampliar ni reescribir los
god-files; el código nuevo va tras una capa/función estrecha testeable.

- `app/services/data_manager_v2.py` — tamaño observado en disco **~33 KB (1253
  líneas aprox. no verificadas)**; registrado en `ruff.toml` `per-file-ignores`
  con `E722`/`F841`/`F401`/`I001`. Parte de su lógica se ha extraído a
  `app/services/data_manager/.../infrastructure/*_adapter.py` (deuda verbatim).
- `app/services/data_sync_service.py` — tamaño observado **~15 KB**; también en
  `per-file-ignores`.

> Nota de alcance: las referencias históricas en `memory/` citan tamaños mayores
> (`data_manager_v2.py` ~166 KB, `data_sync_service.py` ~84 KB). Los tamaños que
> escaneos previos observaron en disco son los indicados arriba; la discrepancia
> es coherente con la descomposición DDD parcial ya realizada (`data_manager/`).
> Mantener la regla de NO ampliar en cualquier caso.

## angular-app/ (Angular 22 + Material 22, PWA)

```
angular-app/
├── src/
│   ├── main.ts, index.html
│   ├── styles.scss              # TEMA GLOBAL Material 3 + tokens semánticos (FUENTE DE VERDAD del diseño)
│   └── app/
│       ├── app.config.ts        # provideHttpClient(withInterceptors([authInterceptor])), router+preloading, service worker
│       ├── app.routes.ts, app.ts
│       ├── app.scss             # Shell: sidebar, toolbar móvil, .active-link, notch (safe-area), responsive
│       ├── core/
│       │   ├── services/
│       │   │   ├── auth.service.ts        # Login/refresh/logout; access token EN MEMORIA (ref. F1)
│       │   │   ├── championship.service.ts# Campeonato activo (signals + localStorage)
│       │   │   ├── analytics|budget|stats|market|roster|sync|favorites|evolution|assistant .service.ts
│       │   ├── interceptors/auth.interceptor.ts  # Añade Bearer + withCredentials; refresh en 401; logout en 403
│       │   ├── guards/auth.guard.ts       # CanActivate: recupera sesión / redirige a /login
│       │   ├── preloading/idle-preloading-strategy.ts  # Precarga lazy diferida por inactividad (BR3.1/BR3.3/NFR4)
│       │   └── models/                     # stats.model.ts, budget.model.ts, evolution.model.ts (DTOs)
│       ├── features/
│       │   ├── login/login.component.ts   # Formulario de login (ref. F1 + ref. de UX de theming)
│       │   ├── splash/, budget/, market/, finances/, calculator/,
│       │   │   transactions/, my-roster/, favorites/, clausulable/,
│       │   │   classification/, evolution/, stats/, settings/, analytics/
│       └── shared/
│           ├── components/      # player-card, badges Sofascore/starter, view-toggle, loading-state, page-header, assistant-*
│           ├── styles/          # _index.scss + _table-common.scss, _player-card.scss, _responsive-grid.scss, _loading-states.scss
│           ├── utils/, pipes/   # player.utils, team-logos, responsive, spanish-date-adapter, money.pipe
├── angular.json                 # builder @angular/build:*, styles: [src/styles.scss], inlineStyleLanguage scss, target test Vitest + coverageThresholds
├── package.json                 # Angular 22, Material 22, Vitest 4.1.11
├── eslint.config.js (advisory), .prettierrc, nginx.prod.conf, Dockerfile, fly.toml
└── ngsw-config.json, public/     # PWA (service worker + manifest + iconos)
```

### Capa de estilos / sistema de diseño (foco de este intent)

La capa de estilos del `angular-app` es la **fuente de verdad** para el sistema
de diseño nativo iOS. Organización observada:

- `src/styles.scss` — punto de entrada único declarado en `angular.json`
  (`styles: ["src/styles.scss"]`). Aplica el tema Material 3 global
  (`mat.theme`: primaria verde, terciaria violeta, tipografía Roboto) y define los
  tokens semánticos del proyecto bajo `// ===== DESIGN SYSTEM TOKENS =====`
  (dinero positivo/negativo, escala `h1`/`h2`/`h3`, tablas, `body.splash-bg`
  gradiente verde, overrides `body.dark-theme`).
- `src/app/app.scss` — estilos del shell (no theming de marca pero sí layout:
  sidebar, toolbar, estado activo, safe-area del notch, responsive).
- `src/app/shared/styles/` — partials reutilizables agregados vía `_index.scss`
  con `@forward`: tablas, tarjetas de jugador, grid responsive y estados de
  carga. Consumen tokens `--mat-sys-*` y variantes `.dark-theme &`.
- Estilos inline por componente (p. ej. `login.component.ts` usa `styles: [...]`
  con `inlineStyleLanguage: scss`), gobernados por el budget de build
  `anyComponentStyle` (warn 8kB / error 12kB en `angular.json`).

## ios/ (cliente nativo Swift/SwiftUI, SwiftPM — añadido por F1)

Paquete SwiftPM (`swift-tools-version:6.0`) con la capa nativa iOS introducida
por el intent F1 `261018-design-system-nativo` (login nativo + sistema de
diseño). Apple SDK únicamente, **cero dependencias externas** (`dependencies: []`).
F2 (Presupuesto + selector de campeonato) construirá SOBRE esta capa.

```
ios/
├── Package.swift               # Paquete SwiftPM: products FutmondoKit (lib) + FutmondoApp (lib), testTarget FutmondoKitTests; platforms iOS 15 / macOS 12
├── xtool.yml                   # Empaquetado iOS (xtool): version 1, bundleID com.futmondo.app, product FutmondoApp
├── Sources/
│   ├── FutmondoKit/            # LIBRARY device-independent y testeable (swift test en Linux/WSL)
│   │   ├── Networking/
│   │   │   ├── NetworkClient.swift          # Protocolo `send` async → Result<T, NetworkError> (Sendable, nunca throw)
│   │   │   ├── URLSessionNetworkClient.swift# Impl URLSession; init throwing rechaza base URL no-https (SEC-N1); inyecta Bearer por request; mapea status→NetworkError
│   │   │   ├── APIRequest.swift             # APIRequest (method/path/headers/body), AnyEncodable, EmptyResponse
│   │   │   ├── HTTPMethod.swift             # enum get/post/put/delete
│   │   │   ├── NetworkError.swift           # enum tipado: unauthorized/forbidden/clientError/server/cancelled/transport/decoding/unexpectedStatus (Equatable, sin credenciales)
│   │   │   └── UserMe.swift                 # DTO `GET /api/v1/user/me` (user_id, email) — smoke F1; modelo completo en F2
│   │   ├── Auth/
│   │   │   ├── AuthService.swift            # actor: access token en memoria, login/refresh/bootstrap/logout, refresh coalescido (una sola in-flight)
│   │   │   ├── AuthDTOs.swift               # LoginRequest/LoginResponse/RefreshRequest/RefreshResponse DTOs (wire keys snake_case)
│   │   │   ├── AuthError.swift              # AuthError (invalidCredentials/network/refreshFailed/unknown) + conformancias Sendable retro
│   │   │   ├── KeychainStore.swift          # Protocolo del almacén seguro del refresh token
│   │   │   ├── KeychainTokenStore.swift     # Impl Keychain Services (#if canImport(Security)); service com.futmondo.app.auth, AfterFirstUnlockThisDeviceOnly
│   │   │   ├── InMemoryKeychainStore.swift  # Doble in-memory para swift test (NSLock), con hooks de error
│   │   │   ├── TokenHolder.swift            # Snapshot Sendable del access token (NSLock) para el provider síncrono del NetworkClient
│   │   │   ├── LogoutFlagStore.swift        # Flag booleano "logout pendiente" (UserDefaults + doble in-memory); NUNCA guarda el refresh token
│   │   │   └── Session.swift                # Session (accessToken en memoria + UserMe) y SessionState (authenticated/unauthenticated/offlinePreserved)
│   │   └── DesignSystem/        # Base PURA (SwiftUI-free) del sistema de diseño → testeable en Linux/WSL
│   │       ├── DSColorValue.swift           # DSRGB (parse #RRGGBB), DSColorValue (light/dark), DSColorToken (roles), DSAppearance, DSSplashGradient
│   │       ├── DSTypographyScale.swift      # Escala h1/h2/h3/body (28/20/16/14) + pesos; familia preferida "Roboto"
│   │       ├── DSSpacing.swift              # Escala xs/sm/md/lg/xl (4/8/16/24/32 pt)
│   │       └── ContrastRatio.swift          # Luminancia relativa + ratio WCAG (umbrales AA 4.5 / 3.0) para validar tokens
│   └── FutmondoApp/            # EXECUTABLE/app product (SwiftUI); todo bajo #if canImport(SwiftUI)
│       ├── FutmondoApp.swift                # @main App: cablea KeychainTokenStore+TokenHolder+URLSessionNetworkClient+AuthService; baseURL https://futmondo-api.fly.dev; arranca en SplashView
│       ├── SplashView.swift                 # Auto-login: ejecuta AuthService.bootstrap(), enruta resumed/offline/noSession; nunca cuelga
│       ├── LoginView.swift                  # Pantalla de login nativa (re-skin U2 con DesignSystem: Card/TextInputField/PrimaryButton/ErrorState)
│       ├── AuthViewModel.swift              # @Observable: estado idle/typing/loading/error/success; delega en AuthService; NUNCA reintenta; limpia password
│       └── DesignSystem/       # Accesores SwiftUI del sistema de diseño
│           ├── DSColor.swift                # Color adaptativo claro/oscuro desde DSColorToken (UIColor dinámico); splashGradient; Color(hex:)
│           ├── DSFont.swift                 # Font con Dynamic Type (relativeTo) + Roboto si está disponible, fallback sistema
│           ├── DSSpacing+SwiftUI.swift      # Accesor CGFloat de DSSpacing
│           ├── Components/
│           │   ├── PrimaryButton.swift      # mat-flat-button primary: estados normal/disabled/loading (loading > disabled), touch ≥44pt
│           │   ├── TextInputField.swift     # mat-form-field outline: normal/focus/error, prefijo, toggle de visibilidad
│           │   └── Containers.swift         # Card (mat-card r16), LoadingState (mat-spinner), ErrorState (icono+texto, no color solo)
│           └── Catalog/
│               └── CatalogView.swift        # Catálogo dev: Colors→Typography→Spacing→Components, toggle claro/oscuro y tamaño de texto
├── Tests/FutmondoKitTests/     # XCTest sobre FutmondoKit
│   ├── AuthServiceTests.swift               # login/refresh/bootstrap/logout, coalescing, teardown
│   ├── NetworkClientTests.swift             # construcción de URLRequest, mapeo de status, Bearer, cancelación
│   └── DesignSystemTests.swift              # resolución de tokens por apariencia, cobertura de roles, contraste
├── scripts/install-app.sh      # Script de instalación del .app
└── .build/, xtool/, .bsp/, .sourcekit-lsp/ # Salidas de build / caches (no son fuente)
```

### Patrón de reutilización del backend (clave para F2)

El cliente nativo habla con el MISMO backend FastAPI por HTTPS
(`https://futmondo-api.fly.dev`): access token JWT en memoria (`TokenHolder`),
refresh token en Keychain enviado en el header `X-Refresh-Token` (ajuste D-01
del backend, ya consumido por `AuthService`). F2 añadirá un cliente de datos
sobre el mismo `NetworkClient`/`AuthService` para los endpoints de
balances/championships.

## Áreas de interés para F2 (Presupuesto nativo + selector de campeonato)

F2 reproduce en SwiftUI la feature de Presupuesto del `angular-app` y añade el
selector de campeonato activo, consumiendo los endpoints ya existentes. Fuentes
de verdad del comportamiento a replicar:

- **Feature Budget Angular** — `angular-app/src/app/features/budget/`:
  - `budget.routes.ts` — rutas de la feature.
  - `budget-overview/budget-overview.component.{ts,html,scss}` — tabla de saldos
    por equipo; `prizes-dialog.component.ts` (premios).
  - `budget-detail/budget-detail.component.{ts,html,scss}` — detalle de altas/bajas.
  - `sync-dialog/sync-dialog.component.{ts,html,scss}` — diálogo de sync.
- **Servicio Budget** — `core/services/budget.service.ts`: `getBalances(championshipId?)`
  → `GET /api/v1/analytics/balances`; `getTeamDetail(teamId, championshipId?)` →
  `GET /api/v1/analytics/balances/{teamId}`; `syncTransactions()` →
  `POST /api/v1/sync/trigger`. Base `/api/v1/analytics`; `championship_id` como
  query param opcional.
- **Servicio Championship** — `core/services/championship.service.ts`: selección
  de campeonato activo con Angular signals; persiste el id en `localStorage`
  (`futmondo_active_championship`); carga `GET /api/v1/user/championships` con
  fallback a `GET /api/v1/championships`; expone `activeChampionship`/`activeId`
  y `hasClauses`. El equivalente nativo del almacén local será un store propio en
  iOS (no `localStorage`).
- **Modelos** — `core/models/budget.model.ts`: `TeamBudget`, `BalancesResponse`,
  `TeamDetailResponse`, `Transaction`, `SyncTriggerResponse`, `SyncTaskResponse`;
  contrato de datos (wire keys snake_case) a reproducir con DTOs Swift en F2.

## Áreas de interés para F1 (login nativo iOS)

- **Backend auth** (`app/auth/`): routes + jwt_utils + token_store son el
  contrato a reutilizar/extender (D-01).
- **Frontend auth como referencia de comportamiento**: `auth.service.ts`
  (access en memoria, refresh por cookie, `tryRecoverSession`),
  `auth.interceptor.ts` (reintento en 401) y `login.component.ts` modelan el flujo
  que el cliente nativo iOS debe replicar con su propio almacén (Keychain) en vez
  de cookie de navegador.

## Áreas de interés para el sistema de diseño nativo iOS (intent 261018)

- `src/styles.scss` (tema + tokens), `src/app/app.scss` (layout del shell),
  `src/app/shared/styles/*.scss` (primitivas compartidas) y
  `features/login/login.component.ts` (pantalla de referencia). Son la base a
  reproducir en SwiftUI con SDK de Apple; `angular.json` confirma el punto de
  entrada de estilos y la configuración de componentes `scss`.

## Sources

- Listados de directorios de `ios/`, `backend/` y `angular-app/` (herramienta de lectura)
- `ios/Package.swift`, `ios/xtool.yml`
- `ios/Sources/FutmondoKit/Networking/*.swift`, `ios/Sources/FutmondoKit/Auth/*.swift`,
  `ios/Sources/FutmondoKit/DesignSystem/*.swift`
- `ios/Sources/FutmondoApp/*.swift` y `ios/Sources/FutmondoApp/DesignSystem/**/*.swift`
- `ios/Tests/FutmondoKitTests/DesignSystemTests.swift` (encabezado)
- `angular-app/src/app/features/budget/*` (listado), `angular-app/src/app/core/services/{budget,championship}.service.ts`,
  `angular-app/src/app/core/models/budget.model.ts`
- `backend/app/api/v1/endpoints/{balances,championships,user}.py`
- `backend/app/main.py`, `backend/app/auth/*.py`, `backend/ruff.toml` (store previo)
- `angular-app/src/app/app.config.ts`, `angular-app/angular.json`
- `angular-app/src/styles.scss`, `angular-app/src/app/app.scss`,
  `angular-app/src/app/shared/styles/*.scss`
- `backend/app/services/integration_errors.py` (store previo)

## Assumptions & Open Questions

- No se abrieron todos los `*_adapter.py` del paquete `data_manager/`; su
  clasificación como "deuda verbatim extraída del god-file" se toma del comentario
  verificado en `ruff.toml`. El subárbol `backend/` no se reanalizó íntegro en
  este run (solo los endpoints de balances/championships/user; prosa restante
  preservada / shallow).
- Del `ios/` se leyeron todos los `.swift` fuente de `Sources/` y los manifiestos;
  de `Tests/` se abrió `DesignSystemTests.swift` por completo y los otros dos
  (`AuthServiceTests.swift`, `NetworkClientTests.swift`) se clasifican por nombre
  y por su cobertura declarada en los comentarios del `AuthService`/`NetworkClient`.
- De `features/budget/` se listó el árbol y se leyeron `budget.service.ts`,
  `championship.service.ts` y `budget.model.ts`; los `.component.ts/.html/.scss`
  concretos de budget se inventarían por nombre (no abiertos línea a línea).
