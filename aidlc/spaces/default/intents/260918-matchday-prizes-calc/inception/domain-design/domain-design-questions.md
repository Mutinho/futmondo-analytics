# Domain Design — Preguntas y confirmación (matchday-prizes-calc)

No hubo preguntas de diseño abiertas: las decisiones de frontera venían fijadas
por los requisitos (FR1 extraer a función pura; FR3 orquestación) y las
prácticas afirmadas (separación cálculo-puro / ingesta / persistencia; no
engordar god-files). El diseño introduce un componente nuevo (`PrizeCalculator`)
y reduce `sync_prizes` a orquestador (`PrizeSyncOrchestrator`).

## Consolidated Summary Confirmation

Resumen del diseño de dominio:

- **Componente nuevo `PrizeCalculator`** (puro, sin I/O ni SQL): calcula los términos del premio de una jornada; incluye la regla de empate (FR1): agrupar equipos premiables por puntos, sumar los premios de las N posiciones contiguas de cada grupo empatado y repartir a partes iguales con `round()` por parte.
- **`PrizeSyncOrchestrator`** (rol reducido de `sync_prizes`): ingesta desde la API Futmondo → cálculo puro → persistencia en `team_prizes` (UPSERT + `DELETE ... NOT IN`), con recálculo retroactivo (FR3.2). No contiene la fórmula (NFR4).
- **Propiedad de entidades**: `PrizeCalculator` posee `TeamRoundPrize` (resultado en memoria); `PrizeSyncOrchestrator` posee `TeamPrizeRow` (fila en `team_prizes`).
- **ADRs**: ADR-001 (extraer cálculo a componente puro; alternativa in-situ rechazada, Q1=A); ADR-002 (propiedad de entidades cálculo vs persistencia).
- La mitad de lectura (routers → `SELECT`/suma sobre `team_prizes`) no se toca.

Does this all look correct before I finalize the domain design?

- Looks correct
- Request changes

[Answer]: Looks correct
