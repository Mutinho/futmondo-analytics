# Unit of Work — Story Map (F2)

> Fase: inception (units-generation). Idioma: castellano; tokens técnicos verbatim en inglés.

| Unidad | Historias | Requisitos | Entrega |
|--------|-----------|------------|---------|
| u1-budget-data | US1 (datos), US2 (datos+store), US3 (sort) | FR1.1–FR1.3, FR2.1, FR3.1–FR3.3, FR4.2, NFR1/NFR2/NFR6 | Lógica verificable con `swift test` |
| u2-budget-ui | US1 (render), US2 (menú), US3 (control de orden), US4 (TabView) | FR1 render, FR4.1, FR5.1, NFR3/NFR4/NFR5 | Pantalla funcional validada en dispositivo |

Cada historia se completa cuando ambas unidades que la tocan están construidas (datos en U1 + presentación en U2). US4 es sólo U2 (andamiaje de navegación).

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/user-stories/stories.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/units-generation/unit-of-work.md`

## Assumptions & Open Questions

None.
