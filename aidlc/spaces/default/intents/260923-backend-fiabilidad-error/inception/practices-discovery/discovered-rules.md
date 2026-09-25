# Reglas Descubiertas — Fiabilidad backend (FR3.2 + FR4)

> **Re-run brownfield.** Sólo restricciones duras **ya afirmadas** (arrastradas de
> `project.md` § Mandated / § Forbidden y del constraint-register de este intent) más
> las que este intent implica de forma inequívoca. No se fabrican reglas nuevas.

## Mandated

- ALWAYS mantener el proyecto a **coste 0 €**: descartar toda mejora o dependencia con gasto recurrente; sólo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free).
- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`; un rojo nunca llega a producción.
- ALWAYS **caracterizar (congelar con tests) el comportamiento brownfield antes de endurecerlo** (characterization-first): extiende el mandato ya afirmado para `sync_prizes`/`SessionStore`/`TaskManager` a cada broad-except / `except: pass` de la primera oleada FR3.2 que se reclasifique y al contrato de `futmondo_client._make_request` ANTES de cambiar su señal de fallo.
- ALWAYS **caracterizar los llamadores de `futmondo_client._make_request` y entregar un inventario verificable de llamadores** ANTES del cambio de contrato de integración (Q4); la migración cubre el núcleo (`_make_request` + los llamadores donde un `None` no detectado corrompe datos) y el resto queda como deuda registrada.
- ALWAYS **aseverar el EFECTO en los specs de modo de fallo** (Q1): recuperable → paso marcado `DEGRADED` vía `sync_step_status.py` y la operación NO falla; fatal → excepción tipada propagada Y sin datos a medias escritos. NUNCA un `pytest.raises` sin aserción de estado (nada de specs espejo que capturan sin aseverar el efecto).
- ALWAYS exigir un `JWT_SECRET` **no-default** en el arranque del servicio web (NFR1.1; endurecido en `test_jwt_startup.py`).
- ALWAYS señalar el fallo de integración externa como **excepción tipada por modo de fallo, propagada** (extendiendo `SofascoreIPBanError`), con `except <Typed>: raise` antes del `except Exception` genérico.
- ALWAYS distinguir en el manejo de errores lo **recuperable** (degrada y continúa; marca `StepStatus.DEGRADED` vía `sync_step_status.py`, sin corromper datos) de lo **fatal** (aborta limpio, sin dejar datos a medias).
- ALWAYS que los tests usen dobles/fakes en memoria (patrón `conftest.py`), sin red, sin DB real y sin credenciales/tokens reales (gitleaks escanea los tests).

## Forbidden

- NEVER ampliar los god-files existentes (`data_sync_service.py` ~84 KB / 1915 líneas, `data_manager_v2.py` ~166 KB) ni el patrón SQL-en-router al tocar el manejo de errores o los contratos de integración; el código nuevo va tras una capa/función estrecha testeable.
- NEVER traer al alcance de este intent los `except: pass` de `data_manager_v2.py` (Intent 3, god-file) ni de `photo_service.py` (Q6): quedan como **deuda registrada**; la primera oleada FR3.2 se mantiene en arranque/migraciones/`db_connection.py`/clientes + los puntos de corrupción de `data_sync_service.py`.
- NEVER incluir el password ni el token Futmondo del usuario en el mensaje, el `repr` ni el `exc_info` de una excepción de integración (Q5); las excepciones llevan modo de fallo + contexto no sensible (status, endpoint), nunca material de credencial. (Extiende las reglas afirmadas de no-credenciales-en-claro.)
- NEVER usar `return None` silencioso como señal de fallo en el cliente de integración; el modo de fallo se expone como excepción tipada propagada (FR4).
- NEVER tragar un fallo que pueda **corromper datos** tras un commit previo (p. ej. el `DELETE FROM team_prizes ... NOT IN (...)` cuyo `try/except → logger.warning` deja la caché en estado mixto sin señal al consumidor); usar reemplazo transaccional atómico como el patrón de referencia ya caracterizado.
- NEVER correr `ruff format` masivo sobre archivos brownfield ya modificados (infla diffs, expone avisos preexistentes e invalida el pase de revisión en vuelo); formatear sólo los archivos nuevos o de forma quirúrgica.
- NEVER bajar/relajar un umbral o piso de cobertura para pasar el gate; el ratcheting sólo sube.
- NEVER almacenar la contraseña Futmondo en claro (ni en memoria ni en base de datos).
- NEVER usar un `JWT_SECRET` por defecto en producción.
- NEVER introducir dependencias de pago; cualquier librería nueva sería OSS y fijada a versión exacta (no se prevé ninguna, stdlib suficiente).