# Contract Design — Preguntas

Intent: **Fiabilidad backend — manejo de errores (FR3.2) + contratos de integración (FR4)**

## Sources

- [desc] Initial description: "FR4 - robustez de integraciones externas: documentar contratos y modos de fallo esperados de Sofascore (API no oficial via curl_cffi, baneo de IP) y Futmondo (endpoints heterogeneos); ante baneo/entrada fallida el sistema lo detecta, no corrompe datos y lo refleja en el estado. NO ampliar god-files; codigo nuevo tras capa/funcion estrecha testeable. Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/team.md#Code Style`: "excepción tipada por modo de fallo, propagada, con `except <Typed>: raise` antes del `except Exception`; nunca `return None` silencioso."

---

## Q1. Contrato de la frontera inter-unidad U1↔U2 (`IntegrationErrors`)

U2 (integraciones) consume la jerarquía de excepciones que define U1. ¿Cómo formalizamos ese contrato de código compartido?

- A. **Contrato de código (shared schema/módulo)**: la jerarquía `IntegrationError` + subtipos por modo de fallo es el contrato. Se especifica: la raíz, los subtipos (baneo, timeout, no-parseable), qué contexto no sensible llevan (status, endpoint, modo de fallo) y la garantía NFR3 (sin secretos). Los clientes (U2) lanzan estos tipos; el consumidor (ruta de sync) los captura.
- B. Otra forma (indícalo en Other).
- X. Other (please specify)

[Answer]: A. Contrato de código (shared schema/módulo): la jerarquía IntegrationError + subtipos por modo de fallo es el contrato (raíz, subtipos baneo/timeout/no-parseable, contexto no sensible que llevan, garantía NFR3). U2 lanza; la ruta de sync captura.

## Q2. Contratos externos — ¿qué documentamos de Sofascore y Futmondo (FR4.5)?

- A. **Contrato de fallo esperado por integración**: para Sofascore (baneo 403 → excepción tipada; rate-limiting preventivo) y Futmondo (login, getters heterogéneos; timeout/no-parseable → excepción tipada), documentar qué se espera, cómo falla, y cómo se detecta/clasifica (recuperable/fatal). No es un contrato que nosotros controlemos (APIs de terceros), sino el contrato de fallo que asumimos.
- B. Otra cosa (indícalo en Other).
- X. Other (please specify)

[Answer]: A. Contrato de fallo esperado por integración: Sofascore (baneo 403 → excepción tipada; rate-limiting preventivo) y Futmondo (login, getters heterogéneos; timeout/no-parseable → excepción tipada); qué se espera, cómo falla, cómo se detecta/clasifica. Contrato de fallo asumido de APIs de terceros.

## Q3. Comportamiento de error/timeout en cada frontera

- A. **Según la taxonomía afirmada**: timeout/respuesta no parseable = recuperable (degradar y continuar, sin retry en este intent); baneo total o fallo en punto de escritura = fatal (abortar limpio, sin datos a medias). Sin reintentos (Q2 de requirements). [memory:M1]
- B. Otra cosa (indícalo en Other).
- X. Other (please specify)

[Answer]: A. Según la taxonomía afirmada: timeout/respuesta no parseable = recuperable (degradar y continuar, sin retry); baneo total o fallo en punto de escritura = fatal (abortar limpio, sin datos a medias).

## Q4. Versionado / cambios rompedores del contrato interno

- A. **Aditivo y sin versionado formal**: al ser un contrato de código intra-proceso (mismo despliegue), los cambios son aditivos (nuevos subtipos de excepción heredan de la raíz; los consumidores capturan la raíz). No hace falta política de versionado formal.
- B. Otra cosa (indícalo en Other).
- X. Other (please specify)

[Answer]: A. Aditivo y sin versionado formal: contrato de código intra-proceso; cambios aditivos (nuevos subtipos heredan de la raíz; los consumidores capturan la raíz).

## Consolidated Summary Confirmation

Resumen de contratos (antes de fijar el artefacto):

- **Frontera inter-unidad U1↔U2 (Q1=A)**: contrato de código compartido = la jerarquía `IntegrationError` (raíz + subtipos por modo de fallo con contexto no sensible; garantía NFR3 sin secretos). U2 lanza, la ruta de sync captura.
- **Contratos externos (Q2=A)**: contrato de fallo esperado de Sofascore (baneo 403, rate-limiting) y Futmondo (login/getters heterogéneos, timeout/no-parseable), documentado como el fallo que asumimos de terceros.
- **Error/timeout (Q3=A)**: timeout/no-parseable = recuperable (degradar, sin retry); baneo total / fallo en escritura = fatal (abortar limpio).
- **Versionado (Q4=A)**: aditivo, sin versionado formal (contrato de código intra-proceso).
- **Artefacto**: contract-summary.md (tabla de contratos + specs fenced shared-schema).

[Answer]: Looks correct
