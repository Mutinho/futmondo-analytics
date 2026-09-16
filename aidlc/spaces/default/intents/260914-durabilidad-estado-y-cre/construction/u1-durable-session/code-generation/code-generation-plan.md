# Code Generation Plan — u1-durable-session

> Etapa Code Generation (Construction), unidad `u1-durable-session`. Plan de implementación de la
> durabilidad de la sesión Futmondo y el aislamiento de la credencial, sobre el backend existente
> `futmondo-api` (FastAPI, Python 3.12, Neon vía `db_connection`). Metodología: **test-after con
> caracterización primero** (Testing Contract embebido abajo). Coste 0€, sin dependencias de pago
> (salvo `cryptography`, que ya está en el entorno estándar de Python para el cifrado del handle).

## Contexto y trazabilidad de origen

- Requisitos: FR1.1, FR1.2, FR1.3, FR5.1, FR5.2; NFR1, NFR2, NFR3, NFR4, NFR5 (requirements.md).
- Reglas: BR1.1–BR1.6 (rules.md). Entidades: `UserSession`, `ProtectedCredential` (entities.md).
- Contrato C1: interfaz `CredentialProtection` (contract-summary.md), reconciliada en NFR Design a
  `protect` / `can_reauthenticate` / `reauthenticate` (pública) + `resolve` (interna-privada).
- Diseño: security-design (handle cifrado en reposo con `FUTMONDO_CRED_KEY`; tipo redactado),
  performance-design (cache-aside), reliability-design (lock BD, distinguir fallo transitorio),
  infrastructure-specification (script SQL idempotente; tablas `user_session`/`protected_credential`).
- Componentes: `SessionService`, `SessionRepository`, `CredentialProtection` (nuevos); `SessionStore`
  (degradado a caché best-effort); re-cableo de `AuthRoutes` (`/auth/refresh`) y
  `FutmondoClientAccessor` (`_helpers.get_user_futmondo_client`).

## Restricciones duras (inputs, no sugerencias)

- NUNCA la contraseña en claro en BD, logs ni retornos (FR5.1/NFR1/BR1.4).
- La BD es la autoridad de estado/concurrencia; el caché es best-effort (BR1.5/NFR5).
- Suite existente permanece en verde (NFR4). Caracterizar `SessionStore` antes de refactorizar (C5).
- Capa de persistencia estrecha (`stores/`), sin ampliar SQL-en-router ni god-files (C3).
- Idiomas: identificadores/docstrings/comentarios en INGLÉS; texto de usuario (`detail` de
  `HTTPException`) en CASTELLANO (Code Style team.md).

## Plan de implementación (pasos numerados)

- [x] **Step 1 — Estructura y configuración de producción.** Crear el paquete `backend/app/stores/`
      (capa de persistencia estrecha) y `backend/app/services/session_service.py`,
      `backend/app/security/credential_protection.py`. Sin ampliar los god-files. Añadir lectura de
      `FUTMONDO_CRED_KEY` desde entorno (secret de Fly.io) en la config existente.
- [x] **Step 2 — Runner de tests listo (antes del primer test).** Verificar `pytest` ejecutable
      desde `backend/` (`pytest.ini`: `testpaths = tests`, `pythonpath = .`) + `pytest-cov`.
      Registrar el comando exacto por-unidad en `unit-test-instructions.md`. Reutilizar el patrón de
      `backend/conftest.py` (fakes de conexión, `clean_jwt_env`).
- [x] **Step 3 — CARACTERIZACIÓN (red de seguridad, antes de refactorizar) — tests.** Escribir tests
      que congelen el comportamiento ACTUAL (deben pasar contra el código de hoy), incluidos los
      fallos conocidos: (a) reinicio pierde sesión → 403 opaco vía
      `_helpers.get_user_futmondo_client`; (b) la divergencia comentario↔comportamiento de ese
      helper; (c) el bug de precedencia de `is_refresh_token_valid`. Con fakes de persistencia, sin
      Neon real. (C5 / BR-caracterización). Estos tests de *fallo* se retirarán/actualizarán de
      forma trazable cuando el comportamiento cambie a propósito.
- [x] **Step 4 — Data model / esquema (implementar).** Script SQL idempotente
      `CREATE TABLE IF NOT EXISTS user_session (...)` y `protected_credential (...)` aplicado al
      arrancar el backend (infra Q1-A). `protected_material BYTEA` (handle cifrado), `scheme TEXT`.
- [x] **Step 5 — Data model / esquema (tests test-after).** Test de que el script es idempotente
      (re-ejecución no falla) y crea el esquema esperado, contra un fake/almacén en memoria.
- [x] **Step 6 — Repository / data access (implementar).** `SessionRepository` y el acceso a
      `ProtectedCredential` en `stores/`: upsert por `user_id`, lectura con `SELECT ... FOR UPDATE`
      (lock por usuario, BR1.1/Q3-A), DELETE perezoso de fila expirada al leer (Q5-A), consultas
      parametrizadas. Sin SQL en routers (C3).
- [x] **Step 7 — Repository (tests test-after).** Tests: upsert idempotente, lock/serialización
      simulada, purga perezosa de expirada, nunca se persiste el password en claro. Fakes de
      persistencia (5–8 tests, Standard).
- [x] **Step 8 — Business logic / seguridad (implementar).** `CredentialProtection` con
      `protect(user_id, plaintext)` (deriva el handle del login, lo CIFRA con `FUTMONDO_CRED_KEY`
      AES-GCM, NO retiene el plaintext), `can_reauthenticate(user_id) -> bool`,
      `reauthenticate(user_id) -> FutmondoSession | None` (descifra en memoria, re-autentica
      internamente, devuelve sesión; `resolve` interno-privado). Tipo `ReauthMaterial` con
      `__repr__`/`__str__` redactado y `__slots__` (control determinista anti-log). `SessionService`
      con `ensureSession(user_id)` idempotente (BR1.2): caché → BD → rehidratar; distingue fallo
      transitorio (error tipado, no destruye handle) de credencial inválida/None → unrecoverable
      (BR1.3/Q4-A). `SessionStore` degradado a caché best-effort (cache-aside).
- [x] **Step 9 — Business logic (tests test-after — NUEVO contrato de durabilidad).** Tests:
      sesión reconstruida tras "reinicio" (caché vacío), idempotencia de `ensureSession`, 401
      accionable cuando no hay re-auth, fallo transitorio NO desloguea, NUNCA aparece el password en
      claro, `__repr__` redactado. Fakes de persistencia (5–8 tests, Standard).
- [x] **Step 10 — API / endpoint (implementar re-cableo).** `AuthRoutes` `/auth/refresh` dispara
      `ensureSession` (BR1.6). `FutmondoClientAccessor` (`_helpers.get_user_futmondo_client`) deja de
      devolver 403 opaco: llama a `ensureSession`, y si es unrecoverable responde **401 accionable**
      (`detail` en castellano, FR1.3). No se añaden endpoints nuevos.
- [x] **Step 11 — API / endpoint (tests test-after).** Tests: `/auth/refresh` rehidrata; primer uso
      tras reinicio reconstruye o da 401 (no 403); idempotencia venga del disparador que venga.
- [x] **Step 12 — Frontend behavior.** N/A para esta unidad (backend-only; el 401 accionable ya lo
      maneja el flujo de re-login existente del frontend). Se omite por inaplicable, sin cambiar la
      metodología.
- [x] **Step 13 — Configuración de entorno/build.** Documentar `FUTMONDO_CRED_KEY` como secret de
      Fly.io (no en repo); añadir gitleaks bloqueante al job `verify` de `fly-deploy.yml` (infra
      Q3-A). Sin dependencias de pago.
- [x] **Step 14 — Documentación y trazabilidad.** Docstrings en inglés; actualizar
      `source-manifest.json`, `code-summary.md` y `traceability.json` (AC/NFR/BR → archivos).

## Traza paso → requisito

| Step | Cubre |
|------|-------|
| 3 | C5 (caracterización), congela FR1.3-actual (403) y bugs conocidos |
| 4–5 | FR1.1, NFR5.1 (tabla durable), infra Q1-A |
| 6–7 | FR1.1, BR1.1/BR1.5, NFR5.2 (lock BD), Q5-A (purga) |
| 8–9 | FR1.2, FR1.3, FR5.1/FR5.2, BR1.2/BR1.3/BR1.4/BR1.6, NFR1 (cifrado handle) |
| 10–11 | FR1.2, FR1.3 (401 no 403), BR1.6 |
| 13 | FR5 (gitleaks en verify), NFR1.2 (secret) |
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
