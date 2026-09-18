# Units Generation — Unidades de trabajo (matchday-prizes-calc)


## Sources

- `components.md` (PrizeCalculator, PrizeSyncOrchestrator) y `decisions.md`
  (ADR-001, ADR-002) del diseño de dominio.
- `requirements.md` (FR1–FR3, NFR1–NFR5).

## Decomposición

El intent es una intervención acotada sobre un único servicio desplegable (el
backend FastAPI). Ambos componentes del diseño de dominio (`PrizeCalculator`
nuevo y `PrizeSyncOrchestrator`, que es el `sync_prizes` reducido) viven en el
mismo servicio y se despliegan juntos; no hay una decomposición en varias
unidades viable ni deseable. Por tanto: **una sola unidad de trabajo**.

## Unidades

| Unit ID | Directory | Nombre | Kind | Complejidad | Deployment |
|---|---|---|---|---|---|
| U1 | u1-matchday-prizes-calc | matchday-prizes-calc | service | M | shared (backend `futmondo-api`) |

### U1 — matchday-prizes-calc

- **Descripción**: Corrección del cálculo del premio de ranking por jornada
  ante empates, extrayendo el cálculo a un componente puro y dejando
  `sync_prizes` como orquestador.
- **Responsabilidades**:
  - `PrizeCalculator` (puro, sin I/O ni SQL): términos del premio + regla de
    empate (agrupar por puntos, sumar posiciones contiguas del grupo, repartir
    `suma/N` con `round()` por parte).
  - `PrizeSyncOrchestrator`: ingesta (API Futmondo) → cálculo puro →
    persistencia (`team_prizes`), con recálculo retroactivo.
- **Kind**: `service` — se integra en el ejecutable desplegado `futmondo-api`.
- **Deployment**: compartido (no es un servicio nuevo; es código dentro del
  backend existente).
- **Complejidad**: M — una regla de negocio nueva + extracción a función pura +
  red de caracterización previa de todas las ramas.
- **Notas/constraints**:
  - Caracterización previa obligatoria de todas las ramas de `sync_prizes`
    (NFR1) con fakes a coste 0 € (NFR3).
  - No engordar los god-files ni el patrón SQL-en-router (NFR4).
  - La mitad de lectura (routers → `SELECT`/suma sobre `team_prizes`) no se toca.

## Assumptions & Open Questions

None.
