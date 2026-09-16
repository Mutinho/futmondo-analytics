<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-15T15:43:00Z — u1-durable-session: TTL modelado como absoluto (no deslizante) para congelar el comportamiento observable actual del SessionStore (C5); purga perezosa al leer evita un job de limpieza (coste 0€). La máquina de estados añade un estado rehydrating explícito para que las dos salidas (active/unrecoverable) mapeen a FR1.2/FR1.3.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-15T15:44:00Z — Revisión adversarial de u1 (iter 1) READY con 2 Minor no bloqueantes, diferidos al gate consolidado del diseño funcional para no invalidar el receipt terminal de U1 en flujo per-unidad gate:false: R-01 (añadir FR5.2 como reverse Deferred en traceability.json de u1) y R-02 (aclarar la etiqueta del edge active->absent en la máquina de estados para no leerse como contradicción de BR1.5). Se incorporarán si el humano lo pide en el gate único.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
