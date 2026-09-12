# Requirements Analysis — FR2: Reemplazo transaccional de la caché de Sofascore

> Intent: `260911-sofascore-cache-atomica` · Scope: `bugfix` · Depth: Minimal ·
> Proyecto brownfield `futmondo-analytics` (FastAPI + Neon PostgreSQL).
>
> **Project depth**: Minimal — cuánto detalle escribo en cada documento.
> **Test strategy**: Minimal — cuántas pruebas escribo.
> Puedes pedirme cambiar cualquiera de las dos en cualquier punto de aprobación.

## Sources

- `[desc]` Initial description: FR2 — reemplazo transaccional de la caché de
  Sofascore. `POST /api/v1/sync/sofascore` hace `DELETE FROM sofascore_cache`
  antes de repoblar jugador a jugador; si el repoblado falla a mitad (baneo de
  IP, exit code 2), la caché queda vacía o incompleta. Objetivo: reemplazo
  atómico que preserve la caché anterior si el repoblado no tiene éxito.
- `[scope]` Workflow-selected scope: `bugfix` (Minimal depth, regresión dirigida
  al bug, suite existente en verde).
- `[Q1]`..`[Q4]` Respuestas del usuario en
  `requirements-analysis-questions.md` (modo Guide me, 2026-09-12).
- Código fuente real (reverse-engineering / lectura directa):
  - `backend/app/api/v1/endpoints/sofascore_sync.py` — endpoint con el bug.
  - `backend/app/services/sofascore_client.py` — cliente Sofascore (`curl_cffi`).
  - `backend/app/services/db_connection.py` — capa de abstracción de BD.
  - Lecturas de la caché: `backend/app/api/v1/endpoints/_sofascore_helpers.py`,
    `sofascore_detail.py`, `market.py`, y JOIN en
    `backend/app/services/assistant_service.py`.
- CodeKB: `business-overview.md`, `architecture.md`, `code-structure.md`
  (mejora arquitectónica ya señalada: "Hacer transaccional el reemplazo de la
  caché Sofascore").

## Intent analysis (qué se quiere conseguir)

El objetivo de negocio es que la analítica de mercado nunca se quede sin ratings
de Sofascore por culpa de un repoblado fallido. Hoy el refresco de la caché es
destructivo-primero (borra y luego repuebla), de modo que un baneo de IP a mitad
del proceso deja a los usuarios con la caché vacía o incompleta hasta el
siguiente refresco exitoso. Se busca que un refresco solo sustituya a la caché
existente cuando produzca un conjunto de datos válido; en cualquier otro caso la
caché anterior debe sobrevivir intacta.

## Functional requirements

### FR1 — Reemplazo atómico todo-o-nada de la caché

- **FR1.1** El endpoint `POST /api/v1/sync/sofascore` DEBE reemplazar la caché
  `sofascore_cache` de forma atómica: o el conjunto nuevo se aplica por completo,
  o no se modifica ninguna fila existente. `[desc]` `[Q1]`
- **FR1.2** El borrado de la caché anterior y la inserción del conjunto nuevo
  DEBEN ejecutarse dentro de una única transacción de base de datos, de modo que
  un fallo antes de completar la inserción revierta el borrado (rollback).
  `[Q1]` (hoy el `DELETE` se confirma en su propia conexión antes de repoblar:
  `sofascore_sync.py` líneas ~68-71).
- **FR1.3** Si el repoblado no supera el criterio de éxito (FR2), la caché
  anterior DEBE quedar exactamente como estaba antes de la ejecución (mismo
  número de filas y mismos valores). `[Q1]`

### FR2 — Criterio de éxito del repoblado (doble protección)

- **FR2.1 (protección principal — detección de baneo)** El cliente Sofascore
  DEBE distinguir un baneo de IP (respuesta HTTP 403) de un "jugador no
  encontrado" (404 / sin resultados). Actualmente `SofascoreClient._get` y
  `search_player` tratan todo status ≠ 200 igual (warning + `None`), por lo que
  un baneo es indistinguible de un no-encontrado. `[Q2c]`
  (`sofascore_client.py`).
- **FR2.2** Cuando se detecta el baneo durante el repoblado, el endpoint DEBE
  abortar el repoblado, NO aplicar el reemplazo (no swap) y conservar la caché
  anterior intacta al 100%. `[Q2]` `[Q2c]`
- **FR2.3** La respuesta del endpoint DEBE señalar explícitamente el caso de
  baneo, de forma diferenciable de un sync normal (p. ej. un campo/estado que el
  frontend y el cron puedan interpretar). `[Q2c]`
- **FR2.4 (red de seguridad secundaria — umbral)** Cuando NO hay baneo pero el
  repoblado es parcial, el reemplazo solo DEBE aplicarse si el número de
  jugadores del computer con rating obtenido alcanza al menos el 50% del total de
  jugadores del computer procesados. Por debajo de ese umbral se conserva la
  caché anterior. `[Q2]` `[Q2b]`
- **FR2.5** El umbral del 50% DEBE ser una constante configurable en el código
  (no un literal disperso), para poder ajustarlo sin cambios de diseño. `[Q2b]`

### FR3 — Caché compartida entre campeonatos

- **FR3.1** El reemplazo DEBE operar sobre toda la tabla `sofascore_cache`
  (caché compartida por todos los campeonatos): un rating de Sofascore pertenece
  al jugador, no al campeonato de Futmondo. `[Q3]`
- **FR3.2** La columna `championship_id` de `sofascore_cache` DEBE marcarse como
  DEPRECADA y documentarse como no leída por ninguna consulta (evidencia: ninguna
  lectura de `sofascore_cache` filtra por `championship_id`). `[Q3]`
- **FR3.3** La retirada del esquema de `championship_id` y el cambio del
  `ON CONFLICT (player_name, championship_id)` a `ON CONFLICT (player_name)` NO
  forman parte de este bugfix (requerirían migración de esquema en Neon). El
  `ON CONFLICT` actual se mantiene sin cambios. `[Q3]` (ver Out of scope).

## Non-functional requirements

- **NFR1 — Integridad de datos** Durante todo el proceso de refresco, cualquier
  lectura concurrente de `sofascore_cache` (p. ej. `GET /market/today`,
  `sofascore_detail`, el asistente IA) DEBE ver, o bien la caché anterior
  completa, o bien la nueva completa, nunca un estado vacío/parcial intermedio.
  Criterio de verificación: la transacción de FR1.2 no expone filas parciales.
- **NFR2 — Coste 0€** La solución DEBE sostenerse en los tiers gratuitos actuales
  (Neon free, Fly.io free allowance, GitHub Actions free) y NO introducir
  dependencias con gasto recurrente ni infraestructura nueva. `[memory:M1]`
  (regla de proyecto vigente en `project.md`).
- **NFR3 — Mínima superficie de cambio** El arreglo DEBE mantener el stack actual
  (FastAPI + Neon PostgreSQL) y evitar reescrituras grandes; se limita al
  endpoint `sofascore_sync.py`, al cliente `sofascore_client.py` (señalización de
  baneo) y a la prueba de regresión. `[desc]`
- **NFR4 — No regresión** La suite de tests existente (6 ficheros pytest de
  caracterización) DEBE permanecer en verde tras el cambio. `[scope]` `[Q4]`

## Constraints

- Stack fijo: FastAPI (Python 3.12) + Neon PostgreSQL; capa de abstracción
  `db_connection.py` que también soporta SQLite (usado por los tests).
- API Sofascore no oficial vía `curl_cffi` con riesgo real de baneo de IP.
- Coste 0€ (regla de proyecto).
- La caché se accede por `player_name` (case-insensitive en los JOIN del
  asistente); el índice de migración es sobre `player_name`.

## Assumptions

- **[assumption]** Un baneo de Sofascore se manifiesta de forma detectable como
  HTTP 403 (posiblemente además time-outs sostenidos). Si en producción el baneo
  se manifiesta de otra forma, la detección de FR2.1 deberá ampliar el patrón.
  Owner: developer, a validar en Code Generation.
- **[assumption]** El umbral del 50% (FR2.4) es un valor inicial razonable sin
  datos históricos; se asume ajustable vía constante (FR2.5).
- **[assumption]** En producción se opera principalmente con un único
  `CHAMPIONSHIP_ID`, por lo que el reemplazo global (FR3.1) no cambia el
  comportamiento observable respecto al borrado global actual.

## Out of scope

- Migración de esquema en Neon para eliminar `championship_id` y cambiar el
  `ON CONFLICT` (trabajo posterior; ver FR3.3).
- Persistir el estado de sync/sesiones (mejora arquitectónica no relacionada con
  este bug).
- Refactor de los "god files" (`data_manager_v2.py`, `data_sync_service.py`).
- Cambios en el script de cron local (`backend/scripts/sync_sofascore_local.py`),
  que ya usa un patrón de reemplazo distinto (DELETE condicionado por frescura).

## Open questions

- Confirmar en diseño/implementación la forma exacta de señalar el baneo en la
  respuesta del endpoint (FR2.3) para que frontend y cron lo consuman de forma
  coherente con el exit code 2 del cron.

## Assumptions & Open Questions

Las asunciones y preguntas abiertas están listadas en las secciones
`## Assumptions` y `## Open questions` anteriores. Ninguna bloquea la generación
de requisitos; se resolverán en las etapas de construcción.

<!-- memory register:
  [memory:M1] = project.md ## Corrections: mantener el proyecto a coste 0€
-->
