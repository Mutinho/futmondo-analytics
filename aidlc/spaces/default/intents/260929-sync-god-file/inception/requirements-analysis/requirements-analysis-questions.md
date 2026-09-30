# Requirements Analysis — Preguntas de clarificación

Intent: `sync-god-file` (Oleada 3 god-files, FR13) · scope `refactor` · depth Minimal.

La petición es muy clara y los artefactos de reverse-engineering la confirman. Estas
preguntas resuelven las pocas decisiones que dan forma a los requisitos; el resto se
tomará como asunción documentada. Responde marcando la opción en el tag `[Answer]:`.

---

## Q1 — Preservación de la superficie pública (`DataSyncService` + 10 `sync_*` + `sync_all()`)

¿Cómo se preserva exactamente el contrato público durante la descomposición?

- A. `DataSyncService` se mantiene como **facade delgado** que delega cada `sync_*`
  en su módulo de aplicación de dominio; misma clase, mismas firmas, mismo import path.
- B. Además del facade, dejar **shims de re-export** en cualquier ruta histórica de
  import que hoy dependa de `data_sync_service` (como `analytics_service.py`/`assistant_service.py`).
- C. Sustituir la clase por funciones libres `sync_*` manteniendo las firmas (cambio de forma).
- D. Sin preferencia — usar el patrón exacto de las oleadas 1-2 (facade + shim si aplica).
- X. Other (please specify)

[Answer]: A (facade delgado que delega cada sync_* en su módulo de dominio; misma clase, firmas e import path; shim de re-export puntual solo donde un import histórico a data_sync_service lo exija)

---

## Q2 — Alcance de la extracción del SQL por dominio (frente al god-file `data_manager_v2.py`)

Cada `sync_*` persiste hoy vía `DataManagerV2` (SQL). El patrón objetivo mete el SQL
tras un `infrastructure/*_adapter.py`. ¿Hasta dónde llega esa extracción en este intent?

- A. Cada dominio extraído accede a datos **solo tras un adaptador de infraestructura**
  (Protocol/port + `*_adapter.py`), sin tocar ni engordar `data_manager_v2.py`; el SQL
  existente se envuelve, no se reescribe.
- B. Como A, pero además **retirar el SQL-en-router** de los endpoints de sync afectados.
- C. Extracción mínima: mover la lógica de dominio a su módulo pero permitir que llame a
  `DataManagerV2` directamente (adaptador diferido como deuda registrada).
- D. Sin preferencia — replicar exactamente lo que hicieron `analytics/`/`assistant/`.
- X. Other (please specify)

[Answer]: A (cada dominio accede a datos solo tras un adaptador de infraestructura Protocol/port + *_adapter.py, sin tocar ni engordar data_manager_v2.py; el SQL existente se envuelve, no se reescribe; el SQL-en-router queda como deuda registrada fuera de alcance)

---

## Q3 — Secuenciación de los 10 dominios y caracterización previa

`prizes` ya está extraído; 8 de 10 dominios no tienen caracterización directa. ¿Cómo se
secuencia el trabajo?

- A. **Characterization-first estricto por dominio**: congelar con tests el comportamiento
  observable de un dominio, extraerlo, verificar verde, y solo entonces pasar al siguiente
  (una unidad por dominio, incremental).
- B. Caracterizar todos los dominios primero (una oleada de tests), luego extraer todos.
- C. Empezar por los dominios de menor riesgo/menor acoplamiento y dejar los complejos
  (p. ej. `performance`, `rosters`) al final, siempre characterization-first.
- D. Sin preferencia — dejar la secuencia exacta para la etapa de diseño/planificación.
- X. Other (please specify)

[Answer]: A (characterization-first estricto por dominio: congelar comportamiento observable, extraer, verificar verde, y solo entonces el siguiente; una unidad por dominio, incremental; el orden concreto de dominios se decide en diseño/planificación)

---

## Q4 — Comportamiento observable a congelar (equivalencia funcional)

El refactor NO debe cambiar comportamiento. ¿Qué nivel de equivalencia se exige?

- A. **Equivalencia funcional estricta**: mismos payloads de retorno por `sync_*`, mismo
  orden en `sync_all()` (players primero por FK), mismo manejo de errores tipados
  (`Integration*Error`), mismo throttling, misma escritura atómica set-replacement.
- B. Como A, pero se permite **mejorar el manejo de errores** de los `except Exception →
  return {"status":"error"}` genéricos hacia el patrón recuperable/fatal ya afirmado.
- C. Equivalencia de resultados en BD, permitiendo pequeñas diferencias de forma en los
  dicts de progreso.
- D. Sin preferencia — equivalencia estricta (A) por defecto en un refactor.
- X. Other (please specify)

[Answer]: A (equivalencia funcional estricta: mismos payloads de retorno por sync_*, mismo orden en sync_all() players-primero-por-FK, mismo manejo de errores tipados Integration*Error, mismo throttling, misma escritura atómica set-replacement; la mejora de los except Exception genéricos queda como deuda registrada fuera de alcance)

---

## Consolidated Summary Confirmation

Resumen de las decisiones antes de generar el artefacto de requisitos:

- **Superficie pública (Q1)**: `DataSyncService` se mantiene como facade delgado que delega cada `sync_*` en su módulo de aplicación de dominio; misma clase, mismas firmas, mismo import path. Shim de re-export puntual solo donde un import histórico a `data_sync_service` lo exija.
- **Alcance de extracción de SQL (Q2)**: cada dominio accede a datos solo tras un adaptador de infraestructura (Protocol/port + `*_adapter.py`), envolviendo el SQL existente sin tocar ni engordar `data_manager_v2.py`. El SQL-en-router queda como deuda registrada, fuera de alcance.
- **Secuenciación (Q3)**: characterization-first estricto por dominio (congelar comportamiento observable → extraer → verde → siguiente), una unidad por dominio, incremental. El orden concreto de dominios se decide en diseño/planificación.
- **Equivalencia funcional (Q4)**: equivalencia estricta — mismos payloads por `sync_*`, mismo orden en `sync_all()` (players primero por FK), mismo manejo de errores tipados `Integration*Error`, mismo throttling, misma escritura atómica set-replacement. La mejora de los `except Exception → return {"status":"error"}` genéricos queda como deuda registrada, fuera de alcance.
- **Restricciones duras (de la petición y reglas afirmadas)**: coste 0 €, sin ampliar los god-files, sin reformateo masivo (`ruff format`), sin relajar el piso `--cov-fail-under=27` (solo sube por trinquete). Idioma: identificadores/docstrings en inglés, texto de usuario/commits en castellano.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
