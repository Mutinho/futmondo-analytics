# Code Summary — u2-integrations (Integraciones)

Intervención de fiabilidad **acotada y aditiva** sobre el backend brownfield.
Metodología **test-after, characterization-first**: cada captura/contrato
brownfield se congeló con tests ANTES de endurecerlo, y los specs de fallo
**aseveran el EFECTO** (no `pytest.raises` a secas). Suite existente en verde en
cada paso. NO se ampliaron los god-files: el código nuevo vive tras funciones
estrechas testeables.

## Ficheros creados / modificados

| Fichero | Acción | Motivo |
|---|---|---|
| `backend/app/services/integration_errors.py` | modificado (aditivo) | añadido `IntegrationRequestError(IntegrationError)` (recuperable por defecto, `failure_mode="request_exception"`), misma forma de constructor (sólo `failure_mode`/`status`/`endpoint`) |
| `backend/app/services/futmondo_client.py` | modificado | `_make_request` deja de tragar fallos: lanza `IntegrationTimeoutError` / `IntegrationRequestError` / `IntegrationUnparseableError` (typed `except` antes del genérico); no-auth sigue devolviendo `None` |
| `backend/app/services/prizes/team_prizes_writer.py` | **creado** | `replace_team_prizes(...)`: reemplazo transaccional atómico (upsert + DELETE stale en UNA transacción; rollback todo-o-nada). Fuera del god-file |
| `backend/app/services/data_sync_service.py` | modificado (endurecer, **no** ampliar) | `sync_prizes`: acumula filas y llama al writer atómico (sustituye el bloque INSERT-por-ronda + cleanup DELETE con warning tragado); ramas `except` tipadas fatal/recuperable antes del genérico; helper `_log_integration_failure` (log estructurado key=value, sin credenciales) |
| `backend/app/api/v1/endpoints/sync.py` | modificado | punto de captura de la ruta de sync: ramas explícitas fatal (`IntegrationBanError` → propaga) / recuperable (`Timeout`/`Unparseable`/`Request` → `record_degraded_step` + continúa) antes del genérico |
| `backend/tests/test_futmondo_client_characterization.py` | **creado** | congela el contrato ACTUAL de `_make_request` + inventario verificable de llamadores (núcleo/deuda) |
| `backend/tests/test_futmondo_client_typed_failures.py` | **creado** | subtipo correcto por modo de fallo + sin credenciales en `str`/`repr` |
| `backend/tests/test_sync_integration_failure_effect.py` | **creado** | recuperable → paso `DEGRADED` y el sync no falla; fatal (baneo) → propagado y sin datos a medias |
| `backend/tests/test_team_prizes_atomic_replacement.py` | **creado** | characterization del defecto legacy (estado mixto) + reemplazo atómico (rollback deja el conjunto previo íntegro) |
| `backend/ruff.toml` | **sin cambio** (ya en estado objetivo) | ver *Desviaciones*: `E722` ya estaba fuera de `ignore` en HEAD con el comentario de trinquete; Step 7 ya satisfecho, no requería edición |

## Inventario verificable de llamadores de `_make_request` (FR4.3, BR6.1)

Congelado y **asertado** en `tests/test_futmondo_client_characterization.py`.

### Núcleo (migrado en U2 — un `None` no detectado corrompe/omite datos de sync)
`_make_request` + **17 getters directos** de `FutmondoClient` que lo invocan y
son consumidos por la ruta de sync (`DataSyncService.sync_prizes` / `sync_*`):

`get_championship_players`, `get_player_summary`, `get_matchday_standings`,
`get_nightmare_team`, `get_dream_team`, `get_match_list`, `get_round_matches`,
`get_round_lineup`, `get_userteam_rounds`, `get_userteam_roster`,
`get_user_roundlineup`, `get_round_ranking`, `get_market_players`,
`get_pressroom_news`, `get_player_fullprofile`, `get_locker_news`,
`get_league_list`.

Más **1 getter indirecto**: `get_matchday_history` (llega a la API vía
`get_matchday_standings`). Total ≈ 20 getters núcleo.

**Migración del núcleo**: al lanzar `_make_request` una excepción tipada en vez
de `None`, los getters ya no reciben `None` como señal de fallo; la excepción
**propaga** por el getter hasta el punto de captura del sync (Step 4), que la
clasifica. No hizo falta tocar el cuerpo de cada getter (no la tragan); el
`if response: ... return None` restante sólo cubre el caso no-autenticado
legítimo.

### Deuda (NO migrada en U2 — documentada)
Los **4 endpoints de `app/api/v1/endpoints/roster.py`** que llaman a
`_make_request`: `putonmarket`, `toggleplayer`, `myplayers`, `cancelsell`.
Quedan con su manejo actual como **deuda registrada** (fuera de alcance de U2).
Riesgo acotado: son acciones de usuario en el borde HTTP, no puntos de escritura
de la caché de sync donde un `None` corrompe datos.

## Contratos y modos de fallo de integración (FR4.5, BR7.1)

### Sofascore (API no oficial vía `curl_cffi`)
- **403 → `SofascoreIPBanError`** (subtipo de `IntegrationBanError`, **fatal**):
  se propaga; el punto de captura aborta limpio, sin datos a medias.
- **404 → `None`** (recurso ausente = "sin datos", **no** es fallo: no marca
  `DEGRADED` ni lanza excepción).
- **timeout / no parseable / error de request → recuperable.**
- Throttle preventivo (~750 ms) intacto. Sin cambios de código en U2 (ya
  entregado): U2 lo **consume** por la raíz `IntegrationError`.

### Futmondo (`_make_request`, endpoints heterogéneos)
- **`requests.exceptions.Timeout` → `IntegrationTimeoutError`** (recuperable).
- **`requests.exceptions.RequestException` → `IntegrationRequestError`**
  (recuperable por defecto; **fatal** si alcanza un punto de escritura con riesgo
  de corrupción — BR2.3).
- **`json.JSONDecodeError` → `IntegrationUnparseableError`** (recuperable).
- **No autenticado → `None`** (no es fallo de red; caso explícito, sin cambio).
- Mensajes de excepción en **inglés** (diagnóstico); nunca password/token.

## Decisiones clave

1. **Punto de captura recuperable/fatal en dos niveles.** `sync_prizes`
   (data_sync_service) reintercepta las excepciones tipadas ANTES de su
   `except Exception` genérico y **propaga** (fatal ban; y recuperable-en-punto-
   de-escritura por BR2.3, ya que las llamadas de integración de `sync_prizes`
   rodean el punto de escritura `team_prizes`), emitiendo el log estructurado. La
   ruta `_run_sync_in_background` (sync.py) es el punto de captura con
   `task_id`/sink: fatal → propaga (task FAILED); recuperable no-de-escritura →
   `record_degraded_step` + continúa. Así el sync no falla ante un recuperable
   benigno y aborta limpio ante fatal/corrupción.
2. **Writer atómico fuera del god-file.** `team_prizes_writer.replace_team_prizes`
   hace upsert de todas las filas + DELETE de las obsoletas en **una** transacción
   (contrato `db_connection`: commit al salir, rollback + re-raise ante
   excepción). Se retiró el `try/except → logger.warning` que tragaba el fallo del
   DELETE y dejaba estado mixto. `sync_prizes` acumula filas y llama al writer una
   vez (sustitución, no ampliación).
3. **Log estructurado sin credenciales.** `_log_integration_failure` emite
   `sync_step / failure_mode / status / endpoint / task_id / reason` (WARNING
   recuperable, ERROR fatal). Sólo recibe la excepción tipada (que por
   construcción no lleva credenciales) y campos no sensibles.
4. **`IntegrationRequestError` aditivo.** Extiende la jerarquía de U1 sin tocar
   god-files ni romper el test de U1 (que se re-ejecuta verde).

## Cobertura y verificación

- **Comando por-unidad** (unit-test-instructions.md), desde `backend/`:
  `test_futmondo_client_characterization.py`,
  `test_futmondo_client_typed_failures.py`,
  `test_sync_integration_failure_effect.py`,
  `test_team_prizes_atomic_replacement.py` → **17 passed, 3 xfailed**.
- **Suite completa** (sin regresión): **203 passed, 3 xfailed** (baseline previa
  186 passed; +17 nuevos). Los 3 `xfail` son los casos de caracterización del
  contrato ANTIGUO de `_make_request` (devolver `None`), que Step 3 cambió
  intencionadamente a lanzar — quedan como `xfail` documentando el cambio, no como
  regresión.
- **`ruff check`** (advisory) sobre los ficheros NUEVOS: *All checks passed*.
- `--cov` observabilidad-only, **sin piso bloqueante** (según Testing Contract);
  no se relajó ningún umbral.

## Desviaciones (registradas)

- **`ruff.toml` ya estaba en el estado objetivo de Step 7.** En HEAD, `ignore`
  ya era `["E501","E402"]` (E722 fuera) con el comentario de trinquete. Se
  verificó que la config del proyecto **reporta** E722 (`ruff check` sobre un
  bare-except lo marca). No se editó el fichero (no había línea que quitar), no
  se corrió `--fix` ni `ruff format`. Por eso **no** figura en
  `source-manifest.json` (no fue escrito por U2); el manifiesto refleja sólo los
  paths realmente creados/modificados para no invalidar el binding de fuente.
- **Un solo fichero de test por deliverable.** La caracterización de Step 5 (bug
  de estado mixto legacy + contrato all-or-nothing del context manager) se
  incluyó DENTRO de `test_team_prizes_atomic_replacement.py` (el fichero previsto
  en el plan para `team_prizes`), en vez de un fichero aparte, para que el comando
  por-unidad fingerprint-bound (4 ficheros) cubra toda la caracterización.
- **Formateo brownfield NO aplicado.** `ruff check` reporta I001/F401 preexistentes
  en `sync.py`, `data_sync_service.py`, `futmondo_client.py` (verificados contra
  HEAD como deuda previa, no introducida por U2). Según la regla afirmada, NO se
  reformatean en masa (inflaría diffs, expondría avisos ajenos e invalidaría el
  pase de revisión); sólo se formatearon quirúrgicamente los ficheros nuevos.

## Assumptions & Open Questions

None.
