# Backend — latencia de `/market/today` y `/favorites/my` (mejora pendiente)

> Conocimiento de equipo (`aidlc-shared`): hallazgo medido durante el desarrollo
> del cliente nativo iOS. NO es una regla de `memory/`; es una mejora candidata
> para un futuro **intent de backend** (optimización), con su evidencia.

## Evidencia (medición 2026-10-23, producción `https://futmondo-api.fly.dev`)

Peticiones autenticadas, cronometradas con `curl` (ttfb ≈ total → el tiempo lo
gasta el servidor procesando, no la red ni el cliente):

| Endpoint | Pantalla | ttfb/total | Nota |
|---|---|---|---|
| `GET /api/v1/championships` | (selector) | **0,24 s** | rápido; no llama a Futmondo |
| `GET /api/v1/analytics/balances` | Presupuesto | **0,42 s** | aceptable; datos ya sincronizados en Neon |
| `GET /api/v1/market/today` | Mercado | **1,57 s** | lento |
| `GET /api/v1/favorites/my` | Favoritos | **3,42 s** | muy lento |

Descartado: cold start de Fly (la 1.ª llamada fue 0,24 s), latencia de red, y
lentitud del cliente nativo (hace una sola petición por pantalla; el render es
instantáneo frente a estos tiempos). La causa es el **procesamiento en el
backend**.

## Diagnóstico

`/market/today` y `/favorites/my` son lentos porque, a diferencia de `balances`
(que lee datos ya sincronizados en Neon), consultan/агregan en vivo contra la
**API de Futmondo y/o Sofascore** en cada request (scraping/agregación en
caliente). Presupuesto va rápido justamente porque lee de la caché sincronizada.

## Mejora propuesta (para un intent de backend, NO de cliente)

- **Servir `/favorites/my` y `/market/today` desde datos pre-sincronizados**
  (Neon) en vez de consultar Futmondo/Sofascore en el request, siguiendo el
  mismo patrón que ya usa `balances`/el sync paso a paso
  (`data_sync_service.py`). La vista de mercado y la de favoritos libres se
  alimentarían de la última sincronización.
- Alternativa / complemento: **caché con TTL** por campeonato en el backend para
  esos dos endpoints (minutos), de modo que la mayoría de requests respondan en
  <0,5 s como balances.
- Restricciones a respetar (memoria del proyecto): coste 0 € (Neon free / Fly
  free), NO ampliar los god-files (`data_sync_service.py` ~84 KB,
  `data_manager_v2.py`) ni el patrón SQL-en-router — el código nuevo tras una
  capa/función estrecha testeable; characterization-first sobre lo que se toque.
- Impacto esperado: `/favorites/my` de ~3,4 s → <0,5 s; `/market/today`
  de ~1,6 s → <0,5 s. El cliente nativo no cambia (ya tiene skeletons + caché en
  memoria que disimulan la espera, pero el objetivo es que la espera deje de
  existir).

## Estado

Pendiente. Candidato a un nuevo intent de backend (p. ej.
`optimizar-latencia-market-favoritos`). El cliente nativo (Mercado, Favoritos)
queda entregado con skeleton + crossfade + caché en memoria `DataFreshness`, que
mitigan la UX de la espera pero no la causa.
