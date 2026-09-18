# Units Generation — Preguntas y confirmación (matchday-prizes-calc)

No hubo preguntas de decomposición abiertas: el intent es una intervención
acotada sobre un único servicio (el backend), por lo que hay una sola unidad de
trabajo.

## Consolidated Summary Confirmation

Resumen de la generación de unidades:

- **Una sola unidad de trabajo `U1` (matchday-prizes-calc)**, kind `service`, complejidad M, desplegada dentro del backend existente `futmondo-api` (no es un servicio nuevo).
- Contiene los dos componentes del diseño: `PrizeCalculator` (puro) y `PrizeSyncOrchestrator` (orquestador).
- **Sin dependencias entre unidades** (edge block: `depends_on: []`); las dependencias externas (API Futmondo, Neon) no son unidades.
- Orden interno: caracterización de todas las ramas → extracción del cálculo puro → regla de empate + tests del nuevo contrato.
- Todos los FR (FR1–FR3) mapeados a U1.

Does this all look correct before I finalize units generation?

- Looks correct
- Request changes

[Answer]: Looks correct
