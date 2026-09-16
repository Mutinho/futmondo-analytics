<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
- 2026-09-15T17:02:00Z — FR5.2 resuelto a favor de NO persistir la contraseña (re-auth via handle) en vez de cifrado en reposo: hace NFR1.1 cierto por construccion y evita gestionar/rotar una clave (coste 0€), a cambio de que un refresh token caducado degrade a 401 accionable (FR1.3, ya disenado) en vez de re-auth transparente. Concurrencia con lock BD (FOR UPDATE) en vez de lock en memoria para tolerar multi-instancia (NFR5.2) sin rediseno futuro.
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
