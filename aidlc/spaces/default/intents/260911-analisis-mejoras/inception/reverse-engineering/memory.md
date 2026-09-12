<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-11T13:00:00Z — Escaneo FULL (NO_STORE) del repo único (workspace root, sin repos registrados). Los "god files" de backend/app/services (data_manager_v2.py 166KB, data_sync_service.py 84KB) se registraron como shallow.paths: conocidos por interfaz/llamadas pero no leídos línea a línea; suficiente para el análisis de arquitectura y para levantar el hallazgo de intestabilidad, pero un intent futuro que los refactorice necesitará escaneo focalizado.
- 2026-09-11T13:00:00Z — Hallazgos concretos con evidencia preservados en el codekb para alimentar requirements-analysis/domain-design/nfr-requirements: sync async in-memory sin persistencia, borrado no transaccional de sofascore_cache, credenciales Futmondo en claro en SessionStore, SSL_VERIFY=0 local, price sin validar en /market/bid, posible bug en is_refresh_token_valid, asimetría de tests frontend (~0) vs backend, linters advisory.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
