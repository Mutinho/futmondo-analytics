# Load Test Plan — Optimización de latencia

## Objetivo

Validar NFR1.1 (`favorites/my` p95 < 0,5 s) y NFR1.2 (`market/today` p95 < 0,8 s)
tras eliminar las llamadas vivas de la ruta normal.

## Patrón de tráfico

Uso personal / grupo pequeño; la concurrencia **no** es el eje (NFR3.3). Se mide
latencia por request, no throughput bajo carga concurrente. Estado estable
(caliente), sin ráfaga.

## Método (fijado en performance-requirements.md)

- **≥ 30 peticiones secuenciales autenticadas** por endpoint.
- Métrica: `time_total` de `curl`.
- Percentil por **interpolación lineal**; se reportan **p50/p95/p99**.
- **Warm-up descartado** (primera petición).
- Entorno: **producción Fly.io** (o equivalente comparable) **con la rama
  desplegada** (ver nota de entorno).

## Comando listo para ejecutar (post-deploy)

```bash
# Requiere: TOKEN (access token válido) y CHAMP (championship_id).
BASE=https://futmondo-api.fly.dev
for ep in "/api/v1/favorites/my?championship_id=$CHAMP" "/api/v1/market/today?championship_id=$CHAMP"; do
  echo "== $ep =="
  for i in $(seq 1 31); do
    curl -s -o /dev/null -w "%{time_total}\n" -H "Authorization: Bearer $TOKEN" "$BASE$ep"
  done | tail -n +2 | sort -n | python3 -c "import sys;v=[float(x) for x in sys.stdin];import statistics as s;q=s.quantiles(v,n=100,method='inclusive');print(f'n={len(v)} p50={q[49]:.3f} p95={q[94]:.3f} p99={q[98]:.3f}')"
done
```

(31 peticiones; la primera `curl` de calentamiento se descarta con `tail -n +2`.)

## Nota de entorno (importante)

La rama `feat/ios-native-app` con el código optimizado **no está desplegada**:
la producción actual ejecuta todavía el código con la llamada viva. Medir ahora
contra producción reflejaría el comportamiento VIEJO. Por decisión del
propietario (Q1-A/Q2-A), la medición empírica p95 queda **`Pending-deploy`**: el
comando de arriba se ejecuta tras el primer despliegue de esta rama. En esta
stage se valida la **causa raíz** analíticamente y con micro-benchmark de la
capa (abajo), a coste 0 y sin forzar un deploy no solicitado.

## Validación analítica + micro-benchmark de la capa (ejecutable ahora)

- `read_favorites` / `read_market_catalog` son **lecturas Neon acotadas** (SELECT
  con `WHERE`/`IN` sobre tablas indexadas por el sync, O(nº favoritos)), **sin
  ninguna llamada HTTP viva** en la ruta normal. La causa raíz de la latencia
  (latencia ∝ nº de llamadas vivas, con timeout de 15 s) queda **eliminada** para
  `favorites/my` y reducida a 1 llamada para `market/today`.
- Micro-benchmark: los 18 tests de la capa (sobre el fake in-memory) corren en
  **~0,19 s en total**, confirmando que el coste de la lógica de lectura/mapeo es
  despreciable frente al presupuesto (<0,5 s); el tiempo real lo dominará el RTT
  a Neon (patrón `balances` ~0,4 s con 1 llamada viva + lecturas Neon).
