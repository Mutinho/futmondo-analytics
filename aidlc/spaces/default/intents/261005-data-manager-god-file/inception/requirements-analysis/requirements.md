# Requirements — Refactor de `data_manager_v2.py` (god-file de acceso a datos)

Intent: `261005-data-manager-god-file` · Scope: `refactor` · Depth: Minimal ·
Fase: Inception.

## Análisis de intención

El objetivo es **descomponer el último god-file original sin tocar**,
`backend/app/services/data_manager_v2.py` (clase única `DataManagerV2`, ~162 KB /
3692 líneas, 57 métodos públicos, 148 sentencias SQL embebidas), al **patrón DDD
ya probado** en el mismo repo por las oleadas de `sync/`, `analytics/`,
`assistant/` y `prizes/` (ver `architecture.md` y `code-structure.md` del
CodeKB). La meta de negocio no es añadir funcionalidad, sino **reducir la deuda
estructural** del último monolito de acceso a datos manteniendo el sistema
**funcionalmente idéntico** en producción (Fly.io + Neon), para que futuras
funcionalidades se construyan sobre una capa de datos mantenible y testeable.

Según `business-overview.md`, `DataManagerV2` es la **única capa de acceso a
datos transversal**: toda la PWA lee por sus `get_*` y toda ingesta externa se
materializa por sus `save_*`. Según `architecture.md`, su superficie pública es
la **frontera de infraestructura** sobre la que ya descansan las 4 oleadas DDD
entregadas (la envuelven verbatim desde `infrastructure/*_adapter.py`). Por eso
el eje del refactor es la **preservación byte-a-byte de esa superficie** con
**characterization-first estricto por responsabilidad**.

El resultado observable para el usuario final debe ser **nulo**: mismos
endpoints, mismos payloads, mismo comportamiento. El valor es interno
(mantenibilidad, testabilidad, rollback quirúrgico por responsabilidad).

## Requisitos funcionales

### FR1 — Descomposición DDD por responsabilidad preservando la superficie pública

- **FR1.1** — `DataManagerV2` DEBE descomponerse al patrón DDD de referencia del
  repo (ver `architecture.md`): **facade delgado** que preserva la superficie
  pública y delega → **orchestrator de aplicación** por responsabilidad (sin SQL)
  → **domain port** `typing.Protocol` consumer-owned (sin SQL ni framework) →
  **`infrastructure/*_adapter`** como **único módulo con SQL**, que envuelve el
  SQL verbatim.
- **FR1.2** — La **superficie pública** de `DataManagerV2` DEBE preservarse
  byte-a-byte: el constructor `DataManagerV2(db_path=None, skip_init=True)` y los
  nombres y firmas de los **57 métodos** (19 `save_*`, 26 `get_*`, 6 privados
  `_*`, resto varios) permanecen invariantes. Pass/fail: los consumidores
  existentes (8 routers + adapters de las 4 oleadas DDD + `data_sync_service` +
  `data_initializer_v2` + `futmondo_service`) compilan e invocan sin cambios.
- **FR1.3** — La extracción DEBE hacerse **una responsabilidad por módulo DDD**
  (≈14 responsabilidades candidatas identificadas en `component-inventory.md` /
  `code-structure.md`: players, teams/standings, performance, transactions,
  clauses, punishments/bonuses, dream-teams/MVP, prizes, market/roster,
  match-odds, news/articles, users/stats/evolution, sync-metadata/cache,
  schema/lifecycle), en orden de **menor a mayor acoplamiento**. (Q4)
- **FR1.4** — El SQL extraído NO DEBE modificarse: se **envuelve verbatim** en el
  adapter de infraestructura, incluida la divergencia de ramas por engine
  (`if self.db.db_type in ["postgresql","postgres"]: ... else: (SQLite)`). No se
  añade ningún método nuevo al god-file durante la extracción. (Regla afirmada:
  NEVER ampliar el god-file.)

### FR2 — Characterization-first estricto por responsabilidad

- **FR2.1** — Antes de extraer cada responsabilidad, DEBEN escribirse
  **characterization tests** que congelen su comportamiento observable usando los
  **fakes in-memory de `conftest.py`** (`_FakeInMemoryDB`/`_FakeCursor` SQLite
  `:memory:`, `fake_db`, `clean_jwt_env`) — sin red, sin BD real, sin
  credenciales/tokens reales. (Q1)
- **FR2.2** — El ciclo por responsabilidad DEBE ser **congelar (tests en verde) →
  extraer → verde de nuevo**. Pass/fail de la equivalencia: los mismos
  characterization tests de la responsabilidad pasan antes y después de la
  extracción, sin modificar sus aserciones para acomodar el refactor. (Q1)
- **FR2.3** — Los characterization tests DEBEN **aseverar el efecto** (payload /
  estado / filas / modo de fallo observable), nunca `assert True` ni specs espejo
  que capturen sin aseverar. (Regla afirmada de posture test-after.)

### FR3 — Equivalencia funcional estricta (sin cambio de comportamiento observable)

- **FR3.1** — El comportamiento observable DEBE preservarse **tal cual** en cada
  extracción: mismas filas devueltas, mismos efectos de escritura, mismas
  excepciones y mismos valores de retorno (incluido `return None` donde hoy
  ocurre). (Q2)
- **FR3.2** — El **manejo de errores heredado** del god-file (18 `except
  Exception`, 5 `except:` desnudos, 16 `return None` — ver
  `code-quality-assessment.md`) NO DEBE cambiarse en este intent: se preserva
  verbatim. Su saneamiento queda como **deuda registrada** (ver OQ1). (Q2)
- **FR3.3** — Los **puntos de reemplazo de conjunto con riesgo de corrupción**
  (p. ej. `delete_orphan_players`, `DELETE ... NOT IN`/`<> ALL(%s)` sin
  transacción compartida con los upserts previos) NO DEBEN elevarse al patrón
  atómico en este intent: se preservan verbatim y quedan como **deuda
  registrada** (ver OQ2). (Q2)

### FR4 — Consumidores intactos

- **FR4.1** — Los **consumidores existentes** NO DEBEN tocarse: los adapters DDD
  de `analytics/`, `assistant/`, los 10 contextos `sync/*` y `prizes/`, y los 8
  routers consumidores (`clausulable_players`, `initialize`, `matchdays`,
  `player_finances`, `reset_db`, `statistics`, `sync`, `user_stats`) siguen
  invocando la misma superficie pública, que tras el refactor es un facade
  delgado que delega en los módulos extraídos. (Q3)
- **FR4.2** — El **SQL-en-router** existente (17 de 23 routers con `cursor.execute`
  inline, ver `code-structure.md`) NO DEBE ampliarse ni retirarse en este intent:
  queda como **deuda registrada**. (Q3; regla afirmada NEVER ampliar SQL-en-router.)

### FR5 — Confirmación del plan de extracción en Plan Approval

- **FR5.1** — El **inventario de responsabilidades definitivo** y el **orden de
  extracción exacto** (de menor a mayor acoplamiento) DEBEN confirmarse en **Plan
  Approval** antes de ejecutar la descomposición; la lista de ≈14 del escaneo es
  el punto de partida, no un compromiso congelado aquí. (Q4)

## Requisitos no funcionales

- **NFR1 — Equivalencia verificable (gate verde)**: la suite de `backend/tests/`
  DEBE permanecer en verde en cada paso del refactor, y el **gate de CI
  bloqueante** (gitleaks + `pytest` + `ng test`) DEBE pasar antes de fusionar a
  `main`. Un rojo nunca llega a producción. (Regla afirmada.)
- **NFR2 — Piso de cobertura sólo-sube**: el piso `--cov-fail-under` NO DEBE
  relajarse para pasar el gate; el characterization nuevo sólo puede subirlo por
  trinquete. Si aparece flapping, se arregla el test no-determinista, nunca se
  baja el piso. (Regla afirmada.)
- **NFR3 — Coste 0 €**: no se introducen dependencias de pago ni servicios fuera
  de los tiers gratuitos (Neon free, Fly.io free, GitHub Actions free); cualquier
  librería nueva sería OSS y fijada a versión exacta (no se prevé ninguna). (Regla
  afirmada.)
- **NFR4 — Higiene de diff brownfield**: NO se ejecuta `ruff format` masivo sobre
  ficheros heredados; el formateo es sólo quirúrgico o sobre los ficheros nuevos
  que surjan de la extracción. La deuda de lint registrada del god-file
  (`per-file-ignores` `E722,F841,F401,I001`) se sanea en los ficheros NUEVOS, no
  in-place. (Regla afirmada.)
- **NFR5 — Idioma**: identificadores, docstrings y comentarios en **inglés**;
  texto de cara al usuario y mensajes de commit (Conventional Commits con scope)
  en **castellano**. (Regla afirmada.)
- **NFR6 — Seguridad de credenciales**: ninguna extracción debe introducir
  credenciales/tokens Futmondo en claro, ni en mensajes, `repr` o `exc_info` de
  excepciones. (Regla afirmada.)

## Restricciones

- **C1** — Patrón de destino **fijado** (no es decisión abierta): facade /
  orchestrator / domain `Protocol` port sin SQL / `infrastructure/*_adapter` que
  envuelve SQL verbatim, con reemplazo de conjunto atómico como patrón de
  referencia (`prizes/team_prizes_writer.py`). (`architecture.md`)
- **C2** — Producción es **PostgreSQL/Neon exclusivamente**; la rama SQLite sólo
  sostiene el fake de tests y debe seguir ejecutándose contra `_FakeInMemoryDB`.
- **C3** — Trunk-based + squash-merge a `main`; cada paso de extracción debe poder
  aterrizar de forma aislada para rollback quirúrgico. (`team.md`)
- **C4** — Este intent levanta la prohibición afirmada "NEVER tocar
  `data_manager_v2.py`" **sólo para este fichero y sólo para descomponerlo**; no
  habilita refactor de oportunidad en otros god-files ni en el SQL-en-router.

## Supuestos

- **A1** — Los fakes in-memory de `conftest.py` cubren el comportamiento SQL
  relevante de las responsabilidades a extraer; si una responsabilidad ejercita
  SQL no soportado por el fake, se amplía el fake de forma aditiva (sin red/BD
  real) como parte de su characterization. Rationale: es el patrón usado en las
  oleadas previas de sync.
- **A2** — La superficie de 57 métodos del escaneo es completa y estable; cualquier
  método no listado que aparezca durante la extracción se trata como parte de su
  responsabilidad y se preserva igual.

## Fuera de alcance

- Saneamiento del manejo de errores del god-file (excepts amplios/desnudos,
  `return None` como señal de fallo) — deuda registrada (OQ1).
- Elevar los puntos de corrupción por reemplazo de conjunto (p. ej.
  `delete_orphan_players`) al patrón atómico — deuda registrada (OQ2).
- Retirar o reducir el SQL-en-router de los routers consumidores (FR4.2).
- Re-cablear los adapters DDD existentes para apuntar a los módulos extraídos en
  vez de al facade.
- Cualquier cambio en frontend Angular, auth, integraciones externas o esquema de
  BD.

## Preguntas abiertas

- **OQ1** — ¿En qué intent futuro se sanea la deuda de manejo de errores del
  god-file (tipado de fallos, distinción `Optional`-"no encontrado" vs fallo
  silencioso)? Se decide fuera de este refactor.
- **OQ2** — ¿En qué intent futuro se eleva `delete_orphan_players` (y otros
  reemplazos de conjunto) al patrón atómico de `team_prizes_writer`? Riesgo de
  corrupción conocido, diferido fuera de este refactor.
- **OQ3** — Inventario y orden de extracción definitivos: se cierran en Plan
  Approval (FR5.1), no aquí.
