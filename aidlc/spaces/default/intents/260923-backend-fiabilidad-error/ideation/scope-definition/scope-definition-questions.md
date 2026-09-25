# Scope Definition — Preguntas de aclaración

Intent: **Fiabilidad backend — manejo de errores (FR3.2) + contratos de integración (FR4)**

## Sources

- [desc] Initial description: "Intent 1 del plan de mejoras (docs/BACKLOG-plan-intents.md), derivado del intent de analisis 260911-analisis-mejoras: FR3.2 + FR4. FR3.2 - reducir los except Exception/bare-except (159+6) del backend, empezando por los except: pass de arranque y migraciones, distinguiendo error recuperable de fatal; continuacion natural de FR3.1 (ya hecho). FR4 - robustez de integraciones externas: documentar contratos y modos de fallo esperados de Sofascore (API no oficial via curl_cffi, baneo de IP) y Futmondo (endpoints heterogeneos); ante baneo/entrada fallida el sistema lo detecta, no corrompe datos (enlaza con FR2 ya hecho) y lo refleja en el estado. Scope feature, brownfield futmondo-analytics. Restricciones: mantener stack actual (Angular + FastAPI + Neon PostgreSQL + Fly.io), sin reescrituras grandes, NO ampliar los god-files (data_sync_service.py, data_manager_v2.py) ni el patron SQL-en-router - el codigo nuevo va tras una capa/funcion estrecha testeable; test-after con specs significativas; gate de CI bloqueante (gitleaks + pytest + ng test) antes de merge a main; coste 0 EUR (tiers gratuitos). Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/project.md#Forbidden`: "NEVER ampliar los god-files existentes (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router."

---

## Q1. Alcance mínimo viable — ¿qué debe entrar sí o sí para que el intent aporte valor?

En feasibility fijamos: FR3.2 primera oleada (arranque + migraciones + `db_connection.py`), FR4 (excepciones tipadas propagadas + estado degradado reusando `sync_step_status.py` + doc de contratos). ¿Cuál es el mínimo que ya aporta valor?

- A. **Las dos patas completas**: FR3.2 primera oleada + FR4 (Futmondo tipado + detección de baneo reflejada en estado + doc de contratos). Es el "hecho" que definiste en intent-capture (Q3=D).
- B. **FR4 primero como MVP**: detección/estado de integración es lo más valioso (evita corrupción de datos); FR3.2 primera oleada entra si da tiempo.
- C. **FR3.2 primero como MVP**: endurecer arranque/migraciones/`db_connection.py` primero; FR4 después.
- D. Not yet defined.
- X. Other (please specify)

[Answer]: A. Las dos patas completas: FR3.2 primera oleada + FR4 (Futmondo tipado + detección de baneo reflejada en estado + doc de contratos). Es el "hecho" que definiste en intent-capture (Q3=D).

## Q2. Must-have vs nice-to-have — clasificación de capacidades

¿Cómo clasificas estas capacidades (MoSCoW)?

- A. **Must**: (1) `futmondo_client.py` deja de tragar excepciones (tipadas+propagadas), (2) detección de baneo/entrada fallida reflejada en estado sin corromper datos, (3) primera oleada de broad-except de arranque/migraciones/`db_connection.py`. **Should**: doc de contratos/modos de fallo. **Could**: extender a más capturas de `data_sync_service.py` (puntos de corrupción concretos). **Won't (this time)**: las 29 capturas completas de `data_sync_service.py`, el resto de broad-except del backend.
- B. Prefiero otra clasificación (indícala en Other).
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Must: (1) `futmondo_client.py` deja de tragar excepciones (tipadas+propagadas), (2) detección de baneo/entrada fallida reflejada en estado sin corromper datos, (3) primera oleada de broad-except de arranque/migraciones/`db_connection.py`. Should: doc de contratos/modos de fallo. Could: extender a puntos de corrupción concretos de `data_sync_service.py`. Won't (this time): las 29 capturas completas de `data_sync_service.py`, el resto de broad-except del backend.

## Q3. Dependencias entre capacidades — orden natural

- A. **FR3.2 (capa de errores) habilita FR4**: primero la taxonomía recuperable/fatal y el endurecimiento de capturas base, luego los clientes de integración se apoyan en ese patrón y el estado.
- B. **FR4 y FR3.2 son en su mayoría independientes**: pueden ir en paralelo; solo comparten `sync_step_status.py` como punto de anclaje.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. FR3.2 (capa de errores) habilita FR4: primero la taxonomía recuperable/fatal y el endurecimiento de capturas base, luego los clientes de integración se apoyan en ese patrón y el estado.

## Q4. Preferencia de secuenciación

- A. **Riesgo primero**: atacar antes lo que más riesgo de corrupción de datos tiene (detección de fallo de integración + punto de corte "no corromper"), luego el resto de endurecimiento.
- B. **Valor primero**: empezar por lo que da valor observable antes (p. ej. Futmondo deja de fallar en silencio).
- C. **Dependencia primero**: seguir el orden natural de dependencias (capa de errores → clientes → estado).
- D. Not yet defined (que lo decida delivery-planning).
- X. Other (please specify)

[Answer]: C. Dependencia primero: seguir el orden natural de dependencias (capa de errores → clientes → estado). Dentro de FR4 se prioriza lo de corrupción de datos.

## Q5. Plazos duros atados a capacidades concretas

- A. **Ninguno**: sin fechas límite; coste 0 € es la única restricción dura (coherente con feasibility Q5=A).
- B. Hay un plazo (indícalo en Other).
- C. Not applicable.
- X. Other (please specify)

[Answer]: A. Ninguno: sin fechas límite; coste 0 € es la única restricción dura (coherente con feasibility Q5=A).

## Q6. Frontera de exclusión explícita (out of scope)

Para que el trinquete de alcance no se desborde, ¿confirmas estas exclusiones explícitas para ESTE intent?

- A. **Sí, excluir explícitamente**: (1) las 29 capturas completas de `data_sync_service.py` salvo puntos de corrupción concretos, (2) el resto de broad-except del backend fuera de la primera oleada, (3) la poda de config/Turso/SQLite muerta (es Intent 2), (4) la descomposición de god-files (Intent 3). Todo ello queda como deuda registrada, sin ampliar los god-files [memory:M1].
- B. Ajustar las exclusiones (indícalo en Other).
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Sí, excluir explícitamente: (1) las 29 capturas completas de `data_sync_service.py` salvo puntos de corrupción concretos, (2) el resto de broad-except del backend fuera de la primera oleada, (3) la poda de config/Turso/SQLite muerta (Intent 2), (4) la descomposición de god-files (Intent 3). Todo como deuda registrada, sin ampliar los god-files.

## Consolidated Summary Confirmation

Resumen de alcance (antes de fijar los artefactos):

- **Alcance (Q1=A)**: las dos patas completas — FR3.2 primera oleada (taxonomía recuperable/fatal + arranque/migraciones/`db_connection.py`) y FR4 (Futmondo tipado + detección de baneo en estado + doc de contratos).
- **MoSCoW (Q2=A)**: Must = Futmondo tipado, detección en estado, primera oleada broad-except; Should = doc de contratos; Could = puntos de corrupción de `data_sync_service.py`; Won't = 29 capturas completas + resto del backend.
- **Dependencia (Q3=A)**: FR3.2 (capa de errores) habilita FR4.
- **Secuenciación (Q4=C)**: dependencia primero (errores → clientes → estado), priorizando corrupción dentro de FR4.
- **Plazos (Q5=A)**: ninguno; coste 0 € única restricción dura.
- **Exclusiones (Q6=A)**: 29 capturas completas de `data_sync_service.py` (salvo corrupción), resto de broad-except, poda (Intent 2), god-files (Intent 3) — todo como deuda, sin ampliar god-files.
- **Artefactos**: scope-document.md, intent-backlog.md.

[Answer]: Looks correct
