<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-16T17:55:00Z — Inspección directa del WSL (es donde corre esta sesión): Ubuntu 26.04 LTS, kernel 6.18.x-microsoft-standard-WSL2, Swift y usbip NO instalados. El spike monta el toolchain desde cero.
- 2026-10-16T17:55:00Z — Entregables ubicados: código Swift en `spikes/ios-xtool/`, hallazgos+runbook en `docs/spikes/ios-xtool.md` (Q4=A). Verificación = evidencia manual + receta de smoke repetible (Q3=B).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-16T17:55:00Z — Swift.org publica binarios oficiales para Ubuntu 22.04/24.04; en 26.04 (muy reciente) puede no haber build nativo. Hipótesis a validar en el montaje: usar `swiftly` o el toolchain etiquetado 24.04 por compatibilidad glibc. No bloquea el GO pero es el primer bloqueo probable.
