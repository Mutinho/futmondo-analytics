# Performance Design — u2-integrations (Integraciones)

Diseño de rendimiento de U2, derivado de `performance-requirements.md`. El único
requisito de rendimiento nuevo es el timeout acotado por petición (Q1); el resto
se hereda sin cambio (proceso batch, sin objetivos p50/p95/p99 interactivos).

Consume: `performance-requirements.md`, `functional-spec.md`, `tech-stack-decisions.md`.
Perspectivas inline: arquitecto + plataforma.

## Diseño por requisito

### NFR-perf.1 — Timeout acotado por petición

- **Diseño**: connect ~5 s, read ~30 s por petición de integración (Q1), vía el
  parámetro `timeout` de `requests` y el equivalente de `curl_cffi`. Acota el
  bloqueo del cron ante un proveedor lento sin cortar respuestas legítimas.
- Un exceso → `IntegrationTimeoutError` (recuperable, ver reliability-design).

### NFR-perf.2 — Sin regresión de rendimiento

- **Diseño**: el endurecimiento (bloques `try/except` tipados + logging
  estructurado) tiene coste despreciable; no introduce trabajo en el camino
  feliz más allá de la construcción del contexto de log al fallar. La suite
  existente debe seguir en verde.

## Sin cambio (heredado)

- **Throttle preventivo de Sofascore (~750 ms)**: se mantiene; regula el ritmo
  de peticiones para evitar el baneo. Es un patrón de rendimiento/anti-baneo ya
  presente; U2 no lo altera.
- **Pool de conexiones a Neon** (`ThreadedConnectionPool` 5–20, retry x3 en
  `db_connection`): **sin cambio**. La transacción atómica de `team_prizes` usa
  el pool existente.
- **Sin caching nuevo**: no aplica (el sync recomputa; no hay caché de lectura
  que introducir en el alcance de U2).

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- CDN / ElastiCache / caching gestionado → NO-APLICA (no hay superficie de U2
  que lo requiera; coste 0 €).
- Objetivos p95/p99 interactivos → no aplican a un proceso batch de sync.

## Assumptions & Open Questions

None.
