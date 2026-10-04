# Requirements — Oleada 3c: descomposición de los 8 dominios de sync (`261002-sync-god-file-8`)

## Intent Analysis

El objetivo es terminar la descomposición de `backend/app/services/data_sync_service.py`
(~77 KB / ~1806 líneas) convirtiéndolo en un **facade delgado**: extraer los **8
dominios de sync que siguen inline** al patrón DDD ya **probado por dos pilotos**
(`sync/match_odds/` y `sync/clauses/`) y **uniformar `sync_prizes`** (cuyo cálculo
puro y escritor atómico ya viven en `prizes/`) a ese mismo patrón de facade. Es un
**refactor estructural con equivalencia funcional estricta**: no cambia ningún
comportamiento observable del sistema en producción; reorganiza dónde vive el
código y reduce la deuda del god-file sin ampliar `data_manager_v2.py`.

Meta final: los 10 dominios de sync viven bajo `backend/app/services/sync/<domain>/`
(orchestrator de aplicación + domain port consumer-owned + infrastructure adapter
que envuelve `DataManagerV2` verbatim), y `data_sync_service.py` queda como
coordinador fino que delega.

Origen de la intención: descripción inicial autoritativa (`project-description.json`),
continuación de los intents `260929-sync-god-file` y `261001-sync-god-file-resto`.

## Functional Requirements

### FR1 — Extracción de los 8 dominios de sync inline al patrón DDD
- **FR1.1**: Cada uno de los 8 dominios inline (`transactions`,
  `punishments_bonuses`, `dream_teams_mvps`, `rosters`, `round_rankings`,
  `player_performance`, `players_full`) debe quedar extraído bajo
  `backend/app/services/sync/<domain>/` replicando el molde de los pilotos:
  `orchestrator.py` (application), `domain/ports.py` (`typing.Protocol`
  consumer-owned, sin SQL ni framework) e `infrastructure/<domain>_adapter.py`
  (único punto que toca `DataManagerV2`, delegando verbatim).
- **FR1.2**: El método público `DataSyncService.sync_<domain>` correspondiente
  debe quedar como **delegación delgada**: import perezoso del orquestador y del
  adapter, instancia con `client=self.client`,
  `championship_id=self.championship_id`,
  `data=DataManager<Domain>Adapter(dm=self.dm)`, y `return orchestrator.sync()`.
- **FR1.3**: El adapter de cada dominio debe construir por defecto el adapter de
  producción (`DataManagerV2(skip_init=True)`) y, en operaciones como
  `update_sync_metadata`, reenviar **solo** los kwargs que la llamada inline
  original suministraba (fila persistida idéntica).
- **FR1.4**: El orden de extracción propuesto (menor a mayor acoplamiento:
  `transactions` → `punishments_bonuses` → `dream_teams_mvps` → `rosters` →
  `round_rankings` → `player_performance` → `players_full`) es **propuesto, no
  vinculante**; el orden definitivo se confirma en Functional Design / Plan
  Approval. (Q1)

### FR2 — Uniformización de `sync_prizes`
- **FR2.1**: `sync_prizes` debe quedar uniformado al patrón de facade: la
  **orquestación** se mueve a `sync/prizes/` (orchestrator) dejando el método
  público como delegación delgada, reutilizando el cálculo puro
  (`prizes/calculator.py`) y la escritura atómica
  (`prizes/team_prizes_writer.replace_team_prizes`) ya existentes.
- **FR2.2**: No se altera la lógica de cálculo de premios ni el patrón de
  escritura set-replacement atómico ya en producción.

### FR3 — Preservación de la superficie pública (contrato congelado)
- **FR3.1**: `DataSyncService` debe conservar byte-a-byte sus **10 métodos
  `sync_*`** y `sync_all()`.
- **FR3.2**: `sync_all()` debe mantener sus **10 claves literales y su orden
  fijo** (incluidas las divergencias nombre-método ↔ clave:
  `team_standings`↔`sync_round_rankings`, `dream_teams`↔`sync_dream_teams_mvps`),
  de las que depende el worker `_run_sync_in_background` del router.
- **FR3.3**: Las firmas públicas (parámetros, nombres) no cambian; cualquier
  cambio rompería el worker del router y queda prohibido.

### FR4 — Tratamiento del SQL crudo sobre `self.dm.db`
- **FR4.1**: El SQL crudo que hoy se ejecuta directamente sobre `self.dm.db`
  fuera de métodos de `DataManagerV2` (`sync_transactions` ALTER/UPDATE,
  `_enrich_market_values`, `_save_favorites` CREATE/DELETE/INSERT con rama
  Postgres `execute_values`, `sync_prizes` vía `get_db()`) debe **envolverse
  verbatim** dentro del `*_adapter` del dominio correspondiente —único punto de
  infraestructura—, **sin trasladarlo a `data_manager_v2.py`** ni reescribir el
  SQL. (Q2)
- **FR4.2**: El helper compartido `_find_championship()` (usado por
  `dream_teams_mvps` y `rosters`) **permanece en el facade `DataSyncService`** y
  se **inyecta** a los orquestadores que lo necesiten; no se duplica ni se crea
  un módulo compartido para él. (Q3)

### FR5 — Equivalencia funcional estricta (characterization-first)
- **FR5.1**: Antes de extraer cada dominio, se debe **congelar con tests de
  caracterización** su **payload observable del `SyncResult`** (forma, claves y
  valores) y su **comportamiento de ingesta observable** (límites de paginación,
  orden de operaciones). (Q4)
- **FR5.2**: Tras la extracción, el `SyncResult` y el comportamiento observable
  de cada dominio deben ser **idénticos** a los previos (equivalencia estricta,
  sin cambio observable).
- **FR5.3**: El `except: pass` silencioso de `sync_transactions` (alrededor de un
  `ALTER TABLE ... IF NOT EXISTS` idempotente) se **preserva verbatim** como
  comportamiento observable y se documenta como **deuda registrada**; no se
  reemplaza por manejo tipado en este intent. (Q5)

### FR6 — Unidad de trabajo por dominio con gate por unidad
- **FR6.1**: El trabajo se organiza como **una unidad por dominio**, con **gate
  por unidad**, de modo que un cierre prematuro deje dominios **completos y
  verificados**, nunca a medias.
- **FR6.2**: Cada unidad sigue el ciclo characterization-first: congelar el
  comportamiento observable → extraer → suite en verde → siguiente dominio.

## Non-Functional Requirements

- **NFR1 — Equivalencia observable**: ningún cambio de comportamiento observable
  en producción; el refactor es transparente para el frontend y las integraciones.
- **NFR2 — Integridad de los god-files**: `data_manager_v2.py` (~166 KB) **no se
  amplía ni se modifica**; `data_sync_service.py` solo se reduce (métodos a
  delegación delgada), nunca se amplía con lógica nueva.
- **NFR3 — Cobertura (ratchet)**: el piso backend `--cov-fail-under=27`
  (line-coverage total en `pytest.ini`) **no se relaja**; solo sube por
  trinquete. La suite existente debe quedar **en verde** tras cada unidad.
- **NFR4 — Gate de CI bloqueante**: `gitleaks` + `pytest` + `ng test` deben pasar
  antes de fusionar a `main`; un rojo nunca llega a producción.
- **NFR5 — No credenciales en errores/logs**: ninguna credencial ni token
  Futmondo/Sofascore puede alcanzar el mensaje de excepción, el `repr`, el
  `exc_info` ni los logs de ningún adapter extraído; se preserva la garantía
  existente (`_log_integration_failure`).
- **NFR6 — Coste 0 €**: solo tiers gratuitos (Neon free, Fly.io free allowance,
  GitHub Actions free); no se introduce ninguna dependencia nueva (stdlib
  suficiente); cualquier librería hipotética sería OSS y fijada a versión exacta.
- **NFR7 — Formateo brownfield**: no se reformatea en masa con `ruff format`;
  solo ficheros nuevos o de forma quirúrgica.
- **NFR8 — Idioma**: identificadores, docstrings y comentarios en **inglés**;
  texto de usuario y mensajes de commit (Conventional Commits con scope) en
  **castellano**.
- **NFR9 — Tests sin red/BD real**: los tests usan dobles/fakes en memoria
  (patrón `conftest.py`), sin red, sin BD real y sin credenciales/tokens reales;
  specs que aseveran el efecto, nunca `assert True` ni specs espejo.

## Constraints

- Patrón de referencia **fijo**: el molde exacto son los pilotos
  `sync/match_odds/` y `sync/clauses/` (orchestrator + domain port + adapter);
  `prizes/` aporta el cálculo puro y la escritura atómica.
- Manejo de errores de integración existente: fatal `IntegrationBanError`
  propaga; recoverable (`IntegrationTimeoutError` / `IntegrationUnparseableError`
  / `IntegrationRequestError`) degrada vía `record_degraded_step`. Se preserva.
- El `time.sleep` de throttling (0.3/0.2/0.1/0.05 según dominio) y los límites de
  paginación (50 vs 1000) son comportamiento observable a preservar por el
  orquestador de cada dominio.
- Trunk-based, squash-merge a `main`; cada unidad en su commit con Conventional
  Commits en castellano.

## Assumptions

- Las fixtures fake in-memory de `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`
  SQLite `:memory:`) son suficientes para caracterizar el `SyncResult` y los
  efectos de persistencia de los 8 dominios sin red ni BD real.
- La divergencia de forma del `SyncResult` entre dominios es intencional y debe
  reproducirse byte-a-byte; no se busca uniformar la forma del payload en este
  intent.
- `_find_price_at_date` (helper puro de `transactions`, sin I/O) es candidato
  natural a vivir en la capa `domain/` de su dominio; su ubicación final se
  decide en Functional Design.

## Out of Scope

- Reescribir o reducir `data_manager_v2.py`.
- Retirar el SQL-en-router (`_check_phantoms`, `get_last_sync_date`,
  `sync.py`): queda como deuda documentada, fuera de este intent.
- Reclasificar/eliminar el `except: pass` silencioso de `sync_transactions`
  (se preserva verbatim; FR5.3).
- Elevar `_save_favorites` al patrón set-replacement atómico (no es objetivo de
  este intent; se envuelve verbatim como el resto del SQL crudo — FR4.1).
- Uniformar la forma del `SyncResult` entre dominios.
- Cambios en el frontend, el pipeline de deploy o los crons.

## Open Questions

- Orden definitivo de extracción de los 8 dominios (FR1.4): se confirma en
  Functional Design / Plan Approval.
- Ubicación final del helper puro `_find_price_at_date` (`domain/` vs
  orchestrator) de `transactions`: se decide en Functional Design.

## Sources

- [desc] Initial description: `project-description.json`
  (`261002-sync-god-file-8`), obtenida verbatim vía
  `aidlc engine workspace project-description`.
- [scope] Workflow-selected scope: `refactor` (depth Minimal, test strategy
  Minimal), de `aidlc-state.md`.
- [memory:M1] `project.md` / `team.md`: superficie pública congelada, nunca
  ampliar god-files, piso `--cov-fail-under=27` solo sube, coste 0 €, idioma
  código/usuario, characterization-first, no reformateo masivo.
- Reverse-engineering CodeKB (`aidlc/spaces/default/codekb/futmondo-analytics/`):
  `business-overview.md`, `architecture.md`, `code-structure.md` — patrón DDD de
  los pilotos, los 8 dominios inline, SQL crudo sobre `self.dm.db`, helpers
  compartidos, superficie pública.
- [Q1]–[Q5] Respuestas de la entrevista de esta etapa
  (`requirements-analysis-questions.md`).

## Assumptions & Open Questions

Ver las secciones **Assumptions** y **Open Questions** arriba. No quedan
contradicciones sin resolver entre las respuestas de la entrevista.
