# Integration Test Instructions — NO APLICA (estrategia Minimal)

## Decisión

La estrategia de test activa es **Minimal** (scope `refactor`). Según la etapa
Build and Test, la estrategia Minimal **no genera ficheros de instrucciones de
test adicionales**: los tests unitarios/caracterización se cubren por dominio en
Code Generation. No se crean tests de integración nuevos en este intent.

## Alcance y justificación

- El refactor no cambia comportamiento observable (equivalencia estricta), así que
  la red de seguridad es la **caracterización por dominio** que congela el payload
  y el modo de fallo, no nuevos tests de integración.
- La suite existente (incluidos tests de integración/degradado ya presentes:
  `test_sync_degraded_steps.py`, `test_sync_integration_failure_effect.py`) se
  mantiene **verde** (scope floor `refactor`).
- Si un dominio futuro lo requiriese, se añadiría de forma dirigida; hoy no aplica.
