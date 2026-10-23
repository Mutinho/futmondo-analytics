# Reverse Engineering — Resumen (F3 Mercado)

> Etapa en modo pipeline (developer-agent). Refresco incremental de la CodeKB del
> proyecto para incorporar la vista de Mercado, fuente de verdad de F3.

## Consolidated Summary Confirmation

Resumen de Reverse Engineering para F3 = Mercado:

- **Refresco incremental** de `aidlc/spaces/default/codekb/futmondo-analytics/`
  (la CodeKB ya existía de F2; mismo commit `f791f06`). Preservada la prosa de
  los 9 artefactos; extendidos 3:
  - **component-inventory.md**: componentes de `market` (MarketComponent,
    BidDialogComponent, ConfirmDialogComponent, SofascoreDetailDialogComponent) y
    modelo MarketPlayer / user_info / SofascoreStats.
  - **api-documentation.md**: endpoints de Mercado con params y shapes reales.
  - **reverse-engineering-timestamp.md**: run 2026-10-20, `kind: partial`,
    fingerprint `91bea54f4c5fef127edfff7c22d82934d8951bb1` (VALID).
- **Contrato real confirmado contra el backend** (`market.py`):
  - `GET /api/v1/market/today?championship_id=` → `{success, …, players[],
    user_info}`; `user_info.max_bid = balance + team_value*0.5`,
    `available_for_bids = max_bid − active_bids_total`.
  - `POST /api/v1/market/bid` (params en query; valida `price>0` y
    `price<=5_000_000_000`, 422 si no).
  - `POST /api/v1/market/cancelbid` (query: championship_id, bid_id).
  - **Corrección clave**: el detalle Sofascore es
    `GET /api/v1/sofascore/player/{player_name}?championship_id=`
    (router `sofascore_detail.py`), **no** `/market/*`.
- **Siguiente etapa**: Practices Discovery.

¿Todo correcto?

- **Looks correct** — confirmo y avanzamos.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
