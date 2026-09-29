# Integration Test Instructions — N/A en esta estrategia

Intent `260929-assistant-god-file`, scope `refactor`, **Test Strategy: Minimal**.

## Aplicabilidad

**No se generan tests de integración nuevos en este intent.** La estrategia Minimal del stage
Build and Test no añade instrucciones de integración: los seams extraídos se cubren por sus
tests de caracterización unit-scoped (Code Generation), y el objetivo del refactor es
**paridad de comportamiento observable**, no funcionalidad nueva que cruce fronteras.

La interacción cross-seam relevante (orquestación `ask()` → guardrails → cuota → factual →
contexto → LLM) se ejercita end-to-end en `backend/tests/test_assistant_facade.py` con dobles
de los `Protocol`s inyectados por constructor, que congela el orden observable y las rutas de
degradación. Eso cumple el nivel Minimal sin un árbol de integración separado.

## Cobertura por la suite existente

- La suite completa (`pytest --cov=app -q`) permanece **verde** tras el refactor (244 passed,
  3 xfailed preexistentes), demostrando que los consumidores reales (endpoints `assistant.py`,
  `market.py`) siguen integrándose con el paquete vía el shim de re-export sin cambios (NFR1.3).
- Cualquier test de integración de más nivel (BD real, red) queda **fuera de alcance** por scope
  y por el mandato de coste 0 € / fakes in-memory.
