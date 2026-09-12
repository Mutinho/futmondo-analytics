# Requirements Analysis — Preguntas (FR2: reemplazo transaccional de la caché Sofascore)

Contexto del bug (fundamentado en el código real,
`backend/app/api/v1/endpoints/sofascore_sync.py`):

- El endpoint `POST /api/v1/sync/sofascore` ejecuta `DELETE FROM sofascore_cache`
  en una conexión propia y hace `commit` implícito al cerrar el `with`, ANTES de
  volver a poblar la tabla jugador a jugador.
- Si el repoblado falla a mitad (baneo de IP de Sofascore, ningún jugador
  encontrado, o excepción), `cache_rows` queda vacío o incompleto y el `INSERT`
  batch nunca repone lo borrado → la caché queda vacía o parcial.
- Además, el `DELETE` no filtra por `championship_id` (borra TODA la tabla)
  aunque el comentario dice "de este campeonato" y el `INSERT` sí escribe
  `championship_id`.

Objetivo declarado: hacer el reemplazo atómico, de modo que la caché anterior
permanezca intacta si el repoblado no tiene éxito. Restricciones: mantener stack
(FastAPI + Neon PostgreSQL), sin reescrituras grandes, coste 0€.

---

## Q1: ¿Qué debe pasar exactamente cuando el repoblado NO tiene éxito?

Cuando el escaneo de Sofascore falla total o parcialmente, ¿cuál es el
comportamiento correcto de la caché?

- A. La caché anterior debe quedar EXACTAMENTE como estaba (no se toca nada si el
  nuevo conjunto no se puede construir con éxito) — reemplazo todo-o-nada.
- B. Reemplazar solo si se obtuvo AL MENOS un jugador con rating; si `cache_rows`
  está vacío, conservar la caché anterior intacta.
- C. Reemplazar siempre que no haya excepción fatal, aunque el nuevo conjunto sea
  más pequeño que el anterior (aceptar caché parcial mientras el proceso "termine").
- X. Other (please specify)

[Answer]: A

## Q2: ¿Cómo definimos "éxito" del repoblado para decidir si se aplica el reemplazo?

¿Qué umbral hace que el nuevo conjunto de ratings se considere válido para
sustituir a la caché anterior?

- A. Basta con ≥1 jugador sincronizado correctamente (`synced >= 1`).
- B. Que no haya habido excepción fatal (independientemente de cuántos jugadores).
- C. Un umbral proporcional (p. ej. ≥50% de los jugadores del computer con rating).
- X. Other (please specify)

[Answer]: C — Umbral proporcional (≥N% de los jugadores del computer con rating)
MÁS abortar el reemplazo si se detecta baneo de Sofascore a mitad del proceso.
Matiz aportado por el usuario en la conversación: el baneo puede ocurrir a mitad
del bucle, produciendo un `cache_rows` parcial (p. ej. 40 de 100); un criterio
`synced >= 1` aplicaría el reemplazo y perdería filas buenas anteriores, por lo
que se exige (a) detectar el baneo y abortar sin hacer swap, y (b) un umbral
proporcional como red de seguridad para fallos parciales no-baneo. Umbral
concreto pendiente de fijar en la pregunta de seguimiento (Q2b).

## Q2b: Umbral proporcional concreto (red de seguridad secundaria)

Cuando NO hay baneo, ¿qué porcentaje mínimo de los jugadores del computer con
rating exigimos para aplicar el reemplazo?

- A. 25% (permisivo)
- B. 50% (punto medio)
- C. 80% (conservador)
- X. Other (please specify)

[Answer]: B — 50%. Es la red de seguridad secundaria; la protección principal
es abortar al detectar el baneo (Q2c). Configurable como constante para poder
ajustarlo sin cambios de diseño.

## Q2c: Detección explícita del baneo de Sofascore (protección principal)

Hoy `SofascoreClient` NO distingue un baneo (HTTP 403) de un "no encontrado":
ante cualquier status != 200 registra un warning y devuelve `None`, por lo que
el bucle del endpoint continúa hasta el final y un baneo a mitad se ve idéntico
a "los jugadores restantes no se encontraron". ¿Añadimos detección explícita?

- A. Sí: el cliente distingue el baneo (403 / patrón de baneo) de "no
  encontrado", y el endpoint aborta el repoblado al detectarlo, sin hacer swap,
  conservando la caché anterior intacta al 100% y señalando el baneo en la
  respuesta.
- B. No tocar el cliente: confiar solo en el umbral proporcional (Q2b).
- X. Other (please specify)

[Answer]: A — El cliente Sofascore distingue el baneo (HTTP 403) de "no
encontrado"; el endpoint aborta el reemplazo en cuanto lo detecta, no hace swap,
conserva la caché anterior intacta al 100% y señala el baneo en la respuesta.
Esta es la protección principal; el umbral (Q2b) es la red secundaria.

## Q3: Alcance del borrado — ¿el reemplazo debe limitarse al campeonato actual?

Hoy el `DELETE FROM sofascore_cache` borra toda la tabla (todos los
campeonatos), aunque el `INSERT` escribe `championship_id` y el comentario dice
"de este campeonato". ¿Corregimos el alcance dentro de este bugfix?

- A. Sí: el reemplazo debe afectar solo a las filas del `championship_id` que se
  está sincronizando (`DELETE ... WHERE championship_id = ?`), como parte de la
  corrección.
- B. No: mantener el borrado global de toda la tabla como está hoy; solo
  arreglar la atomicidad, no el alcance.
- C. No estoy seguro / decídelo tú según lo que sea más seguro y coherente con el
  resto del sistema.
- X. Other (please specify)

[Answer]: Reformulada en la conversación. La caché de Sofascore es COMPARTIDA
por todos los campeonatos (un rating es del jugador, no del campeonato).
Evidencia de código: NINGUNA lectura de `sofascore_cache` filtra por
`championship_id` (`_sofascore_helpers.py`, `sofascore_detail.py`, `market.py`,
y los JOIN por `player_name` en `assistant_service.py`); el único que escribe
`championship_id` es `sofascore_sync.py` vía `ON CONFLICT (player_name,
championship_id)`; el índice de migración es sobre `player_name`. Decisión
(opción 1): el reemplazo es GLOBAL (toda la tabla, swap de todos los jugadores);
`championship_id` se marca como columna DEPRECADA (documentada como no usada por
ninguna lectura), pero su retirada del esquema + migración en Neon NO se hace en
este bugfix (evita una migración de esquema arriesgada; queda como trabajo
posterior). El `ON CONFLICT (player_name, championship_id)` se mantiene tal cual
para no requerir cambio de constraint/índice único.

## Q4: ¿Requiere este arreglo una prueba de regresión automatizada?

La política de scope `bugfix` pide una regresión dirigida al bug concreto, con la
suite existente en verde. El backend tiene 6 ficheros de tests de caracterización
(pytest) y Neon PostgreSQL en producción.

- A. Sí: añadir un test de regresión que simule fallo del repoblado y verifique
  que la caché anterior sobrevive intacta (nivel unit/integración, con la BD que
  usen los tests existentes).
- B. Sí, pero solo si es de bajo coste y no requiere infraestructura nueva
  (coste 0€); si exige una BD real dedicada, documentar el caso en su lugar.
- C. No hace falta test nuevo; validación manual.
- X. Other (please specify)

[Answer]: B — Sí, prueba de regresión de bajo coste y sin infraestructura nueva
(coste 0€): contra la BD que usan los tests existentes (SQLite vía la capa de
abstracción), mockeando el cliente Sofascore para simular el baneo/fallo del
repoblado, verificando que la caché anterior sobrevive intacta. La suite
existente debe permanecer en verde.

## Consolidated Summary Confirmation

Resumen de las decisiones tomadas:

- Reemplazo de la caché de Sofascore ATÓMICO y todo-o-nada: la caché anterior
  queda intacta si el repoblado no tiene éxito (Q1).
- Criterio de éxito con doble protección (Q2, Q2b, Q2c): (a) protección
  principal — el cliente Sofascore distingue el baneo (HTTP 403) de "no
  encontrado" y el endpoint aborta el reemplazo al detectarlo, sin hacer swap;
  (b) red de seguridad secundaria — umbral proporcional del 50% de los jugadores
  del computer con rating (constante configurable) para fallos parciales no-baneo.
- La caché de Sofascore es COMPARTIDA por todos los campeonatos; el reemplazo es
  global (toda la tabla). `championship_id` se marca como columna DEPRECADA (no
  usada por ninguna lectura), pero su retirada de esquema + migración en Neon NO
  se hace en este bugfix; el `ON CONFLICT (player_name, championship_id)` se
  mantiene (Q3).
- Prueba de regresión de bajo coste y sin infraestructura nueva (coste 0€):
  contra la BD de los tests existentes (SQLite), mockeando Sofascore para
  simular baneo/fallo, verificando que la caché anterior sobrevive; suite
  existente en verde (Q4).
- Restricciones mantenidas: stack actual (FastAPI + Neon PostgreSQL), sin
  reescrituras grandes, coste 0€.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
