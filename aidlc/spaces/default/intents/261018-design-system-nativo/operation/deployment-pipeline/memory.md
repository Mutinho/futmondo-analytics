<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T12:28Z — Deployment Pipeline (adaptado al stack real, no AWS): la capa de diseño va embebida en la app iOS; no despliega a servidor. CD del repo (fly-deploy.yml) no modificado; entrega a dispositivo con `xtool dev build` (firma gratuita). Rollback = `git revert` del squash-commit + reinstalar; backend/frontend producción no tocados. Pipeline CD cloud/blue-green/canary NO-APLICA.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
