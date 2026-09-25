<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
- 2026-09-24T14:50:13Z — ARRASTRE a U2 (hallazgo adversarial R-01, nfr-design U1): NFR3 prohíbe la credencial también en `exc_info`/traceback, no solo en str/repr/args. El vector traceback vive en U2 (el frame que lanza el cliente aún tiene el token; el log estructurado NFR1 vive en U2). Restricción de diseño para U2: el camino de log estructurado serializa SOLO los campos tipados no sensibles (failure_mode/status/endpoint), NUNCA exc_info/logger.exception/locals; el spec de defensa de U2 debe aseverar ausencia de credenciales en la representación logueada. U1 solo garantiza la superficie del objeto por construcción.
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
