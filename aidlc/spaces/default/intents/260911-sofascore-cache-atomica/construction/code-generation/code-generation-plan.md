# Plan de Generación de Código — Reemplazo transaccional de la caché de Sofascore

> Intent: `260911-sofascore-cache-atomica` · Scope: `bugfix` · Depth: Minimal ·
> Test strategy: Minimal · Proyecto brownfield (FastAPI + Neon PostgreSQL).
> Trabajo zero-Unit: una única iteración de implementación bajo
> `<record>/construction/code-generation/`.

## Resumen del cambio

Hoy `POST /api/v1/sync/sofascore` borra la caché (`DELETE FROM sofascore_cache`)
y la confirma en su propia conexión ANTES de repoblar jugador a jugador. Si el
repoblado falla a mitad (baneo de IP → HTTP 403, o parcial), la caché queda
vacía o incompleta. Este bugfix hace el reemplazo **atómico todo-o-nada** y añade
**doble protección**: (1) detección de baneo (403) que aborta sin swap, y (2) una
red de seguridad de umbral del 50% de cobertura que descarta repoblados parciales.
El cambio se limita a `sofascore_client.py` (señalización de baneo),
`sofascore_sync.py` (transacción + criterios de éxito) y una prueba de regresión.

## Alcance de ficheros (superficie mínima — NFR3)

- `backend/app/services/sofascore_client.py` — modificar: distinguir 403 (baneo)
  de 404/no-encontrado; propagar señal de baneo.
- `backend/app/api/v1/endpoints/sofascore_sync.py` — modificar: reemplazo en una
  sola transacción (DELETE + INSERT), detección de baneo (no swap), umbral 50%,
  respuesta diferenciada.
- `backend/app/core/constants.py` — modificar: constante `SOFASCORE_MIN_COVERAGE_RATIO`.
- `backend/tests/test_sofascore_sync_characterization.py` — crear: regresión dirigida.

## Metodología de prueba (del Testing Contract)

`test-after`: implementar cada capa aplicable y después escribir/ejecutar sus
pruebas. Capas aplicables a este bugfix: **Business logic** (criterios de éxito y
señalización de baneo) y **API / endpoint** (transacción atómica del endpoint).
Las capas Data model, Repository y Frontend no aplican: no hay migración de
esquema (FR3.3 fuera de alcance), no se añade capa de repositorio nueva, y no hay
cambio de frontend en este bugfix.

## Testing Contract (verbatim — no editar)

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

## Pasos de implementación

- [x] **Step 1 — Configuración de producción / constante de umbral.** En
  `backend/app/core/constants.py` añadir `SOFASCORE_MIN_COVERAGE_RATIO = 0.5`
  (constante configurable, no literal disperso). Implementa FR2.5.
- [x] **Step 2 — Verificar runner de test y registrar el comando unit-scoped.**
  Confirmar que `python -m pytest tests/test_sofascore_sync_characterization.py`
  se ejecuta desde `backend/` (pytest.ini fija `pythonpath = .`). Registrar el
  comando exacto en `unit-test-instructions.md`. (runner_ready_before_first_test)
- [x] **Step 3 — Business logic: señalización de baneo en el cliente.** En
  `sofascore_client.py`: (a) definir excepción `SofascoreIPBanError`; (b) en
  `_get` y `search_player`, distinguir HTTP 403 (baneo → lanzar
  `SofascoreIPBanError`) de 404/sin resultados (→ `None`). Se preserva el
  comportamiento de 404 y de status genéricos ≠200/≠403 (warning + `None`).
  Implementa FR2.1.
- [x] **Step 4 — Business logic: criterio de éxito del repoblado.** Añadir una
  función pura evaluable en `sofascore_sync.py` (o helper de módulo) que decida
  si aplicar el swap: `should_apply_replacement(synced, processed, banned,
  min_ratio)` → `False` si `banned` es True (FR2.2), o si
  `processed > 0 and synced/processed < min_ratio` (FR2.4). Devuelve la razón
  para la respuesta diferenciada (FR2.3). Implementa FR2.2, FR2.4.
- [x] **Step 5 — Business logic: tests (test-after).** En
  `test_sofascore_sync_characterization.py` cubrir `should_apply_replacement`
  y la señalización de baneo del cliente (mock de respuesta 403 → excepción; 404
  → `None`).
- [x] **Step 6 — API / endpoint: reemplazo atómico en una transacción.** En
  `sync_sofascore`: primero recolectar todos los resultados del repoblado
  (búsqueda + stats), capturando `SofascoreIPBanError`; después, en UNA sola
  `with db.get_connection() as conn` (una transacción), ejecutar `DELETE FROM
  sofascore_cache` seguido del INSERT batch, SOLO si `should_apply_replacement`
  es True. Si no se aplica, NO se toca la caché (no DELETE, no INSERT). Elimina
  el `DELETE` prematuro en conexión separada (líneas ~68-71 actuales). Implementa
  FR1.1, FR1.2, FR1.3, FR2.2, FR2.4, FR3.1, NFR1.
- [x] **Step 7 — API / endpoint: respuesta diferenciada.** La respuesta incluye
  `applied` (bool), `reason` (`"ok"` | `"ip_ban"` | `"below_threshold"`),
  `synced`, `errors`, `total_players`. En caso de baneo `success` sigue `True`
  pero `applied=False`, `reason="ip_ban"`, de forma que frontend y cron lo
  distingan. Implementa FR2.3. (El `ON CONFLICT (player_name, championship_id)`
  se mantiene sin cambios — FR3.3.)
- [x] **Step 8 — API / endpoint: tests (test-after) — regresión dirigida.** En
  `test_sofascore_sync_characterization.py`, con un fake de `db` (patrón
  `test_analytics_service.py`, sin BD real) y fakes del cliente Sofascore/futmondo,
  probar: (a) repoblado exitoso → DELETE+INSERT en la misma conexión, caché
  reemplazada; (b) baneo (403) a mitad → NO DELETE, caché intacta,
  `reason="ip_ban"`; (c) repoblado parcial < 50% → NO DELETE, caché intacta,
  `reason="below_threshold"`; (d) parcial ≥ 50% → swap aplicado. Regresión del
  bug (FR1, FR2, NFR4).
- [x] **Step 9 — Documentar la deprecación de `championship_id`.** Comentario en
  el INSERT de `sofascore_sync.py` marcando `championship_id` como DEPRECADA (no
  leída por ninguna consulta; retirada de esquema fuera de alcance — FR3.2,
  FR3.3).
- [x] **Step 10 — Configuración de entorno/build.** Sin cambios: no se añaden
  dependencias ni infraestructura (NFR2 coste 0€, NFR3 superficie mínima).
- [x] **Step 11 — Documentación y trazabilidad.** Escribir `code-summary.md`,
  `source-manifest.json` y `traceability.json`. Verificar suite existente en
  verde (NFR4).

## Trazabilidad requisito → paso

| Requisito | Paso(s) | Fichero(s) |
|-----------|---------|-----------|
| FR1.1 Reemplazo atómico todo-o-nada | Step 6 | `sofascore_sync.py` |
| FR1.2 DELETE+INSERT en una transacción | Step 6 | `sofascore_sync.py` |
| FR1.3 Caché intacta si no hay éxito | Step 6 | `sofascore_sync.py` |
| FR2.1 Detección de baneo (403 vs 404) | Step 3 | `sofascore_client.py` |
| FR2.2 Baneo → no swap, caché intacta | Step 4, Step 6 | `sofascore_sync.py` |
| FR2.3 Respuesta diferenciada de baneo | Step 7 | `sofascore_sync.py` |
| FR2.4 Umbral 50% de cobertura | Step 4, Step 6 | `sofascore_sync.py` |
| FR2.5 Umbral como constante configurable | Step 1 | `constants.py` |
| FR3.1 Reemplazo sobre toda la tabla | Step 6 | `sofascore_sync.py` |
| FR3.2 `championship_id` deprecada (documentar) | Step 9 | `sofascore_sync.py` |
| FR3.3 Sin migración de esquema / `ON CONFLICT` intacto | Step 7 | `sofascore_sync.py` |
| NFR1 Integridad (lecturas ven vieja o nueva completa) | Step 6, Step 8 | `sofascore_sync.py` |
| NFR2 Coste 0€ | Step 10 | — |
| NFR3 Superficie mínima | (todos) | 3 ficheros + 1 test |
| NFR4 No regresión (suite en verde) | Step 5, Step 8, Step 11 | `tests/` |
