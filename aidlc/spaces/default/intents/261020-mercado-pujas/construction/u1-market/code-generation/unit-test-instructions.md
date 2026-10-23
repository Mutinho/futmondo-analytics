# Unit Test Instructions — u1-market

## Runner

- **Framework**: XCTest sobre el target library `FutmondoKit` (SwiftPM).
- **Comando exacto (scoped a la Unit por los ficheros `Market*Tests`)**:

  ```bash
  swift test --package-path ios
  ```

  Para correr sólo los specs de esta Unit:

  ```bash
  swift test --package-path ios --filter 'MarketDTOTests|MarketSorterTests|BidAmountValidatorTests|MarketWriteOutcomeTests|MarketServiceTests|SofascoreServiceTests'
  ```

- **Entorno verificado**: Swift 6.0.3 (x86_64-unknown-linux-gnu). El runner ya
  existía (F1/F2) y corre en este entorno.

## Testable layers (FutmondoKit, cubiertas por `swift test`)

| Componente | Suite | Tests |
|---|---|---|
| DTOs (`MarketPlayer`/`MarketUserInfo`/`MarketTodayResponse`/`SofascoreDetail`/`MarketWriteResponse`) + `balanceMinusBids` | `MarketDTOTests` | 8 |
| `MarketSorter` (7 campos, nulos al final, estable, default `value`) | `MarketSorterTests` | 8 |
| `BidAmountValidator` (`[market_price, available_for_bids]`, `>0`, BR-UI-2) | `BidAmountValidatorTests` | 8 |
| Mapeo `MarketWriteOutcome` (2xx-true/2xx-false/4xx/5xx/transport) | `MarketWriteOutcomeTests` | 8 |
| `HTTPMarketService` (loadToday OK/empty/error + bid/cancel con query exacta) | `MarketServiceTests` | 8 |
| `HTTPSofascoreService` (loaded/empty-404/failed + aislamiento) | `SofascoreServiceTests` | 8 |

Dobles in-memory de `NetworkClient` (`FakeMarketNetworkClient`), sin red, sin
credenciales/tokens reales.

## SwiftUI (fuera del cómputo de cobertura, WSL)

Las vistas SwiftUI (`MarketView`, `MarketBanner`, `MarketPlayerCard`,
`BidSheet`, `SofascoreDetailSheet`, `MarketViewModel`, `SofascoreDetailViewModel`,
integración en `RootTabView`/`SplashView`) van en `FutmondoApp`, guardadas por
`#if canImport(SwiftUI)`, y se validan en dispositivo (iPhone 13 Pro) vía
`xtool dev build`.

**Cobertura (piso feature 80 % línea)**: se mide sobre la lógica testeable de
`FutmondoKit` vía `swift test`. La medición numérica de cobertura por llvm-cov
NO es fiable con el toolchain de Swift en Linux/WSL (aprendizaje durable del
proyecto), así que el piso no se verifica numéricamente aquí; la obligación se
cumple colocando toda la lógica testeable en `FutmondoKit` con 5–8 tests por
componente y manteniendo verde la suite. Nunca se baja ni desactiva un umbral.

**Nota de entorno (SDK)**: en este entorno `xtool dev build` falla al compilar
contra el SDK de iOS 27.1 por un desajuste de versión del compilador (SDK
construido con Swift 6.4; compilador local Swift 6.0.3), ajeno al código de esta
Unit. La validación de las vistas SwiftUI queda, por tanto, para el dispositivo.
