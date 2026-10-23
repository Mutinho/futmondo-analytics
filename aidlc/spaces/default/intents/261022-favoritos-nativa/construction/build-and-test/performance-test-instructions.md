# Performance Test Instructions — Favoritos nativa iOS

## Aplicabilidad
**NO APLICA como test formal** en este intent (estrategia minimal; sin NFR de
rendimiento cuantificado que exija benchmarks locales).

## Hallazgo de rendimiento (medido, informativo)
Durante el desarrollo se midió la latencia del backend en producción (token
efímero): `/favorites/my` ≈ **3,4 s**, `/market/today` ≈ **1,6 s**,
`/analytics/balances` ≈ 0,4 s. La lentitud de carga percibida es del **backend**
(consulta Futmondo/Sofascore en vivo), no del cliente nativo (una sola petición
por pantalla; render instantáneo). Mitigado en el cliente con skeleton +
crossfade + caché en memoria `DataFreshness`. La mejora de raíz es un intent de
**backend** (servir desde datos pre-sincronizados / caché TTL), anotado en
`aidlc/spaces/default/knowledge/aidlc-shared/backend-latency-market-favorites.md`.
