# Component Inventory — Futmondo Analytics

## Backend (FastAPI)

> Nota de cobertura (run 261018-design-system-nativo): el backend no se reanalizó
> en este escaneo enfocado de theming; estas filas se **preservan** del store
> previo (cobertura shallow, no re-verificable en este run).

| Componente | Fichero | Responsabilidad | Dependencias clave |
|---|---|---|---|
| FastAPI app + AuthMiddleware | `app/main.py` | Monta CORS, middleware de auth sobre `/api/v1/*`, routers, fotos estáticas, `/health` | `jwt_utils.verify_token`, routers, `token_store.init_auth_tables` |
| Auth routes | `app/auth/routes.py` | `/auth/login`, `/auth/refresh`, `/auth/logout`; set/clear cookie `HttpOnly`; auto-detección de campeonatos | `FutmondoClient`, `jwt_utils`, `token_store`, `session_store`, `session_service`, `SessionRepository` |
| JWT utils | `app/auth/jwt_utils.py` | Crear/verificar access (60 min) y refresh (30 días) HS256; `hash_token` | `PyJWT`, `config.JWT_SECRET` |
| Auth dependency | `app/auth/dependencies.py` | `get_current_user(request)` desde header Bearer | `jwt_utils.verify_token` |
| Token store | `app/auth/token_store.py` | Tablas `app_users`, `refresh_tokens`, `user_championships`; save/revoke/validate refresh; upsert/get user; migraciones idempotentes | `db_connection.get_db`, `psycopg2`/`sqlite3` |
| Session store (memoria) | `app/auth/session_store.py` | Caché por usuario de `FutmondoClient` (TTL 12h); **nunca** retiene password | `FutmondoClient`, `threading` |
| Auth models | `app/auth/models.py` | `LoginRequest`, `TokenResponse`, `Refresh*` (pydantic) | `pydantic` |
| Session service / repo | `app/services/session_service.py`, `app/stores/session_repository.py` | Sesión durable + rehidratación con handle cifrado | `credential_protection`, `config.FUTMONDO_CRED_KEY` |
| Credential protection | `app/security/credential_protection.py` | Cifra/descifra el handle de re-auth en reposo (sin password en claro) | `FUTMONDO_CRED_KEY` |
| Futmondo client | `app/services/futmondo_client.py` (~27 KB) | Cliente de la API Futmondo: `login()`, `_make_request`, errores tipados | `requests`, `integration_errors` |
| Sofascore client | `app/services/sofascore_client.py` (~16 KB) | Cliente de la API Sofascore (ratings) | `curl_cffi` (stack), `integration_errors` |
| Integration errors | `app/services/integration_errors.py` | Jerarquía tipada recoverable/fatal; constructor sin material de credencial (NFR3) | — |
| Task service / repo | `app/services/task_service.py`, `app/stores/task_repository.py` | Tareas de sync durables + barrido de interrumpidas al arranque | `db_connection` |
| Sync service | `app/services/data_sync_service.py` (~15 KB) | **God-file heredado (deuda, NO ampliar)**: orquestación de sync | — |
| Data manager | `app/services/data_manager_v2.py` (~33 KB) + `data_manager/` | **God-file heredado (deuda, NO ampliar)**; parte extraída a adapters DDD | — |
| Photo service | `app/services/photo_service.py` (~23 KB) | Descarga/servido de fotos de jugador | `requests` |
| Config | `app/core/config.py` | Env vars; `resolve_jwt_secret` (fail-fast NFR1.1); `FUTMONDO_CRED_KEY` | `python-dotenv` |
| DB connection | `app/services/db_connection.py` | Abstracción PostgreSQL/SQLite (`db_type`, `adapt_params`) | `psycopg2`, `sqlite3` |

## Frontend (Angular)

| Componente | Fichero | Responsabilidad | Relevancia F1 |
|---|---|---|---|
| AuthService | `src/app/core/services/auth.service.ts` | `login/refresh/logout/tryRecoverSession`; **access token en memoria** (`accessToken`), user en `localStorage` (no el token); refresh por cookie (`withCredentials`) | **Referencia directa del flujo que iOS debe replicar con Keychain** |
| authInterceptor | `src/app/core/interceptors/auth.interceptor.ts` | Añade `Authorization: Bearer`; `withCredentials` en `/auth/*`; reintento con refresh en `401`; logout en `403` | Modela el manejo de 401/refresh que el cliente nativo debe implementar |
| authGuard | `src/app/core/guards/auth.guard.ts` | `CanActivateFn`: recupera sesión al arrancar / redirige a `/login` | — |
| LoginComponent | `src/app/features/login/login.component.ts` | Formulario email/password (Material) → `AuthService.login` | **Referencia de UX de login para la pantalla nativa** |
| ChampionshipService | `src/app/core/services/championship.service.ts` | Selección de campeonato activo (signals + `localStorage`); fallback `/user/championships` → `/championships` | — |
| IdlePreloadingStrategy | `src/app/core/preloading/idle-preloading-strategy.ts` | Precarga lazy diferida por inactividad (`requestIdleCallback` + fallback), BR3.1/BR3.3/NFR4 | — |
| App config | `src/app/app.config.ts` | Registra `authInterceptor`, router con preloading, service worker | — |
| Feature services | `analytics/budget/stats/market/roster/sync/...service.ts` | Consumo de `/api/v1/*` | Consumidores del access token |
| Feature components | `features/{budget,market,finances,calculator,...}` | UI de cada funcionalidad | — |

## Sistema de diseño / theming del frontend (foco del intent 261018 — fuente de verdad nativa)

| Componente | Fichero | Responsabilidad | Relevancia diseño nativo iOS |
|---|---|---|---|
| Global theme (Material 3) | `src/styles.scss` | `mat.theme` (primaria `mat.$green-palette`, terciaria `mat.$violet-palette`, tipografía Roboto, `density: 0`); genera tokens `--mat-sys-*`; tokens semánticos (`money-positive`/`money-negative`), escala `h1`/`h2`/`h3`, tablas, `body.splash-bg` gradiente verde, overrides `body.dark-theme` | **Fuente de verdad del sistema de diseño a reproducir en SwiftUI** |
| App shell styles | `src/app/app.scss` | Layout: sidebar (`.app-sidenav` 250px / mini 64px), toolbar móvil sticky, `.active-link` `#4CAF50`, `env(safe-area-inset-top)` (notch), `fadeIn`, responsive | Referencia de layout/navegación nativa (tab/nav, safe-area) |
| Shared style partials | `src/app/shared/styles/{_index,_table-common,_player-card,_responsive-grid,_loading-states}.scss` | Primitivas reutilizables: tablas, tarjetas de jugador, chips de posición (fwd/mid/def/gk), tendencias, grid 1→4 cols, estados de carga/error/vacío | Primitivas de componentes a mapear a HIG/SwiftUI |
| Login screen (theming ref) | `src/app/features/login/login.component.ts` | Aplicación concreta del tema: `mat-card` sobre gradiente verde, campos `outline` con `matPrefix`, botón primario, bloque de error | Pantalla de referencia concreta para el diseño nativo |
| Build/style config | `src/angular.json` (`angular-app/angular.json`) | `styles: [src/styles.scss]`, `inlineStyleLanguage: scss`, schematics component `style: scss`, budget `anyComponentStyle` 8kB/12kB | Confirma el punto de entrada único de estilos |

## Cliente nativo iOS (`ios/`, Swift/SwiftUI — añadido por F1; base de F2)

Paquete SwiftPM (Apple SDK only, cero deps externas). F2 (Presupuesto + selector
de campeonato) construye sobre esta capa.

### `FutmondoKit` (library testeable)

| Componente | Fichero | Responsabilidad | Relevancia F2 |
|---|---|---|---|
| NetworkClient (protocolo) | `Networking/NetworkClient.swift` | Contrato `send` async → `Result<T, NetworkError>`, `Sendable`, nunca lanza | Transporte reutilizado por el cliente de datos F2 |
| URLSessionNetworkClient | `Networking/URLSessionNetworkClient.swift` | Impl `URLSession`; init throwing rechaza base URL no-https (SEC-N1); inyecta `Bearer`; mapea status→`NetworkError` | Base HTTP para `/analytics/balances` y `/championships` |
| APIRequest / AnyEncodable / EmptyResponse | `Networking/APIRequest.swift` | Valor de request (method/path/headers/body); body `Encodable` type-erased; marcador 2xx vacío | DTOs de request de F2 |
| HTTPMethod | `Networking/HTTPMethod.swift` | enum get/post/put/delete | — |
| NetworkError | `Networking/NetworkError.swift` | Error tipado `Equatable` (unauthorized/forbidden/clientError/server/cancelled/transport/decoding/unexpectedStatus); sin credenciales | Manejo de errores de datos F2 |
| UserMe (DTO) | `Networking/UserMe.swift` | DTO `GET /api/v1/user/me` (user_id, email); smoke F1, **modelo completo en F2** | F2 amplía el modelo de usuario |
| AuthService | `Auth/AuthService.swift` | `actor`: access token en memoria, login/refresh/bootstrap/logout, refresh coalescido; refresh en header `X-Refresh-Token` (D-01) | Provee el access token a las llamadas de datos F2 |
| AuthDTOs | `Auth/AuthDTOs.swift` | LoginRequest/LoginResponse(+`refresh_token`)/RefreshRequest/RefreshResponse (wire snake_case) | Patrón de DTOs Decodable a imitar |
| AuthError | `Auth/AuthError.swift` | `AuthError` (invalidCredentials/network/refreshFailed/unknown) + conformancias `Sendable` retro | — |
| KeychainStore (protocolo) | `Auth/KeychainStore.swift` | Contrato del almacén seguro del refresh token | — |
| KeychainTokenStore | `Auth/KeychainTokenStore.swift` | Keychain Services (`#if canImport(Security)`); servicio `com.futmondo.app.auth`, `AfterFirstUnlockThisDeviceOnly` | Sesión persistente que habilita las pantallas de datos F2 |
| InMemoryKeychainStore | `Auth/InMemoryKeychainStore.swift` | Doble in-memory (`NSLock`) para `swift test`, con hooks de error | Testing |
| TokenHolder | `Auth/TokenHolder.swift` | Snapshot `Sendable` (`NSLock`) del access token para el provider síncrono del NetworkClient | — |
| LogoutFlagStore | `Auth/LogoutFlagStore.swift` | Flag booleano "logout pendiente" (UserDefaults + doble); NUNCA guarda el refresh token | — |
| Session / SessionState | `Auth/Session.swift` | `Session` (access en memoria + `UserMe`); `SessionState` authenticated/unauthenticated/offlinePreserved | — |
| DSColorValue / DSColorToken | `DesignSystem/DSColorValue.swift` | `DSRGB` parse `#RRGGBB`, `DSColorValue` light/dark, roles `DSColorToken` (primary verde #2E7D32/#66BB6A, moneyPositive/Negative, etc.), `DSSplashGradient` | Tokens que la pantalla de Presupuesto reutiliza (dinero +/-) |
| DSTypographyScale | `DesignSystem/DSTypographyScale.swift` | Escala h1/h2/h3/body (28/20/16/14) + pesos; familia "Roboto" | Tipografía de las tablas de Presupuesto |
| DSSpacing | `DesignSystem/DSSpacing.swift` | Escala xs/sm/md/lg/xl (4/8/16/24/32 pt) | Layout nativo F2 |
| ContrastRatio | `DesignSystem/ContrastRatio.swift` | Luminancia relativa + ratio WCAG (AA 4.5 / 3.0) | Validación de contraste de tokens |

### `FutmondoApp` (app product SwiftUI; `#if canImport(SwiftUI)`)

| Componente | Fichero | Responsabilidad | Relevancia F2 |
|---|---|---|---|
| FutmondoApp (@main) | `FutmondoApp.swift` | Cablea Keychain+TokenHolder+URLSession+AuthService; baseURL `https://futmondo-api.fly.dev`; arranca en SplashView | Punto de entrada donde F2 enlaza sus pantallas |
| SplashView | `SplashView.swift` | Auto-login vía `bootstrap()`; enruta resumed/offline/noSession; nunca cuelga | Tras login, F2 enruta a Presupuesto |
| LoginView | `LoginView.swift` | Login nativo re-skin con DesignSystem (Card/TextInputField/PrimaryButton/ErrorState) | Patrón de pantalla a replicar en Presupuesto |
| AuthViewModel | `AuthViewModel.swift` | `@Observable`: estado idle/typing/loading/error/success; delega en AuthService; NUNCA reintenta | Patrón de ViewModel para F2 |
| DSColor / DSFont / DSSpacingSwiftUI | `DesignSystem/{DSColor,DSFont,DSSpacing+SwiftUI}.swift` | Accesores SwiftUI adaptativos claro/oscuro, Dynamic Type, CGFloat | Estilo de las vistas de Presupuesto |
| PrimaryButton | `DesignSystem/Components/PrimaryButton.swift` | `mat-flat-button` primary: normal/disabled/loading (loading>disabled), touch ≥44pt | Botones de acción F2 |
| TextInputField | `DesignSystem/Components/TextInputField.swift` | `mat-form-field outline`: normal/focus/error, prefijo, toggle de visibilidad | Inputs F2 |
| Card / LoadingState / ErrorState | `DesignSystem/Components/Containers.swift` | `mat-card` r16; spinner con mensaje; error icono+texto (no color solo) | Contenedores/tabla y estados de carga/error de Presupuesto |
| CatalogView | `DesignSystem/Catalog/CatalogView.swift` | Catálogo dev: Colors→Typography→Spacing→Components, toggle tema y tamaño de texto | Verificación visual del DesignSystem |

### Tests `FutmondoKit`

| Fichero | Cobertura |
|---|---|
| `Tests/FutmondoKitTests/AuthServiceTests.swift` | login/refresh/bootstrap/logout, coalescing, teardown |
| `Tests/FutmondoKitTests/NetworkClientTests.swift` | construcción de URLRequest, mapeo de status, Bearer, cancelación |
| `Tests/FutmondoKitTests/DesignSystemTests.swift` | resolución de tokens por apariencia, cobertura de roles, contraste |

## Feature Budget y selector de campeonato (Angular — fuente de verdad de F2)

| Componente | Fichero | Responsabilidad | Relevancia F2 |
|---|---|---|---|
| BudgetService | `src/app/core/services/budget.service.ts` | `getBalances(championshipId?)` → `/api/v1/analytics/balances`; `getTeamDetail` → `/analytics/balances/{teamId}`; `syncTransactions()` → `/api/v1/sync/trigger` | Contrato de datos a replicar en el cliente nativo |
| ChampionshipService | `src/app/core/services/championship.service.ts` | Campeonato activo (signals); `localStorage` `futmondo_active_championship`; carga `/user/championships` con fallback a `/championships`; `hasClauses` | Lógica del selector de campeonato nativo |
| Budget models | `src/app/core/models/budget.model.ts` | `TeamBudget`, `BalancesResponse`, `TeamDetailResponse`, `Transaction`, `SyncTriggerResponse`, `SyncTaskResponse` | DTOs Swift de F2 |
| budget-overview | `features/budget/budget-overview/*` | Tabla de saldos por equipo + `prizes-dialog` | Pantalla a reproducir |
| budget-detail | `features/budget/budget-detail/*` | Detalle de altas/bajas por equipo | Pantalla de detalle |
| sync-dialog | `features/budget/sync-dialog/*` | Diálogo de sincronización | Flujo de sync F2 |

## Feature Market / Mercado (Angular — fuente de verdad de F3)

Vista de Mercado del frontend Angular: jugadores del computer disponibles para
fichar, con puja sugerida, rating Sofascore y % titularidad. Es la 2ª pestaña
del TabView nativo tras Presupuesto (F2). Analizada en profundidad en este run
(F3) porque F2 la dejó shallow/fuera.

| Componente | Fichero | Responsabilidad | Relevancia F3 |
|---|---|---|---|
| MarketComponent | `src/app/features/market/market.component.ts` | Pantalla de Mercado (standalone, `OnPush`). Signals `loading`/`error`/`bidding`/`userInfo`/`viewMode`/`sortField`; `MatTableDataSource<MarketPlayer>`. `loadData()` → `GET /api/v1/market/today?championship_id=…` y setea `players` + `user_info`. `confirmBid()` abre `BidDialogComponent` y hace `POST /api/v1/market/bid` (query `championship_id`/`player_id`/`player_slug`/`price`/`is_clause=false`). `cancelBid()` abre `ConfirmDialogComponent` y hace `POST /api/v1/market/cancelbid` (query `championship_id`/`bid_id`). `openSofascoreDetail()` abre `SofascoreDetailDialogComponent`. `sortCards()` ordena **descendente** por `sortField`; `sortOptions` = value/change/sofascore_rating/starter_pct/suggested_bid/points/average. `viewMode` `cards`\|`table` persistido en `localStorage` (`futmondo_view_market`, default `table`, `cards` en móvil si no hay preferencia). Reacciona al `championshipService.activeId()` vía `effect`. | **Pantalla a reproducir** en SwiftUI; define el modelo de datos y el flujo de puja/cancelación |
| BidDialogComponent | `src/app/features/market/bid-dialog.component.ts` | Diálogo de puja (template inline). `BidDialogData`: `playerName`/`team`/`suggestedBid`/`marketPrice`/`maxBid`. `bidAmount` inicia en `suggestedBid`. Validación: `>0`, `>= marketPrice` (mín), `<= maxBid` (máx); mensajes en castellano. Devuelve `BidDialogResult { confirmed, price }`. | Reglas de validación de puja a replicar nativamente |
| ConfirmDialogComponent | `src/app/features/market/confirm-dialog.component.ts` | Diálogo de confirmación genérico (`ConfirmDialogData`: `title`/`message`/`confirmText`/`cancelText`/`color`). Usado por Mercado para **confirmar cancelación** de puja; devuelve `boolean`. | Patrón de confirmación reutilizable |
| SofascoreDetailDialogComponent | `src/app/features/market/sofascore-detail-dialog.component.{ts,html}` | Diálogo de stats Sofascore de un jugador. Carga **async** `GET /api/v1/sofascore/player/{player_name}?championship_id=…` (endpoint **aparte**, NO `/market/*`). `SofascoreStats` (~19 campos). UI: rating hero circular (clases green/yellow/red) + grid de ~16 stat-cards; estados `loading`/`error`/`404`. | Vista de detalle a reproducir; su endpoint es `/sofascore/player/{name}`, no `/market/*` |

### Modelo de datos de Mercado

- **`MarketPlayer`** (interface TS en `market.component.ts`, ~28 campos): `player_id`,
  `slug`, `name`, `team`, `team_logo`, `position`, `position2`, `value`,
  `market_price`, `change`, `current_bid`, `current_bid_id`, `average`, `points`,
  `home_average`, `away_average`, `matches`, `suggested_bid`, `bid_confidence`,
  `bid_based_on`, `overpay_pct`, `expiration`, `sofascore_rating`, `sofascore_url`,
  `starter_pct`, `is_favorite`. (El backend `/today` emite además `photo`,
  `sofascore_id/goals/assists/appearances`; el frontend consume el subconjunto de
  arriba.)
- **`user_info`** (banner del Mercado): `balance`, `team_value`, `max_bid`,
  `active_bids_total`, `available_for_bids` (el backend añade `active_bids_count`).
  El banner HTML muestra `balance` (Presupuesto), `active_bids_total` (En pujas),
  `balance − active_bids_total` (Balance), `max_bid` (Puja máxima) y
  `available_for_bids` (Disponible).
- **`SofascoreStats`** (`sofascore-detail-dialog.component.ts`): `player_name`,
  `rating`, `goals`, `assists`, `appearances`, `matches_started`, `starter_pct`,
  `minutes_played`, `yellow_cards`, `red_cards`, `tournament`, `season`,
  `successful_dribbles`, `accurate_passes_pct`, `shots_on_target`, `tackles`,
  `interceptions`, `clean_sheets`, `saves`, `synced_at`.

### Backend de Mercado (verificado leyendo el código en este run)

| Componente | Fichero | Responsabilidad | Relevancia F3 |
|---|---|---|---|
| Market router | `backend/app/api/v1/endpoints/market.py` (~24 KB) | `GET /today`, `POST /bid`, `POST /cancelbid` (bajo prefijo `/api/v1/market`). Construye `players`+`user_info`; lee `market_today` (caché) con fallback a la API Futmondo (`/1/market/players`); calcula puja sugerida por % de sobrepago histórico desde `transactions` (`seller_team_id='market_team'`, SQL-en-endpoint, patrón heredado a NO ampliar); enriquece con `sofascore_cache` y favoritos. `bid`/`cancelbid` proxyan a Futmondo (`/1/market/bid`, `/1/market/cancelbid`). Validación de boundary: `price<=0` o `>PRICE_SANITY_CAP` → `422`. | Contrato real que el cliente nativo F3 consume sin cambios de servidor |
| Sofascore detail router | `backend/app/api/v1/endpoints/sofascore_detail.py` | `GET /player/{player_name}` (bajo prefijo `/api/v1/sofascore`): lee `sofascore_cache` por `player_name`; `starter_pct = round(matches_started/38*100)`; `404` si no hay fila. | Endpoint del diálogo de detalle Sofascore |

## Modelo de datos de auth (tablas)

- `app_users(id PK, futmondo_email UNIQUE, futmondo_user_id, display_name, created_at, last_login)`
- `refresh_tokens(token_hash PK, user_id FK, expires_at, revoked, created_at)`
- `user_championships(user_id, championship_id, name, initial_budget, has_clauses, excluded_teams, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank, is_pro, futmondo_team_id, PK(user_id, championship_id))`

## Sources

- `ios/Package.swift`, `ios/xtool.yml`
- `ios/Sources/FutmondoKit/Networking/*.swift`, `ios/Sources/FutmondoKit/Auth/*.swift`,
  `ios/Sources/FutmondoKit/DesignSystem/*.swift`
- `ios/Sources/FutmondoApp/*.swift`, `ios/Sources/FutmondoApp/DesignSystem/**/*.swift`
- `ios/Tests/FutmondoKitTests/*.swift`
- `angular-app/src/app/core/services/{budget,championship}.service.ts`,
  `angular-app/src/app/core/models/budget.model.ts`, `angular-app/src/app/features/budget/*`
- `angular-app/src/app/features/market/market.component.{ts,html}`,
  `bid-dialog.component.ts`, `confirm-dialog.component.ts`,
  `sofascore-detail-dialog.component.{ts,html}` (añadido en el run de F3)
- `backend/app/api/v1/endpoints/market.py`,
  `backend/app/api/v1/endpoints/sofascore_detail.py` (añadido en el run de F3)
- `backend/app/api/v1/endpoints/{balances,championships,user}.py`
- `backend/app/main.py`, `backend/app/auth/{routes,jwt_utils,dependencies,token_store,session_store,models}.py` (store previo)
- `backend/app/services/{integration_errors,futmondo_client,session_store}.py`, `backend/app/core/config.py` (store previo)
- `angular-app/src/app/core/services/auth.service.ts`, `championship.service.ts`
- `angular-app/src/app/core/interceptors/auth.interceptor.ts`
- `angular-app/src/app/core/guards/auth.guard.ts`
- `angular-app/src/app/core/preloading/idle-preloading-strategy.ts`
- `angular-app/src/app/features/login/login.component.ts`
- `angular-app/src/app/app.config.ts`
- `angular-app/src/styles.scss`, `angular-app/src/app/app.scss`, `angular-app/src/app/shared/styles/*.scss`
- `angular-app/angular.json`

## Assumptions & Open Questions

- Tamaños de servicio indicados en KB desde el listado de directorio (bytes),
  no por conteo de líneas de cada fichero. `sofascore_client.py` usa `curl_cffi`
  según el stack del `README.md`/`requirements.txt`; su cuerpo completo no se
  abrió en escaneos previos. El backend no se reanalizó en este run (shallow).
- La traducción exacta de cada token `--mat-sys-*` y primitiva compartida a un
  equivalente SwiftUI/HIG es trabajo del intent de diseño; aquí se inventaría la
  capa Angular de origen.
