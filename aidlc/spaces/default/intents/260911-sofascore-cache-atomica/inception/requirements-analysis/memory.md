<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-12T13:58:00Z — Bugfix reformulado en la conversación más allá de la descripción inicial: la caché de Sofascore se confirmó COMPARTIDA entre campeonatos (evidencia: ninguna lectura filtra por championship_id), así que el reemplazo es global y championship_id queda deprecada sin migración de esquema en este bugfix. El usuario aportó el matiz clave del "baneo a mitad", que elevó la detección explícita del baneo (403 vs no-encontrado) a protección principal, con el umbral del 50% como red secundaria.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
