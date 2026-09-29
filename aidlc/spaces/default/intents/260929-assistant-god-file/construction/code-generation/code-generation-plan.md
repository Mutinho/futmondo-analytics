# Code Generation Plan — descomposición DDD de `assistant_service.py`

Intent: **Oleada 2 god-files (FR13)** · Scope: `refactor` (Minimal) · Brownfield.
Objetivo: descomponer `backend/app/services/assistant_service.py` (~1158 líneas, cobertura CERO)
al paquete `backend/app/services/assistant/` replicando el patrón DDD de la Oleada 1
(`analytics/`), **preservando el comportamiento observable** (superficie pública `get_assistant_service()`
+ `ask()` intacta). Sin cambio funcional. Conversation language: Spanish.

## Estrategia de tests y orden

- **Metodología**: `test-after` (Testing Contract) con **characterization-first por seam** (mandato
  afirmado del proyecto): para cada seam, ESCRIBIR primero un test de caracterización que congele el
  comportamiento observable ACTUAL contra el código existente, LUEGO extraer el seam al paquete, y
  verificar que el mismo test sigue verde sobre el código extraído. El comportamiento ya existe, así
  que caracterizar-primero es coherente con test-after (no es TDD Red/Green de código nuevo).
- **Volumen (Minimal)**: 1 test por requisito al nivel más estrecho + happy-path por seam; la suite
  existente permanece verde; este scope **no** añade piso de cobertura nuevo (el piso `--cov-fail-under=27`
  NO se toca ni se relaja).
- **Fakes in-memory** de `backend/tests/conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`, `fake_db`), sin
  red, sin BD real, sin credenciales/tokens reales.
- **Orden de extracción (Q5=A)**: de menor a mayor acoplamiento — guardrails → AssistantUsageTracker →
  factual → ContextBuilder → `ask()` orquestador + shim.

## Pasos

- [x] **Step 1 — Estructura del paquete y skeleton de configuración de producción.** Crear el árbol
  `backend/app/services/assistant/` (`__init__.py`, `facade.py`, `domain/`, `application/`,
  `infrastructure/`) vacío/mínimo, replicando la disposición de `analytics/`. Sin lógica todavía.
- [x] **Step 2 — Verificar el runner de tests y registrar el comando unit-scoped.** Confirmar que
  `pytest` corre desde `backend/` con `conftest.py`; registrar en `unit-test-instructions.md` el comando
  EXACTO acotado a los tests nuevos del asistente (p. ej. `pytest tests/test_assistant_*.py`), runnable
  ANTES del primer test de caracterización.
- [x] **Step 3 — Guardrails: caracterizar (test-first) el comportamiento observable actual.** Escribir
  `backend/tests/test_assistant_guardrails.py` contra `assistant_service` actual: mensaje bloqueado →
  `GUARDRAIL_RESPONSE` sin factual/LLM [BR1.1]; mensaje permitido continúa [BR1.2]; pureza (sin I/O)
  [BR1.3]. Correr y verificar verde.
- [x] **Step 4 — Guardrails: extraer el módulo puro.** Mover `_check_guardrails` +
  `ALLOWED_KEYWORDS`/`BLOCKED_PATTERNS`/`GUARDRAIL_RESPONSE` a `assistant/domain/guardrails.py` (regex/
  strings, sin I/O). Re-correr los tests de caracterización: siguen verdes.
- [x] **Step 5 — AssistantUsage: caracterizar el tracker (tabla `assistant_usage`).** Escribir
  `backend/tests/test_assistant_usage.py` con `fake_db`: comprobación de cuota antes de servir [BR4.1],
  registro de consumo tras servir [BR4.2], `CREATE TABLE IF NOT EXISTS` idempotente preservado [BR4.3].
  Correr y verificar verde.
- [x] **Step 6 — AssistantUsage: extraer agregado + port + adaptador.** Definir `AssistantUsagePort`
  (Protocol, sin SQL) en `assistant/domain/ports.py`; mover la persistencia con el SQL crudo (incluido
  el `CREATE TABLE IF NOT EXISTS`) a `assistant/infrastructure/` tras el port. Re-correr: verdes.
- [x] **Step 7 — Capa factual: caracterizar.** Escribir `backend/tests/test_assistant_factual.py`:
  coincidencia factual → respuesta desde datos sin LLM [BR2.1]; lecturas vía el port de datos [BR2.2].
  Correr y verificar verde.
- [x] **Step 8 — Capa factual: extraer.** Añadir `AssistantReadPort` (Protocol, solo lectura) a
  `assistant/domain/ports.py`; mover `_try_factual_answer` + handlers `_factual_*` a
  `assistant/application/` sobre el port; SQL de lectura al adaptador de infraestructura. Re-correr: verdes.
- [x] **Step 9 — ContextBuilder: caracterizar (incluida la degradación).** Escribir
  `backend/tests/test_assistant_context.py`: sin factual → ContextBuilder + LLM con contexto [BR3.1];
  SQL solo tras el port [BR3.2]; **degradación**: fallo de lectura de contexto/mercado degrada sin
  romper (omite sección / contexto parcial) [BR3.3]. Correr y verificar verde.
- [x] **Step 10 — ContextBuilder: extraer.** Mover `_build_context` + métodos `_ctx_*` a
  `assistant/application/` sobre `AssistantReadPort`; los ~42 `cursor.execute` van SOLO al adaptador de
  infraestructura (`db.adapt_params` + `?`), incluido `_save_market_to_db`/`market_today`. Re-correr: verdes.
- [x] **Step 11 — LLM: caracterizar el fallback y la degradación.** Escribir
  `backend/tests/test_assistant_llm.py` con un doble del port: Groq→Gemini orden preservado [BR5.1];
  fallo LLM degrada sin romper [BR5.3]; sin credenciales/tokens en excepciones [BR5.4]. Correr verde.
- [x] **Step 12 — LLM: extraer el port/adaptador.** Definir `LLMPort` (`complete(...)`) en
  `assistant/domain/ports.py`; mover la llamada Groq + fallback Gemini + `except Exception` a
  `assistant/infrastructure/` encapsulados [BR5.2]. Re-correr: verdes.
- [x] **Step 13 — `ask()` orquestador + fachada + shim.** Escribir la fachada delgada
  `assistant/facade.py` (`AssistantService`, singleton `get_assistant_service()`, `async ask(...)`
  con inyección por constructor con default de los tres ports) que orquesta guardrails→cuota→factual→
  contexto→LLM→registro→respuesta [BR6.1]. Dejar `backend/app/services/assistant_service.py` como
  **shim de re-export**. Escribir `backend/tests/test_assistant_facade.py`: superficie pública idéntica
  + flujo end-to-end de `ask()` con dobles de los ports (happy factual, happy generativo, bloqueado,
  degradación LLM, degradación contexto). Correr verde.
- [x] **Step 14 — Verificar suite completa e import histórico.** Correr `pytest` del backend completo:
  suite existente verde (sin regresiones, NFR1.1), el endpoint `assistant.py` importa sin cambios
  (`from app.services.assistant_service import get_assistant_service`), cobertura NO baja (NFR1.2).
  Formatear SÓLO los ficheros nuevos del paquete (quirúrgico, sin `ruff format`/`--fix` masivo).
- [x] **Step 15 — Documentación y trazabilidad.** Docstrings en inglés en los módulos nuevos;
  `code-summary.md`, `source-manifest.json` (rutas de app tocadas) y `traceability.json`
  (cada AC/BR/FR → fichero de implementación/test).

## Trazabilidad paso → requisito

| Step | Requisitos / Reglas |
|------|---------------------|
| 1-2  | FR2.1 (estructura del paquete); runner (Testing Contract) |
| 3-4  | FR3.1, BR1.1-BR1.3 (guardrails puro) |
| 5-6  | FR3.4, FR4.2, FR4.3, BR4.1-BR4.3 (AssistantUsage + port) |
| 7-8  | FR3.2, FR4.1, BR2.1-BR2.2 (factual + AssistantReadPort) |
| 9-10 | FR3.3, FR4.1, FR4.3, FR6.2, BR3.1-BR3.3 (ContextBuilder + degradación) |
| 11-12| FR5.1, FR5.2, FR6.2, BR5.1-BR5.4 (LLMPort + fallback + degradación) |
| 13   | FR1.1, FR1.2, FR2.2, BR6.1 (fachada + `ask()` orquestador + shim) |
| 14   | NFR1.1, NFR1.2, NFR1.3, NFR2.1, NFR3.2, NFR4.1 (paridad, suite verde, cobertura, estilo) |
| 15   | trazabilidad + documentación |

## Restricciones aplicadas (inputs, no sugerencias)

- NO ampliar los god-files ni el patrón SQL-en-router; el SQL nuevo vive SOLO en los adaptadores.
- NO bajar/relajar el piso de cobertura (`--cov-fail-under=27`); el trinquete solo sube.
- NO reformatear en masa; formatear sólo los ficheros nuevos o de forma quirúrgica.
- Identificadores/docstrings/comentarios en INGLÉS; texto de usuario en CASTELLANO.
- Tests con fakes in-memory; sin red, sin BD real, sin credenciales/tokens reales.
- Coste 0 € (sin dependencias nuevas; stdlib + pytest existente).

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
