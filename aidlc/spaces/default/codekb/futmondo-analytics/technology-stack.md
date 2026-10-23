# Technology Stack — Futmondo Analytics

Versiones tomadas de `backend/requirements.txt`, `angular-app/package.json`,
`backend/ruff.toml`, `backend/pytest.ini`, `.github/workflows/*.yml` y `.nvmrc`.

> Nota de cobertura (run 261019-presupuesto-selector-cam): refresco incremental
> enfocado en la **capa nativa iOS** (`ios/`) añadida por el intent F1
> `261018-design-system-nativo` y en las áreas Budget/championship que F2 toca.
> El backend auth, los workflows y el frontend Angular (salvo budget/championship)
> **no** se reanalizaron en este run (prosa preservada / shallow del store previo).

## Backend

| Área | Tecnología | Versión | Fuente |
|---|---|---|---|
| Lenguaje/runtime | Python | 3.12 | `pytest.ini`/CI `setup-python 3.12`, `ruff.toml` `target-version=py312` |
| Framework web | FastAPI | 0.141.1 | `requirements.txt` |
| ASGI server | uvicorn[standard] | 0.54.0 | `requirements.txt` |
| Validación | pydantic | 2.13.5 | `requirements.txt` |
| JWT | PyJWT | 2.15.0 | `requirements.txt` (HS256, `jwt_utils.py`) |
| HTTP client (Futmondo) | requests | 2.34.2 | `requirements.txt`, `futmondo_client.py` |
| HTTP client (Sofascore) | curl_cffi | 0.16.3 | `requirements.txt` |
| Driver DB | psycopg2-binary | 2.9.13 | `requirements.txt` |
| Multipart | python-multipart | 0.0.32 | `requirements.txt` |
| Env | python-dotenv | 1.2.3 | `requirements.txt`, `config.py` |
| AI (asistente) | google-genai / groq | 1.14.0 / 0.25.0 | `requirements.txt` |
| Tests | pytest / pytest-cov / httpx | 9.1.1 / 7.1.0 / 0.28.1 | `requirements.txt`, `pytest.ini` |
| Lint/format | ruff | 0.16.9 (pin en CI) | `ci.yml`/`fly-deploy.yml` (`pip install ruff==0.16.9`), `ruff.toml` |
| Dep audit | pip-audit | 2.10.1 (pin en CI) | `ci.yml`/`fly-deploy.yml` |

## Base de datos

| Área | Tecnología | Detalle | Fuente |
|---|---|---|---|
| Producción | Neon PostgreSQL (serverless) | Frankfurt, tier free; único engine soportado vía `DATABASE_URL` | `README.md`, `config.py`, `db_connection.py` |
| Local/tests | SQLite | ruta `db.db_type` para tests/local; fixtures fake in-memory | `db_connection.py`, `conftest.py` |

## Frontend

| Área | Tecnología | Versión | Fuente |
|---|---|---|---|
| Framework | Angular | ^22.2.1 (core/common/forms/router/...) | `package.json` |
| UI | Angular Material + CDK | ^22.2.1 | `package.json` |
| Build system | @angular/build + @angular/cli | ^22.2.0 | `package.json`, `angular.json` |
| Reactividad | RxJS | ~7.8.0 (+ Angular signals) | `package.json`, `auth.service.ts` |
| Charts | chart.js / ng2-charts | ^4.5.1 / ^10.0.0 | `package.json` |
| Markdown | marked | ^18.0.11 | `package.json` |
| Test runner | Vitest (builder `@angular/build:unit-test`, `runner: vitest`) | 4.1.11 | `package.json`, `angular.json` |
| Coverage | @vitest/coverage-v8 | 4.1.11 (pin exacto) | `package.json` |
| DOM test | jsdom | ^25.0.1 | `package.json` |
| Formato | prettier | ^3.8.1 | `package.json`, `.prettierrc` |
| Lint | ESLint (flat config, advisory/diferido) | — | `eslint.config.js`, `ci.yml` (advisory) |
| TypeScript | typescript | ~6.0.2 | `package.json` |
| Node (local) | Node | 22.22.3 (`.nvmrc`); CI usa `node-version: '22'` | `.nvmrc`, CI |
| Lenguaje de UI | PWA (service worker + manifest) | `@angular/service-worker` ^22.2.1 | `package.json`, `ngsw-config.json` |

### Theming / sistema de diseño (frontend) — fuente de verdad del diseño nativo

| Área | Tecnología / token | Detalle | Fuente |
|---|---|---|---|
| Sistema de tema | Angular Material 3 (`mat.theme`) | primaria `mat.$green-palette`, terciaria `mat.$violet-palette`, `typography: Roboto`, `density: 0` | `src/styles.scss` |
| Lenguaje de estilos | SCSS | `inlineStyleLanguage: scss`; entrada única `styles: [src/styles.scss]`; schematics component `style: scss` | `angular.json` |
| Tokens de sistema | CSS custom properties `--mat-sys-*` | surface/on-surface/on-surface-variant/surface-container-*/outline-variant/primary generados por el tema | `styles.scss`, `app.scss`, `shared/styles/*` |
| Tokens semánticos propios | SCSS/CSS | `money-positive` #2e7d32/#66bb6a, `money-negative` #d32f2f/#ef5350; escala `h1`/`h2`/`h3`; gradiente splash `#1b5e20→#2e7d32→#43a047` | `styles.scss` |
| Modo claro/oscuro | Material 3 + `body.dark-theme` | Material gestiona el esquema; overrides custom bajo `body.dark-theme` / `.dark-theme &` | `styles.scss`, `_player-card.scss` |
| Tipografía | Roboto | `font-family: 'Roboto', sans-serif`, base 14px | `styles.scss` |
| Budget de estilos | `@angular/build` budgets | `anyComponentStyle` warn 8kB / error 12kB | `angular.json` |

## Infraestructura y CI/CD

| Área | Tecnología | Detalle | Fuente |
|---|---|---|---|
| Hosting | Fly.io | Apps `futmondo-api` + `futmondo-app` (nginx) | `README.md`, `fly-deploy.yml`, `fly.toml` |
| Reverse proxy | nginx | SPA + proxy `/api/*` y `/auth/*` | `nginx.prod.conf`, `README.md` |
| CI | GitHub Actions | `ci.yml` (PR→main), `fly-deploy.yml` (push→main) | `.github/workflows/` |
| Secret scan | gitleaks (action `@v3`, unificado ambos gates) | bloqueante | `ci.yml`, `fly-deploy.yml` |
| Orquestación local | docker-compose | `docker-compose.yml` | repo root |

## Cliente nativo iOS (`ios/`, SwiftPM) — añadido por F1

Capa nativa iOS introducida por el intent F1 `261018-design-system-nativo`
(login nativo + sistema de diseño). Paquete SwiftPM que reutiliza el backend
FastAPI existente; **Apple SDK únicamente, cero dependencias externas de
SwiftPM** (`dependencies: []` en `Package.swift`).

| Área | Tecnología | Versión / detalle | Fuente |
|---|---|---|---|
| Lenguaje | Swift | `swift-tools-version:6.0` (strict concurrency) | `ios/Package.swift` |
| UI | SwiftUI | vistas bajo `#if canImport(SwiftUI)`; `@available(iOS 17, macOS 14)` en `@main`/vistas | `Sources/FutmondoApp/*.swift` |
| Estado observable | Observation (`@Observable`) | `AuthViewModel` bajo `#if canImport(Observation)` | `AuthViewModel.swift` |
| Build system | SwiftPM (`PackageDescription`) | plataformas `.iOS(.v15)`, `.macOS(.v12)` | `Package.swift` |
| Empaquetado iOS | xtool | `version: 1`, `bundleID: com.futmondo.app`, `product: FutmondoApp` | `ios/xtool.yml` |
| Networking | Foundation `URLSession` (+ `FoundationNetworking` en Linux) | sin libs externas | `URLSessionNetworkClient.swift` |
| Almacén seguro | Keychain Services (`Security`) | bajo `#if canImport(Security)`; `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` | `KeychainTokenStore.swift` |
| Tests | XCTest (`swift test`) | corren solo sobre `FutmondoKit` en Linux/WSL | `Tests/FutmondoKitTests/*.swift` |
| JWT/cripto backend | PyJWT / HS256 (reutilizado) | sin cambios de criptografía en cliente | backend `jwt_utils.py` |

### Productos y targets (`Package.swift`)

- **`FutmondoKit`** (library): lógica device-independent y testeable —
  Networking, Auth (`AuthService`, DTOs, `TokenHolder`, `KeychainStore` + su
  doble in-memory) y la base pura del DesignSystem (tokens/escala/contraste
  SwiftUI-free). El `KeychainTokenStore` real va tras `#if canImport(Security)`
  para compilar en Linux/WSL.
- **`FutmondoApp`** (library product empaquetada por xtool en el `.app`): shell
  SwiftUI (`AuthViewModel`, `LoginView`, `SplashView`, `@main FutmondoApp`) más
  los accesores SwiftUI del DesignSystem y los componentes/catálogo. Todo bajo
  `#if canImport(SwiftUI)`; el target de test NO depende de él, así que
  `swift test` en Linux/WSL nunca arrastra SwiftUI.
- **`FutmondoKitTests`** (testTarget): XCTest sobre `FutmondoKit` únicamente.

### Restricciones del toolchain (WSL/Linux) — ya afirmadas en memoria

- `actool` (asset-catalog compiler) NO disponible en Linux/WSL → los Color Sets
  se definen EN CÓDIGO (`DSColorToken`/`DSColorValue`), no en `Assets.xcassets`;
  `Package.swift` no declara `resources` de asset catalog.
- La cobertura de línea (`llvm-cov`) NO es fiable con el toolchain Swift en
  Linux/WSL: la lógica pura testeable vive en `FutmondoKit` (cubierta con
  `swift test`); las vistas SwiftUI van en `FutmondoApp` tras
  `#if canImport(SwiftUI)` y se validan en dispositivo (iPhone 13 Pro vía
  `xtool dev build`), fuera del cómputo de cobertura.

## Relevancia para F1 (login nativo iOS)

El cliente nativo F1 es **Swift/SwiftUI** (ya presente en el repo bajo `ios/`) y
reutiliza este backend. No introduce coste ni dependencias de pago salvo la
excepción acotada de publicación de distribución nativa (Apple Developer
Program), documentada como excepción al mandato de coste 0 € en `team.md`. El
almacén seguro nativo del refresh token es iOS Keychain (`KeychainTokenStore`,
servicio `com.futmondo.app.auth`, cuenta `refresh_token`). PyJWT/HS256 del
backend se reutiliza sin cambios de criptografía.

## Relevancia para el sistema de diseño nativo iOS (intent 261018)

El tema a reproducir es **Angular Material 3** (paleta verde/violeta, Roboto,
tokens `--mat-sys-*`). El target nativo usa **SwiftUI + SDK de Apple** (coste
0 €, sin dependencias de pago); donde Material 3 no tenga equivalente 1:1 en
SwiftUI (densidad, ciertos tokens de sistema, `::ng-deep`), se cubre con **Apple
HIG**. No se introduce tooling de diseño de pago; Google Stitch quedó descartado
como referencia (decisión del propietario, 2026-10-18).

## Sources

- `ios/Package.swift`, `ios/xtool.yml` (paquete SwiftPM + empaquetado xtool)
- `ios/Sources/FutmondoKit/Networking/URLSessionNetworkClient.swift`,
  `ios/Sources/FutmondoKit/Auth/{AuthService,KeychainTokenStore}.swift`
- `ios/Sources/FutmondoApp/{FutmondoApp,LoginView,SplashView,AuthViewModel}.swift`
- `ios/Tests/FutmondoKitTests/*.swift`
- `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml` (store previo)
- `angular-app/package.json`, `angular-app/angular.json`
- `angular-app/src/styles.scss`, `angular-app/src/app/app.scss`, `angular-app/src/app/shared/styles/*.scss`
- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml` (store previo)
- `.nvmrc`, `README.md`, `backend/app/core/config.py`, `backend/app/services/db_connection.py` (store previo)

## Assumptions & Open Questions

- La versión exacta de nginx no está pineada en los ficheros leídos (viene de la
  imagen base del `Dockerfile`, no abierto línea a línea). La versión concreta
  del toolchain de Swift y de `xtool` no se afirma aquí: `ios/Package.swift`
  declara `swift-tools-version:6.0` pero la instalación del compilador no se
  verificó en este run.
- Las versiones de backend/CI y del frontend (salvo budget/championship) no se
  reverificaron en este run enfocado; se preservan del escaneo previo. El
  subárbol `ios/` y las áreas budget/championship sí se releyeron.
