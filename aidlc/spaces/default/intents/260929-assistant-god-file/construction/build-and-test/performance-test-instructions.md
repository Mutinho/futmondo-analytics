# Performance Test Instructions — N/A en este intent

Intent `260929-assistant-god-file`, scope `refactor`, **Test Strategy: Minimal**.

## Aplicabilidad

**No aplican tests de rendimiento.** El inventario de requisitos (`requirements.md`) no define
ningún NFR de rendimiento (latencia, throughput, escalabilidad) para este intent: es un refactor
de deuda técnica **sin cambio de comportamiento observable** ni objetivo de rendimiento. La
estrategia Minimal no genera instrucciones de performance, y no hay objetivo medible de
rendimiento que verificar ni diferir a `performance-validation`.

## Justificación y coste

- El refactor mueve código entre módulos preservando la lógica; no introduce rutas calientes
  nuevas ni cambia la complejidad algorítmica de `ask()`.
- Cualquier medición de carga formal (k6/Locust, percentiles p95/p99) exigiría un entorno
  production-like y, en su forma gestionada, gasto recurrente — descartado por el mandato de
  **coste 0 €**. Queda como deuda no planificada, fuera de alcance.
