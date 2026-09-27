# Plan de Generación de Código — Oleada 1: extracción DDD de `analytics_service.py`

> Intent `260927-god-files-refactor`, scope `refactor`, depth Minimal, unidad única (zero-Unit). Conversation language: Spanish.
>
> Este es el **primer Bolt de extracción** (Oleada 1 del plan de oleadas de `functional-spec.md`, BR4.1): descomponer `analytics_service.py` (34 KB, 828 líneas) en un bounded context `analytics/` con fachada delgada + capas DDD, **preservando el comportamiento observable** (BR1.1) y **characterization-first** (BR1.3): se congela con tests el comportamiento de los `get_*` sin cobertura ANTES de mover código. Valida el patrón DDD end-to-end sobre el fichero de menor riesgo antes de tocar el núcleo (`data_manager`, Oleada 4).

## Alcance de este Bolt (qué SÍ y qué NO)

**SÍ:**
- Crear el paquete `backend/app/services/analytics/` con capas `domain/`, `application/`, `infrastructure/` y una **fachada** `AnalyticsService` que preserva su superficie pública exacta.
- Preservar el import path `from app.services.analytics_service import AnalyticsService` (el endpoint lo usa) mediante re-export.
- Definir el **puerto consumidor propio** `AnalyticsDataPort` (interfaz en `analytics/domain/`) que expresa SOLO lo que analytics necesita de los datos, e implementar `DataManagerAnalyticsAdapter` (en `analytics/infrastructure/`) **sobre la fachada `DataManagerV2` ACTUAL** (no sobre repositorios de `data_manager`, que aún no existen — Oleada 4). Esto invierte la dependencia (DIP, BR2.3) sin acoplar el orden de oleadas.
- Mover los **2 `cursor.execute` crudos** de `analytics_service` (el `SELECT ... FROM teams` de `_safe_team_info` y el `SELECT ... FROM players WHERE player_id IN (...)` del área `get_market_watchlist`) detrás del adaptador (`infrastructure/`), único sitio con SQL crudo (BR2.2).
- Inyección por constructor con defaults que preservan el comportamiento actual (BR2.6): `AnalyticsService()` sin argumentos sigue funcionando idéntico.
- Characterization-first: extender `backend/tests/test_analytics_service.py` a los `get_*` sin test directo ANTES de mover, y un test de contrato del adaptador.

**NO (fuera de alcance / preservado):**
- NO se modifica ningún consumidor: `backend/app/api/v1/endpoints/analytics.py` y su `get_service()` quedan intactos (FR2.1).
- NO se toca el `SELECT` inline del endpoint `championship/classification-full` (SQL-en-router **preexistente**): es deuda anterior a este intent; tocar el router violaría "consumers not modified". La regla afirmada prohíbe **introducir** SQL-en-router nuevo, no obliga a sanear el existente en este Bolt. Se registra como deuda.
- NO se abordan las Oleadas 2–4 (assistant, sync, data_manager): otros Bolts.
- NO se reformatea en masa `analytics_service.py` ni ningún brownfield; `ruff format` SOLO sobre módulos nuevos (BR5.2).
- NO se introduce dependencia nueva (stdlib `typing.Protocol` basta; coste 0 €, BR5.1).

## Superficie pública preservada (contrato observable — BR1.1)

`AnalyticsService` expone **11 métodos públicos `get_*`** (superficie real verificada por inspección; la funcspec citaba "10"):

| # | Método público | ¿Test directo hoy? |
|---|----------------|--------------------|
| 1 | `get_championship_trends` | Sí (`test_championship_trends`) |
| 2 | `get_championship_custom_classification` | **No — gap** |
| 3 | `get_championship_heatmap` | **No — gap** |
| 4 | `get_player_form` | Sí (`test_player_form`) |
| 5 | `get_player_value_trend` | Sí (`test_player_value_trend`) |
| 6 | `get_user_consistency` | **No — gap** |
| 7 | `get_user_market_activity` | **No — gap** |
| 8 | `get_market_watchlist` | **No — gap** |
| 9 | `get_clause_network` | Sí (`test_clause_network`) |
| 10 | `get_opportunity_streaks` | Sí (`test_opportunity_streaks`) |
| 11 | `get_matchday_projections` | Sí (`test_matchday_projections`) |

Cobertura de caracterización directa: **6 de 11**. Gap a cerrar ANTES de mover código: **5** (`custom_classification`, `heatmap`, `user_consistency`, `user_market_activity`, `market_watchlist`). El constructor `AnalyticsService()` (sin argumentos) se preserva: el endpoint lo llama vía `Depends(get_service)`.

Seams privados a reubicar (detalle de implementación, sin contrato observable propio): `_safe_team_info`, `_resolve_real_team_name`, `_safe_player_info`, `_build_team_lookup`, `_resolve_team`.

## Arquitectura objetivo del paquete

```
backend/app/services/analytics/
├── __init__.py            # re-exporta AnalyticsService (fachada); mantiene import path
├── facade.py              # AnalyticsService: application service delgado; delega en use-cases; ctor inyecta AnalyticsDataPort (default = DataManagerAnalyticsAdapter)
├── domain/
│   ├── __init__.py
│   └── ports.py           # AnalyticsDataPort (Protocol): SOLO los métodos de datos que analytics consume
├── application/
│   ├── __init__.py
│   └── calculations.py    # funciones/casos de uso de cálculo puros que operan sobre el puerto (mueven la lógica get_* + resolución de equipos/jugadores)
└── infrastructure/
    ├── __init__.py
    └── data_manager_adapter.py  # DataManagerAnalyticsAdapter: implementa AnalyticsDataPort sobre DataManagerV2 ACTUAL + aloja los 2 SELECT crudos (teams, players)
```
`backend/app/services/analytics_service.py` se reduce a un **shim de re-export** (`from app.services.analytics.facade import AnalyticsService`) para preservar el import path histórico sin duplicar clases (NUNCA `analytics_service_modified.py`).

## Contrato de Testing (fuente de verdad del orden de tests)

<!-- Pegado verbatim de `aidlc engine testing-posture render`. NO editar. -->

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

**Adaptación del perfil (metodología `test-after` respetada, capas inaplicables omitidas):** este Bolt es un refactor brownfield sin nuevas entidades ni UI. Las capas `Data model / database behavior` y `Frontend behavior` NO aplican (no hay esquema nuevo ni frontend en este intent). Las capas aplicables son `Repository / data access` (el adaptador) y `Business logic` (los cálculos + la fachada). La regla **characterization-first (BR1.3)** es una obligación adicional del intent que **antepone** los tests de caracterización de los `get_*` sin cobertura ANTES de mover código; el resto (contrato del adaptador) sigue `test-after` (implementar la capa, luego su test). No se coacciona a TDD.

**Nota de tooling:** el `applicable_notes` del contrato menciona fixtures `_FakeInMemoryDB`/`clean_jwt_env`/`fake_db` de un `conftest.py`; ese `conftest.py` **no existe** en `backend/tests/`. El patrón real y establecido en `test_analytics_service.py` es un **`StubDM` autocontenido** inyectado en la fachada. Se sigue el patrón real (stub in-memory + inyección por constructor), lo cual el contrato permite (es una nota de tooling/scope, no una anulación de metodología).

## Pasos de implementación (numerados, con checkboxes)

- [x] **Step 1 — Estructura del paquete y config de producción.** Crear el árbol `backend/app/services/analytics/` con `__init__.py` en cada capa (`analytics/`, `domain/`, `application/`, `infrastructure/`). Sin lógica todavía; solo el esqueleto de módulos que las capas rellenarán. Identificadores/docstrings en inglés (Code Style).
- [x] **Step 2 — Verificar runner y registrar el comando unit-scoped.** Confirmar que la suite corre DESDE `backend/` (`pytest.ini`: `pythonpath=.`, `testpaths=tests`). Registrar en `unit-test-instructions.md` el comando EXACTO acotado a esta unidad: `python -m pytest tests/test_analytics_service.py`. El runner ya existe (brownfield): se verifica antes del primer paso de test, no se bootstrappea.
- [x] **Step 3 — Caracterización previa (BR1.3, characterization-first) — CONGELAR ANTES DE MOVER.** Extender `backend/tests/test_analytics_service.py` (extendiendo el `StubDM` con los métodos de datos que falten) para cubrir con test directo los **5 `get_*` sin cobertura**: `get_championship_custom_classification`, `get_championship_heatmap`, `get_user_consistency`, `get_user_market_activity`, `get_market_watchlist`. Cada test asevera el **payload observable** (una clave/valor real del resultado), nunca `assert True`. Estos tests se escriben y corren en VERDE contra el `analytics_service.py` ACTUAL (sin mover), congelando su comportamiento. Este paso PRECEDE a cualquier movimiento de código (Steps 5–7).
- [x] **Step 4 — (capa Data model / DB behavior: N/A)** — no aplica: refactor sin esquema nuevo. Omitido por inaplicabilidad, sin cambiar la metodología.
- [x] **Step 5 — Repository / data access: implementar.** Definir `AnalyticsDataPort` (Protocol) en `analytics/domain/ports.py` con SOLO los métodos de datos que analytics consume (`get_team_standings_history`, `get_latest_matchday`, `get_team_by_id`, `get_player_by_id`, `get_all_users_with_points`, `get_transactions_raw`, `get_clausulable_player_stats`, `get_clauses_raw`, `get_free_agent_candidates`, `get_player_streak_data`, `get_match_odds`, más las lecturas crudas `fetch_all_teams()` y `fetch_players_by_ids(ids)` que sustituyen los 2 `cursor.execute`). Implementar `DataManagerAnalyticsAdapter` en `analytics/infrastructure/data_manager_adapter.py` sobre `DataManagerV2` ACTUAL: delega los métodos de datos en `self.dm.<método>` y **aloja los 2 SELECT crudos** (`SELECT team_id, user_id, team_name FROM teams` y `SELECT player_id, name, real_team_id, value FROM players WHERE player_id IN (...)`) usando `db_connection.get_db()` como hoy, verbatim (mismo SQL, mismo resultado — BR1.2). SQL crudo SOLO aquí (BR2.2). `domain/` no importa `infrastructure/` ni framework (BR2.1).
- [x] **Step 6 — Repository / data access: test tras implementación.** Añadir a `test_analytics_service.py` un test de contrato del adaptador con un doble in-memory de la fachada de BD (patrón `db.get_connection()` como en `test_team_prizes_atomic_replacement.py`): verificar que `fetch_all_teams()` y `fetch_players_by_ids()` devuelven exactamente la forma de fila que el SQL previo producía (BR1.2), y que los métodos delegados llaman al `dm` subyacente. Aserciones sobre el resultado real, no espejo.
- [x] **Step 7 — Business logic: implementar (mover la lógica).** Mover los cálculos de los 11 `get_*` y los helpers de resolución (`_safe_team_info`, `_resolve_real_team_name`, `_safe_player_info`, `_build_team_lookup`, `_resolve_team`) a `analytics/application/calculations.py`, operando SOBRE el puerto (no sobre `self.dm` directo). La fachada `AnalyticsService` (`analytics/facade.py`) preserva los 11 métodos públicos y **solo delega** (BR2.5) en los casos de uso. Constructor: `def __init__(self, data: AnalyticsDataPort | None = None)` → default `DataManagerAnalyticsAdapter()` (BR2.6, OCP). Cachés `_team_cache`/`_player_cache` preservadas en su semántica observable (FR2.3). Convertir `backend/app/services/analytics_service.py` en shim de re-export.
- [x] **Step 8 — Business logic: test tras implementación / re-verificación.** Correr la suite de caracterización extendida (Step 3 + Step 6) contra el código YA movido: los 11 `get_*` deben seguir en verde con idéntico payload (BR1.1). Ajustar el fixture de `test_analytics_service.py` para inyectar el stub vía el nuevo constructor (`AnalyticsService(data=stub_port)`), eliminando el `monkeypatch` de `__init__` si procede (patrón testeable-sin-monkeypatch, BR2.6). NO se baja el piso de cobertura para pasar (ratchet solo sube).
- [x] **Step 9 — (capa API / endpoint: N/A cambios)** — el endpoint `analytics.py` y `get_service()` NO se tocan (FR2.1); se verifica que `AnalyticsService()` sin argumentos sigue construyéndose e importándose por el path histórico. Sin nuevo test de endpoint (consumidor preservado).
- [x] **Step 10 — (capa Frontend: N/A)** — sin frontend en este intent.
- [x] **Step 11 — Config de entorno/build.** `ruff format` SOLO sobre los módulos NUEVOS de `analytics/` (BR5.2); `ruff check` sobre los nuevos (select E,F,I). NO reformatear `analytics_service.py` ni otros brownfield. Sin dependencias nuevas (coste 0 €, BR5.1).
- [x] **Step 12 — Documentación y trazabilidad.** `code-summary.md` (ficheros creados/modificados, decisiones, deviations), `source-manifest.json` (todo path de aplicación tocado), `traceability.json` (cada AC/BR/FR → fichero de implementación o test). Correr la suite completa desde `backend/` verificando verde (BR4.2: comportamiento preservado + ≥1 seam extraído).

## Trazabilidad historia/requisito → paso de código

| Requisito / Regla | Descripción | Paso(s) del plan |
|-------------------|-------------|------------------|
| FR1.1, BR4.1 | Oleada 1 = analytics primero | Todo el Bolt |
| FR2, FR2.1, BR2.5 | Fachada delgada, superficie pública preservada | Step 7, Step 9 |
| FR2.2, BR2.2 | SQL aislado en infrastructure/ (2 cursor.execute) | Step 5 |
| FR2.3, BR2.3, NFR3 | application depende de la interfaz (DIP) | Step 5, Step 7 |
| FR2.3, BR2.6 | inyección por constructor con defaults (OCP, testeable) | Step 7, Step 8 |
| BR2.1 | domain/ sin infra ni framework | Step 5 |
| BR2.4 | un puerto/adaptador coherente para el contexto | Step 5 |
| BR1.2 | repositorio ≡ mismo resultado que SQL inline | Step 5, Step 6 |
| FR3, FR3.2, BR1.3 | caracterización just-enough ANTES de mover (5 get_* sin test) | Step 3 |
| FR3.3, NFR3 | tests con fakes in-memory, sin red/BD/credenciales | Step 3, Step 6, Step 8 |
| FR4.1, FR4.2, NFR2, BR4.2 | suites verdes + ≥1 seam extraído, comportamiento preservado | Step 8, Step 12 |
| NFR1 | menor responsabilidad concentrada (SQL fuera de la fachada) | Step 5, Step 7 |
| NFR4, BR5.1 | coste 0 €, sin dependencias nuevas | Step 11 |
| BR5.2 | sin reformateo masivo brownfield | Step 11 |

## Riesgos y mitigaciones

- **Riesgo:** el fixture de test actual monkeypatchea `__init__`; al introducir inyección por constructor, el fixture debe migrar. **Mitigación:** Step 8 migra el fixture a `AnalyticsService(data=stub_port)`; los tests de caracterización nuevos (Step 3) se escriben contra el código actual primero y se re-verifican tras mover.
- **Riesgo:** divergencia sutil de payload al mover cálculos. **Mitigación:** characterization-first congela los 11 `get_*` antes de mover (Step 3 + los 6 ya existentes); Step 8 re-corre en verde.
- **Riesgo:** los 2 SELECT crudos usan `get_db()` global. **Mitigación:** se mueven verbatim al adaptador (mismo SQL); el adaptador acepta la fábrica de BD por defecto para preservar comportamiento.
