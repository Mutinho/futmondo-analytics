# Domain Design — Resumen (F3 Mercado)

## Consolidated Summary Confirmation

Resumen de Domain Design para F3 = Mercado:

- **FutmondoKit (lógica, testeable)**: C1 `MarketPlayer` (Equatable/Sendable), C2
  `MarketUserInfo`, C3 `MarketTodayResponse`, C4 `MarketWriteOutcome` (enum
  aceptada/rechazada/error), C5 `MarketService` (actor: loadToday/placeBid/
  cancelBid + detalle Sofascore), C6 `MarketSorter` (puro), C7 `BidAmountValidator`
  (puro), C8 `SofascoreDetail`.
- **FutmondoApp (UI, validada en dispositivo)**: V1 `MarketView`, V2
  `MarketViewModel`, V3 `MarketPlayerCard`, V4 `BidSheet`, V5
  `CancelBidConfirmation`, V6 `SofascoreDetailSheet`, V7 `RootTabView` (2ª pestaña).
- **ADRs**: (1) partición datos/UI por el hueco WSL; (2) resultado de escritura
  tipado (no bool/nil silencioso); (3) tope de importe = available_for_bids; (4)
  sin dependencias nuevas (coste 0 €).
- **Trazabilidad** FR1–FR8 cubierta (traceability.json).
- **Reviewer advisory** (architecture-reviewer) sobre `components`: pendiente
  (ahora).
- **Siguiente etapa**: Units Generation.

¿Todo correcto?

- **Looks correct** — confirmo y avanzamos.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
