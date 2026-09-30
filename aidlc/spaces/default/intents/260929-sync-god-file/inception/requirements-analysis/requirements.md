# Requisitos — Oleada 3 god-files: descomposición de `data_sync_service.py`

Intent: `sync-god-file` (FR13) · scope `refactor` · depth Minimal · Brownfield en producción.

## Análisis de intención

El objetivo es **eliminar deuda estructural sin cambiar comportamiento**: descomponer el
god-file `backend/app/services/data_sync_service.py` (~84 KB, 1955 líneas) en un módulo de
aplicación por dominio de sincronización, siguiendo el patrón DDD hexagonal ya establecido y
probado en las oleadas previas (`prizes/`, `analytics/`, `assistant/`). No se busca añadir
funcionalidad ni mejorar el comportamiento observable: se busca que el mismo contrato público
(`DataSyncService` con sus 10 `sync_*` + `sync_all()`) quede respaldado por una estructura
mantenible, testeable y coherente con el resto del backend, protegido por caracterización
previa por dominio. El valor es de mantenibilidad y testabilidad, no de negocio de cara al
usuario.

Los 10 dominios de sync son: `transactions`, `clauses`, `punishments` (`sync_punishments_bonuses`),
`dream_teams` (`sync_dream_teams_mvps`), `performance` (`sync_player_performance`), `rosters`,
`rankings` (`sync_round_rankings`), `players` (`sync_players_full`), `odds` (`sync_match_odds`)
y `prizes` (ya extraído, patrón de referencia).

## Requisitos funcionales

### FR1 — Preservación de la superficie pública de sincronización
- **FR1.1** — `DataSyncService` DEBE seguir existiendo como clase con exactamente las 10
  operaciones públicas `sync_*` (`sync_transactions`, `sync_clauses`, `sync_punishments_bonuses`,
  `sync_dream_teams_mvps`, `sync_player_performance`, `sync_rosters`, `sync_round_rankings`,
  `sync_players_full`, `sync_match_odds`, `sync_prizes`) más `sync_all()`, con las mismas firmas
  e igual ruta de import que hoy.
- **FR1.2** — Tras el refactor, `DataSyncService` DEBE actuar como **facade delgado** que delega
  cada `sync_*` en su módulo de aplicación de dominio; no contiene lógica de ingesta, cálculo ni
  SQL propia.
- **FR1.3** — Donde un import histórico apunte a símbolos internos que se muevan de
  `data_sync_service.py`, DEBE dejarse un **shim de re-export** puntual que preserve esa ruta
  (patrón `analytics_service.py`/`assistant_service.py`). Criterio verificable: ningún llamador
  existente (`api/v1/endpoints/sync.py`, `data_initializer*.py`, tests) cambia sus imports.
- **FR1.3.1** — Antes de mover código, DEBE producirse un **inventario de imports**: enumerar qué
  símbolos de `data_sync_service.py` se importan desde fuera del propio módulo (grep de los
  llamadores en `backend/`), para decidir de forma verificable qué rutas necesitan shim de
  re-export. El shim se añade solo para los símbolos que ese inventario demuestre consumidos
  externamente y que se muevan.

### FR2 — Descomposición por dominio bajo el patrón DDD objetivo
- **FR2.1** — Cada uno de los 10 dominios de sync DEBE quedar en su propio módulo de aplicación,
  replicando el layering demostrado en `analytics/`/`assistant/`: `domain/` (port `Protocol`
  consumer-owned, sin SQL), `application/` (lógica de dominio pura sobre el port),
  `infrastructure/*_adapter.py` (único sitio con SQL) y un punto de entrada de aplicación fino.
- **FR2.2** — `sync_all()` DEBE quedar como **coordinador delgado** que invoca los 10 `sync_*` en
  el orden actual (players primero por dependencia FK) y agrega los resultados por dominio, sin
  lógica de dominio propia.
- **FR2.3** — `sync_prizes` (ya delegado en `prizes/`) es el patrón de referencia; los demás
  dominios DEBEN alinearse a él. No se re-extrae `prizes` salvo lo necesario para uniformar el
  facade.

### FR3 — Acceso a datos tras adaptador de infraestructura
- **FR3.1** — Cada dominio extraído DEBE acceder a la persistencia **solo a través de un adaptador
  de infraestructura** (`Protocol`/port + `*_adapter.py`), no llamando a `DataManagerV2` desde la
  capa de aplicación.
- **FR3.2** — El SQL existente de cada dominio DEBE **envolverse** en su adaptador, no reescribirse;
  `data_manager_v2.py` no se toca ni se amplía.

### FR4 — Caracterización previa por dominio (characterization-first)
- **FR4.1** — Antes de extraer un dominio DEBE congelarse su comportamiento observable con tests de
  caracterización (dobles/fakes en memoria del patrón `conftest.py`, sin red ni BD real ni
  credenciales).
- **FR4.2** — El trabajo procede de forma incremental **una unidad por dominio**: congelar →
  extraer → suite en verde → siguiente dominio. El orden concreto de los dominios se decide en la
  etapa de diseño/planificación.
- **FR4.3** — `prizes` y los flujos de integración/degradado ya caracterizados (p. ej.
  `test_prizes_characterization.py`, `test_sync_degraded_steps.py`,
  `test_sync_integration_failure_effect.py`) se reutilizan; los **9 dominios restantes** sin
  caracterización directa (`transactions`, `clauses`, `punishments_bonuses`, `dream_teams_mvps`,
  `player_performance`, `rosters`, `round_rankings`, `players_full`, `match_odds`) DEBEN
  caracterizarse antes de su extracción (9 de 10; `prizes` ya está extraído).

### FR5 — Equivalencia funcional estricta (sin cambio de comportamiento)
- **FR5.1** — Cada `sync_*` DEBE devolver el **mismo payload de resultado** (estructura y campos)
  que antes del refactor.
- **FR5.1.1** — El dict agregado que devuelve `sync_all()` DEBE conservar exactamente sus **10 claves
  literales** observables, sin renombrar ninguna: `players`, `transactions`, `clauses`,
  `punishments_bonuses`, `dream_teams`, `player_performance`, `rosters`, `team_standings`,
  `match_odds`, `prizes`. Nota de equivalencia: el dominio `rankings` (operación
  `sync_round_rankings`) expone su resultado bajo la clave `team_standings`; el nombre de dominio y
  la clave de payload difieren y AMBOS se preservan tal cual. Estas 10 claves literales se congelan
  como parte de la caracterización previa (FR4).
- **FR5.2** — DEBE preservarse el orden de ejecución en `sync_all()` (players primero por FK) y la
  agregación de resultados por dominio.
- **FR5.3** — DEBE preservarse el manejo de errores tipados de integración (`Integration*Error`) y
  el throttling (`time.sleep()`) tal como se observa hoy.
- **FR5.4** — DEBE preservarse la escritura atómica set-replacement de `prizes`
  (`replace_team_prizes`: upsert del conjunto + `DELETE ... NOT IN` en una sola transacción,
  all-or-nothing).

## Requisitos no funcionales

### NFR1 — Coste 0 €
- El refactor NO introduce dependencias de pago ni servicios que fuercen salir de los tiers
  gratuitos (Neon free, Fly.io free allowance, GitHub Actions free). Cualquier librería nueva sería
  OSS fijada a versión exacta (no se prevé ninguna; stdlib suficiente).

### NFR2 — Piso de cobertura backend (trinquete)
- El piso `--cov-fail-under=27` (line-only) en `pytest.ini` NO se relaja para pasar el gate; solo
  sube por trinquete. La caracterización nueva puede subir la cobertura; nunca bajar el piso. El
  gate de CI bloqueante (gitleaks + `pytest` + `ng test`) DEBE quedar en verde en ambos gates (PR y
  job `verify`) antes de fusionar a `main`.

### NFR3 — No ampliar god-files ni reformateo masivo
- NO se amplían ni reescriben los god-files (`data_sync_service.py`, `data_manager_v2.py`,
  `assistant_service.py`); el código nuevo va en los módulos de dominio nuevos. NO se ejecuta
  `ruff format` masivo sobre ficheros brownfield; solo se formatean los ficheros nuevos o de forma
  quirúrgica. `ruff check` (bloqueante) DEBE pasar sin `--fix` masivo.

### NFR4 — Convenciones de idioma en el código
- Identificadores, docstrings y comentarios en INGLÉS; texto de cara al usuario y mensajes de commit
  (Conventional Commits con scope) en CASTELLANO.

## Restricciones

- **C1** — Sistema brownfield en producción (Fly.io región `cdg`, Neon PostgreSQL Frankfurt); el
  refactor no cambia topología ni orden de despliegue.
- **C2** — Trunk-based sobre `main`, squash-merge, gate de CI obligatorio; cada cambio en rama corta.
- **C3** — Tests con dobles/fakes en memoria (`conftest.py`), sin red, sin BD real, sin
  credenciales/tokens reales (gitleaks escanea también los tests).
- **C4** — Posture test-after: specs que aseveran el efecto (payload/estado/modo de fallo), nunca
  `assert True` ni specs espejo que inflen cobertura.

## Assumptions & Open Questions

### Assumptions
- **[assumption]** El contrato público relevante es exactamente `DataSyncService` + los 10 `sync_*` +
  `sync_all()`; no hay otros símbolos públicos de `data_sync_service.py` consumidos fuera del módulo
  más allá de los detectables por import. (Confirmado por reverse-engineering; a validar por dominio
  al caracterizar.)
- **[assumption]** El orden fijo de `sync_all()` (players primero por FK) es comportamiento
  observable a preservar, no un detalle interno reordenable.
- **[assumption]** Los 8 dominios sin suite de caracterización directa pueden congelarse con los
  fakes en memoria existentes sin necesidad de infraestructura de test nueva.

### Open Questions
- El **orden concreto** de extracción de los 10 dominios (p. ej. de menor a mayor acoplamiento) se
  resuelve en diseño/planificación (FR4.2).
- Si al caracterizar un dominio aparece comportamiento no evidente hoy (ramas de error silenciosas),
  se congela tal cual y se registra como deuda, sin corregirlo en este intent (ver Out of scope).

## Out of scope

- **Mejora del manejo de errores genéricos** (`except Exception → return {"status":"error"}`) hacia
  el patrón recuperable/fatal: queda como **deuda registrada** para un intent posterior; en este
  intent se preserva tal cual (FR5.3).
- **Retirada del SQL-en-router** de los endpoints de sync: anti-patrón heredado que NO se amplía pero
  tampoco se sanea aquí; deuda registrada.
- **Descomposición o saneamiento de `data_manager_v2.py`** (~166 KB): fuera de alcance; solo se
  consume vía adaptador (FR3).
- Cambios de comportamiento, nuevas features, cambios de esquema de BD o de la API pública REST.

## Sources

- **[desc]** Initial description: `Oleada 3 god-files (FR13): descomponer backend/app/services/data_sync_service.py (84 KB) al patrón DDD de las oleadas 1-2 (analytics/, assistant/): un módulo de aplicación por dominio de sync (transactions, clauses, punishments, dream_teams, performance, rosters, rankings, players, odds, prizes) coordinados por un sync_all delgado; sync_prizes ya delega en prizes/ como patrón a replicar; reemplazos de conjunto tras repositorios con escritura atómica (patrón team_prizes_writer). Preservar la superficie pública (los 10 sync_* + sync_all()). Characterization-first por dominio antes de trocear. Coste 0 EUR, sin ampliar god-files, sin reformateo masivo, sin relajar el piso --cov-fail-under=27.` (`project-description.json`)
- **[scope]** Workflow-selected scope: `refactor` (depth Minimal, test-strategy Minimal).
- **[Q1]** Preservación de la superficie pública → facade delgado + shim puntual (FR1).
- **[Q2]** Alcance de extracción de SQL → solo tras adaptador, sin tocar `data_manager_v2.py`; SQL-en-router fuera de alcance (FR3, Out of scope).
- **[Q3]** Secuenciación → characterization-first estricto por dominio, incremental (FR4).
- **[Q4]** Equivalencia → funcional estricta; mejora de errores genéricos como deuda (FR5, Out of scope).
- Reverse-engineering artifacts: `business-overview.md`, `architecture.md`, `code-structure.md`, `component-inventory.md`, `code-quality-assessment.md` (`aidlc/spaces/default/codekb/futmondo-analytics/`).
- **[memory:M1]** Reglas afirmadas (`team.md`/`project.md`): coste 0 €, gate de CI bloqueante, characterization-first, no ampliar god-files, no reformateo masivo, piso de cobertura solo sube.
- **[code]** Piso de cobertura backend `--cov-fail-under=27` (line-only): verificado en `backend/pytest.ini` (medido 27.52%); fuente del valor citado en NFR2.
- **[code]** Claves literales del dict de `sync_all()` (FR5.1.1): verificadas en `backend/app/services/data_sync_service.py` (`players`, `transactions`, `clauses`, `punishments_bonuses`, `dream_teams`, `player_performance`, `rosters`, `team_standings`, `match_odds`, `prizes`).
