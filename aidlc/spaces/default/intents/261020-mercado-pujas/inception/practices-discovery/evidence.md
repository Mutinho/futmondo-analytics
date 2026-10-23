# Evidence — F3 Mercado (261020-mercado-pujas)

> Evidencia de la CodeKB y del repo que respalda cada práctica confirmada.
> Prosa en castellano, tokens técnicos verbatim en inglés. Las rutas de repo se
> citan tal como las documenta la CodeKB; algunas entradas del backend/CI vienen
> del store previo (shallow) marcado en los ficheros de CodeKB.

## Coste 0 € / solo SDK de Apple

- `ios/Package.swift` declara `dependencies: []` — **cero dependencias externas
  de SwiftPM**; solo frameworks del SDK de Apple (Foundation, `URLSession`/
  `FoundationNetworking`, SwiftUI, Observation, Security/Keychain, XCTest).
  Fuente CodeKB: `technology-stack.md` (sección "Cliente nativo iOS"),
  `dependencies.md` (sección "Dependencias del cliente nativo iOS").
- Excepción acotada (Apple Developer Program) documentada en `team.md`
  `## Deployment` / `## Mandated` y `project.md` `## Mandated`; **no activada**
  en F3 (`scope-document.md` → "Distribución … excepción acotada no activada").

## Trunk-based + squash-merge + Conventional Commits

- `team.md` `## Way of Working`: trunk-based sobre `main`, squash-merge, base y
  destino `main`, Conventional Commits con scope en castellano.
- `org.md` `## Way of Working`: misma línea base durable (squash-merge, trunk).

## Gate de CI bloqueante (F3 no lo modifica, lo respeta)

- `.github/workflows/ci.yml` — job `quality`, disparo `pull_request → main`
  (required status check). Fuente CodeKB: `code-quality-assessment.md`
  ("Gate de CI (bloqueante)").
- `.github/workflows/fly-deploy.yml` — job `verify`, disparo `push → main`;
  cadena `verify → deploy-backend → deploy-frontend → smoke-test`.
- Pasos bloqueantes replicados en ambos gates: gitleaks-action **@v3**,
  `ruff check .` (ruff **0.16.9**), `pytest -q --cov=app` con
  `--cov-fail-under=27` (`backend/pytest.ini`), `scripts/check-allowlist-expiry.sh`,
  `pip-audit` (pin **2.10.1**), `ng test --watch=false` (Vitest), `npm audit
  --audit-level=high`. Fuente CodeKB: `code-quality-assessment.md`,
  `technology-stack.md` ("Infraestructura y CI/CD").
- `ruff.toml`: `target-version = py312`, `line-length = 100`,
  `select = ["E","F","I"]`. Fuente CodeKB: `technology-stack.md`.

## Pisos de cobertura (estado del repo; F3 no los toca)

- `backend/pytest.ini`: `--cov-fail-under=27` (line-coverage total, sin
  `--cov-branch`), valor medido exacto (~27.52%). Fuente CodeKB:
  `code-quality-assessment.md` ("Pisos de cobertura heredados").
- `angular.json` (target `test`): `coverageThresholds` `statements 19`,
  `branches 19`, `functions 17`, `lines 18`; enforcement dentro de `ng test`
  (builder `@angular/build:unit-test`, runner Vitest). Fuente CodeKB:
  `code-quality-assessment.md`, `technology-stack.md` ("Frontend").

## Testing posture nativo iOS (test-after, FutmondoKit + XCTest)

- Separación library/app: la lógica (Networking, Auth, DesignSystem puro) vive en
  **`FutmondoKit`** (cubierta por `swift test`); la UI SwiftUI vive en
  **`FutmondoApp`** tras `#if canImport(SwiftUI)`; el testTarget
  `FutmondoKitTests` NO depende de la app → `swift test` compila en Linux/WSL sin
  SwiftUI. Fuente CodeKB: `technology-stack.md` ("Productos y targets"),
  `code-quality-assessment.md` ("Calidad de la capa nativa iOS").
- Cobertura `llvm-cov` no fiable en WSL → piso iOS no verificado numéricamente;
  vistas validadas en dispositivo (iPhone 13 Pro vía `xtool dev build`). Fuente
  CodeKB: `technology-stack.md` ("Restricciones del toolchain"),
  `project.md` `## Corrections` (aprendizaje 2026-10-19).

## Diseño (fuente de verdad = tema Angular Material 3)

- `angular-app/src/styles.scss`: `mat.theme` con primaria `mat.$green-palette`,
  terciaria `mat.$violet-palette`, `typography: Roboto`, tokens `--mat-sys-*`,
  tokens semánticos propios (`money-positive` #2e7d32/#66bb6a, `money-negative`
  #d32f2f/#ef5350, escala `h1`/`h2`/`h3`, gradiente splash
  #1b5e20→#2e7d32→#43a047), modo claro/oscuro vía Material + `body.dark-theme`.
  Fuente CodeKB: `technology-stack.md` ("Theming / sistema de diseño"),
  `code-quality-assessment.md` ("Calidad de la capa de estilos").
- Color Sets en código (`DSColorToken`/`DSColorValue`), no en `Assets.xcassets`
  (`actool` ausente en WSL). Fuente CodeKB: `technology-stack.md`
  ("Restricciones del toolchain"); `project.md` `## Corrections` (2026-10-19).
- Comportamiento = vista Angular `angular-app/src/app/features/market/`. Fuente:
  `intent-statement.md`, `scope-document.md`.

## Seguridad (reforzada por la escritura y el 2º endpoint de F3)

- Refresh token solo en Keychain (`KeychainTokenStore`, servicio
  `com.futmondo.app.auth`, `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`,
  sin iCloud sync); access token solo en memoria. Fuente CodeKB:
  `technology-stack.md` ("Almacén seguro"), `code-quality-assessment.md`
  ("Seguridad del refresh token"), `architecture.md` ("Modelo de autenticación").
- Errores de integración tipados **sin material de credencial**
  (`NetworkError`/`AuthError`/`KeychainError` con payloads `Int`/`String`;
  rechazo de base URL no-https). Fuente CodeKB: `code-quality-assessment.md`
  ("Manejo de errores tipado, sin credenciales"); `project.md` `## Forbidden`
  (2026-09-24).
- `/api/v1/*` exigen `Authorization: Bearer` (AuthMiddleware en `main.py`);
  `JWT_SECRET` no-default obligatorio en arranque (NFR1.1,
  `config.resolve_jwt_secret`), CI inyecta uno efímero no productivo. Fuente
  CodeKB: `architecture.md` ("Modelo de autenticación"),
  `code-quality-assessment.md` (nota de `JWT_SECRET` efímero en CI).

## Consumo de endpoints de Mercado (sin cambios de backend)

- `GET /api/v1/market/today` (banner + cards + orden), `POST /api/v1/market/bid`
  (pujar), `POST /api/v1/market/cancelbid` (cancelar), detalle Sofascore
  (`SofascoreClient`, `curl_cffi`). Fuente CodeKB: `business-overview.md`
  ("Mercado (market)"), `architecture.md` ("Integraciones externas");
  `scope-document.md` (contratos de lectura/escritura/detalle).

## Idioma

- Identificadores/docstrings/comentarios en inglés; texto de usuario y commits en
  castellano. Fuente: `org.md` `## Mandated` (conversation language),
  `team.md` `## Code Style`, `project.md` `## Mandated`.

## Sources

- CodeKB `aidlc/spaces/default/codekb/futmondo-analytics/`: `technology-stack.md`,
  `dependencies.md`, `code-quality-assessment.md`, `architecture.md`,
  `business-overview.md`.
- Rutas de repo citadas por la CodeKB: `ios/Package.swift`, `ios/xtool.yml`,
  `ios/Sources/FutmondoKit/**`, `ios/Sources/FutmondoApp/**`,
  `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`,
  `backend/ruff.toml`, `backend/pytest.ini`, `angular-app/angular.json`,
  `angular-app/package.json`, `angular-app/src/styles.scss`,
  `angular-app/src/app/features/market/`.
- Memoria: `aidlc/spaces/default/memory/{org,team,project}.md`.
- Ideación F3: `.../ideation/intent-capture/intent-statement.md`,
  `.../ideation/scope-definition/scope-document.md`.

## Assumptions & Open Questions

- La CodeKB marca varias secciones de backend/CI y de los manifiestos del
  frontend como **shallow / prosa preservada** del store previo (los runs de
  theming y de budget no reverificaron esas áreas). Las rutas y pins citados
  (`ruff==0.16.9`, `pip-audit==2.10.1`, pisos de cobertura) provienen de ese
  store previo; no se reabrieron fichero a fichero en este run de confirmación.
  No afecta a la conclusión: F3 no modifica backend/CI, solo los respeta.
