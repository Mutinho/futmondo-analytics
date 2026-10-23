<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T11:10Z — U1 code-generation: lógica pura de tokens en FutmondoKit/DesignSystem (DSColorValue/DSSpacing/DSTypographyScale/ContrastRatio) testeable; vistas SwiftUI (DSColor/DSFont, Components, CatalogView) en FutmondoApp guardadas `#if canImport(SwiftUI)`. `swift build` OK; `swift test` 43/43 (14 nuevos + 29 de F1, sin regresión).
- 2026-10-19T11:53Z — U2 code-generation: `LoginView.swift` revestido con componentes/tokens de U1 (TextInputField email, PrimaryButton, ErrorState, Card, DSFont.h1, DSColor/DSSpacing), preservando init/logo/ShakeEffect/focus/sensoryFeedback/labels y sin tocar AuthViewModel. `swift build` OK; `swift test` 43/43 sin regresión.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-19T11:10Z — Step 5: colores en código (alternativa documentada del plan) en vez de Assets.xcassets, por incompatibilidad de `actool` con el toolchain Linux/WSL; hex con fuente única en DSColorToken; Package.swift intacto. Se puede migrar a asset catalog al construir en dispositivo con xtool.
- 2026-10-19T11:10Z — Cobertura line vía llvm-cov no medible de forma fiable en este toolchain Linux; la lógica pura queda ejercitada por 14 tests; vistas SwiftUI fuera del cómputo por contrato (validación en dispositivo).

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
None.
