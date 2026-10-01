# Code Generation Plan — Descomposición DDD de `data_sync_service.py`

Intent: `sync-god-file` (Oleada 3, FR13) · scope `refactor` · depth Minimal ·
test-strategy Minimal · Brownfield · backend-only.

## Enfoque

Refactor de estructura sin cambio de comportamiento (equivalencia funcional
estricta, FR5). Se descompone `backend/app/services/data_sync_service.py` en un
módulo de aplicación por dominio bajo el patrón DDD de `analytics/`/`assistant/`/
`prizes/`, preservando la superficie pública (`DataSyncService` + 10 `sync_*` +
`sync_all()`). **Characterization-first estricto por dominio** (BR6.1): congelar →
extraer → verde → siguiente. `DataSyncService` queda como facade delgado; la
ingesta + manejo de errores tipados + throttling van al orquestador de aplicación
del dominio; el SQL tras un port estrecho + `*_adapter` (nunca inline, nunca
tocando `data_manager_v2.py`).

**Restricciones duras**: no ampliar los god-files, no `ruff format` masivo (solo
ficheros nuevos o quirúrgico), no relajar el piso `--cov-fail-under=27` (solo sube
por trinquete), coste 0 €. Idioma: identificadores/docstrings/comentarios en
INGLÉS. Tests con fakes en memoria de `conftest.py`, sin red/BD/credenciales.

## Alcance de esta pasada (Bolt 1) — decisión de secuenciación

La descomposición completa son 10 dominios. Para respetar characterization-first
y mantener cada paso pequeño y verificable, esta pasada **establece el patrón
extraíble y extrae el primer dominio de menor riesgo de extremo a extremo como
prueba del patrón**, dejando los 9 restantes como pasos secuenciados que se
ejecutan uno a uno (congelar → extraer → verde). El dominio piloto propuesto es
**`match_odds`** (`sync_match_odds`): de los más acotados (ingesta + persistencia,
poca lógica), buen candidato para validar la forma `lightweight` + port estrecho
+ adaptador sin arriesgar los dominios complejos.

> El orden y si se abordan más dominios en esta pasada se confirman en el gate de
> Plan Approval; el ritmo por dominio protege la equivalencia estricta.

## Traceabilidad plan-step → requisito

| Paso | Implementa | Requisito |
|------|-----------|-----------|
| 1–2 | Skeleton del módulo de dominio + runner | FR2.1, NFR3 |
| 3–4 | Caracterización del dominio piloto (congelar payload observable) | FR4.1, FR5.1, BR6.1 |
| 5–8 | Extracción: port + adapter + orquestador + facade delegante | FR1.2, FR2.1, FR3, BR2.1–2.3, BR4.1 |
| 9–10 | Verificación de equivalencia + suite en verde | FR5, NFR2 |
| 11 | Inventario de imports + shim si aplica | FR1.3, FR1.3.1 |
| 12 | Documentación + traceability | — |

## Pasos de implementación

- [x] **Step 1 — Estructura del módulo de dominio.** Crear el paquete del dominio
  piloto `backend/app/services/sync/<domain>/` (forma `lightweight`: `__init__.py`,
  `orchestrator.py`, `domain/ports.py`, `infrastructure/<domain>_adapter.py`),
  espejando la organización de `prizes/`/`analytics/`. Sin lógica aún; solo
  esqueleto con imports y docstrings en inglés. NUNCA tocar `data_manager_v2.py`.
- [x] **Step 2 — Verificar el runner de tests y registrar el comando exacto.**
  Confirmar que `pytest` corre desde `backend/` con las fixtures de `conftest.py`;
  registrar en `unit-test-instructions.md` el comando exacto acotado a los tests
  del dominio (p. ej. `pytest backend/tests/test_sync_<domain>_characterization.py`).
- [x] **Step 3 — Caracterización (Data/behavior): congelar el comportamiento
  observable del dominio piloto ANTES de mover código.** Escribir
  `backend/tests/test_sync_<domain>_characterization.py`: aseverar el payload
  (`SyncResult`) del `sync_<domain>()` actual con fakes en memoria — status
  observable (`success`/`no_new_data`/`error`/variantes `no_*`), `records_synced`,
  presencia de `duration_seconds`; y la clave literal en `sync_all()`
  (`match_odds`). Specs que aseveran el efecto, nunca `assert True`.
- [x] **Step 4 — Ejecutar la caracterización contra el código actual (verde).**
  Debe pasar sobre `data_sync_service.py` sin cambios, fijando la línea base de
  equivalencia.
- [x] **Step 5 — Repository/data access: extraer el SQL tras el port.** Definir
  `<Domain>SyncDataPort` (Protocol consumer-owned, sin SQL) en `domain/ports.py`
  con solo las operaciones que el dominio consume; implementar
  `infrastructure/<domain>_adapter.py` envolviendo el SQL/`DataManagerV2` existente
  **verbatim** (BR2.2), sin reescribir ni ampliar el god-file.
- [x] **Step 6 — Business logic / orquestador de aplicación.** Mover la
  orquestación del dominio (ingesta desde el cliente inyectado + delegación al
  adapter para persistencia) a `orchestrator.py`. Trasladar el bloque
  `try/except Integration*Error` (recuperable/fatal, BR2.3 escala-en-escritura) y
  el `time.sleep()` de throttling tal cual (BR4.1), preservando la semántica
  observable byte a byte (FR5.3). Sin credenciales en excepciones (BR4.2).
- [x] **Step 7 — API/facade: `DataSyncService.sync_<domain>()` delega.** Reducir
  el método del facade a una delegación fina al orquestador del dominio (BR1.2);
  misma firma, mismo retorno (BR1.1).
- [x] **Step 8 — `sync_all()` intacto.** Verificar que `sync_all()` sigue
  invocando `sync_<domain>()` en el mismo orden y bajo la misma clave literal
  (BR3.1); no se toca su cuerpo salvo lo necesario.
- [x] **Step 9 — Ejecutar la caracterización contra el código extraído (verde).**
  Los mismos tests del Step 3 deben seguir en verde sin cambios (equivalencia
  estricta demostrada, FR5).
- [x] **Step 10 — Suite completa + piso de cobertura.** Correr `pytest` backend
  completo; la suite queda en verde y la cobertura no baja del piso
  `--cov-fail-under=27` (NFR2). No relajar el piso.
- [x] **Step 11 — Inventario de imports + shim.** Enumerar (grep) los símbolos de
  `data_sync_service.py` consumidos externamente que se hayan movido; añadir shim
  de re-export puntual solo donde un import histórico lo exija (BR1.3, FR1.3.1).
  Verificar que ningún llamador (`api/v1/endpoints/sync.py`, `data_initializer*.py`)
  cambia sus imports.
- [x] **Step 12 — Documentación inline + traceability.** Docstrings en inglés en
  los ficheros nuevos; `ruff check` limpio en los ficheros nuevos (sin `ruff
  format` masivo). Rellenar `code-summary.md`, `source-manifest.json` y
  `traceability.json`.

## Pasos secuenciados de los dominios restantes (una unidad por dominio)

Cada dominio restante repite Steps 3–11 (congelar → extraer → verde), en su propia
rama/commit, respetando la forma decidida en diseño (`full-layered` para
`player_performance`/`rosters`/`prizes` ya extraído; `lightweight` para los
passthrough). Orden propuesto de menor a mayor acoplamiento (confirmable en el
gate): `match_odds` (piloto) → `clauses` → `transactions` → `punishments_bonuses`
→ `dream_teams` → `rosters` → `round_rankings` → `player_performance` →
`players_full`; `prizes` ya está extraído y solo se uniforma al patrón del facade.

## Notas de test (resumen; detalle en `unit-test-instructions.md`)

- Estrategia Minimal: caracterización dirigida por el comportamiento observable de
  cada dominio (payload/estado/modo de fallo), con fakes en memoria de
  `conftest.py`. Sin red, sin BD real, sin credenciales.
- La suite existente se mantiene verde (scope floor `refactor`); no se añade piso
  nuevo más allá de la estrategia. El piso `--cov-fail-under=27` solo sube por
  trinquete.

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
