# Risk and Sequencing Rationale — F3 Mercado

> El porqué del orden de Bolts. Con una sola Unit el orden es trivial; este
> documento registra la heurística aplicable, la (no) desviación del DAG y el
> registro de riesgos.

## Sources

- `.../inception/delivery-planning/bolt-plan.md`.
- `.../inception/units-generation/unit-of-work-dependency.md` (DAG: 1 nodo,
  `depends_on: []`).
- `.../inception/requirements-analysis/requirements.md` (NFR1–NFR6).

## Heurística de secuenciación

- **Heurística aplicada**: **value-first** trivial — hay un único Bolt que entrega
  todo el valor de F3; no hay ranking entre Bolts que calcular. No se usa WSJF
  (Weighted Shortest Job First: valor+urgencia÷tamaño) porque con una sola Unit no
  hay cola que ordenar.
- **Walking skeleton (Cockburn)**: NO aplica (línea base OFF; sistema en producción,
  capa `ios/` existente). El primer —y único— Bolt no es un esqueleto a arrancar.
- **Desviación del orden topológico del DAG**: **ninguna**. El DAG tiene un único
  nodo `u1-market` sin aristas; cualquier orden lo respeta trivialmente.

## Orden intra-Bolt (no es secuencia económica)

Dentro del Bolt se implementa primero la lógica testeable (`FutmondoKit`, XCTest)
y luego las vistas (`FutmondoApp`, validación en dispositivo). Es una **ordenación
de diseño/test-after intra-unidad**, no una secuencia económica entre Bolts.

## Registro de riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Validación de UI SwiftUI sólo en dispositivo (no en CI/WSL; `llvm-cov` no fiable) | Media | Medio | Cerrar y testear la lógica en `FutmondoKit` (XCTest en WSL) antes de iterar la UI en iPhone 13 Pro (`xtool dev build`); las vistas quedan fuera del cómputo de cobertura (aprendizaje durable). |
| Escritura (pujar/cancelar): distinguir aceptada / rechazada-backend / error-red | Media | Alto | `MarketWriteOutcome` tipado (ADR-2); tests de la lógica de mapeo con dobles; recarga sólo en `.accepted`; `isWriting` global deshabilita acciones durante la operación. |
| Tope de puja divergente (`available_for_bids` vs `max_bid` de Angular) | Baja | Medio | Divergencia confirmada (Q1=A, ADR-3) y aislada en `BidAmountValidator` puro, testeable. |
| Aislamiento del detalle Sofascore (FR8.2) | Baja | Medio | `SofascoreService` actor dedicado y estado local al sheet (ADR-5/ADR-6); un fallo del detalle no toca la lista ni la escritura. |
| Romper la suite existente / gate de CI | Baja | Alto | F3 sólo toca `ios/`; no modifica backend/frontend; el gate corre igual en el PR y debe quedar en verde antes de fusionar. |
| Regresión del shell `RootTabView` al añadir la 2ª pestaña | Baja | Medio | Cambio mínimo aditivo; validación en dispositivo de que Presupuesto (F2) sigue operativo. |

## Assumptions & Open Questions

None.
