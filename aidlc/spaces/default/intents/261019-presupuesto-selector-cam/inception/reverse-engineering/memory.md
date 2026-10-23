<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T15:10Z — Reverse Engineering: refresco INCREMENTAL del codekb existente (no reconstrucción), enfocado en la capa iOS de F1 y las áreas Budget/championship. Hallazgos clave para F2: endpoints `GET /api/v1/analytics/balances?championship_id=` (+`/{team_id}`), `/user/championships` (con fallback a `/championships`); `performance = teamValue + balance - initial_budget`; fallback `INITIAL_BUDGET = 200_000_000`; championships trae más campos de los modelados (`money_per_point`, `money_per_ranking`, `dream_team_bonus`, `mvp_bonus`, `ranking_mode`, `users_to_rank`); auth usa header `X-Refresh-Token`; `ChampionshipService` persiste en `localStorage` (`futmondo_active_championship`) → el selector nativo debe reproducir el patrón con su propio almacén local. `FutmondoKit` sin deps externas, testTarget sólo depende de `FutmondoKit` (compila en WSL sin SwiftUI).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
