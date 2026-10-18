<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-16T17:22:00Z — El spike se enmarca como end-to-end de toolchain (Q1=A, Q2=D): el DONE es la app mínima arrancando en el iPhone 13 Pro físico vía `xtool` desde WSL con firma gratuita. Deliberadamente SIN red/pantallas/auth (Q6=A) para aislar el diagnóstico de la cadena build+firma+install del resto de proto-Units (B-02+).
- 2026-10-16T17:22:00Z — Entregables ampliados a runbook reproducible además de app desechable + nota de hallazgos (Q4=B, Q5=C): el montaje del toolchain (Swift 6.4 + usbmuxd + USB passthrough) se instala y documenta dentro del spike porque hoy no está validado en vivo (Q3=C).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
