<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T17:42Z — NFR Requirements U1: SR1-SR4 (sin credenciales en errores, `UserDefaults` sólo id no sensible, HTTPS, decode estricto) + TS1-TS3 (cero deps, target FutmondoKit testeable con lógica pura determinista, Sendable/async). Reutiliza seguridad/transporte de F1 sin introducir superficie nueva.
- 2026-10-20T09:23Z — NFR Requirements U2: PR1/PR2 render (List/LazyVStack 60fps; loading síncrono <100ms, observación en dispositivo); SR1-SR3 seguridad (la UI no maneja credenciales, errores sin fuga heredados de U1, `UserDefaults` sólo id, sin red nueva); TS1-TS3 (cero deps, target FutmondoApp bajo `#if canImport(SwiftUI)` sin XCTest de vistas en WSL, Liquid Glass automático del SDK).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
