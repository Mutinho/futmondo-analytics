# Code Generation Plan — U1 `u1-error-layer`

Capa de errores: módulo `integration_errors` (jerarquía tipada, sin secretos por
construcción), re-parentado de `SofascoreIPBanError`, endurecimiento
characterization-first de capturas de arranque/migraciones/`db_connection.py`, y
el commit aislado de `E722`. Código nuevo tras una capa estrecha y testeable; NO
ampliar god-files. Coste 0 €, stdlib.

## Pasos

- [x] **Step 1** — Verificar el runner de tests existente (`pytest` desde `backend/`, fixtures de `conftest.py`) y registrar el comando exacto scoped a U1 en `unit-test-instructions.md`. (runner-ready antes del primer test)
- [x] **Step 2** — Crear el módulo nuevo `backend/app/services/integration_errors.py` con la jerarquía: raíz `IntegrationError(Exception)` (constructor `(failure_mode, *, status=None, endpoint=None)`, sin aceptar credenciales — no-filtración por construcción, BR1.4/NFR3) y subtipos `IntegrationBanError` (fatal), `IntegrationTimeoutError` (recuperable), `IntegrationUnparseableError` (recuperable). Mensajes en inglés. (FR4.1)
- [x] **Step 3** — Re-parentar `SofascoreIPBanError` (en `sofascore_client.py`) para que herede de `IntegrationBanError`, preservando su comportamiento FR2.1 (403 → propaga). Cambio quirúrgico, characterization-first: congelar el comportamiento actual con un spec antes de tocar.
- [x] **Step 4** — Characterization-first de las capturas amplias de la primera oleada: escribir specs que congelan el comportamiento observable actual de arranque (`main.py`), migraciones (`scripts/migrate_*`) y `db_connection.py` (init), ANTES de reclasificar.
- [x] **Step 5** — Reclasificar recuperable/fatal en esas capturas (loguear/degradar y seguir vs propagar/abortar limpio), sin ampliar estructura ni cambiar el `rollback()`+`raise` correcto ya presente en las transacciones de `db_connection.py`. (FR3.2.1, FR3.2.2, BR1.6)
- [x] **Step 6** — Commit de config aislado `chore(ci)`: quitar `E722` del `ignore` de `backend/ruff.toml` (ruff sigue advisory), sin `--fix` ni `ruff format`. (FR3.2.3)
- [x] **Step 7 (test-after)** — Tests de la jerarquía `integration_errors`: construcción de cada subtipo, clasificación por tipo, y el **spec de defensa NFR3** que construye con credenciales de prueba y asvera su ausencia en `str/repr/args` (BR1.4). 5-8 tests.
- [x] **Step 8 (test-after)** — Tests de la reclasificación de capturas endurecidas: aseverar el EFECTO (recuperable → sigue/degrada; fatal → propaga), con dobles/fakes en memoria (`conftest.py`), sin red, sin credenciales reales. Nada de `pytest.raises` sin aserción de estado (Q1).
- [x] **Step 9** — `code-summary.md`, `source-manifest.json`, `traceability.json`; docstrings de caracterización con trazas a FR/BR.

## Cobertura y estrategia

- Estrategia **standard**: 5-8 tests por componente + integración en fronteras clave.
- Piso de scope `feature`: 80% de línea + ejecución en CI antes de merge. `--cov`
  observabilidad-only (sin piso bloqueante backend, deuda diferida) — NO se baja
  ningún umbral para pasar el gate.
- Suite existente en verde en cada paso.

## Trazabilidad plan → requisito

| Step | Requisito |
|---|---|
| 2 | FR4.1, NFR3, BR1.1-1.4 |
| 3 | FR4.4 (re-parentado, FR2.1 preservado) |
| 4-5 | FR3.2.1, FR3.2.2, BR1.5, BR1.6 |
| 6 | FR3.2.3 |
| 7-8 | NFR3 (defensa), Q1 (aserción de efecto), piso de cobertura |

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "caracterizar primero (characterization-first) cada captura brownfield que se vaya a endurecer y el contrato de `futmondo_client._make_request` ANTES de cambiarlo — entregando un **inventario verificable de llamadores** de `_make_request` (Q4) —, luego implementar la taxonomía recuperable/fatal con excepciones tipadas propagadas (migrando el núcleo: `_make_request` + los llamadores donde un `None` no detectado corrompe datos; el resto de llamadores queda como deuda), y sólo después escribir specs significativas que **aseveren el EFECTO** por modo de fallo (recuperable → paso marcado `DEGRADED` y la operación NO falla; fatal → excepción tipada propagada Y sin datos a medias escritos) — nada de `pytest.raises` sin aserción de estado (Q1) —, replicando el patrón de referencia `SofascoreIPBanError` ya caracterizado, con la suite existente en verde en cada paso.",
  "scope": "feature",
  "test_strategy": "standard",
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
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Meet an 80% line-coverage floor.",
      "Run the selected tests in CI before merge."
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
  "input_sha256": "sha256:abd79fb715a2903b72c37af312711d4e0727bc29cc65f90ff8cbd387ddd8fd8e",
  "contract_sha256": "sha256:856b3d370c2b1b965c16da5325086de73b1e1dbe68faffb3a954688fa37a5af7"
}
```
