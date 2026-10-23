# Unit Test Instructions — Calculadora nativa iOS

## Framework y setup

- **Framework**: XCTest (SDK de Apple, coste 0 €), target `FutmondoKitTests`
  del paquete SwiftPM en `ios/`.
- Runner ya existente; no requiere bootstrap. Metodología **test-after**: se
  implementa cada capa testeable y después se escriben/corren sus tests.

## Comando (unit-scoped)

La lógica testeable de esta unidad vive en `FutmondoKit`. Comando exacto para
los tests nuevos de la Calculadora (filtro por los casos de esta unidad):

```bash
swift test --package-path ios --filter "CalculatorMathTests|CalculatorSorterTests|CalculatorPreferencesTests|RosterPlayerTests"
```

Para la suite completa (verificar que sigue verde, sin bajar nada):

```bash
swift test --package-path ios 2>&1 | grep -E "Executed [0-9]+ tests"
```

Build:

```bash
swift build --package-path ios
```

## Qué se testea (test-after)

- **`CalculatorMath`** (invariantes FR7): `projectedValue` (incl. `change` nil =
  0), `selectedTotal`, `onSaleTotal`, `futureBalance` con toggle ON y OFF, y que
  `activeBidsTotal` se resta SIEMPRE; caso anti-doble-conteo (un jugador en
  venta no cuenta dos veces).
- **`CalculatorSorter`**: orden descendente por projectedValue/value/change/profit;
  nils al final.
- **`CalculatorPreferences`**: default toggle ON (cualquier valor != 'false' →
  ON), round-trip de orden.
- **DTOs**: decode de `RosterPlayer`/`OnSalePlayer`; `MarketUserInfo` con
  `active_bids_count` **ausente** (→ 0) y **presente** (regresión de R-02).

## Cobertura / mocking

- Objetivo: happy path + ≥2 casos de borde por componente de lógica (toggle
  ON/OFF, proyección con días > 0). ~12-16 tests.
- Sin red: `RosterService` se prueba (si procede) con un doble en memoria de
  `NetworkClient` (patrón ya usado en los tests de Market). `CalculatorMath`,
  `CalculatorSorter` y `CalculatorPreferences` son puros / con `UserDefaults`
  inyectable; no requieren red.
- Las vistas SwiftUI NO se testean con XCTest aquí (llvm-cov no fiable en WSL);
  se validan en dispositivo con `ios/scripts/install-app.sh`.

## Datos de prueba

- Fixtures en memoria (structs `RosterPlayer`/`OnSalePlayer` construidos en el
  test); JSON embebido para los tests de decode. Sin credenciales ni red reales.
