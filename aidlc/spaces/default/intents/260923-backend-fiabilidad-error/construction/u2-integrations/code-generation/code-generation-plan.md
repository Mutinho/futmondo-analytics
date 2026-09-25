# Code Generation Plan — u2-integrations (Integraciones)

Intervención de fiabilidad **acotada y aditiva** sobre código backend existente.
NO se amplían los god-files (`data_sync_service.py`, `data_manager_v2.py`) ni el
patrón SQL-en-router; el código nuevo vive tras una capa/función estrecha
testeable. U1 (`u1-error-layer`) ya entregó `app/services/integration_errors.py`
(`IntegrationError` + `IntegrationBanError`/`IntegrationTimeoutError`/
`IntegrationUnparseableError`) y `SofascoreClient` ya lanza y propaga
`SofascoreIPBanError` (re-parentada bajo `IntegrationBanError`). U2 se apoya en
esa capa.

Metodología: **test-after, characterization-first** (ver Testing Contract abajo).
Cada paso brownfield se congela con tests ANTES de endurecerlo; los specs de
fallo **aseveran el EFECTO** (recuperable → `DEGRADED` + no falla; fatal →
propagada + sin datos a medias). Suite existente en verde en cada paso.

## Alcance y trazabilidad (paso → requisito)

Núcleo migrado (FR4.3): `futmondo_client._make_request` + los llamadores donde un
`None` no detectado corrompe datos. El resto de llamadores queda como **deuda
registrada** (ver Step 3).

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

> Nota de aplicabilidad (test-after brownfield): las capas "Frontend behavior" del
> perfil NO aplican (U2 es backend puro); se omiten sin cambiar la metodología.
> "Data model / database behavior" aplica al punto de escritura `team_prizes`
> (comportamiento transaccional), no a un esquema nuevo. Se antepone la
> caracterización a cada endurecimiento, como fija el `ordering`.

## Pasos de implementación

### Step 1 — Verificar el runner de tests y fijar el comando por-unidad
- [x] Verificar `backend/pytest.ini` (`testpaths = tests`, `pythonpath = .`) y
  `backend/conftest.py` (fixtures `_FakeInMemoryDB`/`_FakeCursor`, `clean_jwt_env`,
  `fake_db`). Runner ya presente (brownfield): no bootstrap.
- [x] Fijar el comando por-unidad exacto en `unit-test-instructions.md`
  (ver ese fichero). Sin `--cov` bloqueante (observabilidad-only).

### Step 2 — Characterization de `_make_request` + inventario de llamadores (FR4.3, BR6.1)
- [x] **Antes de tocar nada**, escribir `backend/tests/test_futmondo_client_characterization.py`
  que congele el comportamiento ACTUAL de `_make_request`: no-auth → `None`;
  `Timeout` → `None`; `RequestException` → `None`; `JSONDecodeError` → `None`;
  200 OK → dict. Con dobles/fakes en memoria (monkeypatch de `self.session.post`),
  sin red ni credenciales.
- [x] Entregar el **inventario verificable de llamadores** de `_make_request`
  como sección en `code-summary.md` (y aserción en el test):
  - En `futmondo_client.py` (~20 `get_*`): todos hoy `resp = _make_request(...)`
    y `if not resp: return None`.
  - En `app/api/v1/endpoints/roster.py` (4): `putonmarket`, `toggleplayer`,
    `myplayers`, `cancelsell`.
- [x] Clasificar **núcleo vs deuda**: núcleo = `_make_request` + los llamadores
  del sync donde un `None` no detectado corrompe/omite datos silenciosamente;
  deuda = el resto (documentada en `code-summary.md`).

### Step 3 — Migrar el contrato de `_make_request` a excepción tipada (FR4.2, BR1.1)
- [x] `_make_request`: `except requests.exceptions.Timeout` →
  `raise IntegrationTimeoutError(status=None, endpoint=endpoint)`;
  `except requests.exceptions.RequestException` →
  `raise IntegrationRequestError(...)` (**ver Step 3a**);
  `except json.JSONDecodeError` → `raise IntegrationUnparseableError(...)`.
  `except <Typed>: raise` ANTES del `except Exception` genérico. Nunca
  `return None` silencioso como señal de fallo. El caso no-autenticado se
  mantiene explícito (no es un fallo de red).
- [x] **Step 3a — `IntegrationRequestError`**: `integration_errors.py` (U1) NO
  tiene subtipo para el modo `request_exception` (functional-design lo añadió al
  modelo). Añadir `IntegrationRequestError(IntegrationError)` (recuperable por
  defecto, `failure_mode="request_exception"`), coherente con la jerarquía. Es
  una extensión aditiva del módulo de U1 (no amplía god-files). Actualizar el
  test de U1 `test_integration_errors.py` sólo si es aditivo (característica
  nueva), sin romper lo existente.
- [x] Migrar los llamadores del **núcleo**: donde el sync consumía `None` como
  "sin datos" y eso corrompía/omitía, capturar la excepción tipada y traducirla
  (ver Step 4). Los llamadores de **deuda** (p. ej. `roster.py`) se dejan con su
  manejo actual documentado como deuda — NO se migran en U2.

### Step 4 — Punto de captura en el sync: recuperable/fatal + DEGRADED + log (FR3.2.1, FR4.4, NFR1, BR2.2/BR2.3/BR3.1/BR3.2)
- [x] En el punto de captura de la ruta de sync que consume Futmondo/Sofascore
  (endurecer capturas existentes en `data_sync_service.py`, SIN ampliarlo):
  dos ramas `except` explícitas — fatal (`IntegrationBanError`) → propagar/abortar
  limpio; recuperable (`IntegrationTimeoutError`/`IntegrationUnparseableError`/
  `IntegrationRequestError`) → `record_degraded_step(...)` vía `sync_step_status`
  y continuar — antes del `except Exception`.
- [x] **BR2.3 (elevación en escritura)**: un recuperable que ocurra en/antes de un
  punto de escritura con riesgo de corrupción se trata como fatal.
- [x] **Log estructurado** clave=valor (`sync_step`, `failure_mode`, `status`,
  `endpoint`, `task_id`, `reason`), `WARNING` recuperable / `ERROR` fatal, vía
  `logging` stdlib. Nunca credenciales (NFR3).

### Step 5 — No-corrupción de `team_prizes`: reemplazo transaccional atómico (NFR2, BR5.1)
- [x] **Characterization primero**: crear un test que congele el comportamiento
  ACTUAL del bloque INSERT + `DELETE ... NOT IN` de `data_sync_service.py` (hoy el
  `DELETE` va en su propia transacción con `try/except → logger.warning`, que ante
  fallo deja la caché en estado mixto).
- [x] Endurecer hacia **reemplazo transaccional atómico**: encapsular el
  borrado+repoblado de `team_prizes` en **una sola transacción** tras una
  **función estrecha testeable nueva** (`app/services/prizes/team_prizes_writer.py`),
  fuera del god-file; un fallo → `rollback` completo (todo-o-nada), el conjunto
  previo queda íntegro. Se retira el `try/except → logger.warning` que traga el
  fallo del `DELETE`.
- [x] El punto de escritura llama a la función nueva; `data_sync_service.py` no
  se amplía estructuralmente (se sustituye el bloque por la llamada).

### Step 6 — Specs de efecto por modo de fallo (Q1, BR5.2)
- [x] `test_futmondo_client_typed_failures.py`: `_make_request` lanza el subtipo
  correcto por modo de fallo (timeout/request/unparseable), aseverando el tipo y
  el contexto no sensible (sin credenciales en `str`/`repr`).
- [x] `test_sync_integration_failure_effect.py`: recuperable → paso marcado
  `DEGRADED` (estado verificado vía sink fake) **y** la operación NO falla; fatal
  (baneo) → excepción propagada **y** sin datos a medias.
- [x] `test_team_prizes_atomic_replacement.py`: fuerza un fallo dentro de la
  transacción de reemplazo y **asevera** que la tabla/caché queda consistente
  (conjunto previo íntegro), no a medias. Nada de `pytest.raises` sin aserción de
  estado.
- [x] Todos con dobles/fakes en memoria (`conftest.py`), sin red, sin DB real,
  sin credenciales/tokens reales.

### Step 7 — `E722` advisory por trinquete (FR3.2.3) — commit aislado
- [x] En `backend/ruff.toml`, quitar `E722` de `ignore` (una sola línea) para que
  `ruff check` lo reporte. **Sin** promover ruff a bloqueante, **sin** `--fix` ni
  `ruff format`. Va en su **propio commit** `chore(ci)`, aislado del resto.

### Step 8 — Documentación y trazabilidad
- [x] `code-summary.md` (ficheros nuevos/modificados, inventario de llamadores
  núcleo/deuda, decisiones, cobertura, desviaciones).
- [x] `source-manifest.json` (todo path de código creado/modificado/borrado).
- [x] `traceability.json` (AC/`BRx.y`/`NFRx.y` → fichero de implementación/test).
- [x] Formatear SÓLO los ficheros nuevos (o quirúrgico); NUNCA `ruff format`
  masivo sobre brownfield ya modificado.

## Ficheros previstos (resumen)

| Fichero | Acción | Motivo |
|---|---|---|
| `backend/app/services/integration_errors.py` | modificar (aditivo) | añadir `IntegrationRequestError` |
| `backend/app/services/futmondo_client.py` | modificar | `_make_request` lanza tipadas; migrar llamadores núcleo |
| `backend/app/services/data_sync_service.py` | modificar (endurecer, no ampliar) | punto de captura recuperable/fatal + llamar al writer atómico |
| `backend/app/services/prizes/team_prizes_writer.py` | crear | función estrecha testeable de reemplazo atómico |
| `backend/ruff.toml` | modificar (1 línea, commit aislado) | `E722` advisory |
| `backend/tests/test_futmondo_client_characterization.py` | crear | characterization + inventario |
| `backend/tests/test_futmondo_client_typed_failures.py` | crear | specs de tipo por modo de fallo |
| `backend/tests/test_sync_integration_failure_effect.py` | crear | specs de efecto DEGRADED/fatal |
| `backend/tests/test_team_prizes_atomic_replacement.py` | crear | spec de no-corrupción |

## Assumptions & Open Questions

None.
