# Functional Design — Preguntas · u2-integrations (Integraciones)

Fase Construction, profundidad Standard: las preguntas son excepcionales. El
diseño de U2 ya está muy fijado por `requirements.md` (FR4.2–FR4.5, NFR1/NFR2),
`components.md` (SofascoreClient, FutmondoClient, SyncService, SyncStepStatus,
DbConnection) y `contract-summary.md` (jerarquía `IntegrationError`, contratos
de fallo de Sofascore/Futmondo). Estas preguntas cierran sólo los huecos
genuinos que quedaban explícitamente diferidos a functional-design.

---

## Q1 — Nombres exactos de los subtipos de `IntegrationError`

El módulo `IntegrationErrors` (U1) declara la raíz común `IntegrationError` y
subtipos por modo de fallo; el contrato acordó la **forma** pero dejó los
**nombres exactos** para functional-design (FR4.1; open question de
`contract-summary.md`). ¿Qué juego de nombres fijamos para que U2 los lance y
`SyncService` los capture?

- A. `IntegrationBanError` (baneo/403, fatal), `IntegrationTimeoutError`
  (timeout, recuperable), `IntegrationUnparseableError` (respuesta
  heterogénea/no parseable, recuperable) — nombres genéricos bajo la raíz común;
  `SofascoreIPBanError` existente se re-parenta para heredar de
  `IntegrationBanError` (o directamente de `IntegrationError`).
- B. Nombres con prefijo por proveedor (`FutmondoTimeoutError`,
  `SofascoreBanError`, …) para distinguir el origen en el tipo.
- C. Un único subtipo por clasificación (`RecoverableIntegrationError` /
  `FatalIntegrationError`) y el modo de fallo sólo como atributo `failure_mode`.
- X. Other (please specify)

[Answer]: A

---

## Q2 — Ubicación del `SofascoreIPBanError` existente en la jerarquía

`SofascoreClient` ya lanza y propaga `SofascoreIPBanError` ante 403 (FR2.1, ya
presente). Para alinearlo a la raíz común sin romper a sus captores actuales:

- A. Re-parentar `SofascoreIPBanError` para que herede del subtipo de baneo de
  `IntegrationError` (mantiene el nombre y el `except SofascoreIPBanError`
  existente sigue funcionando, y además queda cubierto por `except
  IntegrationError`).
- B. Sustituir `SofascoreIPBanError` por el subtipo genérico de baneo y adaptar
  sus captores.
- X. Other (please specify)

[Answer]: A

---

## Q3 — Traducción recuperable/fatal en el punto de captura de `SyncService`

`SyncService` es el punto donde la excepción tipada se traduce en acción
(recuperable → `DEGRADED` vía `SyncStepStatus` y continúa; fatal → aborta limpio
sin datos a medias). ¿Cómo decide la clasificación en el `except`?

- A. Captura por la **raíz** `IntegrationError` y decide leyendo un atributo/una
  clasificación asociada al tipo (p. ej. `failure_mode` o una marca
  recuperable/fatal en la propia clase); un único bloque de traducción.
- B. Dos ramas `except` explícitas: primero los subtipos fatales
  (`except <Fatal>: propagar/abortar`), luego los recuperables
  (`except <Recoverable>: DEGRADED + continuar`), antes del `except Exception`.
- X. Other (please specify)

[Answer]: B

---

## Q4 — Alcance del punto de no-corrupción `team_prizes` en U2

NFR2 exige que ante un fallo fatal en el punto de escritura de `team_prizes`
(`DELETE ... NOT IN (...)` + repoblado) la tabla quede todo-o-nada, usando el
patrón de reemplazo transaccional atómico ya caracterizado (FR2). En el diseño
funcional de U2:

- A. Especificar el workflow de reemplazo `team_prizes` como transacción única
  (borrado + repoblado en la misma transacción; fallo → rollback completo, sin
  estado mixto) y aseverar el efecto con un spec que fuerza el fallo — endurecer
  el punto existente, sin ampliar el god-file.
- B. Dejar `team_prizes` fuera del diseño de U2 (tratarlo sólo en
  code-generation) y limitar functional-design a clientes + traducción de
  estado.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
