# Requirements Analysis — Preguntas de aclaración

Intent: **Fiabilidad backend — manejo de errores (FR3.2) + contratos de integración (FR4)**

## Sources

- [desc] Initial description: "Intent 1 del plan de mejoras (docs/BACKLOG-plan-intents.md), derivado del intent de analisis 260911-analisis-mejoras: FR3.2 + FR4. FR3.2 - reducir los except Exception/bare-except (159+6) del backend, empezando por los except: pass de arranque y migraciones, distinguiendo error recuperable de fatal; continuacion natural de FR3.1 (ya hecho). FR4 - robustez de integraciones externas: documentar contratos y modos de fallo esperados de Sofascore (API no oficial via curl_cffi, baneo de IP) y Futmondo (endpoints heterogeneos); ante baneo/entrada fallida el sistema lo detecta, no corrompe datos (enlaza con FR2 ya hecho) y lo refleja en el estado. Scope feature, brownfield futmondo-analytics. Restricciones: mantener stack actual (Angular + FastAPI + Neon PostgreSQL + Fly.io), sin reescrituras grandes, NO ampliar los god-files (data_sync_service.py, data_manager_v2.py) ni el patron SQL-en-router - el codigo nuevo va tras una capa/funcion estrecha testeable; test-after con specs significativas; gate de CI bloqueante (gitleaks + pytest + ng test) antes de merge a main; coste 0 EUR (tiers gratuitos). Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/team.md#Testing Posture`: "Un spec de fallo NO basta con `pytest.raises`: debe aseverar el EFECTO."
- [memory:M2] `aidlc/spaces/default/memory/team.md#Code Style`: "las excepciones de integración viven en un **módulo estrecho y testeable `integration_errors`** con una **raíz común `IntegrationError`**."

---

## Q1. Requisito de observabilidad — ¿NFR de logging estructurado del fallo?

Además de reflejar el fallo en el estado del sync (`DEGRADED`), ¿quieres un requisito no-funcional explícito de **logging estructurado** del modo de fallo (campos `sync_step`, `reason`, `task_id`) para que `fly logs` + `grep` sirvan de observabilidad a coste 0 €?

- A. **Sí, NFR de logging estructurado**: cada fallo de integración (recuperable o fatal) emite un log estructurado con modo de fallo + contexto no sensible (status, endpoint), nunca material de credencial.
- B. No; basta con el estado `DEGRADED`, sin requisito de logging.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Sí, NFR de logging estructurado: cada fallo de integración (recuperable o fatal) emite un log estructurado con modo de fallo + contexto no sensible (status, endpoint), nunca material de credencial.

## Q2. Requisito de reintentos — ¿entra el retry/backoff en este intent?

Ante un fallo recuperable de integración (p. ej. timeout puntual), ¿el sistema debe **reintentar** (retry/backoff) o solo detectar+degradar?

- A. **Solo detectar + degradar** en este intent: no se añade lógica de reintentos; recuperable = marcar `DEGRADED` y continuar. El retry/backoff queda como deuda/fuera de alcance (evita dependencias y complejidad).
- B. **Incluir retry/backoff** para fallos recuperables transitorios.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Solo detectar + degradar en este intent: no se añade lógica de reintentos; recuperable = marcar DEGRADED y continuar. El retry/backoff queda como deuda/fuera de alcance.

## Q3. Criterio de aceptación medible de "no corromper datos"

Para el requisito de no-corrupción ante fallo fatal, ¿cuál es el criterio de aceptación verificable?

- A. **Estado verificado tras el fallo**: un spec provoca el fallo fatal en el punto de escritura (p. ej. el `DELETE ... NOT IN` de `team_prizes`) y asvera que la tabla/caché queda en estado consistente (todo-o-nada), no a medias. (Coherente con el floor de aserción de efecto [memory:M1].)
- B. Otro criterio (indícalo en Other).
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Estado verificado tras el fallo: un spec provoca el fallo fatal en el punto de escritura (p. ej. el DELETE ... NOT IN de team_prizes) y asvera que la tabla/caché queda en estado consistente (todo-o-nada), no a medias.

## Consolidated Summary Confirmation

Resumen antes de generar `requirements.md`:

- **FR3.2** (manejo de errores): taxonomía recuperable/fatal; primera oleada de broad-except en arranque (`main.py`), migraciones (`scripts/migrate_*`) y `db_connection.py`; `E722` re-habilitado advisory.
- **FR4** (contratos de integración): excepciones tipadas propagadas en módulo `integration_errors` (raíz `IntegrationError`); `futmondo_client` deja de tragar a `None`; inventario de llamadores de `_make_request` como entregable previo; detección de baneo/entrada fallida reflejada en estado; doc de contratos/modos de fallo Sofascore/Futmondo.
- **NFR logging (Q1=A)**: log estructurado del modo de fallo con contexto no sensible, nunca credenciales.
- **Reintentos (Q2=A)**: fuera de alcance; recuperable = detectar + degradar, sin retry/backoff.
- **No-corrupción (Q3=A)**: criterio verificable = spec fuerza el fallo fatal en el punto de escritura y asvera estado todo-o-nada.
- **Restricciones**: stack fijo, no ampliar god-files, coste 0 €, gate CI bloqueante, sin dependencias nuevas.
- **Out of scope**: 29 capturas completas de `data_sync_service.py` (salvo corrupción), `except: pass` de `data_manager_v2.py`/`photo_service.py`, resto de broad-except, poda (Intent 2), god-files (Intent 3).

[Answer]: Looks correct
