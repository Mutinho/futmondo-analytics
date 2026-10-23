# Unit of Work — F3 Mercado

> Decomposición de los componentes de Domain Design en unidades de trabajo
> implementables. F3 es una feature de UI nativa iOS (SwiftUI) que reproduce la
> vista Angular de Mercado como 2ª pestaña del `RootTabView` tras Presupuesto
> (F2), sin cambios de backend. Topología solamente: la secuencia económica
> (Bolts) la decide Delivery Planning (2.9).

## Sources

- `.../inception/domain-design/components.md` (catálogo `yaml`, C1–C8 + V1–V7).
- `.../inception/domain-design/decisions.md` (ADR-1…ADR-6).
- `.../inception/requirements-analysis/requirements.md` (FR1–FR8, NFR1–NFR6).
- `.../inception/user-stories/stories.md` (US1–US7).

## Unidades

| Unit ID | Directory | Nombre | Kind | Complejidad |
|---|---|---|---|---|
| U1 | u1-market | Mercado (pantalla nativa de puja/cancelación + detalle Sofascore) | ui | M |

### U1 — `u1-market` (kind: `ui`)

- **Descripción**: la pantalla de Mercado nativa completa como 2ª pestaña del
  `RootTabView`: carga de `/market/today`, banner económico, lista de cards con
  orden, puja y cancelación (escritura) y sheet de detalle Sofascore.
- **Fronteras**: amplía el paquete SwiftPM `ios/` existente. Contiene **toda** la
  lógica de Mercado en `FutmondoKit` y **todas** las vistas en `FutmondoApp`; no
  toca backend, datos ni CI/CD.
- **Responsabilidades (qué posee y entrega)**:
  - Lógica/datos (`FutmondoKit`): C1 `MarketPlayer`, C2 `MarketUserInfo`,
    C3 `MarketTodayResponse`, C4 `MarketWriteOutcome`, C5 `MarketService`,
    C6 `MarketSorter`, C7 `BidAmountValidator`, C8 `SofascoreDetail` +
    `SofascoreService`.
  - UI (`FutmondoApp`, `#if canImport(SwiftUI)`): V1 `MarketView`,
    V2 `MarketViewModel`, V3 `MarketPlayerCard`, V4 `BidSheet`,
    V5 `CancelBidConfirmation`, V6 `SofascoreDetailSheet`, V7 `RootTabView`
    (modificación mínima: añade la 2ª pestaña).
- **Modelo de despliegue**: **embedded** — sin despliegue nuevo. No se publica la
  app en este intent; no toca la topología Fly.io ni el gate de CI. El entregable
  es código nativo que se funde a `main` como un único PR squash-merge.
- **Reutilización (no son unidades nuevas; son estado del repo de F1/F2)**:
  `NetworkClient` y `AuthService`/sesión autenticada (Bearer) de F1, el
  `DesignSystem` (tokens, `Card`, `PrimaryButton`, `TextInputField`,
  estados loading/error) de F1/F2, y el `RootTabView` existente.
- **Contratos backend consumidos (sin cambios de servidor)**:
  `GET /api/v1/market/today`, `POST /api/v1/market/bid`,
  `POST /api/v1/market/cancelbid`, `GET /api/v1/sofascore/player/{name}`.
- **Orden intra-unidad (test-after)**: implementar y testear primero la lógica
  pura/`FutmondoKit` (modelos, `MarketService`/`SofascoreService`, `MarketSorter`,
  `BidAmountValidator`, mapeo `MarketWriteOutcome`) con XCTest (`swift test`);
  después las vistas SwiftUI (validadas en dispositivo, fuera del cómputo de
  cobertura — `llvm-cov` no fiable en WSL).
- **Notas y constraints**:
  - Coste 0 €: sólo SDK de Apple; `Package.swift` sigue con `dependencies: []`.
  - Seguridad: toda llamada con `Authorization: Bearer`; refresh token sólo en
    Keychain; ningún material de credencial en logs/mensajes de error.
  - Divergencias confirmadas (ADR-2/ADR-3/ADR-5): resultado de escritura tipado
    (`MarketWriteOutcome`), tope de puja = `available_for_bids`, `SofascoreService`
    dedicado para aislar el fallo del detalle (FR8.2).
  - No ampliar los god-files del backend (no aplica aquí: sin cambios backend).

## Assumptions & Open Questions

None.
