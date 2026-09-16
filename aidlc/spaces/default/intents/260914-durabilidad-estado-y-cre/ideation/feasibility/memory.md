<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-09-14T17:05Z — Stage CONDITIONAL ejecutada (no trivial): hay restricciones duras (coste 0 €, sin reescrituras grandes), integración con Neon PostgreSQL/Fly.io y decisiones técnicas con riesgo moderado (persistir sesiones/tareas, tratar el secreto de credenciales). market-research se saltó por ser intent técnico interno, así que no hay artefactos de mercado que consumir; el consumo obligatorio es intent-statement.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
