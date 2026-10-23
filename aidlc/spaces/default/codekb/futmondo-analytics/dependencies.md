# Dependencies — Futmondo Analytics

> Nota de cobertura (run 261018-design-system-nativo): este intent es de theming
> nativo y no reanalizó manifiestos de dependencias; la prosa se **preserva** del
> escaneo previo (store UNVERIFIED) y queda como cobertura shallow. No hay nuevas
> dependencias por el diseño nativo (SwiftUI usa SDK de Apple, coste 0 €).

## Backend (`backend/requirements.txt`, versiones exactas pineadas)

| Dependencia | Versión | Uso | Relevancia F1 |
|---|---|---|---|
| requests | 2.34.2 | Cliente HTTP de `FutmondoClient` (login + datos) | Backend que iOS reutiliza |
| python-dotenv | 1.2.3 | Carga de env en `config.py` | — |
| fastapi | 0.141.1 | Framework del backend reutilizado por F1 | Alto |
| uvicorn[standard] | 0.54.0 | ASGI server | — |
| pydantic | 2.13.5 | Modelos (`LoginRequest`, etc.) | Contrato de login |
| python-multipart | 0.0.32 | Form/multipart en FastAPI | — |
| psycopg2-binary | 2.9.13 | Driver PostgreSQL/Neon | — |
| curl_cffi | 0.16.3 | Cliente HTTP de Sofascore | — |
| PyJWT | 2.15.0 | Emisión/validación JWT access+refresh (HS256) | **Alto: núcleo del contrato auth que F1 reutiliza** |
| google-genai | 1.14.0 | Asistente AI (Gemini) | — |
| groq | 0.25.0 | Asistente AI (fallback) | — |
| pytest | 9.1.1 | Suite de tests (gate CI) | — |
| pytest-cov | 7.1.0 | Cobertura backend | — |
| httpx | 0.28.1 | Requerido por `starlette.testclient.TestClient` | — |

Herramientas del gate pineadas en los workflows (no en `requirements.txt`):
`ruff==0.16.9`, `pip-audit==2.10.1`.

Allowlist de pip-audit (`backend/.pip-audit-allowlist`): **vacía** — no hay
findings sin fix registrados. Formato: `CVE_ID dep version motivo alta caducidad`;
una entrada caducada vuelve a bloquear (`scripts/check-allowlist-expiry.sh`).

## Frontend (`angular-app/package.json`, rangos `^`/`~` con lock)

### dependencies

| Dependencia | Rango | Uso |
|---|---|---|
| @angular/{animations,cdk,common,compiler,core,forms,material,platform-browser,router,service-worker} | ^22.2.1 | Framework + UI + PWA. **Material + CDK** son la base del tema (Material 3) |
| chart.js | ^4.5.1 | Gráficos |
| ng2-charts | ^10.0.0 | Wrapper Angular de Chart.js |
| marked | ^18.0.11 | Render markdown (asistente) |
| rxjs | ~7.8.0 | Reactividad |
| tslib | ^2.3.0 | Runtime TS |

### devDependencies

| Dependencia | Rango/versión | Uso |
|---|---|---|
| @angular/build | ^22.2.0 | Builder (build + unit-test); compila `styles.scss` |
| @angular/cli | ^22.2.0 | CLI |
| @angular/compiler-cli | ^22.2.1 | AOT |
| @vitest/coverage-v8 | 4.1.11 (exacto) | Cobertura frontend (pin exacto, gate bloqueante) |
| vitest | 4.1.11 | Test runner |
| jsdom | ^25.0.1 | DOM para tests |
| prettier | ^3.8.1 | Formato |
| typescript | ~6.0.2 | Compilador |

> Nota: ESLint se cita como presente (flat config `eslint.config.js`) pero sus
> devDependencies no están instaladas y el paso es advisory/diferido (deuda); no
> aparece en `package.json`.

## Dependencias de infraestructura/servicios

- **Neon PostgreSQL** (tier free) vía `DATABASE_URL`.
- **Fly.io** (apps `futmondo-api`, `futmondo-app`; `flyctl` en CD).
- **GitHub Actions** (tier free) + **gitleaks-action @v3**.
- APIs externas: **Futmondo** (`BASE_URL` default `https://api.futmondo.com`) y
  **Sofascore**.

Todas sostenibles en tiers gratuitos (mandato coste 0 €). La única excepción
acotada afirmada en `team.md` es el coste de publicación de distribución nativa
(Apple Developer Program) para habilitar la distribución de la app nativa.

## Dependencias del cliente nativo iOS (`ios/`, SwiftPM — añadido por F1)

- **SwiftPM**: `ios/Package.swift` declara `dependencies: []` — **cero
  dependencias externas**; solo frameworks del **SDK de Apple** (Foundation,
  `URLSession`/`FoundationNetworking`, SwiftUI, Observation, Security/Keychain,
  XCTest). Coste 0 € de librerías.
- **Empaquetado**: `xtool` (`ios/xtool.yml`) para construir el `.app` iOS; OSS.
- **Guardas de plataforma**: `#if canImport(SwiftUI)` / `#if canImport(Security)`
  permiten que `swift test` compile `FutmondoKit` en Linux/WSL sin SwiftUI ni
  Keychain reales.
- Única excepción de coste acotada (afirmada en `team.md`): el coste de
  publicación de distribución nativa (Apple Developer Program), no una
  dependencia de software.

## Dependencias de diseño nativo iOS (intent 261018)

- **SwiftUI + SDK de Apple**: sin dependencias de pago; es la base del sistema de
  diseño nativo que reproduce el tema Material 3 de Angular.
- Donde Material 3 no tenga equivalente 1:1, **Apple HIG** (guía, no dependencia).
- Google Stitch **descartado** como herramienta/referencia de diseño (decisión
  del propietario, 2026-10-18).

## Dependencias internas (cross-módulo, auth)

- `auth/routes.py` → `jwt_utils`, `token_store`, `session_store`,
  `session_service`, `SessionRepository`, `FutmondoClient`.
- `main.py` (AuthMiddleware) → `jwt_utils.verify_token`, `token_store.init_auth_tables`.
- `jwt_utils` → `config.JWT_SECRET`.
- `futmondo_client` → `integration_errors`, `config.BASE_URL`.
- Frontend: `app.config.ts` → `authInterceptor` → `AuthService`;
  `authGuard` → `AuthService`.
- Frontend (estilos): `angular.json` → `src/styles.scss`;
  `shared/styles/_index.scss` → `@forward` de los partials compartidos.
- iOS (`ios/`): `FutmondoApp` → `FutmondoKit` (único enlace entre targets);
  `AuthService` → `NetworkClient` + `KeychainStore` + `TokenHolder` + `LogoutFlagStore`;
  `URLSessionNetworkClient` → `APIRequest`/`NetworkError`; los accesores SwiftUI
  del DesignSystem (`DSColor`/`DSFont`) → tokens puros de `FutmondoKit`
  (`DSColorToken`/`DSTypographyScale`/`DSSpacing`). El testTarget
  `FutmondoKitTests` → solo `FutmondoKit`.

## Sources

- `ios/Package.swift`, `ios/xtool.yml` (SwiftPM, cero deps externas)
- `ios/Sources/FutmondoKit/Auth/AuthService.swift`, `.../Networking/URLSessionNetworkClient.swift`
- `backend/requirements.txt`, `backend/.pip-audit-allowlist`, `backend/ruff.toml` (store previo)
- `angular-app/package.json`, `angular-app/eslint.config.js`, `angular-app/angular.json`
- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml` (store previo)
- `backend/app/auth/routes.py`, `backend/app/services/futmondo_client.py` (store previo)
- `backend/app/core/config.py` (store previo)

## Assumptions & Open Questions

- No se auditó `package-lock.json` para resolver las versiones exactas instaladas
  de cada rango `^`/`~` del frontend; se reportan los rangos declarados. El gate
  usa `npm ci` (lock) y `npm audit --audit-level=high`. Los manifiestos no se
  reverificaron en este run enfocado de theming (prosa preservada / shallow).
