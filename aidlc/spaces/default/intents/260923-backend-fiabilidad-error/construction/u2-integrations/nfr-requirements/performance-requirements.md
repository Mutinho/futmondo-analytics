# Performance Requirements — u2-integrations (Integraciones)

U2 es una intervención de fiabilidad sobre la ruta de integración/sync; **no
introduce objetivos de rendimiento interactivos nuevos** ni cambia la topología.
El sync es un proceso batch (crons Fly one-shot + bajo demanda), no un endpoint
sensible a latencia p95/p99. El único requisito de rendimiento nuevo es el
**timeout acotado** por petición de integración (Q2), que es tanto de rendimiento
como de fiabilidad.

Consume: `functional-spec.md`, `requirements.md`, `technology-stack.md`.

## Requisitos de rendimiento (derivados)

| ID | Requisito | Fuente | Verificación |
|----|-----------|--------|--------------|
| NFR-perf.1 | **Timeout acotado por petición**: cada llamada de integración (Futmondo vía `requests`, Sofascore vía `curl_cffi`) tiene un timeout explícito (connect + read); ninguna espera es ilimitada. El valor concreto se fija en nfr-design/code-generation. | Q2, FR4.4 | Spec: una petición que excede el timeout lanza `IntegrationTimeoutError` (recuperable) |
| NFR-perf.2 | El endurecimiento de errores **no degrada** el rendimiento del sync respecto a la línea base (añadir `try/except` tipado y logging estructurado es coste despreciable). | NFR4 | Suite existente en verde; sin regresión perceptible |

## Sin cambio (heredado)

- **Throttle preventivo de Sofascore (~750 ms entre peticiones)**: se mantiene; U2 no lo modifica. Evita el baneo 403.
- **Pool de conexiones a Neon** (`ThreadedConnectionPool` 5–20, retry x3 en `db_connection`): **sin cambio**.
- **Latencia interactiva de la API** (`/api/v1/*`): fuera del alcance de U2; no se toca.
- **Sin objetivos p50/p95/p99**: no aplican a un proceso batch de sync; no se inventan.

## Assumptions & Open Questions

None.
