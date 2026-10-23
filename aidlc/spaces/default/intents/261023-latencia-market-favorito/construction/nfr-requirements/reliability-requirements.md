# Reliability Requirements — Optimización de latencia

Deriva de inception **NFR2/NFR6** y de las reglas de fallback/degradación del
Functional Design (BR3.1, BR3.2). IDs `NFR2.x`.

## Postura: sin regresión de disponibilidad

El diseño garantiza que la respuesta **nunca empeora** respecto a hoy: ante
cualquier ausencia de datos sincronizados o fallo de la llamada de pujas, se
degrada con gracia a un comportamiento al menos tan bueno como el actual.

| ID | Requisito | Criterio pass/fail | Fuente |
|---|---|---|---|
| NFR2.1 | Fallback en sync-miss | Si el `SELECT` sincronizado devuelve 0 jugadores del campeonato, se sirve por la **ruta viva actual** (correcta aunque más lenta) + `log`; nunca se devuelve vacío por falta de caché | BR3.1, FR4.1/4.2 |
| NFR2.2 | Degradación de pujas | Si `POST /1/market/players` falla/timeout con catálogo disponible, se sirve el catálogo con campos de puja a cero + `logger.warning`; la respuesta entera **no falla** ni omite campos del contrato | BR3.2 |
| NFR2.3 | Coherencia tras operar | Tras un `bid`/`cancelbid` aceptado, la siguiente lectura de `market/today` refleja la operación (pujas leídas en vivo, sin caché que desincronizar) | BR4.2/BR5.1, FR2.2 |
| NFR2.4 | Sin pérdida ni corrupción de datos | La optimización sólo **lee**; no escribe ni migra. Sin riesgo de corrupción. El sync existente sigue siendo la única escritura | NFR6, O2 |
| NFR2.5 | Sin SLA/SLO formal nuevo | No se introduce un SLO con ventana/burn-rate (requeriría tooling de pago; no aplica a Fly.io+Neon free). La fiabilidad se expresa como "no regresión" + degradación con gracia | Q3-A |

## Modos de fallo y respuesta

| Fallo | Respuesta | Señal |
|---|---|---|
| Campeonato sin sincronizar (0 filas) | Ruta viva de fallback | `logger.info` sync-miss |
| Llamada de pujas falla (catálogo OK) | Catálogo con pujas a cero (DEGRADED) | `logger.warning` bid-call degraded |
| Neon no disponible | Mismo comportamiento que hoy para cualquier endpoint (error propagado) | log existente |
