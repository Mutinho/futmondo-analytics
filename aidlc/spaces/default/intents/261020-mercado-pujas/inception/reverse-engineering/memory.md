<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-20 — Refresco INCREMENTAL de la CodeKB del proyecto (ya existía de F2, mismo commit f791f06). Delegado a developer-agent (pipeline). Preservada la prosa de los 9 artefactos; extendidos sólo 3: component-inventory (componentes de market + MarketPlayer/user_info/SofascoreStats), api-documentation (endpoints de Mercado) y timestamp (run 2026-10-20, kind partial, fingerprint 91bea54f4c5fef127edfff7c22d82934d8951bb1, VALID).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-20 — CORRECCIÓN de contrato aportada por el backend (market.py): (1) el detalle Sofascore NO es /market/*, sino GET /api/v1/sofascore/player/{player_name}?championship_id= (router sofascore_detail.py); (2) /market/bid valida price>0 y price<=5_000_000_000 (422 si no); (3) user_info.max_bid = balance + team_value*0.5, available_for_bids = max_bid − active_bids_total; (4) players[] del backend trae más campos que el MarketPlayer del frontend (el frontend consume un subconjunto). Estos contratos los usará U1 (datos) en Construcción.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
