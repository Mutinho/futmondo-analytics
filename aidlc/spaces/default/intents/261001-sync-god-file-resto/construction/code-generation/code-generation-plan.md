# Code Generation Plan — `261001-sync-god-file-resto`

> Scope `refactor`, profundidad Minimal, test strategy Minimal, brownfield.
> Directivo zero-Unit (sin DAG de unidades). Equivalencia funcional ESTRICTA
> (FR5), characterization-first por dominio (FR7). Idioma: identificadores/
> docstrings/comentarios en INGLÉS; prosa de este plan y commits en CASTELLANO.

## Alcance y estrategia de ejecución (leer antes de aprobar)

La descripción del intent cubre **8 dominios de sync pendientes + la uniformación
de `prizes/`**, cada uno con characterization-first ESTRICTO ("congelar → extraer
→ verde → siguiente") sobre el god-file `data_sync_service.py` (~84 KB) que está
**en producción**. El flujo AI-DLC está ejecutando code-generation como una sola
iteración zero-Unit (units-generation se saltó por scope). Para respetar FR1.3/Q1
("una unidad por dominio") y minimizar el blast radius, este plan **acota la
primera entrega al primer dominio del orden acordado: `clauses`** (el de menor
acoplamiento), dejando los 7 dominios restantes + `prizes/` como entregas
sucesivas que repiten exactamente el mismo patrón en pases posteriores de
code-generation (vía Build-and-Test verde → re-entrada, o re-invocación de la
etapa). Esto se confirma en el Plan Approval abajo (opción de ajustar el alcance
del pase).

**Patrón objetivo (molde `match_odds`, idéntico para cada dominio):**
`sync/<domain>/orchestrator.py` (application) + `sync/<domain>/domain/ports.py`
(`Protocol` consumer-owned con los métodos de `DataManagerV2` verbatim) +
`sync/<domain>/infrastructure/<domain>_adapter.py` (único SQL, delega 1:1 a
`DataManagerV2`). El método público `sync_clauses` queda como delegación fina.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "medir y congelar la señal de cobertura y el estado advisory del gate antes de subir cualquier umbral o promover un check a bloqueante; luego sanear/silenciar quirúrgicamente la deuda heredada que cada promoción reportaría, aplicar cada endurecimiento en su commit `chore(ci)` aislado con el trinquete fijado, y sólo al FINAL del escalón fijar el piso de cobertura backend (`--cov-fail-under`) al valor medido exacto sobre la suite ya estabilizada, verificando en verde en AMBOS gates (PR + job `verify`) sin escribir asserts espejo que pasen siempre.",
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
      "text": "- **Methodology**: test-after\n- **Ordering**: medir y congelar la señal de cobertura y el estado advisory del gate antes de subir cualquier umbral o promover un check a bloqueante; luego sanear/silenciar quirúrgicamente la deuda heredada que cada promoción reportaría, aplicar cada endurecimiento en su commit `chore(ci)` aislado con el trinquete fijado, y sólo al FINAL del escalón fijar el piso de cobertura backend (`--cov-fail-under`) al valor medido exacto sobre la suite ya estabilizada, verificando en verde en AMBOS gates (PR + job `verify`) sin escribir asserts espejo que pasen siempre.\n- **Cobertura backend (FR11)**: hoy `--cov=app` es **observability-only, sin\n  piso** (`ci.yml`; `pytest.ini` documenta cobertura como métrica informativa,\n  activable con `--cov=app`). Este intent introduce un **piso bloqueante único\n  `--cov-fail-under` en `pytest.ini`** (line-coverage total, dentro del mismo\n  `addopts` de `pytest` — config, no un paso extra), fijado al **valor medido\n  exacto SIN margen** (Q6; medición previa obligatoria) y que sube **sólo por\n  trinquete**; nunca se relaja para pasar el gate. Si aparece flapping, se\n  arregla el test no-determinista, NUNCA se baja el piso. El piso es\n  **line-only** en este intent (no se añade `--cov-branch`); una eventual paridad\n  de branch-coverage con el frontend queda fuera de alcance.\n- **Paridad de la señal backend (asimetría a CREAR — FR17.3)**: `ci.yml` mide\n  `--cov=app` mientras el job `verify` de `fly-deploy.yml` corre `pytest -q`\n  **sin `--cov`**. Este intent **cierra la asimetría** llevando la misma\n  invocación con cobertura y el mismo piso a `verify`, para que un rojo de\n  cobertura no pueda colarse por el push directo a `main`. Esta paridad aterriza\n  en el **mismo commit** que introduce el piso en `ci.yml`, o inmediatamente\n  después (Q4), para que no exista una ventana en la que el piso viva sólo en el\n  PR-gate.\n- **Cobertura frontend (SÓLO ratchet — ya tiene paridad de enforcement)**: el\n  enforcement vive DENTRO de `ng test` (builder `@angular/build:unit-test` +\n  `@vitest/coverage-v8` pin `4.1.11`), con umbrales por métrica en `angular.json`\n  (`coverageThresholds`: statements 15 / branches 15 / functions 13 / lines 14),\n  y **ambos** workflows (PR-gate y push-gate) ya corren `ng test`. Es decir, el\n  frontend **YA tiene paridad de enforcement** entre gates; su única tarea en\n  este intent es **subir el ratchet** de esos cuatro umbrales al valor medido. No\n  hay paridad frontend que crear (a diferencia del backend); no se debe inducir\n  ese trabajo inexistente. `angular.json` es la fuente única de umbral (sin pasos\n  extra ni `continue-on-error`).\n- **Tooling y coste 0 €**: backend `pytest` + `pytest-cov` desde `backend/` con\n  las fixtures fake in-memory de `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`\n  SQLite `:memory:`, `clean_jwt_env`, `fake_db`) — sin red, sin BD real, sin\n  credenciales/tokens reales (gitleaks escanea también los tests). No se prevén\n  dependencias nuevas de test; cualquiera sería OSS y **fijada a versión\n  exacta**. Un piso alto con aserciones débiles es peor que uno modesto con\n  aserciones reales: la posture test-after se mantiene con specs que aseveran el\n  efecto (payload/estado/modo de fallo), nunca `assert True` ni specs espejo.\n- **Sin bajar cobertura para pasar el gate**: el ratchet (backend y frontend)\n  **sólo sube**; nunca se relaja un umbral/piso existente para hacer pasar el\n  gate."
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
  "input_sha256": "sha256:ecea62614f79c3c11fff8e333f4a41f0f402a7ee7b2dd66004a56fac66c28f13",
  "contract_sha256": "sha256:5b6e8d0595fa2a9cbd528cb7fb86e8e9ab82badb56be52a2afd06cf869fa8cd3"
}
```

## Metodología aplicada (test-after, adaptada a characterization-first)

El contrato es **test-after**. Para un refactor de equivalencia estricta, la
posture test-after se materializa como **characterization-first**: el test de
caracterización se escribe PRIMERO contra el código ACTUAL (debe pasar verde
antes de tocar nada), se extrae el dominio, y el MISMO test debe seguir verde
(FR7.1-FR7.3). Las capas aplicables aquí son **Business logic** (orchestrator) y
**Repository/data access** (adapter + port); no hay cambios de data-model
(esquema sin cambios), API/endpoint (superficie preservada) ni frontend.

## Plan de implementación — dominio `clauses` (primera entrega)

- [x] **Step 1 — Estructura**: crear el paquete `backend/app/services/sync/clauses/`
      con `__init__.py`, `domain/__init__.py`, `domain/ports.py`,
      `infrastructure/__init__.py`, `infrastructure/clauses_adapter.py`,
      `orchestrator.py`, replicando la forma de `sync/match_odds/`. (FR1.1, FR1.2, BR1.1)
- [x] **Step 2 — Runner**: verificar el runner de tests existente y registrar el
      comando exacto scoped a esta unidad en `unit-test-instructions.md`
      (`pytest backend/tests/test_sync_clauses_characterization.py`). (plan_profile.runner_step)
- [x] **Step 3 — Caracterización (test-FIRST contra código actual)**: escribir
      `backend/tests/test_sync_clauses_characterization.py` que congela (a) el
      `SyncResult` observable de `sync_clauses` (claves y tipos exactos) y (b) las
      llamadas a `DataManagerV2` (métodos + argumentos), con fakes en memoria
      (patrón `conftest.py`), sin red/BD real/credenciales. DEBE pasar verde
      contra el `data_sync_service.py` actual. (FR7.1, FR7.2, FR7.3, BR6.1)
- [x] **Step 4 — Repository/data access (adapter + port)**: implementar
      `domain/ports.py` (`ClausesSyncDataPort` Protocol con los métodos de
      `DataManagerV2` que `sync_clauses` invoca hoy, verbatim) y
      `infrastructure/clauses_adapter.py` (`DataManagerClausesAdapter` que delega
      1:1 a `DataManagerV2`, sin ampliarlo). (FR3.1, BR1.2, BR3.1)
- [x] **Step 5 — Repository tests (after)**: tests de que el adapter delega
      verbatim a `DataManagerV2` (métodos + args), con fake de DataManagerV2 en
      memoria. (BR1.2)
- [x] **Step 6 — Business logic (orchestrator)**: implementar
      `orchestrator.py` (`ClausesSyncOrchestrator`) alojando la orquestación hoy
      inline en `sync_clauses` (ingesta vía `FutmondoClient` inyectado, throttling
      `time.sleep`, mapeo, manejo de errores verbatim), delegando persistencia al
      port. (FR1.2, FR6.1, FR6.2, FR6.3, BR2.1, BR4.1, BR4.2)
- [x] **Step 7 — Business logic tests (after)**: completar la caracterización del
      orchestrator (recoverable → DEGRADED sin fallar; fatal → propaga; sin
      credenciales en logs), aseverando el EFECTO, nunca `assert True`. (FR6, BR4.1, BR4.2)
- [x] **Step 8 — Adelgazar el método público**: reescribir `sync_clauses` en
      `data_sync_service.py` como delegación fina al `ClausesSyncOrchestrator`
      (sin ingesta/SQL/`time.sleep`), devolviendo su `SyncResult`. Verificar que la
      caracterización (Step 3) sigue verde. NO ampliar `data_manager_v2.py`;
      formateo quirúrgico sólo en los ficheros nuevos. (FR2.1, FR2.2, FR5.3, BR2.1, BR8.1)
- [x] **Step 9 — Suite verde + superficie**: correr la suite backend; confirmar
      que `sync_all()` mantiene sus 10 claves y orden, y que el worker del router
      no se rompe (FR5.1, FR5.2, FR5.4, BR5.1). Piso `--cov-fail-under=27` sin
      bajar (NFR2.1, BR8.2).
- [x] **Step 10 — Config/entorno**: ninguna dependencia nueva (stdlib suficiente:
      `typing.Protocol`); sin cambios de `requirements.txt`. (NFR3.1)
- [x] **Step 11 — Documentación y trazabilidad**: docstrings en inglés citando
      FR/BR; `code-summary.md`, `source-manifest.json`, `traceability.json`.

## Story-to-code-step traceability

| Step | Requisitos / reglas |
|------|---------------------|
| 1 | FR1.1, FR1.2, BR1.1 |
| 2 | plan_profile.runner_step |
| 3 | FR7.1, FR7.2, FR7.3, BR6.1 |
| 4 | FR3.1, BR1.2, BR3.1 |
| 5 | BR1.2 |
| 6 | FR1.2, FR6.1, FR6.2, FR6.3, BR2.1, BR4.1, BR4.2 |
| 7 | FR6.1, FR6.2, FR6.3, BR4.1, BR4.2 |
| 8 | FR2.1, FR2.2, FR5.3, BR2.1, BR8.1 |
| 9 | FR5.1, FR5.2, FR5.4, NFR2.1, BR5.1, BR8.2 |
| 10 | NFR3.1 |
| 11 | trazabilidad / documentación |

## Dominios restantes (entregas sucesivas, mismo patrón)

`transactions` → `punishments_bonuses` → `dream_teams` → `rosters` →
`round_rankings`/`team_standings` → `player_performance` → `players_full`, y
finalmente uniformar `prizes/`. Cada uno repite Steps 1-11 con su nombre de
dominio y su variante de `SyncResult`. Se abordan en pases posteriores de
code-generation para mantener diffs quirúrgicos y characterization-first por
dominio.
