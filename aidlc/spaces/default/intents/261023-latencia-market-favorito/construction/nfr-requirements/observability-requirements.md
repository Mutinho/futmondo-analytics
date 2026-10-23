# Observability Requirements — Optimización de latencia

Deriva de las reglas de fallback/degradación (BR3.1, BR3.2) y de NFR5 (sin
credenciales). IDs `NFR_OBS.x`. Alineado con el stack real (Fly.io + Neon,
coste 0): sólo herramientas gratuitas (`logger` estructurado + `fly logs`).

| ID | Requisito | Criterio pass/fail | Fuente |
|---|---|---|---|
| NFR_OBS.1 | Log de sync-miss | Cuando se activa el fallback a la ruta viva por 0 filas sincronizadas, se emite un `logger.info` con `championship_id` y el endpoint; permite detectar campeonatos sin sync | BR3.1, Q4-A |
| NFR_OBS.2 | Log de degradación de pujas | Cuando `POST /1/market/players` falla con catálogo disponible, se emite un `logger.warning` con `championship_id`; **el mensaje, el `repr` y el `exc_info` de ese log NO incluyen el token/password Futmondo** (la llamada degradada va justo sobre la llamada con credencial, así que se verifica explícitamente aquí, no solo por NFR_OBS.3) | BR3.2, Q4-A, NFR5 |
| NFR_OBS.3 | Sin credenciales en logs | Ningún log (incl. los de error) incluye password/token Futmondo; sólo contexto no sensible | NFR5, regla afirmada |
| NFR_OBS.4 | (Opcional) duración de lectura | Log opcional de la duración de la lectura desde sync, para verificar el objetivo de NFR1 en producción vía `fly logs` | Q4-A |
| NFR_OBS.5 | Sin tooling de pago | NO se añaden métricas/tracing distribuido (Prometheus/OTel) ni dashboards de pago; fuera de coste 0 y de alcance | Q4-A, NFR3 |

## Verificación

- Los logs se observan con `fly logs` (herramienta gratuita del stack).
- No hay SLI/SLO formal nuevo (ver reliability NFR2.5): la observabilidad es
  diagnóstica (detectar fallback/degradación), no de alerting con burn-rate.
