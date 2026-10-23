# Code Summary — u1-market (pantalla de Mercado)

## Ficheros creados / modificados

### `FutmondoKit` (lógica testeable)
- `ios/Sources/FutmondoKit/Market/MarketPlayer.swift` — modelo de jugador (Codable/Equatable/Sendable).
- `ios/Sources/FutmondoKit/Market/MarketTodayResponse.swift` — `MarketUserInfo` (+ `balanceMinusBids`) y `MarketTodayResponse`.
- `ios/Sources/FutmondoKit/Market/MarketWriteOutcome.swift` — enum tipado `.accepted/.rejected/.networkError` + `MarketWriteResponse` y `from(...)` (mapeo W6).
- `ios/Sources/FutmondoKit/Market/SofascoreDetail.swift` — DTO del detalle + `SofascoreDetailOutcome`.
- `ios/Sources/FutmondoKit/Market/MarketSortField.swift` — enum de los 7 campos de orden.
- `ios/Sources/FutmondoKit/Market/MarketSorter.swift` — orden desc, nulos al final, estable, default `value`.
- `ios/Sources/FutmondoKit/Market/BidAmountValidator.swift` — `.valid/.tooLow/.tooHigh/.nonPositive`.
- `ios/Sources/FutmondoKit/Market/MarketService.swift` — actor `loadToday/placeBid/cancelBid` (contratos de query exactos).
- `ios/Sources/FutmondoKit/Market/SofascoreService.swift` — actor dedicado; `404 → .empty`; aislado.

### `FutmondoApp` (vistas SwiftUI, `#if canImport(SwiftUI)`)
- `ios/Sources/FutmondoApp/Market/MarketViewModel.swift` — `@MainActor`; `isWriting` global; recarga sólo en `.accepted`.
- `ios/Sources/FutmondoApp/Market/MarketView.swift` — banner + barra de orden + lista + estados + sheets/alert.
- `ios/Sources/FutmondoApp/Market/MarketBanner.swift` — 5 tiles con color de dinero por signo/umbral + etiquetas.
- `ios/Sources/FutmondoApp/Market/MarketPlayerCard.swift` — PUJAR / "Puja activa"+cancelar; tendencia flecha+signo.
- `ios/Sources/FutmondoApp/Market/BidSheet.swift` — default = `suggested_bid`, validación inline.
- `ios/Sources/FutmondoApp/Market/SofascoreDetailSheet.swift` — `SofascoreDetailViewModel`, estado local aislado.
- `ios/Sources/FutmondoApp/Budget/RootTabView.swift` — **modificado**: añade la 2ª pestaña "Mercado" (Presupuesto intacta).
- `ios/Sources/FutmondoApp/SplashView.swift` — **modificado**: cablea `MarketViewModel` + servicio Sofascore sobre el mismo cliente HTTPS y store activo.

### Tests (`ios/Tests/FutmondoKitTests/`, 40 nuevos)
- `MarketDTOTests.swift` (8), `MarketSorterTests.swift` (8), `BidAmountValidatorTests.swift` (8), `MarketWriteOutcomeTests.swift` (8), `MarketServiceTests.swift` (MarketService 8 + SofascoreService 8, con `FakeMarketNetworkClient` in-memory).

## Decisiones clave de implementación

- **Partición F1/F2**: lógica + DTOs + los dos actores de servicio en `FutmondoKit`
  (ejecutables con `swift test`); vistas SwiftUI + view models `@MainActor` en
  `FutmondoApp` bajo `#if canImport(SwiftUI)` (validación en dispositivo).
- **W6 centralizado** en `MarketWriteOutcome.from`: 2xx-true→`.accepted`;
  2xx-false o 4xx→`.rejected(message)`; 5xx/transport/cancelled/decoding→
  `.networkError`. Avisos en castellano inyectados desde el VM (sin fugas de
  inglés ni de credenciales).
- **Contratos de query** aseverados por tests: `bid` lleva `is_clause=false`;
  `cancelbid` lleva `championship_id`/`bid_id`; `today`/`sofascore` llevan
  `championship_id`. El `NetworkError` tipado nunca refleja la URL (sin fuga de
  id/token, aseverado).
- **BR-UI-2**: tope de puja = `available_for_bids` (no `max_bid`), con test dedicado.
- **FR8.2**: `SofascoreService` + `SofascoreDetailViewModel` separados; VM fresco
  por sheet; `404 → .empty`; un fallo nunca toca `MarketViewModel`.
- Reutiliza componentes/tokens del `DesignSystem`; identificadores de
  accesibilidad + etiquetas VoiceOver; significado no sólo por color.

## Cobertura de tests

- `swift test --package-path ios`: **153/153 verde** (40 nuevos de Mercado).
  Verificado por el orquestador.
- Piso feature 80% línea medido sobre la lógica de `FutmondoKit`; el número de
  `llvm-cov` no es fiable en WSL (aprendizaje durable) — se documenta, **no se
  relaja ni se desactiva** ningún umbral. Las vistas SwiftUI quedan fuera del
  cómputo (validación en dispositivo).

## Desviaciones del plan

- **Step 12 (validación en dispositivo `xtool dev build`, iPhone 13 Pro)**: NO
  completado en este entorno. `xtool dev build` falla al compilar contra el iOS
  SDK 27.1 instalado por desajuste compilador/SDK (SDK built con Swift 6.4;
  compilador local Swift 6.0.3 — "this SDK is not supported by the compiler").
  Es un problema **preexistente de entorno/toolchain**, ajeno al código de
  `u1-market`; las vistas SwiftUI quedan validadas sólo en dispositivo, conforme
  al aprendizaje durable de WSL. Step 12 queda **sin marcar** por honestidad. No
  se falseó ningún pase de test.
- Steps 1–11 y 13 marcados; `source-manifest.json` escrito con todas las rutas.

## Assumptions & Open Questions

None.
