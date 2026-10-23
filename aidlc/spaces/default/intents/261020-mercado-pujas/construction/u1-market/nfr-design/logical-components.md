# Logical Components — u1-market

> Inventario de componentes lógicos de `u1-market`: fronteras, dominios de fallo,
> blast radius y aislamiento. Puente entre el diseño NFR y (si aplicara)
> Infrastructure Design. Para una Unit `ui` embebida en el paquete `ios/`
> existente, no hay infraestructura nueva: los "componentes" son los límites de
> actor/servicio y de estado dentro del cliente.

## Sources

- `.../construction/u1-market/nfr-design/{performance-design,security-design}.md`.
- `.../construction/u1-market/functional-design/functional-spec.md` (W1–W7).
- `.../inception/domain-design/components.md` (C1–C8, V1–V7).
- `nfr-design-questions.md` (Q3).

## Componentes lógicos y dominios de fallo

| Componente lógico | Rol | Dominio de fallo | Blast radius de un fallo |
|---|---|---|---|
| `MarketService` (actor) | Carga de `/market/today` + escritura (`bid`/`cancelbid`) | Red del Mercado | Un fallo se refleja en `loadState = error` (carga) o en `MarketWriteOutcome.rejected/networkError` (escritura); no cae la app ni la pestaña de Presupuesto. |
| `SofascoreService` (actor) | Carga del detalle `/sofascore/player/{name}` | Red del detalle (endpoint aparte) | **Aislado**: el fallo queda en el estado local del `SofascoreDetailSheet`; NO afecta a la lista ni a la capacidad de pujar (FR8.2). |
| Lógica pura (`MarketSorter`, `BidAmountValidator`, mapeo `MarketWriteOutcome`) | Orden, validación, mapeo de desenlace | Ninguno (determinista, sin I/O) | No puede fallar por red; testeable aislada con XCTest. |
| `MarketViewModel` (@MainActor) | Estado observable + orquestación | Estado de pantalla | Contiene el estado; un error de servicio se traduce a estado observable, no a crash. |
| Vistas SwiftUI (`MarketView`, cards, sheets) | Presentación | Render | Presentacionales; sin estado de negocio propio. |

## Estrategia de aislamiento

- **Separación de actores**: `MarketService` y `SofascoreService` no comparten
  estado; el detalle Sofascore es un dominio de fallo independiente (Q3, ADR-5).
- **Pureza de la lógica de negocio**: orden/validación/mapeo viven en funciones y
  tipos puros de `FutmondoKit`, aislados de la UI y de la red → testeables y sin
  blast radius.
- **Estado local del sheet**: el `SofascoreDetailSheet` no escribe en el estado de
  la lista; cerrarlo descarta su estado.
- **Escritura serializada**: `isWriting` global garantiza una sola escritura en
  vuelo (sin condiciones de carrera entre pujas/cancelaciones concurrentes).

## Recursos compartidos

- `NetworkClient` y la sesión `AuthService` de F1 son **compartidos** (reutilizados
  por ambos servicios y por el resto de la app); `u1-market` no introduce nuevos
  recursos compartidos ni almacenamiento.

## Infraestructura nueva

Ninguna. `u1-market` se empaqueta dentro del target `FutmondoApp`/`FutmondoKit`
existente; no hay despliegue, pipeline ni recurso de infraestructura nuevo
(Infrastructure Design no aplicará a esta Unit `ui`).

## Assumptions & Open Questions

None.
