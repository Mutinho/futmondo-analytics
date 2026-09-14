# Plan de Code Generation — Arreglo de tests de AnalyticsService

Scope: bugfix (Minimal). Brownfield. Cambio acotado a UN fichero de test:
`backend/tests/test_analytics_service.py`. NO se modifica código de producción
(`backend/app/`). Estrategia: arreglar en el test (Alternativa A, ADR-RE-001).

Trazabilidad plan-step → requisito:
- Step 3 → FR1.1 (caches en fixture), FR1.2, FR1.3
- Step 4 → FR2.1, FR2.2, FR2.3
- Step 5 → FR3.1, FR3.2, NFR1, NFR2, NFR3

## Pasos de implementación

- [x] **Step 1 — Verificar runner y comando de test (runner readiness).** Confirmar el runner existente (`pytest`, config en `backend/pytest.ini`, `pythonpath = .`). Comando unit-scoped exacto (desde `backend/`): `python -m pytest tests/test_analytics_service.py -q`. Registrarlo en `unit-test-instructions.md`. No se crea runner nuevo (brownfield).
- [x] **Step 2 — FR1: inicializar caches en el fixture.** En `fake_init` (dentro del fixture `analytics_service`), añadir `self._team_cache = {}` y `self._player_cache = {}` junto a `self.dm = stub_dm`, replicando el estado del `__init__` real (`analytics_service.py:16-17`) sin instanciar `DataManagerV2`. Arregla `test_championship_trends` (FR1.2) y `test_clause_network` (FR1.3) — desaparece el `AttributeError`.
- [x] **Step 3 — FR2: alinear la aserción de clave.** En `test_player_value_trend`, cambiar `result["players"][0]["latest_price"]` por `result["players"][0]["last_transaction_price"]`, conservando el valor esperado `1000000` (clave real emitida por el servicio en `analytics_service.py:477`). No se toca el servicio (FR2.2). Con Step 2 + Step 3, `test_player_value_trend` pasa (FR2.3).
- [x] **Step 4 — Ejecución de tests (test-after).** El cambio ES la modificación del propio fichero de tests; tras aplicarlo, ejecutar el comando del Step 1 y comprobar que los 6 tests de `test_analytics_service.py` pasan (los 3 arreglados + `test_player_form`, `test_opportunity_streaks`, `test_matchday_projections` — FR3.1). La ejecución real y su verde se validan en Build and Test si el entorno actual no tiene pytest.
- [x] **Step 5 — Regresión dirigida (scope floor bugfix).** Los 3 tests arreglados SON la regresión dirigida al bug (congelan el comportamiento correcto: presencia de caches + clave `last_transaction_price`). No se añaden tests nuevos adicionales (Minimal); se preserva el resto de la suite de caracterización (FR3.2).
- [ ] **Step 6 — Documentación y traceability.** Generar `code-summary.md`, `source-manifest.json` (solo `backend/tests/test_analytics_service.py`) y `traceability.json` (FR1/FR2/FR3/NFR → fichero de test).
- [ ] **Step 7 — FR4 (loop-back 1): arreglar el fallo de resolución de team_name en el test.** Al ejecutar la suite real aflora un tercer fallo (antes enmascarado por el AttributeError): `test_championship_trends` recibe `team-1` en vez de `Team One` porque `_safe_team_info` consulta la BD directamente (`get_db()` + `SELECT ... FROM teams`) y bajo el fixture no hay BD (`except Exception: pass` deja `_team_cache` vacío). Arreglo en el TEST (Alternativa A, sin tocar producción): poblar `self._team_cache` en `fake_init` con los equipos que el stub conoce (p. ej. `self._team_cache = {"team-1": {"team_id": "team-1", "user_id": None, "team_name": "Team One"}}`) y marcar `self._player_cache = {"__teams_loaded__": True}` para que `_safe_team_info` sirva desde caché sin tocar la BD. Con esto `test_championship_trends` pasa. Verificar toda la suite en verde.

## Notas de capas testables
- Data model / repository / API / frontend: **no aplican** (el arreglo es en la capa de test unitario del servicio de analítica). Solo aplica la capa "Business logic / test" a nivel de fixture y aserción.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "org",
  "ordering": "implement each applicable testable layer, then write and run",
  "scope": "bugfix",
  "test_strategy": "minimal",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
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
      "Include a targeted regression for the bug or vulnerability.",
      "Keep the existing test suite green."
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
  "input_sha256": "sha256:933f32e0a09112bec79e6ad9d9b07d8fa79b601a7b325fbe1f9a283f191ae54c",
  "contract_sha256": "sha256:99478f464d6c420b35c11685f3bcb32edde86a8c85b8236e74f7cf898a3796b8"
}
```
