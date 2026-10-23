# Units Generation — Preguntas de decomposición (F3 Mercado)

> Objetivo: agrupar los 15 componentes de Domain Design en unidades de trabajo
> implementables, con su kind (`service`/`spec`/`ui`/`packaging`/`library`) y el
> DAG de dependencias (topología; la secuencia económica es de Delivery
> Planning). Contexto: F3 es una **feature de UI nativa iOS (SwiftUI)** que
> reproduce la vista Angular de Mercado como 2ª pestaña del `RootTabView` tras
> Presupuesto (F2), **sin cambios de backend**, construyendo sobre la capa
> `FutmondoKit`/`FutmondoApp` ya existente de F1/F2.

## Contexto para las respuestas

Los 15 componentes se reparten entre dos targets ya existentes del paquete
SwiftPM `ios/`:

- **`FutmondoKit`** (librería testeable con XCTest): `MarketPlayer`,
  `MarketUserInfo`, `MarketTodayResponse`, `MarketWriteOutcome`, `MarketService`,
  `MarketSorter`, `BidAmountValidator`, `SofascoreDetail`, `SofascoreService`.
- **`FutmondoApp`** (vistas SwiftUI, validadas en dispositivo): `MarketView`,
  `MarketViewModel`, `MarketPlayerCard`, `BidSheet`, `CancelBidConfirmation`,
  `SofascoreDetailSheet`, `RootTabView` (modificación mínima).

Todos cambian juntos para entregar una sola pantalla y se funden a `main` como
un único PR squash-merge. No hay backend nuevo, ni pipeline nuevo, ni
distribución nativa en este intent.

## Q1 — Estrategia de frontera de unidades

¿Cómo agrupamos los componentes en unidades?

- A. **Una sola unidad de feature** (`u1-market`) que contiene la lógica
  `FutmondoKit` + las vistas `FutmondoApp` de Mercado. Es la forma natural para
  una pantalla cohesiva que se entrega y fusiona junta, y coincide con cómo F2
  decompuso Presupuesto.
- B. **Dos unidades**: una `library`/`spec` con la lógica `FutmondoKit` y una
  `ui` con las vistas `FutmondoApp` dependiente de la primera.
- C. Otro (especificar).

[Answer]: A

## Q2 — Granularidad

¿Preferencia de granularidad?

- A. **Coarse-grained** (una unidad de feature), coherente con el tamaño del
  cambio y con F2. Dentro de la unidad, la lógica `FutmondoKit` se implementa y
  testea antes que las vistas (orden intra-unidad), pero es una sola unidad.
- B. Fine-grained (varias unidades pequeñas).
- C. Otro (especificar).

[Answer]: A

## Q3 — kind de la unidad

¿Qué kind recibe la unidad (determina qué artefactos de diseño de Construction
aplican)?

- A. **`ui`** — F3 es una superficie de frontend nativa; su lógica testeable va
  en `FutmondoKit` pero el entregable es una pantalla de UI. Como `ui`, no debe
  un modelo de escalabilidad de servidor ni contrato de API nuevo (reutiliza los
  contratos backend existentes).
- B. `library`.
- C. `service`.
- D. Otro (especificar).

[Answer]: A

## Q4 — Modelo de despliegue y dependencias

¿Modelo de despliegue e integración de la unidad?

- A. **Embedded / sin despliegue nuevo**: la unidad amplía el paquete `ios/`
  existente; no se publica la app en este intent, no toca Fly.io ni CI/CD. Su
  única dependencia es sobre componentes ya existentes de F1/F2 (`NetworkClient`,
  `AuthService`/sesión, `DesignSystem`, `RootTabView`), que son estado del repo,
  no unidades nuevas de F3. Por tanto el DAG de F3 tiene **una unidad sin
  dependencias de unidad nuevas** (`depends_on: []`).
- B. Despliegue independiente.
- C. Otro (especificar).

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Resumen de Units Generation para F3 = Mercado, antes de generar los artefactos:

- **1 unidad**: `u1-market` (directorio `u1-market`), **kind `ui`**, complejidad
  **M**.
- **Contenido**: la lógica `FutmondoKit` (C1–C8: `MarketPlayer`,
  `MarketUserInfo`, `MarketTodayResponse`, `MarketWriteOutcome`, `MarketService`,
  `MarketSorter`, `BidAmountValidator`, `SofascoreDetail`, `SofascoreService`) +
  las vistas `FutmondoApp` (V1–V7: `MarketView`, `MarketViewModel`,
  `MarketPlayerCard`, `BidSheet`, `CancelBidConfirmation`, `SofascoreDetailSheet`,
  `RootTabView`).
- **DAG**: `u1-market` con **`depends_on: []`** (sólo depende de componentes ya
  existentes de F1/F2 —`NetworkClient`, `AuthService`/sesión, `DesignSystem`,
  `RootTabView`—, que son estado del repo, no unidades nuevas de F3). Sin
  paralelismo (una sola unidad). Sin despliegue nuevo.
- **Orden intra-unidad**: primero la lógica `FutmondoKit` (con sus XCTest), luego
  las vistas SwiftUI (validadas en dispositivo).
- **Trazabilidad**: US1–US7 (y FR1–FR8) mapeadas a `u1-market`.
- **Artefactos a generar**: `unit-of-work.md`, `unit-of-work-dependency.md`
  (con bloque `yaml` de aristas), `unit-of-work-story-map.md`, `traceability.json`.
- **Nota**: la secuencia económica / Bolts es decisión de Delivery Planning
  (siguiente etapa), no de aquí.

¿Todo correcto antes de generar los artefactos?

- **Looks correct** — confirmo y genero.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
