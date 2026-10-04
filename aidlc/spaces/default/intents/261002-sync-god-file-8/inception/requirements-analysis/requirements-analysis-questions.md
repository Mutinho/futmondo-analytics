# Requirements Analysis — Questions

Contexto: refactor brownfield, alcance y patrón ya muy definidos por la
descripción inicial y la memoria del proyecto (patrón DDD de los pilotos
`match_odds`/`clauses`, superficie pública congelada, characterization-first
estricto por dominio, una unidad de trabajo por dominio con gate por unidad,
coste 0 €, piso `--cov-fail-under=27` solo sube). Estas preguntas solo cubren
lo que NO está ya decidido, para no re-preguntar lo acordado.

## Q1. Orden de extracción de los 8 dominios

La descripción propone un orden de menor a mayor acoplamiento (confirmable en
Plan Approval): `transactions` → `punishments_bonuses` → `dream_teams_mvps` →
`rosters` → `round_rankings` (`team_standings`) → `player_performance` →
`players_full`; y la uniformización de `sync_prizes`. ¿Fijamos ese orden como
requisito, o lo dejamos como propuesto a confirmar en el diseño?

- A. Fijar exactamente ese orden como requisito
- B. Dejarlo como orden propuesto, confirmable en Functional Design / Plan Approval (Recommended)
- C. Empezar por `sync_prizes` (el más simple, lógica ya extraída) y luego el resto en ese orden
- D. Priorizar primero los dominios con SQL crudo sobre `self.dm.db` (transactions, rosters)
- X. Other (please specify)

[Answer]: B. Dejarlo como orden propuesto, confirmable en Functional Design / Plan Approval

## Q2. Alcance de los helpers con SQL crudo sobre `self.dm.db`

Varios dominios ejecutan SQL crudo directo sobre `self.dm.db` fuera de métodos
de `DataManagerV2` (`sync_transactions` ALTER/UPDATE, `_enrich_market_values`,
`_save_favorites` CREATE/DELETE/INSERT, `sync_prizes` vía `get_db()`). ¿Cómo se
tratan al extraer su dominio?

- A. Envolver ese SQL crudo verbatim dentro del `*_adapter` del dominio (único punto de infraestructura), sin tocar `data_manager_v2.py` (Recommended)
- B. Dejar el SQL crudo donde está y extraer solo el resto del dominio (deuda registrada)
- C. Elevar `_save_favorites` (DELETE+INSERT) al patrón set-replacement atómico (`team_prizes_writer`) y el resto envolver verbatim
- D. Decidir caso por caso en Functional Design
- X. Other (please specify)

[Answer]: A. Envolver ese SQL crudo verbatim dentro del `*_adapter` del dominio, sin tocar `data_manager_v2.py`

## Q3. Ubicación del helper compartido `_find_championship()`

`_find_championship()` lo comparten `dream_teams_mvps` y `rosters`. ¿Dónde vive
tras la extracción?

- A. Como helper compartido en un módulo común bajo `sync/` (p. ej. `sync/_shared/`)
- B. Duplicado/encapsulado en cada dominio que lo use (sin acoplamiento cruzado)
- C. Mantenerlo en el facade `DataSyncService` e inyectarlo a los orquestadores que lo necesiten (Recommended)
- D. Decidir en Functional Design según el acoplamiento real observado
- X. Other (please specify)

[Answer]: C. Mantenerlo en el facade `DataSyncService` e inyectarlo a los orquestadores que lo necesiten

## Q4. Criterio de equivalencia funcional (characterization) por dominio

FR5 exige equivalencia estricta sin cambio observable. ¿Qué nivel de congelación
caracterizamos por dominio antes de extraer?

- A. Congelar el payload observable del `SyncResult` (forma + claves + valores) por dominio, además del comportamiento de ingesta observable (límites de paginación, orden) (Recommended)
- B. Solo el `SyncResult` de cada `sync_*` (forma y claves)
- C. `SyncResult` + efectos de persistencia verificables en la BD fake in-memory
- D. Además, congelar el `time.sleep` de throttling (0.3/0.2/0.1/0.05) como parte del contrato observable
- X. Other (please specify)

[Answer]: A. Congelar el payload observable del `SyncResult` por dominio, además del comportamiento de ingesta observable (límites de paginación, orden)

## Q5. Tratamiento del `except: pass` silencioso en `sync_transactions`

En `sync_transactions` hay un `except: pass` silencioso alrededor de un
`ALTER TABLE ... IF NOT EXISTS` idempotente. ¿Qué hacemos al extraer?

- A. Preservarlo verbatim como comportamiento observable (equivalencia estricta); documentarlo como deuda registrada (Recommended)
- B. Reemplazarlo por manejo de error tipado / log explícito como parte de la extracción
- C. Dejarlo fuera del alcance de este intent (deuda registrada, sin tocar)
- X. Other (please specify)

[Answer]: A. Preservarlo verbatim como comportamiento observable (equivalencia estricta); documentarlo como deuda registrada

## Consolidated Summary Confirmation

Resumen de las decisiones de esta etapa:

- Alcance y patrón ya fijados por la descripción/memoria (no re-preguntados):
  descomponer los 8 dominios de sync inline + uniformar `sync_prizes` al patrón
  DDD de los pilotos `match_odds`/`clauses`; superficie pública congelada
  (10 `sync_*` + `sync_all()`, 10 claves literales, orden fijo); una unidad de
  trabajo por dominio con gate por unidad; characterization-first estricto;
  coste 0 €; piso `--cov-fail-under=27` solo sube; nunca ampliar/tocar
  `data_manager_v2.py`; sin reformateo masivo.
- Q1: El orden de extracción (transactions → punishments_bonuses →
  dream_teams_mvps → rosters → round_rankings/team_standings →
  player_performance → players_full → uniformar sync_prizes) queda como
  **orden propuesto**, confirmable en Functional Design / Plan Approval.
- Q2: El SQL crudo sobre `self.dm.db` se **envuelve verbatim** dentro del
  `*_adapter` de cada dominio (único punto de infraestructura), sin tocar
  `data_manager_v2.py`.
- Q3: El helper compartido `_find_championship()` se **mantiene en el facade
  `DataSyncService`** y se inyecta a los orquestadores que lo necesiten.
- Q4: La characterization por dominio congela el **payload observable del
  `SyncResult`** (forma + claves + valores) **y** el comportamiento de ingesta
  observable (límites de paginación, orden).
- Q5: El `except: pass` silencioso de `sync_transactions` (ALTER idempotente) se
  **preserva verbatim** como comportamiento observable y se documenta como deuda
  registrada.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
