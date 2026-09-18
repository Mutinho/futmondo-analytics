# Plan de Generación de Código — Backend Security Hardening

> Scope `security-patch`, depth Minimal, test strategy Minimal, brownfield.
> Trabajo sin Units (zero-Unit): una sola iteración de implementación sobre el
> código existente. Cinco correcciones de seguridad de esfuerzo pequeño (FR6,
> FR7, FR8, FR9, FR18), naturaleza «verificar y, si aplica, corregir con test de
> regresión».

## Alcance y Trazabilidad

Cada corrección traza a su requisito funcional (`requirements.md`) y al NFR de
seguridad detallado (`nfr-requirements/security-requirements.md`). Sin cambios
de frontend salvo lo estrictamente necesario (ninguno se prevé). Idioma en
código: identificadores/docstrings/comentarios en inglés; `HTTPException.detail`
en castellano.

| FR | NFR | Fichero(s) objetivo | Naturaleza | AC |
|----|-----|---------------------|------------|-----|
| FR6 | NFR1.4/1.5 | `backend/app/api/v1/endpoints/market.py` | Corrección (validar `price>0` → 422) + test | FR6.1–FR6.3 |
| FR7 | NFR1.6 | `backend/app/main.py` (docs), test nuevo | Confirmar + documentar + test que congela | FR7.1–FR7.3 |
| FR8 | NFR1.8 | `docker-compose.yml`, test estático | Eliminar flag huérfano + test anti-`verify=False` | FR8.1–FR8.2 |
| FR9 | NFR1.3 | `backend/app/auth/token_store.py`, `backend/tests/test_auth_characterization.py` | Corrección de bug + regresión + actualizar caracterización | FR9.1–FR9.3 |
| FR18 | NFR1.9 | `backend/tests/test_db_admin_guard.py` | Confirmar/consolidar cobertura (sin cambio de código) | FR18.1–FR18.2 |

## Metodología de Test (Testing Contract autoritativo)

La metodología resuelta es **test-after** con orden **caracterización primero**
para el comportamiento observable existente. Aplicado a este patch:

- **FR9** ya tiene tests de caracterización que congelan el *bug*
  (`test_auth_characterization.py`). El comportamiento esperado cambia a
  propósito: primero se corrige el código, luego se **actualizan de forma
  trazable** esos tests de caracterización y se añade la regresión del contrato
  correcto (test-after del comportamiento corregido).
- **FR6/FR7/FR8/FR18**: implementar/confirmar la corrección y a continuación
  escribir y ejecutar su test dirigido (uno verificable por FR, cubriendo el
  camino de error donde aplique — la regresión acotada del scope
  `security-patch`).
- Capas testables del contrato acotadas a este intent: **API / endpoint**
  (FR6, FR7, FR18) y **lógica de negocio de auth** (FR9). No hay capa de
  data-model, repository ni frontend nueva en este patch.
- La suite existente debe permanecer en verde (NFR4). Sin piso de cobertura
  porcentual bloqueante adicional (NFR5, decisión de equipo).

<!-- Testing Contract emitido por `aidlc engine testing-posture render`, verbatim -->
## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "caracterización primero (congelar con tests el comportamiento",
  "scope": "security-patch",
  "test_strategy": "minimal",
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
  "input_sha256": "sha256:91ce8457972bf4ac8e6f8bfb76c5d79fc30e692d681626780cc83f9c6c8787c3",
  "contract_sha256": "sha256:332119b61a669b4846e867daee7f74367cac9b9a879942f35f06558dc4e52001"
}
```

## Pasos de Implementación (ordenados)

Orden aplicado del contrato, acotado a las capas presentes en el patch:
verificación del runner primero, luego lógica de negocio de auth (FR9), luego
capa API/endpoint (FR6, FR7, FR18), luego configuración (FR8), y finalmente
documentación/trazabilidad. Cada corrección seguida de su test (test-after);
FR9 corrige el código y después actualiza la caracterización.

- [x] **Step 1 — Verificar runner de tests y comando exacto (readiness).**
  Confirmar que `pytest` corre desde `backend/` con `pytest.ini`
  (`testpaths=tests`, `pythonpath=.`) y que `JWT_SECRET` de arranque efímero está
  disponible (los tests usan `os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")`).
  Registrar el comando exacto por FR en `unit-test-instructions.md`. Sin este
  comando ejecutable, ningún paso de test posterior es válido.

- [x] **Step 2 — [FR9] Corregir `is_refresh_token_valid` (lógica de negocio auth).**
  En `backend/app/auth/token_store.py`, reemplazar el ternario de precedencia
  ambigua
  `if expires_at and datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc) if expires_at.tzinfo is None else expires_at:`
  por una comparación inequívoca: normalizar `expires_at` a *aware* (si es naive,
  asumir UTC con `.replace(tzinfo=timezone.utc)`) y comparar
  `datetime.now(timezone.utc) > expires_at_aware` → si es futuro, token válido.
  Un token activo con `expires_at` aware futuro debe devolver `True`; expirado o
  revocado → `False`. No ampliar SQL-en-router ni tocar otros métodos.
  Traza: FR9.1, NFR1.3.

- [x] **Step 3 — [FR9] Regresión + actualización trazable de caracterización (test-after).**
  En `backend/tests/test_auth_characterization.py`:
  - Actualizar deliberadamente `test_is_refresh_token_valid_BUG_aware_future_token_returns_false`
    para que ahora afirme el comportamiento **correcto**: token aware futuro →
    `True` (renombrar quitando `BUG` y documentar el cambio de contrato en el
    docstring). Traza: FR9.3.
  - Mantener/confirmar: naive futuro → `True`, naive pasado → `False`,
    revocado → `False`, ausente → `False`.
  - Añadir regresión explícita del contrato corregido: token **aware pasado** →
    `False` (camino de error del caso real PostgreSQL). Traza: FR9.2.
  Usar el `patch_db` / `_FakeDB` existente (sin BD real).

- [x] **Step 4 — [FR6] Validar `price` en el backend de pujas (capa API/endpoint).**
  En `backend/app/api/v1/endpoints/market.py::place_bid`, antes de resolver el
  cliente Futmondo y de cualquier efecto lateral, validar
  `price` entero estrictamente positivo (`price > 0`). Si es inválido, lanzar
  `HTTPException(status_code=422, detail="El precio de la puja debe ser un entero positivo")`.
  Colocar la validación al inicio del cuerpo, dentro del `try`, de modo que el
  `except HTTPException: raise` la propague como 422 (no como 500). No realizar
  la llamada `POST /1/market/bid` de Futmondo si `price` es inválido.
  Traza: FR6.1, FR6.2, FR6.3, NFR1.4, NFR1.5.

- [x] **Step 5 — [FR6] Test dirigido de `place_bid` (test-after).**
  Nuevo `backend/tests/test_market_bid_validation.py`: montar el router `market`
  en una `FastAPI` mínima (patrón de `test_db_admin_guard.py`), parcheando
  `get_user_futmondo_client` con un doble espía. Casos: `price=0` → 422 y el
  cliente Futmondo **no** se invoca; `price` negativo → 422; happy path
  (`price>0`) → el cliente sí se invoca (con doble que devuelve
  `{"answer": {"code": "api.general.ok"}}`). Cubre el camino de error.
  Traza: FR6.1, FR6.2.

- [x] **Step 6 — [FR7] Documentar exposición del endpoint de fotos (sin cambio funcional).**
  En `backend/app/main.py`, añadir/ajustar docstrings/comentarios (en inglés)
  que documenten explícitamente: (a) `GET /api/v1/photos/{player_id}` está
  protegido por `AuthMiddleware` (no está en `AUTH_EXCLUDED_PATHS`); (b)
  `/static/photos/*` (StaticFiles) es una superficie **pública intencionada**
  por quedar fuera del prefijo protegido, y las fotos no son datos sensibles.
  No cambiar comportamiento. Traza: FR7.1, FR7.2, NFR1.6.

- [x] **Step 7 — [FR7] Test que congela ambos comportamientos (test-after).**
  Nuevo `backend/tests/test_photos_exposure.py`: verificar de forma estática que
  `/api/v1/photos` no está en `AUTH_EXCLUDED_PATHS` y que la lógica del
  `AuthMiddleware` exige Bearer para rutas `/api/v1/*` fuera de la exclusión
  (petición sin token → 401), y que `/static/photos` cae fuera del prefijo
  protegido (público a propósito). Import de `AUTH_EXCLUDED_PATHS` desde
  `app.main`. Congela el estado actual sin cambio funcional. Traza: FR7.3, NFR1.6.

- [x] **Step 8 — [FR18] Confirmar/consolidar cobertura de la guarda de administración.**
  Revisar `backend/tests/test_db_admin_guard.py` (ya cubre 404 por defecto, 404
  con valor no afirmativo, 200 con `ENABLE_DB_ADMIN=1`). No se requiere cambio de
  código en `reset_db.py` (`_require_db_admin` ya correcto). Consolidar solo si
  falta un caso afirmativo alternativo (`true`/`yes`/`on`); si la cobertura es
  suficiente, dejar constancia en `code-summary.md` de que no se necesita cambio.
  Traza: FR18.1, FR18.2, NFR1.9.

- [x] **Step 9 — [FR8] Eliminar `SSL_VERIFY=0` de `docker-compose.yml` (configuración).**
  Quitar la entrada `environment: - SSL_VERIFY=0` del servicio `backend` en
  `docker-compose.yml` (flag huérfano, ningún módulo Python lo consume, ausente
  de `fly.toml`). Traza: FR8.1, NFR1.8.

- [x] **Step 10 — [FR8] Test estático anti-`verify=False` (test-after).**
  Nuevo `backend/tests/test_tls_verification.py`: aserción estática que (a)
  confirma que `SSL_VERIFY` no aparece en `docker-compose.yml`, y (b) escanea el
  árbol `backend/app/**` en busca de `verify=False` (o equivalente) en clientes
  HTTP de la ruta de producción; falla si aparece. Traza: FR8.2, NFR1.8.

- [x] **Step 11 — Ejecutar la suite completa y confirmar verde (NFR4).**
  Correr `pytest` desde `backend/` y confirmar que toda la suite existente sigue
  en verde tras las correcciones y los tests nuevos/actualizados.

- [x] **Step 12 — Documentación y trazabilidad.**
  Generar `code-summary.md`, `source-manifest.json` (toda ruta creada/modificada)
  y `traceability.json` (cada AC/FR/NFR → fichero de implementación o test).

## Invariantes de Seguridad (no regresión)

- No reintroducir credenciales en claro ni `JWT_SECRET` por defecto (NFR1.1, NFR1.2, NFR1.7).
- No abrir ninguna ruta protegida ni añadir exclusiones al middleware (NFR1.1).
- No ampliar el SQL-en-router ni los god-files de `services/` (NFR2).
- Coste 0 €: sin dependencias nuevas de pago (NFR3).
- No debilitar, bajar ni desactivar ningún target de calidad medible para pasar un paso.
