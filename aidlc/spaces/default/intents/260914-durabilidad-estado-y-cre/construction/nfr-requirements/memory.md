<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-15T15:53:00Z — u1: NFR2 se fija como presupuesto de coste de BD por operación (≤1 op, 0 en cache-hit), no como p95/p99 absoluto, porque requirements.md difiere el umbral a medición en build y no hay infra de load-testing a coste 0€. Seguridad se apoya en guards existentes (test_jwt_startup, gitleaks) en vez de inventar controles. Observabilidad = logging estructurado sin secretos sobre logs de Fly.io (sin infra de pago).
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-15T15:54:00Z — Revisión adversarial de u1 nfr-requirements (iter 1) READY con 2 Minor no bloqueantes, diferidos al gate consolidado para no invalidar el receipt terminal en flujo per-unidad gate:false: R-01 (el resumen confirmado enumeraba NFR2→2.1 y NFR5→5.1/5.2, pero los artefactos añaden NFR2.2 y NFR5.3 — cobertura aditiva, mismos upstream IDs) y R-02 (NFR5.3 agrupado bajo NFR5 en traceability pero su Fuente declarada es FR1.3 — etiqueta de linaje imprecisa). Se incorporan si el humano lo pide en el gate único.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
