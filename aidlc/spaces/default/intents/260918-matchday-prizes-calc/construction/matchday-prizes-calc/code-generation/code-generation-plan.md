# Code Generation — Plan (matchday-prizes-calc)

Unidad: `matchday-prizes-calc` (service, dentro del backend `futmondo-api`).
Metodología: **test-after** con **characterization-first** (Testing Contract
abajo). Brownfield: modificar en sitio, sin duplicados; extraer el cálculo puro
sin engordar el god-file `data_sync_service.py`.

## Trazabilidad plan→requisitos

- FR1 (reparto ante empates) → Step 3 (cálculo puro) + Step 4 (regla de empate) + Step 6 (tests nuevo contrato).
- FR2 (elegibilidad + premio por posición) → Step 3.
- FR3 (gating + retroactividad) → Step 3 (gating movido al cálculo puro) + Step 5 (orquestación).
- NFR1/NFR3 (caracterización a coste 0 €) → Step 2. NFR4 (no engordar god-file) → Step 3/5. NFR2/NFR5 → Build and Test.

## Pasos

- [x] **Step 1 — Runner readiness.** Verificar el runner de tests del backend
  (`pytest` desde `backend/`, `pytest.ini`: `testpaths=tests`, `pythonpath=.`).
  Registrar el comando unit-scoped exacto en `unit-test-instructions.md`. (El
  runner ya existe; brownfield.)

- [x] **Step 2 — Caracterización (characterization-first, ANTES de tocar el cálculo).**
  Crear `backend/tests/test_prizes_characterization.py` que congele el
  comportamiento observable ACTUAL de la producción del premio, cubriendo TODAS
  las ramas (Q2=A): `points_prize` (siempre), gating `round_fully_played`,
  ranking flop/top, MVP, dream-team, jornada adelantada/negativa (pseudo-jornada
  con matchday sintético negativo) y el borrado defensivo `DELETE ... NOT IN`.
  Usa **fake de la API Futmondo** (respuestas de ronda deterministas, sin red ni
  `time.sleep`) y **fake de persistencia** (`fake_db`/`_FakeInMemoryDB` de
  `conftest.py`, almacén en memoria de `team_prizes`). **Incluye un test que
  congele el bug actual de empates** (dos equipos con los mismos puntos reciben
  premios de posición distintos) — se marcará como el test que cambia a propósito
  en el Step 6. Deben pasar contra el código ACTUAL.

- [x] **Step 3 — Extraer el cálculo puro (`PrizeCalculator`).** Crear
  `backend/app/services/prizes/calculator.py` con una función pura (sin I/O ni
  SQL) que recibe la lista de entradas de ronda (team_id, round_points), la
  config (`money_per_ranking`, `ranking_mode`, `users_to_rank`, `money_per_point`,
  `mvp_bonus`, `dream_team_bonus`), las señales de gating (`award_round_prizes`),
  el `mvp_team_id` y `dream_team_counts`, y devuelve por equipo
  (`ranking_prize`, `mvp_prize`, `points_prize`, `dream_team_prize`,
  `display_position`). Reproduce EXACTAMENTE la fórmula actual por posición
  (BR2.2) para el caso sin empate. Naming desambiguador (`*_points` vs
  `*_prize`).

- [x] **Step 4 — Regla de empate (FR1/BR3.1/BR3.2).** Dentro del cálculo puro,
  agrupar los premiables por `round_points`; para cada grupo de N que ocupa
  posiciones contiguas p..p+N-1, `ranking_prize` de cada miembro =
  `round(sum(prize(pos) for pos in p..p+N-1) / N)`. N=1 recibe `prize(p)` exacto.

- [x] **Step 5 — Reducir `sync_prizes` a orquestador.** En
  `data_sync_service.py`, reemplazar el bloque de cálculo del `ranking_prize`
  por posición por una llamada a `PrizeCalculator`. `sync_prizes` mantiene
  ingesta (API) y persistencia (UPSERT + `DELETE ... NOT IN`); no gana lógica de
  cálculo nueva (NFR4). Mapear `display_position → position` en la fila.

- [x] **Step 6 — Tests del nuevo contrato (test-after).** Crear
  `backend/tests/test_prizes_calculator.py` (tests unitarios de la función pura,
  5-8): sin empate (sin regresión), 2 empatados (ejemplo jornada 5 =
  1.500.000/1.500.000), 3 empatados, gating no-premiable (solo points_prize),
  equipo con 0 puntos. **Actualizar/retirar de forma trazable** el test de Step 2
  que congelaba el bug de empates (ahora describe el comportamiento correcto).

- [x] **Step 7 — Verificación.** Ejecutar el comando unit-scoped; toda la suite
  del backend en verde. Escribir `code-summary.md`, `source-manifest.json` y
  `traceability.json`.
  <!-- Tests VERDES: unit-scoped 15/15; suite completa 150/150 (baseline 135 + 15
       nuevos, sin regresiones). code-summary.md / source-manifest.json /
       traceability.json los escribe el conductor (fuera del alcance del developer). -->


## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "caracterizar primero `data_sync_service.sync_prizes()` — congelar con",
  "scope": "classic",
  "test_strategy": "standard",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "- **Methodology**: test-after\n- **Ordering**: caracterizar primero `data_sync_service.sync_prizes()` — congelar con\n  tests su comportamiento observable actual en **TODAS las ramas (Q2=A)**: premio por\n  puntos (`points_prize`, siempre), gating de ronda completa (`round_fully_played`),\n  ranking flop/top, MVP, dream-team, jornada adelantada/negativa (pseudo-jornada) y el\n  borrado defensivo `DELETE ... NOT IN`, **incluidos los bugs conocidos si los hubiera**\n  — y solo después implementar la mejora del cálculo (sobre la función pura extraída) y\n  escribir/ejecutar los tests del nuevo contrato (test-after); la suite existente debe\n  permanecer en verde.\n\nDetalle del orden de dos fases para este intent:\n\n1. **Fase caracterización (characterization-first, antes de tocar `sync_prizes`)**:\n   escribir tests que congelen la **PRODUCCIÓN** del premio en `sync_prizes` (hoy con\n   **cobertura directa cero** — GAP CRÍTICO del RE), cubriendo TODAS las ramas de Q2. Es\n   red de seguridad, no TDD: deben pasar contra el código actual. Se apoya en dobles/fakes\n   de la API Futmondo y de la capa de persistencia (patrón `conftest.py`, almacén en\n   memoria) para evitar `time.sleep()` real, llamadas de red y coste. El **CONSUMO** ya está\n   caracterizado (`test_finance_characterization.py`); el hueco es la producción.\n2. **Fase mejora (test-after)**: implementar la mejora de corrección/fiabilidad del cálculo\n   sobre la **función pura extraída** (gating de ronda completa, jornadas adelantadas, modos\n   de ranking) y después escribir los tests del *nuevo* contrato.\n   **Q3=C — incertidumbre abierta**: **aún NO se sabe si hay bugs de cálculo a corregir**;\n   se decide en el análisis de requisitos y la propia caracterización. Por tanto **no se\n   afirma que los importes cambien ni que se conserven**. Si en requisitos se decide cambiar\n   un comportamiento a propósito, los tests de fase 1 que describan ese comportamiento se\n   **retiran/actualizan de forma deliberada y trazable**.\n\n**Separación de responsabilidades al extraer (integrado del OBJECT de developer, aditivo).**\n`sync_prizes` mezcla hoy tres responsabilidades: (a) **ingesta** desde la API Futmondo (I/O\ncon `time.sleep()`), (b) **cálculo puro** de los términos del premio + su gating, y (c)\n**persistencia** (UPSERT `ON CONFLICT` + limpieza `DELETE ... NOT IN` sobre `team_prizes`).\nLa extracción de Q1 separa el **cálculo puro (sin I/O ni SQL)** de ingesta y persistencia,\ndejando estas últimas como colaboradores inyectados. Esa separación es la que hace realizable\nla caracterización a coste 0 €; sin ella \"capa estrecha testeable\" queda ambiguo. La mitad de\nlectura ya existente (routers → `SELECT`/suma sobre `team_prizes`) **puede quedarse como está,\npero no debe crecer** ni introducir recálculo.\n\nNotas y evidencia:\n\n- **Cobertura**: el suelo del scope `feature` (80% líneas) queda como **referencia global**,\n  no como piso bloqueante adicional. Se **exige** que existan tests cubriendo los **caminos\n  nuevos y de error** de `sync_prizes` (producción del premio), **sin piso porcentual\n  adicional bloqueante**. No existe `cov-fail-under`/`fail_under`/`coverageThreshold` en el\n  repo (ratcheting diferido consciente).\n- **Definición mínima de \"hecho\" (testing) del intent**: `sync_prizes` pasa de **0 tests de\n  producción** a caracterizado *antes* del cambio, y con tests del nuevo contrato *después*.\n  Sin esa red, el núcleo del intent no se fusiona.\n- **Herramientas**: backend `pytest` (`backend/pytest.ini`: `testpaths = tests`,\n  `pythonpath = .`, ejecutado desde `backend/`) + `pytest-cov`; frontend `ng test` con\n  **Vitest** + `jsdom` vía builder `@angular/build:unit-test`.\n- **Patrón de aislamiento reutilizable**: `backend/conftest.py` inyecta fakes de\n  `DataManager`/conexión y factories para APIs externas; `test_finance_characterization.py`\n  ya usa un doble de `DataManagerV2` + `get_db` falso. La caracterización de `sync_prizes`\n  debe seguir el mismo patrón: **fake de la API Futmondo** (respuestas de ronda deterministas,\n  sin red ni `sleep`) y **fake de la capa de persistencia** (almacén en memoria de\n  `team_prizes`). Cada test crea y limpia su propio almacén; nunca comparte estado mutable.\n- **Gate**: `pytest`, `ng test` y el escaneo de secretos (gitleaks) son **BLOQUEANTES** en\n  CI (PR→`main`) desde el inicio; lint (ruff/ESLint) y auditorías de dependencias\n  (pip-audit/npm audit) son **advisory** en la fase de saneamiento.\n- **Hueco conocido — paridad `verify`↔gate-de-MR (Q5=A: DIFERIDO)**: el job `verify` de\n  `fly-deploy.yml` (push→`main`) corre `pytest -q` **sin `--cov`**, mientras el gate de PR\n  (`ci.yml`) sí mide cobertura con `--cov=app`. La **paridad de SEGURIDAD ya está cerrada**:\n  gitleaks es BLOQUEANTE en ambos caminos (verificado por devsecops: `@v3` en PR, `@v2` en\n  `verify`, ambos sin `continue-on-error`), y por tanto **lo único diferido es la señal de\n  cobertura (`--cov`) en `verify`** — que es una decisión de calidad/pipeline, no de\n  seguridad. Se **DIFIERE a un futuro diseño de pipeline**, fuera de alcance de este intent;\n  queda registrado como deuda de pipeline, no cerrado por omisión."
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
  "input_sha256": "sha256:995d0f3cc6a6e285f4766c8033e0369d8b92f88c4003cf283db01c7d193e6d82",
  "contract_sha256": "sha256:7ecf99100092769f76e53e5e567b73c87f4cf20142365d637cf8d83211e7b203"
}
```
