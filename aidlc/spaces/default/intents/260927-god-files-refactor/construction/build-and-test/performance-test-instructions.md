# Instrucciones de Tests de Rendimiento — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, test strategy **Minimal**. Conversation language: Spanish.

## Aplicabilidad

**N/A en esta oleada.** No existen requisitos NFR de rendimiento nuevos para este intent (`requirements.md` no fija umbrales de latencia/throughput; NFR1–NFR4 son mantenibilidad, preservación de comportamiento, testabilidad y coste). El refactor es de estructura con comportamiento preservado: no cambia el perfil de rendimiento observable de los endpoints.

## Nota

La preservación de rendimiento es indirecta: los mismos SQL se ejecutan (movidos verbatim al adaptador, BR1.2), por lo que el número y forma de consultas a Neon no cambia. No hay carga sintética ni benchmark que ejecutar en esta oleada. Cualquier validación de rendimiento formal quedaría fuera de alcance (coste 0 €; sin tooling de carga de pago).
