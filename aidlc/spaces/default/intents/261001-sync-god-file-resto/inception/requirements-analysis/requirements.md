# Requirements — Oleada 3b god-files (`261001-sync-god-file-resto`)

> Scope `refactor`, profundidad Minimal. Continuación de `260929-sync-god-file`
> (FR13). Equivalencia funcional estricta, coste 0 €. Idioma: identificadores,
> docstrings y comentarios en INGLÉS; texto de usuario y mensajes de commit en
> CASTELLANO.

## Sources

- `[desc]` Initial description: `project-description.json` (descripción
  autoritativa del intent — descomponer el resto de `data_sync_service.py`
  extrayendo los dominios de sync pendientes al patrón DDD del piloto
  `match_odds` y uniformar `prizes/`).
- `[scope]` Workflow-selected scope: `refactor` (profundidad Minimal).
- CodeKB (reverse-engineering 2.1): `business-overview.md`, `architecture.md`,
  `code-structure.md` (superficie pública de sync, patrón objetivo DDD,
  anti-patrones heredados, formas de `SyncResult` por dominio).
- `[Q1]`–`[Q6]` `requirements-analysis-questions.md` (decisiones confirmadas en
  el resumen consolidado).
- `[memory]` `project.md` / `team.md` (reglas afirmadas: no ampliar god-files,
  no SQL-en-router, no `ruff format` masivo, piso de cobertura sólo sube,
  no-credenciales-en-logs, patrón de escritura atómica).

## Intent analysis

El objetivo es dejar `backend/app/services/data_sync_service.py` como un **facade
delgado**: cada operación de sincronización por dominio pasa a vivir bajo
`backend/app/services/sync/<domain>/` siguiendo el patrón hexagonal por dominio
ya probado end-to-end por el piloto `match_odds` (orchestrator de aplicación +
domain port `Protocol` consumer-owned + infrastructure `*_adapter` que envuelve
`DataManagerV2` verbatim), y uniformar el contexto `prizes/` (ya con cálculo y
escritura atómica extraídos) al mismo patrón de facade. No se añade ni se cambia
comportamiento observable: es una reestructuración interna con **equivalencia
funcional estricta**. El valor es reducir la deuda del god-file (~84 KB), hacer
cada dominio testeable de forma aislada y preservar la superficie pública de la
que depende el worker del router y el frontend.

## Functional requirements

### FR1 — Descomposición por dominio al patrón DDD `[desc]`,`[Q1]`,`CodeKB:code-structure`
- **FR1.1** Extraer cada uno de los 8 dominios de sync pendientes (`clauses`,
  `transactions`, `punishments_bonuses`, `dream_teams`, `rosters`,
  `round_rankings` con clave literal `team_standings`, `player_performance`,
  `players_full`) a su propio contexto bajo `backend/app/services/sync/<domain>/`.
- **FR1.2** Cada contexto replica la estructura del piloto `match_odds`:
  `orchestrator.py` (capa application: ingesta vía `FutmondoClient` inyectado,
  throttling, manejo de errores, delegación al port), `domain/ports.py`
  (`typing.Protocol` consumer-owned, sin SQL ni framework) e
  `infrastructure/<domain>_adapter.py` (único punto con SQL; envuelve
  `DataManagerV2` verbatim).
- **FR1.3** El trabajo se organiza como **una unidad por dominio**, en orden de
  menor a mayor acoplamiento (`clauses` → `transactions` → `punishments_bonuses`
  → `dream_teams` → `rosters` → `round_rankings`/`team_standings` →
  `player_performance` → `players_full`), más una unidad final para `prizes/`.
  Pass/fail: existe exactamente una unidad de trabajo por dominio. `[assumption]`
  El orden fino es reconfirmable en Plan Approval (delivery-planning).

### FR2 — Facade delgado por delegación fina `[Q2]`,`CodeKB:architecture`
- **FR2.1** Tras extraer un dominio, su método público en `DataSyncService`
  queda como **delegación fina** al orchestrator del dominio (como
  `sync_match_odds` hoy): sin ingesta, sin SQL, sin `time.sleep` inline.
- **FR2.2** El método público devuelve el `SyncResult` producido por el
  orchestrator, sin reformatearlo. Pass/fail: el cuerpo del método no contiene
  llamadas a `FutmondoClient`, SQL, ni `time.sleep`.

### FR3 — Ubicación del SQL `[Q3]`,`[memory]`,`CodeKB:code-structure`
- **FR3.1** La persistencia principal de cada dominio va a su
  `infrastructure/<domain>_adapter.py`, que envuelve `DataManagerV2` **verbatim**
  (los mismos métodos con los mismos argumentos). Nunca se amplía ni se modifica
  `data_manager_v2.py`.
- **FR3.2** Los `ALTER TABLE`/migraciones idempotentes y los helpers
  transversales (`_enrich_market_values`, `_save_favorites`, el
  `SELECT user_championships` de `sync_prizes`) quedan **fuera de alcance** de
  este intent como deuda registrada; sólo se mueve la persistencia principal del
  dominio. Pass/fail: el método de servicio extraído no contiene SQL; la deuda
  transversal queda documentada en "Out of scope".

### FR4 — Uniformar `prizes/` al patrón de facade `[desc]`,`[Q1]`,`CodeKB:component-inventory`
- **FR4.1** Dotar a `prizes/` del facade/orchestrator uniforme (comparable con
  `analytics/__init__.py` y `assistant/__init__.py`, que re-exportan desde
  `facade.py`), conservando el cálculo puro (`calculator.py`) y la escritura
  atómica set-replacement (`team_prizes_writer.replace_team_prizes`).
- **FR4.2** `sync_prizes` queda como delegación fina a ese facade/orchestrator,
  preservando su `SyncResult` observable (`rounds_processed`,
  `stale_prizes_removed`).

### FR5 — Equivalencia funcional estricta (superficie pública) `[desc]`,`[Q4]`,`[Q5]`,`CodeKB:api-documentation`
- **FR5.1** La superficie pública se preserva byte-a-byte: `DataSyncService` con
  sus 10 métodos `sync_*` y `sync_all()`.
- **FR5.2** `sync_all()` sigue devolviendo las **10 claves literales en el orden
  fijo**: `players`, `transactions`, `clauses`, `punishments_bonuses`,
  `dream_teams`, `player_performance`, `rosters`, `team_standings`, `match_odds`,
  `prizes`.
- **FR5.3** El `SyncResult` observable de cada dominio conserva su forma exacta
  (las claves y su tipo varían por dominio: `status`, `records_synced`,
  `last_sync_id` / `last_sync_matchday` / `rounds_synced` /
  `rounds_processed`+`stale_prizes_removed` según el dominio).
- **FR5.4** El worker del router `_run_sync_in_background` (`endpoints/sync.py`)
  sigue invocando los 10 `sync_*` con el mismo orden y claves. Está **prohibido**
  cualquier cambio de firma que lo rompa.

### FR6 — Manejo de errores y throttling preservados `[Q6]`,`[memory]`,`CodeKB:architecture`
- **FR6.1** Al reubicar cada dominio en su orchestrator, el comportamiento de
  errores y el throttling (`time.sleep`) se preservan **verbatim**: no se
  reclasifica ni se "mejora" ningún `except` en este intent — sólo se reubica.
- **FR6.2** Se mantiene la clasificación tipada existente donde ya exista (fatal
  `IntegrationBanError` propaga; recoverable `IntegrationTimeoutError` /
  `IntegrationUnparseableError` / `IntegrationRequestError` degrada vía
  `record_degraded_step`), sin extenderla a dominios que hoy no la tengan.
- **FR6.3** Ninguna credencial ni token Futmondo del usuario aparece en el
  mensaje, el `repr`, el `exc_info` ni los logs de una excepción
  (`_log_integration_failure`, NFR1/BR4.2).

### FR7 — Caracterización primero por dominio `[Q4]`,`[memory]`
- **FR7.1** Antes de extraer un dominio se escribe un test de caracterización que
  **congela el `SyncResult` observable** del método público, usando dobles/fakes
  en memoria (patrón `conftest.py`), sin red, sin BD real y sin
  credenciales/tokens reales.
- **FR7.2** El test congela además las **llamadas a `DataManagerV2`** (qué
  métodos se invocan y con qué argumentos) para blindar que el adapter delega
  verbatim.
- **FR7.3** El test está verde antes de la extracción y debe seguir verde
  después (equivalencia). Los tests aseveran el efecto; nunca `assert True` ni
  specs espejo que inflen cobertura.

## Non-functional requirements

### NFR1 — Seguridad / secretos
- **NFR1.1** No se incluyen credenciales ni tokens reales en código, specs ni
  logs; los tests usan fakes en memoria (gitleaks escanea también los tests).
- **NFR1.2** Se preserva la garantía de no-credenciales-en-logs de FR6.3.

### NFR2 — Cobertura y gate de CI
- **NFR2.1** El piso `--cov-fail-under=27` (line-only, en `pytest.ini`) no se
  relaja; el ratchet sólo sube. Si aparece flapping, se arregla el test
  no-determinista, nunca se baja el piso.
- **NFR2.2** El gate de CI bloqueante (gitleaks + `pytest` + `ng test`) debe
  seguir verde antes de fusionar a `main`.

### NFR3 — Coste y dependencias
- **NFR3.1** Coste 0 €: sólo tiers gratuitos (Neon free, Fly.io free allowance,
  GitHub Actions free). No se introducen dependencias de pago; cualquier
  librería nueva sería OSS y fijada a versión exacta (no se prevé ninguna —
  stdlib suficiente: `typing.Protocol`, `dataclasses`).

### NFR4 — Mantenibilidad del diff
- **NFR4.1** No se ejecuta `ruff format` masivo sobre ficheros brownfield ya
  modificados; sólo se formatean quirúrgicamente los ficheros nuevos de cada
  dominio.
- **NFR4.2** Cada dominio se extrae tras una capa/función estrecha y testeable;
  no se amplían los god-files (`data_sync_service.py`, `data_manager_v2.py`) ni
  el patrón SQL-en-router.

## Constraints

- Python 3.12 (backend) + FastAPI; frontend Angular fuera de alcance.
- `DataManagerV2` (`data_manager_v2.py`, ~166 KB) NO se amplía ni se toca; sólo
  se envuelve verbatim desde los adapters.
- El patrón objetivo y el molde a replicar están fijados por el piloto
  `sync/match_odds/`.
- Idioma: identificadores/docstrings/comentarios en inglés; texto de usuario y
  mensajes de commit (Conventional Commits con scope) en castellano.

## Assumptions

- `[assumption]` El orden fino de extracción (y un posible agrupamiento) se
  reconfirma en Plan Approval; aquí se fija sólo "una unidad por dominio, orden
  de menor a mayor acoplamiento" (FR1.3).
- `[assumption]` Las formas de `SyncResult` por dominio observadas en el escaneo
  son completas; cada caracterización (FR7) las verifica antes de extraer.

## Out of scope

- Descomposición o reescritura de `data_manager_v2.py` (god-file; deuda
  registrada).
- Retirada del SQL-en-router de `endpoints/sync.py` (`_check_phantoms`,
  `get_last_sync_date`) y el helper `phantoms` del worker.
- Migraciones idempotentes `ALTER TABLE`/`CREATE TABLE IF NOT EXISTS` y helpers
  transversales (`_enrich_market_values`, `_save_favorites`, el
  `SELECT user_championships` de `sync_prizes`) — deuda registrada (FR3.2).
- Reclasificación o "mejora" del manejo de `except` más allá de reubicarlo
  verbatim (FR6.1).
- Cambios en el frontend, auth, analytics o assistant.
- Subir umbrales de cobertura más allá de preservar el piso vigente.

## Open questions

- Ninguna bloqueante. El orden/agrupamiento exacto de las unidades se cierra en
  delivery-planning (ver FR1.3), fuera del alcance de requisitos.
