# Evidence — Practices Discovery F2 `261019-presupuesto-selector-cam`

> Evidencia concreta (fichero y, donde aplica, líneas/símbolos) para cada práctica
> confirmada. Tokens técnicos verbatim en inglés.

## 1. Way of Working / trunk-based + squash-merge

- `aidlc/spaces/default/memory/team.md` → `## Way of Working`: "Mantenemos
  **trunk-based development** … **squash-merge** a `main`. Base de worktree `main`,
  destino `main`."
- `aidlc/spaces/default/memory/org.md` → `## Way of Working`: trunk-based, base/target
  `main`, squash-merge por defecto.

## 2. Coste 0 € + cero dependencias externas iOS

- `ios/Package.swift` → `dependencies: []` (línea de `dependencies` del `Package`) y
  comentario de cabecera: "Apple SDK only: zero external SwiftPM dependencies
  (NFR-2 / P-3)."
- `aidlc/.../codekb/.../dependencies.md` → "SwiftPM: `ios/Package.swift` declara
  `dependencies: []` — **cero dependencias externas**; solo frameworks del **SDK de
  Apple**."
- `team.md` → `## Deployment` / `project.md` → `## Mandated`: mandato coste 0 € con
  excepción acotada Apple Developer Program.

## 3. Gate de CI bloqueante (replicado PR + push)

- `aidlc/.../codekb/.../code-quality-assessment.md` → `## Gate de CI (bloqueante)`:
  tabla con gitleaks @v3, `ruff check` (ruff 0.16.9), `pytest --cov-fail-under=27`,
  `pip-audit` (2.10.1), `ng test` (Vitest), `npm audit --audit-level=high`; replicado
  en `ci.yml` job `quality` y `fly-deploy.yml` job `verify`.
- Pisos de cobertura: backend `--cov-fail-under=27` en `backend/pytest.ini`; frontend
  `coverageThresholds` 19/19/17/18 en `angular.json`.

## 4. Política de idioma (EN símbolos / ES prosa)

- `ios/Sources/FutmondoApp/DesignSystem/DSColor.swift` → docstring en inglés
  ("SwiftUI accessor for the design-system color tokens…"), símbolos en inglés
  (`DSColor`, `primary`, `onPrimary`, `moneyPositive`, `moneyNegative`).
- `ios/Sources/FutmondoKit/DesignSystem/DSColorValue.swift` → docstrings en inglés,
  tipos `DSAppearance`, `DSRGB` en inglés.
- `aidlc/spaces/default/memory/project.md` → `## Mandated` (affirmed 2026-10-18):
  "identificadores, docstrings y comentarios en INGLÉS y texto de cara al usuario /
  mensajes de commit en CASTELLANO".

## 5. Tema Angular Material 3 como fuente de verdad del diseño nativo

- `ios/Tests/FutmondoKitTests/DesignSystemTests.swift` →
  `testPrimaryTokenResolvesByAppearance()`:
  `DSColorToken.primary.value.hex(for: .light) == "#2E7D32"` /
  `.dark == "#66BB6A"` (verde Angular, light/dark). `[BR1.1, FR1]`.
- `ios/Sources/FutmondoApp/DesignSystem/DSColor.swift` → tokens de rol
  (`primary`, `tertiary`, `surface`, `onSurface`, `onSurfaceVariant`,
  `moneyPositive`, `moneyNegative`) reproduciendo la paleta Material 3.
- `aidlc/.../codekb/.../technology-stack.md` → sección "Theming / sistema de diseño
  (frontend) — fuente de verdad del diseño nativo" (tokens `--mat-sys-*`,
  `money-positive` #2e7d32/#66bb6a, `money-negative` #d32f2f/#ef5350).
- `project.md` → Correction learned 2026-10-18 (Google Stitch descartado; Material 3
  como fuente de verdad).

## 6. Estructura y testing de la capa nativa iOS

- `ios/Package.swift`:
  - target `FutmondoKit` (library, `path: "Sources/FutmondoKit"`), `dependencies: []`.
  - target `FutmondoApp` (library empaquetada por xtool, `dependencies: ["FutmondoKit"]`).
  - `testTarget` `FutmondoKitTests` con `dependencies: ["FutmondoKit"]` (NO depende de
    `FutmondoApp`).
  - Comentario: "`swift test` on Linux/WSL compiles only `FutmondoKit` +
    `FutmondoKitTests` and never pulls in SwiftUI."
- `ios/Sources/FutmondoApp/DesignSystem/DSColor.swift` → `#if canImport(SwiftUI)` +
  `@available(iOS 15.0, macOS 12.0, *)` guard sobre el accessor SwiftUI.
- `ios/Sources/FutmondoKit/DesignSystem/DSColorValue.swift` → "Pure, SwiftUI-free
  enum so the token logic compiles and is testable on Linux/WSL (`swift test`)."
- `ios/xtool.yml` → `product: FutmondoApp`; "`swift test` on WSL/Linux verifies
  `FutmondoKit`; the app, SwiftUI views and real Keychain are validated on the
  iPhone 13 Pro via `xtool dev build`."
- `project.md` → Corrections learned 2026-10-19 (lógica pura en `FutmondoKit`, vistas
  en `FutmondoApp` bajo `#if canImport(SwiftUI)`, validación en dispositivo; Color
  Sets en código; `llvm-cov` no fiable en WSL).

## 7. Seguridad de credenciales

- `aidlc/.../codekb/.../code-quality-assessment.md` → "Seguridad del refresh token:
  solo en Keychain (`AfterFirstUnlockThisDeviceOnly`, sin iCloud sync); el access
  token solo en memoria; `LogoutFlagStore` persiste solo un booleano."
- `ios/Sources/FutmondoKit/Auth/KeychainTokenStore.swift` (guardado bajo
  `#if canImport(Security)`; servicio `com.futmondo.app.auth`, cuenta
  `refresh_token`).
- `project.md` → `## Forbidden` (affirmed 2026-10-18): refresh token a almacenamiento
  seguro nativo, NUNCA a `localStorage`/`ApplicationSettings`.

## 8. Metodología de testing test-after

- `team.md` → `## Testing Posture`: "**Methodology**: test-after … implementa cada
  capa testeable y después se escriben y corren sus tests (test-after)."
- Tests presentes como evidencia del patrón: `AuthServiceTests.swift`,
  `NetworkClientTests.swift`, `DesignSystemTests.swift` en
  `ios/Tests/FutmondoKitTests/`.

## 9. No ampliar god-files (backend, no tocado por F2)

- `aidlc/.../codekb/.../code-structure.md` → marcados "God-file heredado (DEUDA
  CONOCIDA, NO ampliar)": `data_manager_v2.py`, `data_sync_service.py`.
- `project.md` → `## Forbidden`: NEVER ampliar los god-files ni el patrón
  SQL-en-router.

## Sources

- `ios/Package.swift`, `ios/xtool.yml`
- `ios/Sources/FutmondoKit/DesignSystem/{DSColorValue,DSTypographyScale,ContrastRatio}.swift`
- `ios/Sources/FutmondoKit/Auth/KeychainTokenStore.swift`
- `ios/Sources/FutmondoApp/DesignSystem/DSColor.swift`
- `ios/Tests/FutmondoKitTests/{DesignSystemTests,AuthServiceTests,NetworkClientTests}.swift`
- `aidlc/spaces/default/codekb/futmondo-analytics/{technology-stack,code-quality-assessment,dependencies,code-structure}.md`
- `aidlc/spaces/default/memory/{team.md,project.md,org.md}`

## Assumptions & Open Questions

- La existencia física de `ios/Sources/FutmondoKit/Auth/KeychainTokenStore.swift` y
  la separación de targets se confirmaron por listado de directorio y por
  `Package.swift`; el contenido línea a línea del `KeychainTokenStore` real no se
  abrió en este run (basta la evidencia del `Package.swift`, el `xtool.yml` y el
  code-quality-assessment preservado). Las aserciones de hex del tema se leyeron
  directamente en `DesignSystemTests.swift`.
