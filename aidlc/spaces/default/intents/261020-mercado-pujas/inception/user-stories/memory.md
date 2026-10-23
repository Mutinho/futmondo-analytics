<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-20 — 7 historias (US1 abrir/carga, US2 banner, US3 cards, US4 orden, US5 pujar, US6 cancelar, US7 Sofascore) en Given/When/Then, actor P1 (el mánager). Cobertura completa FR1–FR8 (traceability.json). US1–US6 Must, US7 Should. Riesgo anotado: US5/US6 tienen efecto real en el campeonato; validar en dispositivo con cuidado (jugador de prueba).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-20 — Reviewer advisory (product-lead, 1 iter) sobre stories: READY, 1 Major + 3 Minor aplicados. Major: US5 desdoblado rechazo-backend (2xx false/4xx, con message, sin recarga) vs error-de-red/5xx (aviso genérico, sin recarga). Minor: US6 mismo desdoble; US4 añade criterio de orden por defecto (value desc); US2 precisa umbrales de color (Balance verde si ≥0, Disponible verde si >0), alineado con el Angular.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
