# Performance Requirements — Optimización de latencia

Deriva de inception **NFR1** (y NFR2 de frescura). IDs `NFR1.x`.

## Target Verification Matrix

| ID | Requisito | Objetivo (pass/fail) | Método de medición | Fuente |
|---|---|---|---|---|
| NFR1.1 | Latencia `favorites/my` | **p95 < 0,5 s** (en caliente, tras warm-up) | ≥ 30 peticiones secuenciales autenticadas con `curl`, `time_total`; percentil con interpolación lineal (método `numpy.percentile`/`statistics.quantiles` explícito); p50/p95/p99; primera petición descartada | NFR1, Q1-A, Q2-A |
| NFR1.2 | Latencia `market/today` (catálogo desde sync) | **p95 < 0,8 s** (acotado por la llamada viva `POST /1/market/players`, irreducible sin cambio de esquema) | igual que NFR1.1 (≥ 30 muestras, interpolación lineal) | NFR1, Q1-A |
| NFR1.3 | Referencia de sanidad | `favorites/my` y el catálogo de `market/today` ≤ el patrón de `balances` (~0,4 s, 1 llamada viva + lecturas Neon) | comparación directa en la misma corrida | NFR1, A3 |
| NFR1.4 | Métricas reportadas | p50, p95 y p99 reportados como contexto (no solo el umbral) | del mismo script | Q1-A |
| NFR1.5 | Frescura aceptable (NFR2) | valores/stats/catálogo reflejan la **última sincronización** (como balances); NO es un objetivo de latencia sino de staleness tolerada | n/a (revisión de diseño) | NFR2 |

## Notas de rendimiento

- **Causa raíz** (del reverse-engineering): la latencia es proporcional al número
  de llamadas HTTP vivas a Futmondo por request. La gran ganancia está en
  `favorites/my`, que hoy descarga el catálogo COMPLETO en vivo
  (`get_championship_players`) solo para filtrar favoritos; al leer desde sync se
  elimina esa descarga → p95 objetivo < 0,5 s.
- `market/today` ya lee el catálogo de caché; su única llamada viva restante
  (`POST /1/market/players`, pujas del usuario) **no es sincronizable** sin
  cambio de esquema (fuera de alcance, NFR6/O1), por eso su objetivo p95 es < 0,8
  s, no < 0,5 s. La distinción se documenta para no fijar un umbral que dé falsos
  rojos.
- La verificación formal (corrida de medición y comparación contra estos
  umbrales) ocurre en la stage **Performance Validation**; aquí se fija el
  objetivo y el método.

## Presupuesto de latencia (favorites/my, objetivo)

| Componente | Presupuesto aprox. |
|---|---|
| `SELECT player_id FROM player_favorites` | < 50 ms |
| `SELECT` jugadores sincronizados (JOIN players + stats + sofascore_cache) | < 300 ms |
| Mapeo + orden + serialización | < 50 ms |
| **Total objetivo p95** | **< 0,5 s** |
