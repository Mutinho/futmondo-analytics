# Integration Test Instructions — NO APLICA (Minimal / refactor)

## Decisión

El scope es **refactor** → estrategia **Minimal**. Por diseño, Build and Test
**no genera** ficheros de test de integración nuevos en Minimal: los unit tests
los cubre Code Generation por módulo. Este fichero existe para dejar la decisión
explícita y trazable.

## Por qué no aplica aquí

- Es una descomposición de equivalencia: **no hay comportamiento nuevo** que
  integrar. Los contratos entre consumidores y la fachada `DataManagerV2` se
  preservan **byte a byte** (BR1.1/BR4.1), así que la "integración"
  consumidor↔fachada ya está cubierta por la suite existente que corre verde.
- La integración real módulo-extraído ↔ fachada ↔ consumidores se ejerce a
  través de los **57 métodos públicos** que la suite completa invoca; los 68
  tests de caracterización nuevos aseveran el efecto observable sobre los fakes
  in-memory, y las suites de `sync/*`, `analytics`, `prizes`, `auth`, `finance`
  existentes siguen pasando (414 passed) — esa es la verificación de integración
  disponible a coste 0 sin red/BD real (NFR6).

## Qué se ejecuta en su lugar

El gate de integración efectivo es la **suite completa `backend/tests/`**
(ver `build-instructions.md` y `test-results.md`): equivalencia estricta +
piso de cobertura. No se añade árbol de integración paralelo.
