# Performance Test Results — Optimización de latencia

## Resumen

Validación en dos partes (Q1-A/Q2-A): (1) **validación de la causa raíz** y
micro-benchmark de la capa — **ejecutados ahora**; (2) **medición empírica p95**
contra el endpoint — **`Pending-deploy`** (la rama no está desplegada; medir
ahora reflejaría el código viejo).

## Parte 1 — Causa raíz + micro-benchmark (ejecutado)

### Análisis de causa raíz (del reverse-engineering, confirmado en código)

- La latencia era **proporcional al nº de llamadas HTTP vivas a Futmondo** por
  request (`FutmondoClient._make_request`, timeout 15 s), no a Neon.
  - `favorites/my` (~3,4 s): descargaba el catálogo COMPLETO en vivo
    (`get_championship_players`) + standings + roster → **2-3 llamadas vivas**.
  - `market/today` (~1,6 s): catálogo de caché + **1 llamada viva** de pujas.
  - `balances` (~0,4 s, referencia rápida): 1 llamada viva + lecturas Neon.

### Efecto del cambio (medible en la capa)

- `favorites/my`: ruta normal pasa a **0 llamadas vivas** (lee de
  `players`/`player_championship_stats`/`market_today`/`sofascore_cache`). Según
  el modelo latencia∝llamadas, cae del rango de 2-3 llamadas (~3,4 s) al patrón
  de solo-lecturas-Neon (≈ `balances` sin su llamada viva).
- `market/today`: catálogo desde caché; se mantiene **1** llamada viva (pujas),
  irreducible → queda en el entorno de `balances` (~0,4 s) + esa llamada.

### Micro-benchmark de la capa (fake in-memory)

- Los 18 tests de la capa (`test_favorites_read*`, `test_market_read`,
  `test_sync_read_endpoints`) corren en **~0,19 s total**. El coste de la lógica
  de lectura/mapeo/orden es **despreciable** frente al presupuesto <0,5 s; el
  tiempo real lo dominará el RTT a Neon, ya caracterizado como rápido (`balances`).
- Presupuesto de latencia objetivo (`favorites/my`): SELECT favoritos <50 ms +
  SELECT jugadores sincronizados <300 ms + mapeo/orden <50 ms → **<0,5 s**.

**Veredicto Parte 1:** la causa raíz de la latencia está **eliminada** para
`favorites/my` y **reducida a 1 llamada** para `market/today`. Consistente con
NFR1.1/NFR1.2.

## Parte 2 — Medición empírica p95 (Pending-deploy)

- **Estado:** `Pending-deploy`. La rama `feat/ios-native-app` no está desplegada;
  la producción ejecuta el código viejo.
- **Comando listo:** ver `load-test-plan.md` (≥31 peticiones, warm-up descartado,
  p50/p95/p99 por interpolación).
- **Umbral pass/fail:** `favorites/my` p95 < 0,5 s; `market/today` p95 < 0,8 s.
- **Owning step:** ejecutar el comando tras el primer despliegue de la rama a
  Fly.io.

## Tasa de errores / bottlenecks

- Sin errores nuevos: la suite completa (440 passed, 0 failed) cubre las ramas
  normal, fallback (sync-miss) y degradada (fallo de pujas).
- Bottleneck restante en `market/today`: la única llamada viva de pujas
  (`POST /1/market/players`), irreducible sin cambio de esquema (fuera de alcance).
