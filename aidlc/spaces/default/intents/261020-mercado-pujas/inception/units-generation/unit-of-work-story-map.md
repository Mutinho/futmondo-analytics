# Unit of Work — Story Map — F3 Mercado

> Mapeo de cada historia de usuario (US1–US7) a la unidad que la implementa.
> Como existe `stories.md`, las filas se keyean por `USx.y` (una fila por
> historia). Todas las historias caen en la única unidad `u1-market`.

## Sources

- `.../inception/user-stories/stories.md` (US1–US7).
- `.../inception/units-generation/unit-of-work.md` (U1 / u1-market).
- `.../inception/domain-design/components.md` (componentes por historia).

## Mapa

| Historia (US) | Unit ID | Directory | Componentes implicados | Orden intra-unidad |
|---|---|---|---|---|
| US1 — Abrir el Mercado | U1 | u1-market | RootTabView, MarketView, MarketViewModel, MarketService, MarketTodayResponse | 2 (vistas) tras 1 (servicio/DTO) |
| US2 — Ver situación económica (banner) | U1 | u1-market | MarketUserInfo, MarketView | 2 |
| US3 — Explorar jugadores en cards | U1 | u1-market | MarketPlayer, MarketView, MarketPlayerCard | 2 (card) tras 1 (modelo) |
| US4 — Ordenar la lista | U1 | u1-market | MarketSorter, MarketView, MarketViewModel | 1 (sorter puro) → 2 (UI) |
| US5 — Pujar por un jugador | U1 | u1-market | BidAmountValidator, MarketWriteOutcome, MarketService, MarketViewModel, MarketPlayerCard, BidSheet | 1 (validador/outcome/servicio) → 2 (sheet) |
| US6 — Cancelar mi puja | U1 | u1-market | MarketWriteOutcome, MarketService, MarketViewModel, MarketPlayerCard, CancelBidConfirmation | 1 (servicio/outcome) → 2 (confirmación) |
| US7 — Consultar detalle Sofascore | U1 | u1-market | SofascoreDetail, SofascoreService, SofascoreDetailSheet | 1 (servicio/DTO) → 2 (sheet) |

## Concerns transversales (span multi-unidad)

Ninguno: todas las historias caen en `u1-market` (una sola unidad). Dentro de la
unidad, el patrón transversal es el orden **test-after**: la lógica pura y los
servicios de `FutmondoKit` (orden 1, con XCTest) antes que las vistas SwiftUI de
`FutmondoApp` (orden 2, validadas en dispositivo).

## Verificación de cobertura

- **Toda historia asignada**: US1–US7 → `u1-market` (7/7). Sin GAP.
- **Toda unidad con filas**: `u1-market` tiene 7 filas.

## Assumptions & Open Questions

None.
