# Domain Design — Preguntas de aclaración

Intent: **Fiabilidad backend — manejo de errores (FR3.2) + contratos de integración (FR4)**

## Sources

- [desc] Initial description: "Intent 1 del plan de mejoras (docs/BACKLOG-plan-intents.md), derivado del intent de analisis 260911-analisis-mejoras: FR3.2 + FR4. FR3.2 - reducir los except Exception/bare-except del backend, distinguiendo error recuperable de fatal; FR4 - robustez de integraciones externas: contratos y modos de fallo de Sofascore y Futmondo; ante baneo/entrada fallida el sistema lo detecta, no corrompe datos y lo refleja en el estado. Scope feature, brownfield. NO ampliar god-files; codigo nuevo tras capa/funcion estrecha testeable. Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/team.md#Code Style`: "las excepciones de integración viven en un módulo estrecho y testeable `integration_errors` con una raíz común `IntegrationError`."
- [memory:M2] `aidlc/spaces/default/memory/project.md#Forbidden`: "NEVER ampliar los god-files existentes (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router."

---

## Q1. Límite del nuevo componente `integration_errors`

FR4.1 afirma un módulo `integration_errors` con raíz `IntegrationError`. ¿Cuál es su responsabilidad y límite como bloque lógico?

- A. **Solo la jerarquía de excepciones tipadas** (raíz `IntegrationError` + subtipos por modo de fallo: baneo, timeout, respuesta no parseable). Un módulo de definiciones puro, sin lógica de decisión; los clientes las lanzan y la ruta de sync las clasifica.
- B. **Jerarquía + helper de clasificación**: además de las excepciones, incluye una función/tipo que mapea excepción → recuperable/fatal, para que la ruta de sync no repita la lógica.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Solo la jerarquía de excepciones tipadas (raíz IntegrationError + subtipos por modo de fallo: baneo, timeout, respuesta no parseable). Módulo de definiciones puro, sin lógica de decisión; los clientes las lanzan y la ruta de sync las clasifica.

## Q2. Dónde vive la clasificación recuperable→acción (degradar vs abortar)

La taxonomía recuperable/fatal (FR3.2.1) necesita traducirse en acción. ¿Dónde vive esa traducción?

- A. **En el punto de captura de la ruta de sync**, reusando `sync_step_status.record_degraded_step` para recuperable y dejando propagar para fatal. Sin componente nuevo: es comportamiento del componente de sync existente (sin ampliarlo estructuralmente, solo endurecer capturas).
- B. **En un helper nuevo y estrecho** (p. ej. dentro de `integration_errors` o adyacente) que reciba la excepción y decida degradar/abortar, invocado desde la ruta de sync.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. En el punto de captura de la ruta de sync, reusando sync_step_status.record_degraded_step para recuperable y dejando propagar para fatal. Sin componente nuevo: es comportamiento del componente de sync existente (solo endurecer capturas, sin ampliarlo estructuralmente).

## Q3. ¿Componente separado para el "inventario de llamadores" de `_make_request`?

FR4.3 pide un inventario verificable de llamadores como entregable previo. ¿Es un artefacto de diseño/documento, o un componente de código?

- A. **Artefacto de diseño/documento** (no un componente de código): el inventario es una tabla/documento que guía la migración; no crea un bloque lógico nuevo.
- B. Otra cosa (indícalo en Other).
- X. Other (please specify)

[Answer]: A. Artefacto de diseño/documento (no un componente de código): el inventario es una tabla/documento que guía la migración; no crea un bloque lógico nuevo.

## Consolidated Summary Confirmation

Resumen del diseño de dominio (antes de fijar los artefactos):

- **Componente nuevo (Q1=A)**: `IntegrationErrors` — módulo de definiciones puro: raíz `IntegrationError` + subtipos por modo de fallo (baneo, timeout, respuesta no parseable). Sin lógica de decisión, sin dependencias.
- **Clasificación recuperable→acción (Q2=A)**: vive en el punto de captura de la ruta de sync (componente de sync existente, solo endureciendo capturas), reusando `sync_step_status.record_degraded_step` (recuperable) y dejando propagar (fatal). Sin componente nuevo para esto.
- **Inventario de llamadores (Q3=A)**: artefacto de diseño/documento, no un componente de código.
- **Componentes existentes modificados** (no ampliados estructuralmente): `SofascoreClient`, `FutmondoClient` (lanzan tipadas), la ruta de sync (`SyncService`, captura/clasifica), `DbConnection` (endurece capturas), reusa `SyncStepStatus`.
- **Decomposición única viable** → sin bloque de opciones múltiples.
- **Artefactos**: components.md (catálogo YAML + diagrama + tablas), decisions.md (ADRs), traceability.json (FR → componente).

[Answer]: Looks correct
