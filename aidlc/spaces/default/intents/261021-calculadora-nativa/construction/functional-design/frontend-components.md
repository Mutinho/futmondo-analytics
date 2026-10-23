# Frontend Components — Calculadora nativa iOS (SwiftUI)

Jerarquía de componentes SwiftUI y puntos de integración. Reutiliza el design
system y la estética de tiles de la pantalla de Mercado (NFR4, FR5.1).

## Capas (dónde vive cada cosa)

- **FutmondoKit (lógica pura, XCTest)**:
  - `RosterPlayer`, `OnSalePlayer` (DTO Codable, snake_case → camelCase).
  - `MarketUserInfo` extendido con `activeBidsCount` (campo nuevo **opcional con
    default 0**: `decodeIfPresent ?? 0` + parámetro de init por defecto, para no
    romper el decode de Mercado ni los callers — R-02).
  - `RosterService` (protocolo) + `HTTPRosterService` (actor sobre `NetworkClient`):
    `fetchRoster`, `fetchOnSale`, `sell`, `cancelSale`. `sell` devuelve el tipo
    dedicado `SellOutcome` (total/partial/none/networkError, R-01); `cancelSale`
    reutiliza `MarketWriteOutcome`.
  - `SellOutcome` (enum): `total(sold)`, `partial(sold,total)`, `none(total)`,
    `networkError(message)` — transporta `sold`/`total` del backend `/roster/sell`.
  - `CalculatorMath` (struct de funciones puras): `projectedValue(player,days)`,
    `selectedTotal(players,selectedIds,days)`, `onSaleTotal(onSale)`,
    `futureBalance(balance,selectedTotal,onSaleTotal,includeOnSale,activeBidsTotal)`.
  - `CalculatorSorter` (orden por projectedValue/value/change/profit).
  - `CalculatorPreferences` (lectura/escritura `UserDefaults`, con el default
    ON de BR5.1).
  - Reutiliza `DataFreshness`, `MarketWriteOutcome`, `MarketImageURL`.
- **FutmondoApp (vistas SwiftUI, `#if canImport(SwiftUI)`, validadas en dispositivo)**:
  - `CalculatorView`, `CalculatorViewModel`, `CalculatorHeader`,
    `OnSaleSection`, `CalculatorPlayerCard`, `SellConfirmation` (reutiliza
    confirmación nativa), `SellFloatingButton`.

## Jerarquía de componentes (vista)

```
CalculatorView
├── CalculatorHeader            // Saldo actual, En venta, Pujas activas(N), Seleccionadas, Saldo futuro
│   └── (toggle "Incorporar jugadores en venta")
├── DatePicker (Fecha de venta) + etiqueta "Hoy / N días a futuro"
├── Menu (orden)                // projectedValue/value/change/profit — patrón Mercado
├── OnSaleSection               // visible si includeOnSale && !onSale.isEmpty (BR6.1)
│   └── OnSaleRow[]  (cancelar venta con confirmación)
├── LazyVGrid de CalculatorPlayerCard[]   // 2-up, estética tiles de Mercado
└── SellFloatingButton          // overlay, visible si selectedCount>0 (BR8.1)
```

## Estado (CalculatorViewModel, @MainActor, ObservableObject)

- `players: [RosterPlayer]` (lista seleccionable recompuesta), `rawRoster`,
  `onSalePlayers: [OnSalePlayer]`, `onSaleIds: Set<String>`.
- `economy: EconomySnapshot?` (balance, activeBidsTotal, activeBidsCount).
- `selectedIds: Set<String>`, `includeOnSale: Bool`, `daysAhead: Int`,
  `sortField`.
- `phase: Loading | Loaded | Error(message) | Selling | Cancelling`.
- `sellResult: (success, message)?`.
- Derivados (vía `CalculatorMath`): `selectedTotal`, `onSaleTotal`,
  `futureBalance`, `projectedValue(for:)`.
- `freshness: DataFreshness` + `loadIfNeeded()` + `invalidate()`.
- `onWriteAccepted: () -> Void` (cross-invalidación de Presupuesto/Mercado, BR10.1).

## Flujos de interacción (resumen; detalle en functional-spec.md)

- Tap card → `toggle(playerId)` → recálculo (W2).
- Toggle en venta → persistir + filtrar selección en venta + recomponer (W4/BR4.2).
- Fecha → `daysAhead` → recálculo (W3).
- "Vender (N)" → confirmación → `sell` → resultado total/parcial/error (W5/BR8.2).
- Cancelar → confirmación → `cancelSale` → recarga (W6).

## Validación / reglas de UI

- El botón "Vender (N)" solo actúa con `selectedCount > 0` (BR8.1).
- `DatePicker` acotado a `>= hoy` (FR4.1).
- Cifras con semántica money (positivo/negativo), plusvalía con signo (BR7.1).
- Accesibilidad: selección por icono+estado, no solo color; Reduce Motion (NFR6).

## Integración con servicios (sin cambio de backend, C1)

| Acción | Llamada | Notas |
|---|---|---|
| Cargar plantilla | `RosterService.fetchRoster(championshipId)` | NUEVO cliente |
| Bloque económico | `MarketService.loadToday(championshipId)` | reutilizado; +activeBidsCount |
| En venta | `RosterService.fetchOnSale(championshipId)` | NUEVO |
| Poner a la venta | `RosterService.sell(championshipId, ids)` | NUEVO; devuelve `SellOutcome` total/partial/none/networkError |
| Cancelar venta | `RosterService.cancelSale(championshipId, playerId)` | NUEVO; devuelve `MarketWriteOutcome` |

## Navegación

- 3.ª pestaña del `RootTabView` (FR11.1), tinte verde neón, accesibilidad por
  icono + etiqueta.
