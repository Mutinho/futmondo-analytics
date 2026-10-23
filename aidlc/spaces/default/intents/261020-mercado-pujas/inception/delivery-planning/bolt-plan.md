# Bolt Plan — F3 Mercado

> Un **Bolt** es una pasada de Construction sobre una pieza de trabajo (una o más
> Units) que termina en algo que corre, con su Definición de Hecho e hipótesis de
> confianza. Este plan ordena los Bolts; la topología viene del DAG de Units
> Generation, aquí se elige el camino. F3 tiene una sola Unit, así que hay un
> solo Bolt.

## Sources

- `.../inception/units-generation/unit-of-work.md`, `unit-of-work-dependency.md`,
  `unit-of-work-story-map.md`.
- `.../inception/domain-design/components.md`.
- `.../inception/requirements-analysis/requirements.md` (FR1–FR8, NFR1–NFR6),
  `.../inception/user-stories/stories.md` (US1–US7),
  `.../inception/refined-mockups/mockups.md` (M1–M4).
- `aidlc/spaces/default/memory/team.md` (walking skeleton OFF, deploy on-merge),
  `project.md` (coste 0 €, gate CI).

## Secuencia de Bolts

### Bolt 1 — `u1-market` (pantalla de Mercado nativa)

- **Units incluidas**: `u1-market` (U1) — única Unit del intent.
- **Walking skeleton**: no (OFF; el sistema ya está en producción y la capa
  `ios/` existe desde F1/F2; este Bolt añade una pantalla a un shell existente,
  no arranca nada de cero).
- **Contenido**:
  - Lógica/datos (`FutmondoKit`, con XCTest): `MarketPlayer`, `MarketUserInfo`,
    `MarketTodayResponse`, `MarketWriteOutcome`, `MarketService`, `MarketSorter`,
    `BidAmountValidator`, `SofascoreDetail`, `SofascoreService`.
  - UI (`FutmondoApp`, `#if canImport(SwiftUI)`, validada en dispositivo):
    `MarketView`, `MarketViewModel`, `MarketPlayerCard`, `BidSheet`,
    `CancelBidConfirmation`, `SofascoreDetailSheet`, `RootTabView` (2ª pestaña).
- **Definición de Hecho (DoD)**:
  - La lógica `FutmondoKit` está implementada y **en verde con `swift test`**
    (XCTest): modelos, servicios (`MarketService`/`SofascoreService`),
    `MarketSorter`, `BidAmountValidator`, mapeo de `MarketWriteOutcome`.
  - Las vistas SwiftUI están **validadas en dispositivo** (iPhone 13 Pro vía
    `xtool dev build`): lista con estados loading/error/empty/data, banner,
    sheet de puja con validación inline, confirmación de cancelación, sheet de
    detalle Sofascore.
  - La **suite existente sigue en verde** en el gate de CI (backend `pytest`,
    frontend `ng test`) — F3 no la modifica.
  - **US1–US7 cubiertas**; sin dependencias nuevas (`Package.swift`
    `dependencies: []`); seguridad preservada (Bearer, refresh en Keychain, sin
    credenciales en logs).
- **Hipótesis de confianza (qué prueba enviar este Bolt)**: la pantalla de
  Mercado nativa carga `/market/today` del campeonato activo, ordena la lista,
  permite **pujar y cancelar** distinguiendo los tres desenlaces tipados
  (aceptada / rechazada por backend / error de red) y muestra el **detalle
  Sofascore aislado** (un fallo del detalle no afecta a lista ni a escritura,
  FR8.2) — reproduciendo la vista Angular de Mercado sobre la capa nativa de
  F1/F2 **sin cambios de backend**.
- **Demo esperada**: en un iPhone 13 Pro autenticado, abrir la 2ª pestaña
  "Mercado", ver banner + cards, reordenar, abrir el sheet de puja (default =
  sugerida, validación min/max), pujar y ver el aviso + recarga, cancelar una
  puja activa, y abrir el detalle Sofascore de un jugador.
- **Mob/propietario**: `aidlc-developer-agent` (IA; sin equipos humanos).

## Orden intra-Bolt (test-after)

1. Lógica `FutmondoKit` + XCTest (modelos, servicios, sorter, validador, outcome).
2. Vistas SwiftUI + validación en dispositivo (cards, banner, sheets, 2ª pestaña).

## Assumptions & Open Questions

None.
