<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T14:54Z — Rough Mockups: wireframes low-fi de Presupuesto (filas/cards por equipo con saldo/rendimiento/puja máx/premios, tokens money-pos/neg con signo + color), selector como `Menu` desde el título de la navigation bar, menú de orden con las claves de la web, estados carga/error, y `TabView` 1-pestaña (Liquid Glass) abajo. User-flow con selección/persistencia en `UserDefaults` y fallback de endpoints de campeonatos como la web. Accesibilidad: filas como elementos VoiceOver, Dynamic Type, color no es único portador de significado.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
