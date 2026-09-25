# Feasibility & Constraints — Preguntas de aclaración

Intent: **Fiabilidad backend — manejo de errores (FR3.2) + contratos de integración (FR4)**

## Sources

- [desc] Initial description: "Intent 1 del plan de mejoras (docs/BACKLOG-plan-intents.md), derivado del intent de analisis 260911-analisis-mejoras: FR3.2 + FR4. FR3.2 - reducir los except Exception/bare-except (159+6) del backend, empezando por los except: pass de arranque y migraciones, distinguiendo error recuperable de fatal; continuacion natural de FR3.1 (ya hecho). FR4 - robustez de integraciones externas: documentar contratos y modos de fallo esperados de Sofascore (API no oficial via curl_cffi, baneo de IP) y Futmondo (endpoints heterogeneos); ante baneo/entrada fallida el sistema lo detecta, no corrompe datos (enlaza con FR2 ya hecho) y lo refleja en el estado. Scope feature, brownfield futmondo-analytics. Restricciones: mantener stack actual (Angular + FastAPI + Neon PostgreSQL + Fly.io), sin reescrituras grandes, NO ampliar los god-files (data_sync_service.py, data_manager_v2.py) ni el patron SQL-en-router - el codigo nuevo va tras una capa/funcion estrecha testeable; test-after con specs significativas; gate de CI bloqueante (gitleaks + pytest + ng test) antes de merge a main; coste 0 EUR (tiers gratuitos). Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/project.md#Forbidden`: "NEVER ampliar los god-files existentes (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router."
- [memory:M2] `aidlc/spaces/default/memory/project.md#Corrections`: "ALWAYS mantener el proyecto a coste 0€: descartar toda mejora o dependencia con gasto recurrente; solo proponer soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free) (learned 2026-09-11)"
- [memory:M3] `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md#Contexto del stack real`: "Hosting: Fly.io (región `cdg`) — backend `futmondo-api` (puerto 8000, check `/health`)... BD: Neon PostgreSQL (Frankfurt, tier free)."

---

## Q1. Restricciones de integración — patrón de detección de fallo por cliente

El código ya tiene precedentes dispares: `sofascore_client.py` define `SofascoreIPBanError` y propaga el baneo (403) sin tragarlo (FR2.1); `futmondo_client.py`, en cambio, traga `RequestException`/`Timeout`/`JSONDecodeError` y devuelve `None` (fallo silencioso). ¿Qué patrón quieres consolidar en FR4?

- A. **Excepción tipada por modo de fallo, propagada**: extender el patrón de Sofascore — cada modo de fallo esperado (baneo, timeout, respuesta heterogénea/no parseable) es una excepción tipada que se propaga hasta quien decide degradar/abortar; nada de `return None` silencioso.
- B. **Resultado explícito (objeto/estado), no excepción**: los clientes devuelven un resultado que distingue éxito / fallo-recuperable / fallo-fatal, y el llamante decide; sin excepciones nuevas.
- C. **Mixto**: baneo/fatal como excepción tipada (ya existe en Sofascore); fallos recuperables como estado explícito.
- D. Not yet defined (que lo proponga el diseño).
- X. Other (please specify)

[Answer]: A. Excepción tipada por modo de fallo, propagada: extender el patrón de Sofascore — cada modo de fallo esperado (baneo, timeout, respuesta heterogénea/no parseable) es una excepción tipada que se propaga hasta quien decide degradar/abortar; nada de `return None` silencioso.

## Q2. Punto de anclaje del estado — ¿dónde se refleja "detectado, no corrompe, reflejado"?

FR3.1 ya introdujo `sync_step_status.py` con `StepStatus.DEGRADED` y `record_degraded_step(...)`, fuera de los god-files. ¿Es ese el punto de anclaje para reflejar el fallo de integración de FR4?

- A. **Sí, reusar y extender `sync_step_status.py`**: el baneo/entrada fallida marca el paso como `degraded`/fallido vía el helper existente (o una extensión estrecha), sin tocar los god-files [memory:M1].
- B. **Nuevo helper estrecho adyacente**: crear una función/módulo nuevo y testeable para el estado de integración, separado del de pasos de sync.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Sí, reusar y extender `sync_step_status.py`: el baneo/entrada fallida marca el paso como `degraded`/fallido vía el helper existente (o una extensión estrecha), sin tocar los god-files.

## Q3. Requisitos regulatorios / compliance

El sistema maneja credenciales Futmondo del usuario y datos de campeonatos; ya hay reglas afirmadas (no credenciales en claro, `JWT_SECRET` no-default). ¿Hay algún requisito regulatorio formal que deba entrar en el registro de restricciones?

- A. **Ninguno formal**: proyecto personal/hobby, sin PCI/HIPAA/SOC2/GDPR formal; se mantienen las reglas de seguridad ya afirmadas (credenciales, secretos) como restricciones internas, no como cumplimiento regulatorio.
- B. **GDPR ligero**: hay datos personales (emails/credenciales de usuarios), conviene anotarlo como restricción de manejo de datos aunque sin proceso formal.
- C. Not applicable.
- X. Other (please specify)

[Answer]: A. Ninguno formal: proyecto personal/hobby, sin PCI/HIPAA/SOC2/GDPR formal; se mantienen las reglas de seguridad ya afirmadas (credenciales, secretos) como restricciones internas, no como cumplimiento regulatorio.

## Q4. Stack y perfil técnico — confirmación de restricciones de plataforma

El conocimiento de operación fija el stack en Fly.io (`cdg`) + Neon PostgreSQL (Frankfurt) + GitHub Actions, todo en tiers gratuitos [memory:M3]. Para el registro de restricciones de ESTE intent:

- A. **Confirmado sin cambios**: FastAPI/Python 3.12, Neon, Fly.io, gate CI (gitleaks + pytest + ng test); este intent no toca infraestructura ni añade dependencias de pago [memory:M2]. Cualquier dependencia nueva (si la hubiera) sería OSS y fijada a versión.
- B. **Hay un matiz** (indícalo en Other): p. ej. quieres permitir una librería concreta de manejo de errores/reintentos.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Confirmado sin cambios: FastAPI/Python 3.12, Neon, Fly.io, gate CI (gitleaks + pytest + ng test); este intent no toca infraestructura ni añade dependencias de pago. Cualquier dependencia nueva (si la hubiera) sería OSS y fijada a versión.

## Q5. Presupuesto y plazo — restricciones de entrega

- A. **Sin plazo duro, coste 0 €**: mantenedor único, sin fecha límite externa; la única restricción dura es coste 0 € (tiers gratuitos) [memory:M2].
- B. **Hay un plazo** (indícalo en Other).
- C. Not applicable.
- X. Other (please specify)

[Answer]: A. Sin plazo duro, coste 0 €: mantenedor único, sin fecha límite externa; la única restricción dura es coste 0 € (tiers gratuitos).

## Q6. Bloqueadores organizativos / riesgos de ejecución

Trabajar sobre un sistema en producción con syncs en curso y clientes externos frágiles tiene riesgos. ¿Cuáles reconoces como los principales a registrar en el RAID?

- A. **Regresión funcional al endurecer capturas**: cambiar un `except Exception: pass` por un manejo estricto podría romper un flujo que hoy "funciona" tragando el error. Mitigación: characterization-first en las zonas tocadas, gate CI bloqueante.
- B. **Baneo real de Sofascore durante pruebas**: ejercitar la detección de baneo podría provocar/depender de un 403 real. Mitigación: tests con dobles/mocks, sin red (como ya hacen los specs existentes).
- C. **Ambos** (A y B) son los riesgos principales.
- D. Not identified.
- X. Other (please specify)

[Answer]: C. Ambos (A y B) son los riesgos principales.

## Q7. Incertidumbre técnica — la taxonomía recuperable/fatal

En intent-capture fijaste (Q6=A) que recuperable → degradado y sigue; fatal → aborta limpio sin datos a medias. ¿Dónde ves la mayor incertidumbre técnica a resolver en diseño?

- A. **Clasificar cada captura existente**: decidir, para las capturas de arranque/migraciones/`db_connection.py`, cuáles son recuperables y cuáles fatales, sin romper comportamiento actual.
- B. **Punto de corte "no corromper datos"**: definir exactamente en qué punto de la ruta de sync un fallo fatal debe abortar antes de escribir, para no dejar datos a medias (enlaza con FR2, ya hecho).
- C. **Ambas** son las incógnitas técnicas centrales.
- D. Not yet defined.
- X. Other (please specify)

[Answer]: C. Ambas son las incógnitas técnicas centrales.

## Consolidated Summary Confirmation

Resumen de viabilidad (antes de fijar los artefactos):

- **Veredicto**: viable, riesgo bajo-medio, sin dependencias nuevas (stdlib), sin cambios de infraestructura.
- **Patrón FR4 (Q1=A)**: excepción tipada por modo de fallo, propagada — extiende `SofascoreIPBanError`; se elimina el `return None` silencioso de Futmondo.
- **Estado (Q2=A)**: reusar/extender `sync_step_status.py` (FR3.1) fuera de los god-files.
- **Compliance (Q3=A)**: sin marco regulatorio formal; controles de seguridad ya afirmados como restricciones internas.
- **Plataforma (Q4=A)**: stack fijo (FastAPI/Neon/Fly.io), gate CI existente, coste 0 €.
- **Entrega (Q5=A)**: sin plazo duro; única restricción dura = coste 0 €.
- **RAID (Q6=C, Q7=C)**: riesgos = regresión al endurecer capturas (mitiga characterization-first + gate) y baneo real en pruebas (mitiga dobles/mocks); incertidumbres = clasificar recuperable/fatal y fijar el punto de corte "no corromper datos".
- **Artefactos**: feasibility-assessment.md, constraint-register.md, raid-log.md.

[Answer]: Looks correct
