# Code Generation Plan — Limpieza de configuración y residuos (FR14 + FR15)

Intent: `260925-limpieza-config-residuos` · Scope: `refactor` (Minimal) · Brownfield.
Poda de bajo riesgo funcional, **sin lógica nueva**, characterization-first, coste 0 €.
Ejecución zero-Unit (sin Unit DAG): una sola iteración de stage.

## Hechos verificados (pre-plan)

Estas verificaciones cierran las preguntas abiertas OQ1/OQ2 y los hallazgos
advisory R-01/R-04/R-05 del análisis de requisitos:

- **FR15.1.2 — clientes de `/v1/matchdays`**: `grep` en `angular-app/src`, `proxy`
  y `.github` NO encuentra ningún consumo del prefijo no canónico. Retirada segura.
  (`main.py` L173 `/api/v1/matchdays`, L196 `/v1/matchdays`, mismo router.)
- **FR14.2 — IDs hardcodeados**: confirmados en `backend/app/core/config.py`
  L17-18 (`CHAMPIONSHIP_ID`, `LEAGUE_ID` con default literal), NO en `constants.py`.
- **FR14.1.4 — huérfanos**: sin refs vivas a `entrypoint.sh`, `nixpacks.toml`,
  `migrate_to_turso.py`, `migrate_data_to_turso.py` en `Dockerfile*`, `fly.toml`,
  `docker-compose.yml` ni `.github/`. `libsql-experimental==0.0.55` vive en
  `requirements.txt:9`.
- **FR15.2 — residuos trackeados (lista exhaustiva, cierra R-05)**: `git ls-files`
  confirma trackeados: `30825.jpg:Zone.Identifier`, `42874.jpg`,
  `42874.jpg:Zone.Identifier`, `IMG_9904.PNG:Zone.Identifier`,
  `stitch_angular_material_card_redesign/{DESIGN.md,code.html,screen.png}`,
  `stitch_team_card_dashboard/{DESIGN.md,code.html,screen.png}`.
- **FR15.2.3 — ya-ignorados (cierra OQ2)**: `node_modules.old-*/` y `*.db` NO
  están trackeados (git ls-files vacío) → `git rm --cached` resulta **no-op**;
  no hay acción. `.gitignore` ya cubre `*.db` y `node_modules.old-*/`, pero NO
  `Zone.Identifier` ni `stitch_`.

## Estrategia de commits (aislados, Conventional Commits en castellano)

1. `chore(backend)` — FR14.1: retirada dead-path SQLite/Turso + huérfanos.
2. `chore(backend)` — FR14.2: retirada IDs hardcodeados en `config.py`.
3. `refactor(backend)` — FR15.1: unificar montaje `matchdays`.
4. `chore(repo)` — FR15.2: `git rm` residuos + endurecer `.gitignore`.

(La secuenciación por commit se materializa en Build and Test / merge; el plan
agrupa los pasos por FR para trazabilidad.)

---

## Pasos de implementación

### Bloque 0 — Runner y baseline (Testing Contract)

- [x] **Step 1** — Verificar el runner de tests existente y registrar el comando
  exacto unit-scoped. Backend: `pytest` desde `backend/` con las fixtures de
  `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor` SQLite `:memory:`,
  `clean_jwt_env`, `fake_db`). Comando de esta unidad en
  `unit-test-instructions.md`. (Runner-ready antes del primer test.)
- [x] **Step 2** — Baseline: correr la suite backend actual y registrar
  passing/failing como línea base brownfield (test-after; suite verde en cada paso).

### Bloque 1 — FR14.1: characterization-first + retirada dead-path SQLite/Turso

- [x] **Step 3** *(characterization-first, C3/FR14.1.5)* — ANTES de tocar
  `db_connection.py`, escribir/confirmar tests de caracterización que congelen el
  contrato del cursor bajo el path **PostgreSQL/Neon**: `get_connection`,
  `adapt_sql`, `adapt_params`, `get_last_insert_id` para el motor `postgresql`.
  Verificar que ningún llamador de producción depende del comportamiento SQLite
  (`?` placeholders) fuera del fake de tests. Confirmar que el fake in-memory
  (`db_type="sqlite"` en `conftest.py`/`test_db_engine_characterization.py`) es
  independiente de la rama SQLite de producción. Traza: FR14.1.5.
- [x] **Step 3bis** *(R-01, Critical)* — `backend/tests/test_db_engine_characterization.py`
  contiene tests que afirman comportamiento **turso** e importan
  `_TursoCursorWrapper` (L38 `test_adapt_params_turso_keeps_qmark`, L64
  `test_get_cursor_wraps_turso_cursor_only`, L76-78). Como Step 4 retira esa rama,
  **actualizar esos tests en el mismo cambio**: eliminar/reemplazar las aserciones
  turso por las del path PostgreSQL/Neon (el único que queda), de modo que la suite
  siga verde. Este ajuste de tests forma parte de la retirada, no la contradice.
- [x] **Step 4** — `db_connection.py`: eliminar `_init_turso`,
  `_TursoCursorWrapper`, `_init_sqlite` y las ramas `turso`/`sqlite` de
  producción en `get_connection`/`adapt_sql`/`adapt_params`/`get_last_insert_id`/`sync`,
  dejando solo el path PostgreSQL/Neon. Traza: FR14.1.2.
  - *(R-03)* Reescribir `DBConnection.__init__` (L69-90) **en lockstep** con Step 5:
    hoy importa `DATABASE_TYPE`/`POSTGRES_*` de `config.py`; tras la retirada debe
    resolver directamente `DATABASE_URL` (Neon) sin `DATABASE_TYPE` ni `db_type`.
    Retirar `_convert_params` (L15) y el `_TursoCursorWrapper.__init__`/`execute`
    que lo usan, ya que quedan muertos al eliminar la rama turso. Step 4 y Step 5
    van en el mismo commit para no dejar un `ImportError` intermedio.
- [x] **Step 5** — `config.py`: eliminar la cascada
  `DATABASE_URL → TURSO_DATABASE_URL → sqlite` y las vars `TURSO_DATABASE_URL`,
  `TURSO_AUTH_TOKEN`, `DATABASE_TYPE` (y `POSTGRES_*` manuales solo del dead-path),
  dejando la resolución directa de `DATABASE_URL` (Neon). Traza: FR14.1.1.
  - *(R-02)* **CONSERVAR `DATABASE_PATH` (L31)**: la consumen vivos
    `photo_service.py` (L12,22) y el god-file `data_manager_v2.py` (L21,31).
    Retirarla rompería imports y tocar el god-file está prohibido (C2). Se deja
    con un comentario que la marca como ruta de caché local (no dead-path Turso),
    y su limpieza queda como **deuda registrada** (ligada al Intent 3 de god-files).
- [x] **Step 6** — `requirements.txt`: eliminar `libsql-experimental==0.0.55`
  tras confirmar (grep) que no queda import vivo al retirar `_init_turso`.
  Traza: FR14.1.3.
- [x] **Step 7** — Eliminar ficheros huérfanos (verificados sin refs vivas):
  `backend/nixpacks.toml`, `backend/scripts/migrate_to_turso.py`,
  `backend/scripts/migrate_data_to_turso.py`, `backend/entrypoint.sh`.
  *(R-04: rutas reales bajo `backend/`, no en raíz.)* Traza: FR14.1.4.
- [x] **Step 8** — Retirar comentarios obsoletos "Railway"/"Turso" **solo** en los
  ficheros ya tocados (`config.py`, `db_connection.py`, `docker-compose.yml` si se
  toca), quirúrgico, sin reformateo masivo. Traza: FR14.1.6.
- [x] **Step 9** — Correr los tests de caracterización del Step 3 + suite backend:
  verde. Confirma no-regresión del path Neon y del fake de tests. Traza: NFR1.

### Bloque 2 — FR14.2: IDs hardcodeados

- [x] **Step 10** — `config.py` L17-18: neutralizar los defaults hardcodeados de
  `CHAMPIONSHIP_ID`/`LEAGUE_ID` (a `None`/vacío, obligados por entorno), tras
  confirmar que el flujo multi-usuario de producción usa datos del usuario logado
  y no esos defaults. El código falla explícito si se usara sin configurar.
  Traza: FR14.2.1, FR14.2.2.
- [x] **Step 11** — Test: aserción de que un arranque sin `CHAMPIONSHIP_ID`/
  `LEAGUE_ID` configurados no expone el default legacy (modo de fallo explícito
  o ausencia de valor). Traza: FR14.2 (cierra R-02: modo de fallo aseverado).

### Bloque 3 — FR15.1: unificar montaje matchdays

- [x] **Step 12** — `main.py`: eliminar la línea 196
  (`prefix="/v1/matchdays"`), conservando solo `/api/v1/matchdays` (L173).
  Verificación de clientes ya hecha (ninguno). Traza: FR15.1.1, FR15.1.2.
- [x] **Step 13** — Test: aserción de que `/api/v1/matchdays` sigue montado y
  responde (happy-path), sin dependencia del prefijo retirado. *(R-05)* Confirmar
  que el spec Angular existente que ejercita matchdays (`evolution.service.spec.ts`)
  sigue verde y usa el prefijo canónico. Traza: FR15.1.

### Bloque 4 — FR15.2: residuos + .gitignore

- [x] **Step 14** — `git rm` de los 6 residuos trackeados verificados:
  `30825.jpg:Zone.Identifier`, `42874.jpg`, `42874.jpg:Zone.Identifier`,
  `IMG_9904.PNG:Zone.Identifier`, `stitch_angular_material_card_redesign/` (3),
  `stitch_team_card_dashboard/` (3). Traza: FR15.2.1.
- [x] **Step 15** — Endurecer `.gitignore`: añadir `*:Zone.Identifier` y
  `stitch_*/`. Traza: FR15.2.2.
- [x] **Step 16** — FR15.2.3: confirmar que `node_modules.old-*/` y `*.db` NO
  están trackeados → no-op documentado (no hay `git rm --cached`). Traza: FR15.2.3.

### Bloque 5 — Cierre

- [x] **Step 17** — Suite completa backend (`pytest`) + frontend (`ng test`) en
  verde. Sin bajar umbrales (NFR2, NFR4). Traza: NFR1, NFR2.
- [x] **Step 18** — `code-summary.md`, `source-manifest.json` y `traceability.json`;
  documentación quirúrgica de los cambios. Traza: NFR4.

---

## Trazabilidad plan → requisito

| Step | Requisito |
|------|-----------|
| 3, 9 | FR14.1.5 (characterization-first), NFR1 |
| 4 | FR14.1.2 |
| 5 | FR14.1.1 |
| 6 | FR14.1.3 |
| 7 | FR14.1.4 |
| 8 | FR14.1.6 |
| 10, 11 | FR14.2.1, FR14.2.2 |
| 12, 13 | FR15.1.1, FR15.1.2 |
| 14 | FR15.2.1 |
| 15 | FR15.2.2 |
| 16 | FR15.2.3 |
| 1, 2, 17, 18 | NFR1, NFR2, NFR4 |

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "caracterizar primero (characterization-first) cada captura brownfield que se vaya a endurecer y el contrato de `futmondo_client._make_request` ANTES de cambiarlo — entregando un **inventario verificable de llamadores** de `_make_request` (Q4) —, luego implementar la taxonomía recuperable/fatal con excepciones tipadas propagadas (migrando el núcleo: `_make_request` + los llamadores donde un `None` no detectado corrompe datos; el resto de llamadores queda como deuda), y sólo después escribir specs significativas que **aseveren el EFECTO** por modo de fallo (recuperable → paso marcado `DEGRADED` y la operación NO falla; fatal → excepción tipada propagada Y sin datos a medias escritos) — nada de `pytest.raises` sin aserción de estado (Q1) —, replicando el patrón de referencia `SofascoreIPBanError` ya caracterizado, con la suite existente en verde en cada paso.",
  "scope": "refactor",
  "test_strategy": "minimal",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "- **Methodology**: test-after\n- **Ordering**: caracterizar primero (characterization-first) cada captura brownfield que se vaya a endurecer y el contrato de `futmondo_client._make_request` ANTES de cambiarlo — entregando un **inventario verificable de llamadores** de `_make_request` (Q4) —, luego implementar la taxonomía recuperable/fatal con excepciones tipadas propagadas (migrando el núcleo: `_make_request` + los llamadores donde un `None` no detectado corrompe datos; el resto de llamadores queda como deuda), y sólo después escribir specs significativas que **aseveren el EFECTO** por modo de fallo (recuperable → paso marcado `DEGRADED` y la operación NO falla; fatal → excepción tipada propagada Y sin datos a medias escritos) — nada de `pytest.raises` sin aserción de estado (Q1) —, replicando el patrón de referencia `SofascoreIPBanError` ya caracterizado, con la suite existente en verde en cada paso.\n- **Cobertura/tooling (Q5-quality)**: `--cov` se mantiene **observabilidad-only, sin piso** (`cov-fail-under`) en este intent — el ratcheting de cobertura backend sigue diferido. La asimetría de la señal de cobertura entre `ci.yml` (`--cov=app`) y el job `verify` de `fly-deploy.yml` (`pytest -q` sin `--cov`) queda registrada como **deuda diferida**; este intent no introduce piso ni cierra la asimetría.\n\nDetalle del encuadre para este intent (aditivo sobre la posture afirmada):\n\n1. **Marco general — test-after con specs significativas.** Se mantiene la posture\n   afirmada del equipo: test-after, specs con aserciones reales (payload, estado,\n   modo de fallo), nunca el anti-patrón `expect(true).toBe(true)` / `assert True`.\n2. **Characterization-first al endurecer brownfield.** El mandato ya afirmado cubre\n   `sync_prizes`, `SessionStore` y `TaskManager`; **se extiende** el mismo principio\n   a: (a) cualquier `except Exception` / `except: pass` de la primera oleada FR3.2\n   que se vaya a reclasificar (arranque `main.py`, migraciones `scripts/migrate_*`,\n   `db_connection.py`), y (b) el **contrato de `futmondo_client._make_request`**\n   antes de convertir su `None`/`bool` en excepción tipada — el cambio toca muchos\n   llamadores del god-file de sync, así que se congela el comportamiento actual con\n   dobles/fakes en memoria antes de tocarlo, **entregando un inventario verificable\n   de llamadores** de `_make_request` como artefacto previo a la migración (Q4). La\n   migración de contrato cubre el **núcleo** (`_make_request` + los llamadores donde\n   un `None` no detectado corrompe datos); el resto de llamadores queda como **deuda**.\n2bis. **Floor de aserción significativa por modo de fallo (Q1).** Un spec de fallo NO\n   basta con `pytest.raises`: debe aseverar el EFECTO. Recuperable → el paso se marca\n   `DEGRADED` vía `sync_step_status.py` **y** la operación no falla; fatal → la\n   excepción tipada se propaga **y** no quedan datos a medias escritos (estado de la\n   caché/tabla verificado tras el fallo). El anti-patrón prohibido es el spec espejo\n   que captura la excepción sin aseverar el efecto lateral (o su ausencia).\n3. **Herramientas y coste 0 €.** Backend `pytest` + `pytest-cov` desde `backend/`,\n   con las fixtures compartidas de `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`\n   SQLite `:memory:` honrando el contrato de `db_connection`, `clean_jwt_env`,\n   `fake_db`): **sin red, sin DB real, sin credenciales**. No se prevén dependencias\n   nuevas (stdlib suficiente); cualquiera sería OSS y fijada a versión exacta.\n4. **Sin bajar cobertura para pasar el gate.** No existe piso de cobertura\n   bloqueante backend hoy (`cov-fail-under` diferido); el ratcheting sólo sube y\n   nunca se relaja para hacer pasar el gate.\n5. **Enforcement de bare-except (`E722`) — decisión afirmada (Q2).** `E722` está hoy\n   en `ignore` en `backend/ruff.toml` y `ruff check` es advisory. Este intent\n   **re-habilita `E722` como ADVISORY por trinquete**: se quita del `ignore` para que\n   `ruff check` lo reporte, **sin** promover ruff a bloqueante. El cambio va en su\n   **propio commit aislado** (`chore(ci)`), **sin `--fix` ni `ruff format`**, aislando\n   el reflow de la regla afirmada de NO reformatear brownfield en masa. La reviewer\n   corre `ruff check` (no `ruff format`)."
    }
  ],
  "obligations": {
    "strategy": "minimal",
    "strategy_volume": [
      "One verifiable test per requirement at the narrowest effective level.",
      "At least one happy-path unit test per component.",
      "Unit tests are the default; a bugfix/security scope floor may require an integration or E2E regression when that is the narrowest level that reproduces the defect."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "test-after",
    "runner_step": "Verify the existing test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Verify the existing test runner/configuration and record the exact unit-scoped command.",
      "Data model / database behavior - implement.",
      "Data model / database behavior - write and run its tests after implementation.",
      "Repository / data access - implement.",
      "Repository / data access - write and run its tests after implementation.",
      "Business logic - implement.",
      "Business logic - write and run its tests after implementation.",
      "API / endpoint - implement.",
      "API / endpoint - write and run its tests after implementation.",
      "Frontend behavior - implement.",
      "Frontend behavior - write and run its tests after implementation.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:15a01d4d16eea4301ecc38edbf82d1e0c1ef8fa3edcfea1452b89c075d28c441",
  "contract_sha256": "sha256:55cc2fcb1df5bf6bec9f37707d64c77fb48f53d3eec187f149b53b0bd1ece246"
}
```

Nota: el bloque `applicable_notes`/`obligations`/`plan_profile` del contrato es la posture afirmada del equipo (test-after, characterization-first, Minimal strategy, coste 0 €). Este plan aplica su ordering: runner-ready → caracterizar (`db_connection.py`) antes de endurecer → implementar retiradas → tests que aseveran el efecto → suite verde en cada paso.
