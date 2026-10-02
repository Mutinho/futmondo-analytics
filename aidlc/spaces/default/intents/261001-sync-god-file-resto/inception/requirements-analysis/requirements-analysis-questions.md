# Requirements Analysis — Preguntas

> Intent `261001-sync-god-file-resto` (scope `refactor`, profundidad Minimal).
> La descripción del proyecto ya fija el patrón objetivo, el orden de extracción,
> la preservación de la superficie pública, characterization-first estricto,
> coste 0 €, el piso `--cov-fail-under=27` y el idioma. Estas preguntas sólo
> cubren los puntos genuinamente abiertos para fijar requisitos verificables.
> Idioma de conversación: castellano.

---

## Q1 — Granularidad de la unidad de trabajo / Bolt

La descripción dice "una unidad de trabajo por dominio" (8 dominios pendientes +
la uniformación de `prizes/`). ¿Cómo quieres estructurar el trabajo de cara al
plan de entrega?

- A. Una unidad por dominio, extraídas en el orden propuesto de menor a mayor acoplamiento (`clauses` → `transactions` → `punishments_bonuses` → `dream_teams` → `rosters` → `round_rankings`/`team_standings` → `player_performance` → `players_full`), más una unidad final para uniformar `prizes/`. Cada una characterization-first, verde, y entonces la siguiente.
- B. Lo mismo que A, pero `prizes/` primero (ya tiene cálculo + escritura atómica extraídos; sólo le falta el facade/orchestrator), como calentamiento del patrón antes de los 8 dominios.
- C. Agrupar dominios de baja complejidad en una sola unidad (p. ej. `clauses`+`transactions`) para reducir el número de Bolts.
- D. Dejar el agrupamiento y el orden exactos para confirmarlos en Plan Approval (delivery-planning), fijando aquí sólo "una unidad por dominio, orden de menor a mayor acoplamiento" como requisito.

[Answer]: A (recomendación aplicada por indicación del usuario, 2026-10-01) — una unidad por dominio en el orden propuesto de menor a mayor acoplamiento + unidad final para uniformar `prizes/`; characterization-first por dominio. El orden fino puede reconfirmarse en Plan Approval.

---

## Q2 — Alcance exacto del método público tras la extracción

Hoy 8 de 10 `sync_*` mezclan ingesta + SQL/persistencia + cálculo. Tras extraer
cada dominio, ¿qué debe quedar en el método público de `DataSyncService`?

- A. El método público queda como **delegación fina** al orchestrator del dominio (como `sync_match_odds` hoy): sin ingesta, sin SQL, sin `time.sleep` inline; sólo construir/obtener el orchestrator y devolver su `SyncResult`.
- B. Igual que A, pero se permite que el método público conserve el logging/formato del `SyncResult` y el manejo del `except Exception` final de red si eso reduce el riesgo de cambio observable.
- C. Otro reparto (especificar).

[Answer]: A (recomendación aplicada por indicación del usuario, 2026-10-01) — el método público queda como delegación fina al orchestrator del dominio (sin ingesta, sin SQL, sin `time.sleep` inline); devuelve el `SyncResult` del orchestrator.

---

## Q3 — Destino del SQL inline no estrictamente "de dominio"

Algunos `sync_*` ejecutan SQL que no es la persistencia principal del dominio:
`sync_transactions` hace `ALTER TABLE` + `UPDATE ... bids_json`; helpers como
`_enrich_market_values` (`SELECT`/`UPDATE`), `_save_favorites`
(`CREATE TABLE IF NOT EXISTS`/`DELETE`/`INSERT`) y el `SELECT user_championships`
de `sync_prizes`. ¿Dónde va ese SQL al extraer?

- A. Todo el SQL del dominio (incluidos `ALTER TABLE`/migraciones idempotentes y los helpers) va al `*_adapter` de infraestructura del dominio, envolviendo `DataManagerV2` verbatim; NUNCA se amplía `data_manager_v2.py` ni se deja SQL en el método de servicio.
- B. Igual que A para la persistencia principal, pero los `ALTER TABLE`/migraciones idempotentes y los helpers transversales (`_enrich_market_values`, `_save_favorites`) quedan **fuera de alcance** de este intent como deuda registrada, moviéndose sólo la persistencia principal del dominio.
- C. Otro (especificar).

[Answer]: B (recomendación aplicada por indicación del usuario, 2026-10-01) — la persistencia principal del dominio va a su `*_adapter` envolviendo `DataManagerV2` verbatim; los `ALTER TABLE`/migraciones idempotentes y los helpers transversales (`_enrich_market_values`, `_save_favorites`, `SELECT user_championships`) quedan como deuda registrada fuera de alcance. Nunca se amplía `data_manager_v2.py`.

---

## Q4 — Criterio de "equivalencia funcional estricta" (FR5) verificable

La descripción exige equivalencia funcional estricta sin cambio de comportamiento
observable. ¿Cuál es el criterio de aceptación verificable por dominio?

- A. Un test de caracterización por dominio que **congela el `SyncResult` observable** (todas sus claves con su forma exacta por dominio: `status`, `records_synced`, `last_sync_id`/`last_sync_matchday`/`rounds_synced`/`rounds_processed`+`stale_prizes_removed` según el dominio) con dobles/fakes en memoria, escrito ANTES de extraer y que debe seguir verde después; más la suite existente verde y el piso `--cov-fail-under=27` sin bajar.
- B. Igual que A pero además congelando las **llamadas a `DataManagerV2`** (qué métodos se invocan y con qué argumentos) para blindar que el adapter delega verbatim.
- C. Sólo la suite existente verde + piso de cobertura, sin test de caracterización nuevo por dominio.
- D. Otro (especificar).

[Answer]: B (recomendación aplicada por indicación del usuario, 2026-10-01) — test de caracterización por dominio que congela el `SyncResult` observable (claves con su forma exacta por dominio) Y las llamadas a `DataManagerV2` (métodos + argumentos), con dobles/fakes en memoria, escrito antes de extraer y verde después; más la suite existente verde y el piso `--cov-fail-under=27` sin bajar.

`_run_sync_in_background` (en `endpoints/sync.py`) replica el orden/claves de
`sync_all()` y añade `phantoms` fuera de la superficie de `DataSyncService`.
¿Qué requisito fijamos sobre él?

- A. El worker del router y `sync_all()` deben seguir invocando los 10 `sync_*` con **las mismas 10 claves literales y el mismo orden fijo** tras el refactor; `phantoms` sigue siendo un helper del router fuera de alcance; cualquier cambio de firma que rompa el worker está prohibido (FR5).
- B. Además de A, llevar también el SQL-en-router de `sync.py` (`_check_phantoms`, `get_last_sync_date`) tras un adapter en este intent.
- C. Otro (especificar).

[Answer]: A (recomendación aplicada por indicación del usuario, 2026-10-01) — `sync_all()` y el worker `_run_sync_in_background` siguen invocando los 10 `sync_*` con las mismas 10 claves literales y orden fijo; `phantoms` y el SQL-en-router de `sync.py` quedan fuera de alcance; prohibido cualquier cambio de firma que rompa el worker (FR5).

Los `sync_*` tienen `except Exception → return {"status":"error"}` de red final y
`time.sleep` de throttling inline; existe clasificación recoverable/fatal tipada
(`IntegrationBanError` fatal propaga; `IntegrationTimeout/Unparseable/Request`
degrada vía `record_degraded_step`). ¿Qué hacemos al extraer?

- A. **Preservar verbatim** el comportamiento de errores y throttling existente al moverlo al orchestrator (equivalencia estricta); no se reclasifica ni se "mejora" ningún `except` en este intent — sólo se reubica. La garantía de no-credenciales-en-logs (`_log_integration_failure`, NFR1/BR4.2) se mantiene.
- B. Igual que A, pero aprovechar para armonizar el manejo tipado recoverable/fatal en los dominios que hoy no lo tengan, siempre que no cambie el `SyncResult` observable.
- C. Otro (especificar).

[Answer]: A (recomendación aplicada por indicación del usuario, 2026-10-01) — preservar verbatim el comportamiento de errores y el throttling al reubicarlo en el orchestrator (equivalencia estricta); no se reclasifica ni se "mejora" ningún `except` en este intent. Se mantiene la garantía de no-credenciales-en-logs (`_log_integration_failure`, NFR1/BR4.2).

## Consolidated Summary Confirmation

Resumen de las decisiones (todas con recomendación del conductor aplicada por indicación del usuario):

- Q1 — Una unidad de trabajo por dominio, en orden de menor a mayor acoplamiento (`clauses` → `transactions` → `punishments_bonuses` → `dream_teams` → `rosters` → `round_rankings`/`team_standings` → `player_performance` → `players_full`) + unidad final para uniformar `prizes/`; characterization-first por dominio; orden fino reconfirmable en Plan Approval.
- Q2 — Cada método público queda como delegación fina al orchestrator del dominio (sin ingesta, sin SQL, sin `time.sleep` inline), devolviendo el `SyncResult` del orchestrator.
- Q3 — La persistencia principal del dominio va a su `*_adapter` (envuelve `DataManagerV2` verbatim); los `ALTER TABLE`/migraciones idempotentes y helpers transversales (`_enrich_market_values`, `_save_favorites`, `SELECT user_championships`) quedan como deuda registrada fuera de alcance; nunca se amplía `data_manager_v2.py`.
- Q4 — Criterio FR5 verificable: test de caracterización por dominio que congela el `SyncResult` observable y las llamadas a `DataManagerV2` (métodos + argumentos), con fakes en memoria, verde antes y después; suite existente verde; piso `--cov-fail-under=27` sin bajar.
- Q5 — `sync_all()` y el worker `_run_sync_in_background` preservan las 10 claves literales y el orden fijo; `phantoms` y el SQL-en-router de `sync.py` fuera de alcance; prohibido romper la firma del worker (FR5).
- Q6 — Manejo de errores y throttling se preservan verbatim al reubicarlos en el orchestrator (sin reclasificar `except`); se mantiene la garantía de no-credenciales-en-logs (NFR1/BR4.2).

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
