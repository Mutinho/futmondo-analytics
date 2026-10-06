# Performance Test Instructions — calculadora-mejora

## Estado

**NO-APLICA** en este intent. No hay NFR de rendimiento asociados a la mejora
del toggle; el cambio es una reorganización de cálculo con `computed()` signals
en el cliente, sin impacto medible de rendimiento. Estrategia Minimal, scope
refactor: no se generan pruebas de carga ni benchmarks.

## Sources

- `requirements.md` (sin NFR de rendimiento para esta unidad).
- `aidlc-state.md` → `Test Strategy: Minimal`.

## Assumptions & Open Questions

None.
