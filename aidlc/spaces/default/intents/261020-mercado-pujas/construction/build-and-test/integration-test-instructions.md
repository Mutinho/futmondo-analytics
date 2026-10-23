# Integration Test Instructions — F3 Mercado (u1-market)

> Standard strategy → se generan instrucciones de integración para las fronteras
> clave de `u1-market`. La única Unit del intent es `u1-market`, así que no hay
> interacción cross-unit nueva dentro de F3; las fronteras de integración son
> **u1-market ↔ capa F1/F2 reutilizada** y **u1-market ↔ contratos backend**.

## Marco y configuración

- XCTest sobre `FutmondoKit` (`swift test --package-path ios`), con el doble
  in-memory `FakeMarketNetworkClient` inyectado en los servicios. Sin red, sin
  credenciales reales.

## Fronteras de integración y cómo testearlas

| Frontera | Qué se verifica | Dónde |
|---|---|---|
| `MarketService` ↔ `NetworkClient` (F1) | `APIRequest` resultante: método, path, query params exactos (`championship_id`, `player_id`, `player_slug`, `price`, `is_clause=false`, `bid_id`), header `Bearer`; mapeo de status a `MarketWriteOutcome` | `MarketServiceTests` |
| `SofascoreService` ↔ `NetworkClient` (F1) | path `/sofascore/player/{name}` + `championship_id`; `404 → .empty`; aislamiento (fallo no muta estado de Mercado) | `MarketServiceTests` (sección Sofascore) |
| `MarketViewModel` ↔ servicios | orquestación: carga sustituye lista+banner; `isWriting` global; recarga sólo en `.accepted` | validado vía los tipos puros (`MarketSorter`, `MarketWriteOutcome.from`) + dispositivo |
| `RootTabView` ↔ `MarketView` | la 2ª pestaña monta Mercado sin romper Presupuesto (F2) | validación en dispositivo |

## Cómo correr

```
swift test --package-path ios
```

Filtros útiles durante desarrollo:

```
swift test --package-path ios --filter MarketService
swift test --package-path ios --filter Market
```

## Objetivos de cobertura

- Las fronteras de red de `FutmondoKit` se cubren con los dobles in-memory
  (incluidas en los 40 tests nuevos). Las fronteras de UI (`RootTabView` ↔
  `MarketView`) se validan en dispositivo (fuera del cómputo de cobertura, WSL).

## Gestión de datos de test

- Fixtures JSON sintéticos de `/market/today`, `/market/bid`, `/market/cancelbid`,
  `/sofascore/player/{name}`. Sin tokens ni datos reales (gitleaks escanea tests).

## Assumptions & Open Questions

None.
