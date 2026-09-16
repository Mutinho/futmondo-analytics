# Code Generation Plan — u2-durable-sync-tasks

> Etapa Code Generation (Construction), unidad `u2-durable-sync-tasks`. Plan de implementación de la
> durabilidad del estado de las tareas de sync sobre el backend existente `futmondo-api` (FastAPI,
> Python 3.12, Neon vía `db_connection`). Metodología: **test-after con caracterización primero**
> (Testing Contract embebido abajo). Coste 0€, sin dependencias de pago.
>
> **Nota de proceso (importante):** las etapas de diseño per-unit (functional-design, nfr-requirements,
> nfr-design, infrastructure-design) quedaron marcadas `[S] skipped` para esta unidad al reiniciar la
> etapa Code Generation (jump forward). Por tanto u2 NO tiene artefactos de diseño propios; este plan
> incorpora el diseño de la durabilidad de tareas, fundamentado en `requirements.md` (FR1.4/1.5/1.6),
> `unit-of-work.md` (U2), `contract-summary.md` (DAG sin aristas; sin contrato inter-unidad) y el
> código brownfield existente (`task_manager.py`, `api/v1/endpoints/sync.py`), reutilizando el patrón
> `stores/` ya establecido en u1. **Esto es una decisión a validar en el gate de Plan Approval.**

## Contexto y trazabilidad de origen

- Requisitos: FR1.4 (estado consultable tras reinicio), FR1.5 (marcar interrumpida-por-reinicio al
  arrancar; no se reanuda), FR1.6 (unicidad 409 contra estado persistido, salvo interrumpida); NFR3
  (coste 0€), NFR4 (no regresión), NFR5 (autoridad de concurrencia en BD, no asumir instancia única).
- Reglas/constraints: C3 (capa de persistencia estrecha, sin ampliar SQL-en-router ni god-files),
  C5 (caracterizar `TaskManager` antes de refactorizar), NFR5 (BD autoridad; caché best-effort).
- Contrato: ninguno inter-unidad (contract-summary: U1 y U2 independientes, DAG sin aristas). No hay
  API pública nueva; los endpoints `/api/v1/sync/*` conservan su contrato observable.
- Componentes (del unit-of-work U2): `TaskService`, `TaskRepository` (nuevos); `TaskManager`
  (existente, degradado a caché best-effort); re-cableo de `SyncEndpoints` (`/api/v1/sync/trigger`,
  `/task/{id}`) para delegar en `TaskService`.
- Código brownfield observado: `task_manager.py` (in-memory, estados pending/running/completed/failed,
  `get_active_task` con staleness 10min, `create_task` cap 20); `sync.py` (`/trigger` con 409 por
  tarea activa, worker en thread daemon, `/task/{id}` polling).

## Restricciones duras (inputs, no sugerencias)

- La BD es la autoridad de estado/concurrencia; el caché (`TaskManager`) es best-effort (BR/NFR5).
- Suite existente permanece en verde (NFR4). Caracterizar `TaskManager` antes de refactorizar (C5).
- Capa de persistencia estrecha (`stores/`), sin ampliar SQL-en-router ni god-files (C3).
- Idiomas: identificadores/docstrings/comentarios en INGLÉS; texto de usuario (`detail` de
  `HTTPException`) en CASTELLANO (Code Style team.md).
- Coste 0€: reutilizar `db_connection` (Neon); sin servicios ni dependencias nuevas.
- No se reanudan tareas automáticamente (out of scope): solo se persiste y se marca el estado (FR1.5).

## Plan de implementación (pasos numerados)

- [x] **Step 1 — Estructura y configuración.** Añadir `TaskRepository` en `backend/app/stores/`
      (paquete ya creado en u1) y `backend/app/services/task_service.py`. Sin ampliar god-files.
- [x] **Step 2 — Runner de tests listo (antes del primer test).** Verificar `pytest` desde `backend/`
      (`pytest.ini`) + reutilizar `backend/conftest.py` (fixture `fake_db` de persistencia en memoria
      ya añadida en u1). Registrar el comando exacto por-unidad en `unit-test-instructions.md`.
- [x] **Step 3 — CARACTERIZACIÓN (red de seguridad, antes de refactorizar) — tests.** Congelar el
      comportamiento ACTUAL de `TaskManager` (deben pasar contra el código de hoy), incluidos fallos
      conocidos: (a) tarea de sync se pierde tras reinicio (in-memory); (b) `get_active_task` marca
      stale a los 10min in-memory; (c) cap de 20 tareas. Con fakes, sin Neon real. (C5).
- [x] **Step 4 — Data model / esquema (implementar).** Script SQL idempotente
      `CREATE TABLE IF NOT EXISTS sync_task (...)` aplicado al arranque (junto al de u1): `task_id`
      PK, `sync_type`, `championship_id`, `status`, `current_step`, `progress` (JSON/TEXT), `result`
      (JSON/TEXT), `error`, `created_at`, `started_at`, `completed_at`.
- [x] **Step 5 — Data model / esquema (tests test-after).** Test de idempotencia del script y de que
      crea el esquema esperado, contra el fake de persistencia.
- [x] **Step 6 — Repository / data access (implementar).** `TaskRepository` en `stores/`: insert de
      tarea, update de estado/progreso, lectura por `task_id`, consulta de tarea activa por
      `championship_id` contra BD (FR1.6), y marcado masivo de tareas `running`/`pending` →
      `interrupted_by_restart` al arrancar (FR1.5). SQL parametrizado, sin SQL en routers (C3).
- [x] **Step 7 — Repository (tests test-after).** Tests: persistencia y lectura de tarea; consulta de
      activa contra BD; marcado interrumpida-por-reinicio; idempotencia. Fakes (5–8 tests, Standard).
- [x] **Step 8 — Business logic (implementar).** `TaskService`: crear tarea (persiste + puebla caché),
      actualizar progreso/estado (BD autoridad + caché best-effort), consultar (caché → BD), unicidad
      409 contra BD (FR1.6) salvo que la previa esté `interrupted_by_restart` (permite relanzar),
      y `mark_interrupted_on_startup()` (FR1.5). `TaskManager` degradado a caché best-effort.
- [x] **Step 9 — Business logic (tests test-after).** Tests: tarea consultable tras "reinicio" (caché
      vacío, lee BD, FR1.4); unicidad 409 contra BD (FR1.6); relanzable si interrumpida; marcado al
      arranque (FR1.5); no reanuda automáticamente. Fakes (5–8 tests, Standard).
- [x] **Step 10 — API / endpoint (implementar re-cableo).** `sync.py`: `/trigger` consulta la unicidad
      contra `TaskService` (BD) en vez de solo `TaskManager` in-memory (FR1.6); `/task/{id}` lee de
      `TaskService` (caché → BD) para ser consultable tras reinicio (FR1.4). El worker persiste
      transiciones de estado vía `TaskService`. Sin endpoints nuevos; contrato observable preservado.
- [x] **Step 11 — API / endpoint (tests test-after).** Tests: `/task/{id}` devuelve estado tras
      "reinicio"; `/trigger` da 409 contra estado persistido y permite relanzar si interrumpida;
      una tarea en curso al reinicio aparece como interrumpida.
- [x] **Step 12 — Frontend behavior.** N/A para esta unidad (backend-only; el frontend ya reconecta
      al task vía polling/localStorage). Se omite por inaplicable, sin cambiar la metodología.
- [x] **Step 13 — Configuración de entorno/build.** Sin secretos ni dependencias nuevas (el esquema
      se aplica con la misma función de arranque idempotente). Sin cambios de coste.
- [x] **Step 14 — Documentación y trazabilidad.** Docstrings en inglés; escribir `source-manifest.json`,
      `code-summary.md` y `traceability.json` (FR/NFR → archivos).

## Traza paso → requisito

| Step | Cubre |
|------|-------|
| 3 | C5 (caracterización de `TaskManager`), congela comportamiento in-memory actual |
| 4–5 | FR1.4 (estado durable), infra (tabla `sync_task`), NFR5 |
| 6–7 | FR1.4, FR1.5 (marcado al arranque), FR1.6 (activa contra BD), C3 |
| 8–9 | FR1.4, FR1.5, FR1.6, NFR5 (BD autoridad; caché best-effort) |
| 10–11 | FR1.4 (consultable tras reinicio), FR1.6 (409 contra BD) |
| 14 | NFR4 (no regresión), trazabilidad |

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "caracterización primero (congelar con tests el comportamiento",
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
      "text": "- **Methodology**: test-after\n- **Ordering**: caracterización primero (congelar con tests el comportamiento\n  observable actual de `SessionStore`/`TaskManager`, **incluidos los bugs conocidos**,\n  antes de refactorizar) y, a continuación, implementar la durabilidad y escribir y\n  ejecutar los tests de cada capa (test-after). La suite existente debe permanecer en\n  verde.\n\nDetalle del orden de dos fases para este intent (integrado de la contribución de calidad):\n\n1. **Fase caracterización** (antes de tocar `SessionStore`/`TaskManager`): escribir\n   tests que congelen el comportamiento actual, *incluido el de fallo* (p. ej. reinicio\n   pierde sesión → 403, tarea de sync huérfana tras redeploy, y la divergencia\n   comentario↔comportamiento de `_helpers.get_user_futmondo_client`, y el bug de\n   precedencia de `is_refresh_token_valid`). Es red de seguridad, no TDD: deben pasar\n   contra el código actual.\n2. **Fase durabilidad (test-after)**: implementar la persistencia y después escribir los\n   tests del *nuevo* contrato (sesión reconstruida tras reinicio, idempotencia de tarea,\n   no reintroducir `password` en claro). Los tests de la fase 1 que describían el *fallo*\n   se actualizan/retiran de forma deliberada y trazable cuando el comportamiento esperado\n   cambia a propósito.\n\nNotas y evidencia adicional:\n\n- **Cobertura (decisión humana Q3)**: el suelo del scope `feature` (80% líneas) queda\n  como **referencia global**, no como piso bloqueante adicional. Se **exige** que existan\n  tests cubriendo los **caminos nuevos y de error** de las piezas de durabilidad\n  (`SessionStore`/`TaskManager`), **sin piso porcentual adicional bloqueante**. La\n  cobertura es hoy una métrica consciente (ratcheting diferido), no una omisión: no existe\n  `cov-fail-under` / `fail_under` / `coverageThreshold` en el repo.\n- **Definición mínima de \"hecho\" (testing) del intent**: `SessionStore` y `TaskManager`\n  pasan de 0 tests a cubiertos en caracterización *antes* del refactor, y con tests del\n  nuevo contrato de durabilidad *después*. Sin esa red, el núcleo del intent no se fusiona.\n- **Herramientas**: backend `pytest` (`backend/pytest.ini`: `testpaths = tests`,\n  `pythonpath = .`, ejecutado desde `backend/`) + `pytest-cov`; frontend `ng test` con\n  **Vitest** + `jsdom` vía builder `@angular/build:unit-test`.\n- **Patrón de aislamiento reutilizable**: `backend/conftest.py` inyecta fakes de\n  `DataManager`/conexión y factories para APIs externas, y la fixture `clean_jwt_env`\n  aísla variables de entorno de arranque. El diseño de durabilidad debe seguir el mismo\n  patrón: **fakes de la capa de persistencia** (almacén en memoria en el test) en lugar\n  de BD Neon real, para tests rápidos, deterministas y sin coste. Cada test crea y limpia\n  su propio almacén; nunca comparte estado mutable entre tests.\n- **Gate**: los tests (`pytest`, `ng test`) y el escaneo de secretos (gitleaks) son\n  **BLOQUEANTES** en CI desde el inicio; lint (ruff/ESLint) y auditorías de dependencias\n  (pip-audit/npm audit) son **advisory** en la fase de saneamiento.\n- **Hueco/nota conocida (a resolver en diseño de CI, no bloquea esta etapa)**: el job\n  `verify` de `fly-deploy.yml` (push→`main`) **no es idéntico** al gate de PR — corre\n  `pytest -q` **sin `--cov`** y **sin gitleaks**. Es defensa en profundidad razonable (el\n  MR ya gateó), pero implica que un secreto introducido por un push directo a `main` solo\n  lo detendría el gate de MR (relevante a FR5). Se apoya en branch protection para forzar\n  MRs; formalizar si `verify` debe replicar gitleaks queda para diseño de pipeline."
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
  "input_sha256": "sha256:c109a3a3368730182e4f6f54120c82a3fcca90919d96d01b385f3c2a24246864",
  "contract_sha256": "sha256:87c021634e2f1fd270ca7294e9e5bea5b01f1908271a028337e9d54969e7c7c1"
}
```
