# Domain Design — Architecture Decision Records (matchday-prizes-calc)


## ADR-001: Extraer el cálculo del premio a un componente puro (`PrizeCalculator`)

- **Context**: La fórmula del premio de jornada vive hoy entera dentro de
  `data_sync_service.sync_prizes()` (~300 líneas en un fichero de ~84 KB),
  mezclada con ingesta desde la API Futmondo (I/O con `time.sleep`) y
  persistencia (UPSERT + `DELETE ... NOT IN`). Esa producción tiene cobertura
  directa cero (GAP crítico del RE). El intent debe corregir el reparto del
  premio de ranking ante empates (FR1) de forma testeable y a coste 0 €, sin
  engordar el god-file (NFR4) y con caracterización previa de todas las ramas
  (NFR1). Decisión humana Q1=A.
- **Decision**: Extraer el cálculo de los términos del premio a un componente
  **puro** (`PrizeCalculator`) sin I/O ni SQL, que recibe datos ya
  materializados y la configuración, y devuelve los importes por equipo.
  `sync_prizes` queda como `PrizeSyncOrchestrator`: ingesta → cálculo puro →
  persistencia. La regla de empate (suma de posiciones contiguas / N, `round()`
  por parte) vive dentro del cálculo puro.
- **Consequences**:
  - (+) El cálculo se caracteriza y se testea de forma aislada, determinista y
    sin red/coste (NFR1/NFR3); la corrección del empate queda acotada.
  - (+) El god-file no crece en lógica de cálculo (NFR4).
  - (−) Introduce una frontera nueva y un punto de integración (orquestador →
    calculadora) que hay que cablear con cuidado para no alterar el gating ni la
    persistencia existentes.
- **Alternatives Rejected**: corregir *in situ* dentro de `sync_prizes` (Q1=B):
  deja la fórmula sin frontera testeable y engorda el god-file. Rechazada por el
  usuario.

## ADR-002: Propiedad de entidades — cálculo vs persistencia

- **Context**: El resultado del cálculo (importes por equipo) y la fila
  persistida en `team_prizes` son la misma información en dos momentos: cálculo
  puro y persistencia. Hay que evitar que la calculadora conozca el esquema SQL.
- **Decision**: `PrizeCalculator` posee `TeamRoundPrize` (resultado en memoria,
  sin dependencia de BD); `PrizeSyncOrchestrator` posee `TeamPrizeRow` (la fila
  real en `team_prizes`). Cada `TeamRoundPrize` se materializa como una
  `TeamPrizeRow` en la persistencia, que sigue siendo responsabilidad del
  orquestador.
- **Consequences**:
  - (+) La calculadora no depende del esquema ni del SQL; mantiene su pureza.
  - (+) La mitad de lectura (routers → `SELECT`/suma sobre `team_prizes`) no se
    toca.
  - (−) Hay un mapeo explícito resultado→fila en el orquestador (trivial: mismos
    campos).
- **Alternatives Rejected**: que la calculadora devuelva directamente tuplas de
  BD — rompería su pureza y la acoplaría al esquema.
