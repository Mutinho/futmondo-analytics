# Delivery Planning — Plan de Bolts (matchday-prizes-calc)

## Sources

- `unit-of-work.md`, `unit-of-work-dependency.md`, `unit-of-work-story-map.md`
  (una sola unidad U1).
- `requirements.md` (FR1–FR3, NFR1–NFR5), `components.md`.
- `team-practices.md`: walking skeleton OFF; mob por defecto (scope classic).

## Plan de Bolts

Un **Bolt** es un pase de construcción sobre una porción del trabajo que termina
en algo que funciona. Como el intent tiene una sola unidad de trabajo, el plan
es de **un único Bolt**.

### Bolt 1 — matchday-prizes-calc

- **Unidad(es) incluida(s)**: U1 (matchday-prizes-calc).
- **Walking skeleton**: No (OFF; sistema ya en producción, intervención acotada).
- **Definition of Done**:
  - `PrizeCalculator` extraído como función/módulo puro (sin I/O ni SQL);
    `sync_prizes` reducido a orquestador.
  - Red de caracterización de TODAS las ramas de `sync_prizes` en verde contra
    el código actual (NFR1) antes del cambio de comportamiento.
  - Regla de empate implementada (FR1) con tests del nuevo contrato (2 y 3
    empatados; caso jornada 5 = 1.500.000/1.500.000).
  - Suite existente en verde; gate de CI bloqueante (gitleaks + pytest + ng
    test) pasado (NFR5).
- **Confidence hypothesis**: al recalcular, los premios de jornada con empates
  se reparten equitativamente (suma de posiciones del grupo / N), y las jornadas
  sin empate no cambian de importe.
- **Demo esperada**: test que reproduce el ranking de la jornada 5 del
  campeonato de ejemplo y verifica el reparto 1.500.000/1.500.000; suite verde.

## Secuenciación

Trivial: un solo Bolt, sin dependencias. No hay desviación respecto al DAG
topológico (una única unidad).
