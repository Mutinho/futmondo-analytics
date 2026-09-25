# Tech Stack Decisions — u2-integrations (Integraciones)

U2 **no introduce tecnología nueva**. El stack está fijado y este intent es
aditivo sobre él: la stdlib de Python basta para todo lo que U2 necesita
(excepciones tipadas, `try/except`, `logging` estructurado, timeout de los
clientes HTTP ya presentes). Cualquier dependencia nueva sería OSS y fijada a
versión exacta — pero no se prevé ninguna.

Consume: `technology-stack.md` (CodeKB), `functional-spec.md`, `requirements.md`.

## Decisiones de tecnología (todas heredadas / sin alta)

| Decisión | Elección | Rationale |
|----------|----------|-----------|
| Lenguaje/runtime backend | Python 3.12 (fijado) | Stack existente; `libsql-experimental` sólo compila en 3.12. |
| Módulo de errores de integración | `integration_errors` (código propio, stdlib `Exception`) | Módulo estrecho y testeable, raíz común `IntegrationError`; sin dependencia externa (práctica afirmada Q3). |
| Logging estructurado | `logging` de la stdlib, formato clave=valor | Coste 0 €, sin dependencia nueva; grep-able en `fly logs` (Q1, NFR1.3). |
| Cliente HTTP Futmondo | `requests` (`>=2.31.0`, ya presente) | Existente; sus `Timeout`/`RequestException` se tipan en vez de tragarse a `None`. Se usa su parámetro `timeout` (NFR-perf.1). |
| Cliente HTTP Sofascore | `curl_cffi` (`>=0.16.0`, ya presente) | Existente (fingerprint TLS, impersonate, throttle 750 ms); se alinea `SofascoreIPBanError` a la raíz común. Timeout vía su API. |
| Test tooling | `pytest` + `pytest-cov` + fakes en memoria (`conftest.py`) | Existente; caracterización sin red/DB real/credenciales (coste 0 €). |
| Dependencias nuevas | **Ninguna** | La stdlib basta; NUNCA introducir dependencias de pago (práctica afirmada). |

## Restricciones de stack (fijadas)

- **Coste 0 €**: sólo tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free); ninguna dependencia con gasto recurrente.
- **No ampliar los god-files** (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router; el código nuevo vive tras una capa/función estrecha testeable.
- **Sin cambios de infraestructura** (topología Fly.io, Neon) en este intent.

## Assumptions & Open Questions

None.
