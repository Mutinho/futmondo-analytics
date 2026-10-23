# Feasibility Assessment — F3 Mercado (app nativa iOS)

## Sources

- `.../ideation/intent-capture/intent-statement.md` — alcance: lectura +
  escritura (pujar/cancelar) + detalle Sofascore, 2ª pestaña del `TabView`.
- `.../ideation/market-research/build-vs-buy.md` — decisión **Build** con SDK de
  Apple, reutilizando `FutmondoKit`/`DesignSystem`, coste 0 €.
- `.../ideation/market-research/competitive-analysis.md`,
  `.../market-trends.md` — F3 complementa Futmondo; nativo iOS, Liquid Glass.
- Código: `angular-app/src/app/features/market/` (fuente de verdad del
  comportamiento); `README.md` (endpoints); base `ios/` de F1/F2.

## Veredicto de viabilidad

**Viable** con alta confianza. F3 reproduce una pantalla ya existente consumiendo
endpoints ya en producción; la base nativa (`FutmondoKit` + `DesignSystem` +
`RootTabView`) de F1/F2 reduce el trabajo a: (1) modelo + servicio de Mercado en
`FutmondoKit` (lectura y escritura), (2) UI SwiftUI en `FutmondoApp` (banner,
cards, orden, puja/cancelar, sheet Sofascore) y (3) una segunda pestaña en el
`TabView`.

## Elementos técnicos conocidos (confirmados en código)

- **Lectura**: `GET /api/v1/market/today?championship_id=` → `{ players: [...],
  user_info }`. `MarketPlayer` con ~28 campos; `user_info` con balance,
  team_value, max_bid, active_bids_total, available_for_bids.
- **Escritura puja**: `POST /api/v1/market/bid` (query: championship_id,
  player_id, player_slug, price, is_clause=false) → `{success, message}`.
- **Escritura cancelar**: `POST /api/v1/market/cancelbid` (query:
  championship_id, bid_id) → `{success, message}`. Requiere `current_bid_id`.
- **Detalle Sofascore**: endpoint aparte (no en `/today`); carga asíncrona
  independiente, estados loading/error.
- **Reutilizable**: `NetworkClient` (HTTPS + Bearer), `AuthService` (sesión +
  Keychain), `ActiveChampionshipStore` (championship_id activo),
  `MoneyFormatter`, y el `DesignSystem` oscuro/neón.

## Esfuerzo / complejidad (cualitativo)

- **Baja-media**. Lo nuevo frente a F2 es la **escritura** (dos POST con efecto
  real) y el **segundo endpoint** (Sofascore). El patrón de datos+UI+orden ya
  está probado en F2.

## Riesgos de viabilidad (detallados en raid-log)

- Hueco WSL: errores arm-only que sólo afloran en build de dispositivo con
  `xtool` (Equatable, strict concurrency Swift 6, APIs UIKit/SwiftUI, colisión
  `FutmondoKit.Transaction` vs `SwiftUI.Transaction`).
- Escritura con efecto económico real: necesita validación de importe y señal de
  resultado inequívoca; no debe dejar estado ambiguo.

## Assumptions & Open Questions

None.
