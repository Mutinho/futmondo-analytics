# Developer Scan — Reverse Engineering (F3 Mercado, repo futmondo-analytics)

**Collaborator:** aidlc-developer-agent

## Alcance de la contribución

Refresco **incremental** de la CodeKB del proyecto
(`aidlc/spaces/default/codekb/futmondo-analytics/`) para incorporar la vista de
**Mercado** del frontend Angular, fuente de verdad del comportamiento de F3. La
CodeKB ya existía de F2 (commit `f791f06d14f41ec44884ab55314c6daaf4b9dae1`, el
mismo que el actual): se **preservó** la prosa de los 9 artefactos y se
**extendieron** 3.

## Artefactos actualizados

- **component-inventory.md** — sección de los componentes de `market`
  (MarketComponent, BidDialogComponent, ConfirmDialogComponent,
  SofascoreDetailDialogComponent) + modelo MarketPlayer (~28 campos), user_info,
  SofascoreStats.
- **api-documentation.md** — endpoints de Mercado con params y shapes reales.
- **reverse-engineering-timestamp.md** — run 2026-10-20, `kind: partial`,
  fingerprint `91bea54f4c5fef127edfff7c22d82934d8951bb1` (validado con
  `codekb-scope-diff --check` → VALID).

No se tocaron business-overview, architecture, code-structure, technology-stack,
dependencies ni code-quality-assessment.

## Contrato real confirmado contra el backend (`market.py`, `sofascore_detail.py`)

- `GET /api/v1/market/today?championship_id=` → `{success, …, players[],
  user_info}`. `user_info.max_bid = balance + team_value*0.5`,
  `available_for_bids = max_bid − active_bids_total`. `players[]` del backend trae
  más campos que el `MarketPlayer` del frontend (que consume un subconjunto).
- `POST /api/v1/market/bid` — params en **query** (body `{}`): championship_id,
  player_id, player_slug, price (int), is_clause (bool, default false). Valida
  `price>0` y `price<=5_000_000_000` → 422 si no. Proxya a Futmondo.
- `POST /api/v1/market/cancelbid` — query: championship_id, bid_id.
- **Corrección**: el detalle Sofascore es
  `GET /api/v1/sofascore/player/{player_name}?championship_id=` (router
  `sofascore_detail.py`), **no** `/market/*`. `starter_pct =
  round(matches_started/38*100)`; 404 si no hay fila.

## Sources

- `angular-app/src/app/features/market/` (market.component.ts/html,
  bid-dialog, confirm-dialog, sofascore-detail-dialog).
- `backend/app/api/v1/endpoints/market.py` y `sofascore_detail.py`.
- CodeKB previa de F2 en `aidlc/spaces/default/codekb/futmondo-analytics/`.

## Assumptions & Open Questions

None.
