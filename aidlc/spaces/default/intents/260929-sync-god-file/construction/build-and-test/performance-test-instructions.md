# Performance Test Instructions — NO APLICA (estrategia Minimal, sin NFR de rendimiento)

## Decisión

Estrategia **Minimal** y **sin requisitos NFR de rendimiento** en este intent
(refactor de estructura, sin cambio de comportamiento ni de rendimiento
observable). No se generan tests de rendimiento.

## Justificación

- El objetivo es equivalencia funcional estricta; el rendimiento observable no
  cambia (mismo SQL envuelto, misma ingesta, mismo throttling).
- Coste 0 €: no se introducen herramientas de carga ni entornos de rendimiento.
- Cualquier validación de rendimiento formal (con burn-rate/SLO) queda fuera de
  alcance y, de necesitarse, correspondería a `performance-validation`.
