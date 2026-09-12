# Code Summary — Reemplazo transaccional de la caché de Sofascore

> Intent: `260911-sofascore-cache-atomica` · Scope: `bugfix` · Metodología:
> `test-after` (Testing Contract del plan). Proyecto brownfield FastAPI + Neon
> PostgreSQL. Trabajo zero-Unit: una única iteración de implementación.

## Qué se cambió y por qué

El endpoint `POST /api/v1/sync/sofascore` borraba la caché
(`DELETE FROM sofascore_cache`) y la confirmaba en su propia conexión **antes**
de repoblar jugador a jugador. Un baneo de IP a mitad (HTTP 403) o un repoblado
parcial dejaba la caché vacía o incompleta. Este bugfix hace el reemplazo
**atómico todo-o-nada** y añade doble protección: detección de baneo (403) y una
red de seguridad de umbral de cobertura del 50%.

## Ficheros modificados/creados

| Fichero | Cambio |
|---|---|
| `backend/app/core/constants.py` | **Modificado.** Nueva constante `SOFASCORE_MIN_COVERAGE_RATIO = 0.5` con comentario (FR2.5). |
| `backend/app/services/sofascore_client.py` | **Modificado.** Nueva excepción `SofascoreIPBanError`; `_get` y `search_player` distinguen HTTP 403 (baneo → excepción) de 404 (→ `None`); ambos `except` genéricos re-propagan `SofascoreIPBanError` (FR2.1). |
| `backend/app/api/v1/endpoints/sofascore_sync.py` | **Modificado.** Función pura `should_apply_replacement`; `sync_sofascore` reestructurado: recolecta resultados, elimina el DELETE prematuro, aplica DELETE+INSERT en una única transacción solo si el repoblado supera el criterio; respuesta diferenciada `applied`/`reason`; comentario de deprecación de `championship_id` (FR1, FR2.2-2.4, FR3.1-3.3, NFR1). |
| `backend/tests/test_sofascore_sync_characterization.py` | **Creado.** 13 tests de regresión (lógica pura, cliente, endpoint). |

## Decisiones clave de implementación

1. **Transacción única para el swap.** El DELETE y el INSERT batch se ejecutan
   sobre la misma `with db.get_connection() as conn`. El context manager de
   `db_connection.py` hace `commit()` al salir sin excepción y `rollback()` si
   la hay, de modo que un fallo del INSERT revierte el DELETE y preserva la
   caché (FR1.2, NFR1). Se eliminó el `DELETE FROM sofascore_cache` prematuro
   en conexión separada (líneas ~68-71 originales).
2. **Detección de baneo por excepción.** `SofascoreIPBanError` se propaga desde
   el cliente (403) a través de `get_player_full_info`/`search_player` hasta el
   bucle del endpoint, que marca `banned=True` y **aborta** el bucle. El `except
   Exception` genérico del bucle NO la traga porque se captura antes en un
   `except SofascoreIPBanError` específico.
3. **`processed == 0` → no vaciar la caché.** Se documentó y decidió que sin
   jugadores del computer que procesar no hay conjunto nuevo válido; se devuelve
   `(False, "below_threshold")` para preservar la caché anterior en lugar de
   vaciarla (coherente con FR1.3).
4. **Umbral inclusivo.** `synced/processed < min_ratio` es estricto, por lo que
   exactamente el 50% aplica el swap (el umbral es un mínimo inclusivo).
5. **`championship_id` deprecada.** Se documenta en el INSERT como columna no
   leída por ninguna consulta; se sigue escribiendo por compatibilidad con el
   `ON CONFLICT (player_name, championship_id)` actual (FR3.2, FR3.3). La
   retirada de esquema queda fuera de alcance.
6. **Compatibilidad de respuesta.** Se conservan las claves `success`, `synced`,
   `errors`, `total_players`; se añaden `applied` (bool) y `reason`
   (`"ok"`|`"ip_ban"`|`"below_threshold"`). En baneo/umbral `success` sigue
   `True` pero `applied=False` (FR2.3).
7. **Rama PostgreSQL/SQLite intactas.** `execute_values` con `ON CONFLICT` para
   Postgres y `INSERT OR REPLACE` para SQLite se mantienen sin cambios, ahora
   dentro de la transacción del swap.

## Cobertura de tests (test-after, estrategia Minimal + suelo bugfix)

`backend/tests/test_sofascore_sync_characterization.py` — 13 tests:

- **Lógica pura `should_apply_replacement`** (5): OK ≥ umbral → `(True,"ok")`;
  baneo → `(False,"ip_ban")`; parcial < 50% → `(False,"below_threshold")`; 50%
  exacto → `(True,"ok")`; `processed==0` → `(False,"below_threshold")`.
- **Cliente Sofascore** (4): `search_player`/`_get` con 403 → `SofascoreIPBanError`;
  con 404 → `None`.
- **Endpoint (regresión del bug)** (4): (a) repoblado exitoso → DELETE+INSERT en
  la misma conexión, una sola conexión; (b) baneo a mitad → sin DELETE, sin
  conexión de escritura, `reason="ip_ban"`; (c) parcial < 50% → sin DELETE,
  `reason="below_threshold"`; (d) parcial ≥ 50% → swap aplicado.

## Resultado de ejecución

`pytest`, `fastapi` y `python3.12` **no están disponibles** en el entorno de
ejecución (el sistema tiene Python 3.14 gestionado por el SO bajo PEP 668, sin
`ensurepip`/`python3-venv`, y no puedo instalar paquetes sin sudo ni romper el
entorno gestionado). Por tanto **NO pude ejecutar el comando exigido**
`python -m pytest tests/test_sofascore_sync_characterization.py -ra` ni la suite
completa `python -m pytest tests -ra`.

Verificación alternativa realizada (sin inventar resultados):
- `python3 -m py_compile` sobre los 4 ficheros → COMPILE OK (sintaxis válida).
- Ejecución equivalente de las 13 aserciones con stubs de `fastapi`/`config` y
  fakes de `db`/clientes (curl_cffi sí está disponible): **las 13 pasan**. Esto
  reproduce exactamente la lógica de cada test del fichero, pero no es el runner
  `pytest` real.

**Acción pendiente para Build & Test (3.6):** ejecutar en un entorno con las
dependencias del proyecto (`backend/requirements.txt` + pytest):
`cd backend && python -m pytest tests/test_sofascore_sync_characterization.py -ra`
y `python -m pytest tests -ra` para confirmar la no regresión (NFR4).

## Desviaciones del plan

- **Step 11 / suite verde**: no pude ejecutar `pytest` por falta de entorno
  (documentado arriba); los tests quedan escritos y completos y la lógica se
  validó de forma equivalente. Sin desviaciones de diseño ni de superficie de
  ficheros (3 fuentes + 1 test, NFR3). No se añadieron dependencias (NFR2).
