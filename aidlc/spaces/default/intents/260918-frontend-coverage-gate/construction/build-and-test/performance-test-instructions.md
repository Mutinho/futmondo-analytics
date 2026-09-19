# Performance Test Instructions — frontend-coverage-gate

**No aplica a este intent.** El análisis de requisitos (`requirements.md`) no define ningún NFR de rendimiento (carga, latencia, benchmarks). El intent es una intervención de tooling de cobertura + specs; no cambia rutas calientes de runtime ni añade endpoints.

- **NFR aplicables**: NFR1 (coste 0 €), NFR2 (sin reescrituras), NFR3 (suite en verde), NFR4 (determinismo de tests), NFR5 (reproducibilidad de tooling). Ninguno es de rendimiento.
- **Coste del gate de test**: la suite frontend corre en ~2 s (62 tests) en `node:22.22.3`; no hay riesgo de tiempo de CI. No se define umbral de rendimiento bloqueante (coste 0 €, sin herramienta de benchmark de pago).

No se generan pruebas de rendimiento. Si en el futuro se define un NFR de rendimiento, se añadirá aquí.
