# Scalability Requirements — Optimización de latencia

Deriva de inception **NFR1/NFR3**. IDs `NFR1.x`/`NFR3.x` según corresponda.

## Postura

El cambio **reduce** la carga sobre dependencias externas (menos llamadas HTTP
vivas a Futmondo por request) y desplaza la carga a lecturas Neon ya existentes,
que son el patrón rápido de referencia (`balances`). No introduce nuevos
requisitos de escala.

| ID | Requisito | Criterio | Fuente |
|---|---|---|---|
| NFR3.1 | Menos dependencia externa | `favorites/my` pasa de 2-3 llamadas vivas a 0 (ruta normal); `market/today` mantiene 1. Menos presión sobre la API de Futmondo y su timeout de 15 s | reverse-engineering |
| NFR3.2 | Carga sobre Neon | Las lecturas nuevas son `SELECT` con `WHERE`/`JOIN` sobre tablas ya pobladas e indexadas por el sync; dentro del tier Neon free (coste 0) | NFR3, C3 |
| NFR3.3 | Concurrencia | No es el eje del problema hoy (uso personal/pequeño grupo); no se fija objetivo de concurrencia nuevo. La lectura desde sync escala mejor que N descargas de catálogo en vivo | Q2-A |

## Out of scope

- Autoescalado, sharding, réplicas de lectura: no aplican al stack actual
  (Fly.io + Neon free) ni al tamaño de uso.
