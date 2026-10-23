<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T15:35Z — Requirements: FR1 (carga/visualización Presupuesto con 9 campos de `TeamBudget` + formato M/K con tokens de dinero), FR2 (ordenación por 6 claves web), FR3 (selector en navigation bar con fallback de endpoints + persistencia `UserDefaults` + primer campeonato por defecto), FR4 (carga/error con reintento sin corromper estado), FR5 (andamiaje `TabView` 1-pestaña + `NavigationStack`). NFR1 cero deps, NFR2 seguridad reutiliza F1, NFR3 fidelidad validada en dispositivo, NFR4 60fps/<100ms, NFR5 accesibilidad, NFR6 verificación `FutmondoKit`+`swift test`. Todo trazado a scope/backlog/codekb (fórmula performance y endpoints verificados en reverse-engineering).
- 2026-10-19T15:40Z — Tras review advisory READY, aplicados los 4 findings a requirements.md: FR1.3 con tabla de formato M/K concreta (umbral, decimales, redondeo, signo) testeable; FR2.1 orden descendente-sólo como decisión explícita (toggle asc/desc diferido); FR3.1 caso ambos-endpoints-fallan enlazado a FR4.2; FR4.1 criterio de aceptación explícito (<100 ms). Re-pase de reviewer iteración 2 por cambio en artefacto `produces`.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
