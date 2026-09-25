# Functional Design — U1 `u1-error-layer` (preguntas)

Unidad: **U1 capa de errores** (FR3.2 + FR4.1 + NFR3). `kind: library`.

## Sources

- [desc] Initial description: "FR3.2 (manejo de errores, recuperable/fatal; primera oleada arranque/migraciones/db_connection) + FR4.1 (modulo integration_errors con raiz IntegrationError). NO ampliar god-files; codigo nuevo tras capa/funcion estrecha testeable. Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/team.md#Code Style`: "las excepciones de integración viven en un módulo estrecho y testeable `integration_errors` con una raíz común `IntegrationError`; mensajes de excepción en INGLÉS."
- [memory:M2] `aidlc/spaces/default/memory/project.md#Forbidden`: "NEVER incluir el password ni el token Futmondo del usuario en el mensaje, el `repr` ni el `exc_info` de una excepción de integración (NFR3)."

---

## Q1. Estructura de la jerarquía `IntegrationError`

¿Qué subtipos concretos define U1 bajo la raíz `IntegrationError`?

- A. **Tres subtipos por modo de fallo**: `IntegrationBanError` (baneo, fatal), `IntegrationTimeoutError` (timeout, recuperable), `IntegrationUnparseableError` (respuesta heterogénea/no parseable, recuperable). La raíz `IntegrationError` es la que capturan los consumidores. El `SofascoreIPBanError` existente pasa a heredar de `IntegrationBanError` (o de la raíz) preservando su comportamiento FR2.1.
- B. Otra estructura (indícala en Other).
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Tres subtipos por modo de fallo: IntegrationBanError (baneo, fatal), IntegrationTimeoutError (timeout, recuperable), IntegrationUnparseableError (no parseable, recuperable). La raíz IntegrationError es la que capturan los consumidores. SofascoreIPBanError pasa a heredar de IntegrationBanError preservando FR2.1.

## Q2. Atributos de contexto que lleva cada excepción

- A. **Contexto no sensible**: `failure_mode` (enum), `status` (HTTP opcional), `endpoint` (ruta no sensible opcional). NUNCA password/token en mensaje/`repr`/`exc_info` (NFR3) [memory:M2]. Mensajes en inglés [memory:M1].
- B. Otra cosa (indícala en Other).
- X. Other (please specify)

[Answer]: A. Contexto no sensible: failure_mode (enum), status (HTTP opcional), endpoint (ruta no sensible opcional). NUNCA password/token en mensaje/repr/exc_info (NFR3). Mensajes en inglés.

## Q3. Clasificación recuperable/fatal — regla por subtipo

- A. **El subtipo codifica la clasificación**: baneo total = fatal; timeout / no-parseable = recuperable. Un fallo en un punto de escritura que ya hizo commit previo (p. ej. el `DELETE ... NOT IN` de `team_prizes`) = fatal (no corromper datos). El consumidor (ruta de sync) enruta: recuperable→`DEGRADED`; fatal→propaga.
- B. Otra cosa.
- X. Other (please specify)

[Answer]: A. El subtipo codifica la clasificación: baneo total = fatal; timeout/no-parseable = recuperable; fallo en punto de escritura tras commit previo (DELETE ... NOT IN de team_prizes) = fatal. El consumidor enruta: recuperable→DEGRADED; fatal→propaga.

## Q4. Endurecimiento de capturas de arranque/migraciones/`db_connection.py`

RE encontró que arranque (`main.py`) degrada a warning y las migraciones loguean (no hay `except: pass` ahí); `db_connection.py` ya hace rollback+raise en transacciones pero tiene capturas amplias en init.

- A. **Reclasificar, no reescribir**: en cada captura amplia de la primera oleada, distinguir recuperable (loguear/degradar, seguir) de fatal (propagar/abortar limpio), characterization-first (congelar el comportamiento actual con un spec antes de tocar). Sin ampliar estructura ni cambiar la semántica transaccional correcta ya presente.
- B. Otra cosa.
- X. Other (please specify)

[Answer]: A. Reclasificar, no reescribir: distinguir recuperable de fatal en cada captura amplia de la primera oleada, characterization-first (congelar comportamiento actual antes de tocar), sin ampliar estructura ni cambiar la semántica transaccional correcta ya presente.

## Consolidated Summary Confirmation

Resumen del diseño funcional de U1 (antes de fijar los artefactos):

- **Jerarquía (Q1=A)**: raíz `IntegrationError` + `IntegrationBanError` (fatal), `IntegrationTimeoutError` (recuperable), `IntegrationUnparseableError` (recuperable). `SofascoreIPBanError` hereda de `IntegrationBanError` (FR2.1 preservado).
- **Contexto (Q2=A)**: `failure_mode`, `status?`, `endpoint?`; sin secretos (NFR3); mensajes en inglés.
- **Clasificación (Q3=A)**: el subtipo codifica recuperable/fatal; fallo en punto de escritura tras commit = fatal; el consumidor enruta.
- **Endurecimiento (Q4=A)**: reclasificar recuperable/fatal en arranque/migraciones/`db_connection.py`, characterization-first, sin reescribir ni cambiar la semántica transaccional correcta.
- **Artefactos**: entities.md (jerarquía de excepciones como modelo), rules.md (reglas BR de clasificación/NFR3), functional-spec.md (flujo de clasificación + diagrama), traceability.json.

[Answer]: Looks correct
