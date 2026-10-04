# Functional Design — Questions (unit: sync-domains-decomposition)

Intent: `261002-sync-god-file-8` — descomposición de los dominios de sync inline
del god-file `data_sync_service.py` al patrón DDD de los pilotos + uniformización
de `sync_prizes`. Scope `refactor` (depth Minimal). Equivalencia funcional
estricta.

El patrón de referencia (orchestrator + domain port consumer-owned + adapter que
envuelve `DataManagerV2` verbatim) ya está **fijado y probado** por los pilotos
`sync/match_odds/` y `sync/clauses/`, y la superficie pública (`requirements.md`
FR3) ya está congelada. Casi todas las decisiones de diseño están resueltas en
requirements. Estas preguntas cubren sólo los **huecos genuinos** que requirements
dejó abiertos (secciones Open Questions), más una confirmación del orden de las
unidades.

---

## Q1. Orden definitivo de extracción de los dominios (FR1.4)

El orden propuesto en requirements va de menor a mayor acoplamiento:
`transactions` → `punishments_bonuses` → `dream_teams_mvps` → `rosters` →
`round_rankings` → `player_performance` → `players_full`, cerrando con la
uniformización de `sync_prizes`. Es "propuesto, no vinculante" y se confirma
aquí. ¿Qué orden fijamos como secuencia de unidades?

A. Confirmar el orden propuesto tal cual (menor→mayor acoplamiento), con
   `sync_prizes` al final como uniformización.
B. Confirmar el orden propuesto pero mover `sync_prizes` al principio (su cálculo
   puro y escritor atómico ya existen en `prizes/`, es la extracción más barata).
C. Otro orden (lo indico en el detalle).
X. Other (please specify)

[Answer]: A. Confirmar el orden propuesto tal cual (menor→mayor acoplamiento), con `sync_prizes` al final como uniformización. **Mode:** guided

---

## Q2. Ubicación final del helper puro `_find_price_at_date` del dominio `transactions` (FR hueco en Open Questions)

`_find_price_at_date(prices, txn_date, prefer_previous_day)` es un helper **puro,
sin I/O** usado dentro de `_enrich_market_values` de `transactions`. Requirements
lo marca como "candidato natural a vivir en la capa `domain/`". ¿Dónde vive su
código tras la extracción?

A. En la capa `domain/` del dominio `transactions` (p. ej.
   `sync/transactions/domain/pricing.py`), como función pura reutilizable, sin
   I/O ni framework — alineado con el espíritu DDD de los pilotos.
B. Como método/función privada dentro del `orchestrator.py` de `transactions`
   (lo mantiene junto a su único llamador, mínima superficie nueva).
C. Lo decide el implementador en code-generation según resulte más limpio, sin
   fijarlo aquí.
X. Other (please specify)

[Answer]: A. En la capa `domain/` del dominio `transactions` (p. ej. `sync/transactions/domain/pricing.py`), como función pura reutilizable, sin I/O ni framework. **Mode:** guided

---

## Q3. Tratamiento de `_find_championship()` y los helpers con SQL/I-O crudo compartidos

Requirements (FR4.2) fija que `_find_championship()` **permanece en el facade
`DataSyncService`** y se **inyecta** a los orquestadores que lo necesiten
(`dream_teams_mvps`, `rosters`); no se duplica ni se crea módulo compartido. Los
otros helpers con SQL crudo (`_store_bids`, `_enrich_market_values`,
`_save_favorites`, `_find_price_at_date`) pertenecen cada uno a un único dominio
(`transactions`). ¿Confirmamos este reparto de helpers como diseño?

A. Confirmar FR4.2 tal cual: `_find_championship` se queda en el facade y se
   inyecta como dependencia (callable) a los orquestadores de `dream_teams_mvps`
   y `rosters`; los helpers mono-dominio migran dentro de su dominio (en adapter
   si tocan `self.dm.db`/SQL, en domain/orchestrator si son puros).
B. Mover también `_find_championship` dentro de un dominio o módulo compartido
   (desvío de FR4.2 — lo justifico en el detalle).
X. Other (please specify)

[Answer]: A. Confirmar FR4.2 tal cual: `_find_championship` se queda en el facade y se inyecta como dependencia (callable) a los orquestadores de `dream_teams_mvps` y `rosters`; los helpers mono-dominio migran dentro de su dominio (en adapter si tocan `self.dm.db`/SQL, en domain/orchestrator si son puros). **Mode:** guided

---

## Consolidated Summary Confirmation

Resumen de decisiones:

- Patrón: orchestrator (application) + domain port consumer-owned (`typing.Protocol`, sin SQL/framework) + infrastructure adapter que envuelve `DataManagerV2` verbatim, replicando los pilotos `sync/match_odds/` y `sync/clauses/`. Cada `sync_<domain>` del facade queda como delegación delgada.
- Q1: Orden de unidades confirmado menor→mayor acoplamiento: `transactions` → `punishments_bonuses` → `dream_teams_mvps` → `rosters` → `round_rankings` → `player_performance` → `players_full`, cerrando con la uniformización de `sync_prizes`.
- Q2: `_find_price_at_date` (puro) vive en `sync/transactions/domain/` (p. ej. `pricing.py`).
- Q3: `_find_championship` permanece en el facade e inyectado como callable a `dream_teams_mvps` y `rosters`; los helpers mono-dominio migran dentro de su dominio (SQL crudo → adapter; puros → domain/orchestrator).
- Equivalencia funcional estricta (FR5): `SyncResult` y comportamiento observable idénticos; `except: pass` de `sync_transactions` preservado verbatim como deuda registrada; SQL crudo envuelto verbatim sin tocar `data_manager_v2.py`.
- Superficie pública congelada (FR3): 10 métodos `sync_*` + `sync_all()` con sus 10 claves literales y orden fijo (incluidas las divergencias `team_standings`↔`sync_round_rankings`, `dream_teams`↔`sync_dream_teams_mvps`).

- Looks correct
- Request changes

[Answer]: Looks correct
