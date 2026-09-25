# Performance Test Instructions — Construction (FR3.2 + FR4)

## Aplicabilidad

Estrategia **Standard** + intent de fiabilidad backend sobre proceso **batch**
(sync por crons one-shot), no interactivo. **No se generan tests de rendimiento
formales** (load/latencia p95/p99) en este intent: no hay objetivo de rendimiento
interactivo nuevo (ver `nfr-design/performance-design.md`).

## Único requisito de rendimiento (verificado por diseño, no por load test)

- **Timeout acotado por petición** (NFR-perf.1): connect ~5s / read ~30s. No
  requiere un load test; su efecto (timeout → `IntegrationTimeoutError`
  recuperable) se cubre en `tests/test_futmondo_client_typed_failures.py`.

## NO-APLICA (adaptación coste 0 € / Fly.io)

- Load/stress/soak con herramientas gestionadas de pago → **NO-APLICA**.
- SLO formal con burn-rate → diferido (ver observability-design).
