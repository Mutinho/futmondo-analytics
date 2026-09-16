# Code Summary — u1-durable-session

> Etapa Code Generation (Construction), unidad `u1-durable-session`. Resumen de la implementación
> de la durabilidad de la sesión Futmondo y el aislamiento de la credencial sobre el backend
> existente `futmondo-api` (FastAPI, Python 3.12, Neon vía `db_connection`). Metodología test-after
> con caracterización primero. Coste 0€.

## Archivos creados

| Ruta | Contenido |
|------|-----------|
| `backend/app/stores/__init__.py` | Exports de la capa de persistencia estrecha |
| `backend/app/stores/session_repository.py` | `SessionRepository`, `ProtectedCredentialRepository`, `SessionRecord`, `ProtectedCredentialRecord`, `ensure_durable_session_schema()`; DDL idempotente (`user_session`, `protected_credential` con `protected_material BYTEA`/`scheme TEXT`); upsert por `user_id`, `SELECT ... FOR UPDATE` (PostgreSQL), purga perezosa de fila expirada al leer, SQL parametrizado, DB inyectable |
| `backend/app/security/__init__.py` | Exports del paquete de seguridad |
| `backend/app/security/credential_protection.py` | `CredentialProtection` (`protect`/`can_reauthenticate`/`reauthenticate` públicas; `_resolve` privada; `forget`); `ReauthMaterial` con `__slots__` y `__repr__`/`__str__` redactado (`<ReauthMaterial redacted>`); `FutmondoSession`; `CredentialProtectionUnavailable`; cifrado Fernet con `FUTMONDO_CRED_KEY`; nunca retiene el plaintext |
| `backend/app/services/session_service.py` | `SessionService.ensure_session`/`ensureSession` idempotente (caché → BD → rehidratar); `TransientSessionError` vs `SessionUnrecoverableError`; sin reintentos internos; `get_session_service()` provider |
| `backend/tests/test_durable_session_characterization.py` | Tests de caracterización (bug de precedencia de `is_refresh_token_valid` congelado; retirada trazable de los fallos 403/docstring) |
| `backend/tests/test_durable_session_repository.py` | 12 tests: esquema idempotente, upsert, purga perezosa, nunca password en claro |
| `backend/tests/test_durable_session_service.py` | 15 tests: cifrado en reposo, tipo redactado, `ensureSession`, transitorio vs unrecoverable |
| `backend/tests/test_durable_session_api.py` | 5 tests: re-cableo del helper (401 accionable), idempotencia, rehidratación tras reinicio |

## Archivos modificados (en su sitio, sin duplicados)

| Ruta | Cambio |
|------|--------|
| `backend/app/core/config.py` | Lectura de `FUTMONDO_CRED_KEY` desde entorno (secret de Fly.io) |
| `backend/app/auth/session_store.py` | Degradado a caché best-effort; `UserSession` ya NO guarda `password`; `store_reauthenticated()` añadido; `get_client` no re-loguea con password |
| `backend/app/auth/routes.py` | `/auth/login` persiste sesión durable + credencial cifrada; `/auth/refresh` dispara `ensure_session` (BR1.6) y reemplaza `__import__` dinámico por import estático; `/auth/logout` purga estado durable + handle |
| `backend/app/api/v1/endpoints/_helpers.py` | `get_user_futmondo_client` usa `ensure_session` y devuelve **401 accionable** (castellano) en vez de 403 opaco (FR1.3) |
| `backend/app/main.py` | `ensure_durable_session_schema()` en el arranque (Step 4) |
| `backend/conftest.py` | Fixture `fake_db` (almacén SQLite en memoria que respeta el contrato de `db_connection`) |
| `.github/workflows/fly-deploy.yml` | gitleaks BLOQUEANTE en el job `verify` (cierra el hueco FR5 en push→`main`) |
| `docs/DEPLOY.md` | `FUTMONDO_CRED_KEY` documentado como secret de Fly.io (nunca en repo) |

## Decisiones clave de implementación

- **Handle de re-auth cifrado (FR5.1/FR5.2/NFR1/BR1.4):** el medio de re-autenticación se cifra con
  Fernet usando `FUTMONDO_CRED_KEY`; el plaintext solo vive en una variable local efímera dentro de
  `protect`, nunca en atributos, logs, retornos ni BD.
- **`SessionStore` sin password en memoria (FR5, regla dura project.md):** `UserSession` ya no retiene
  el password; la rehidratación tras reinicio va por el handle cifrado, no por un password recordado.
  Se preserva la API pública (`store_session(..., password="")` acepta el parámetro pero lo descarta).
- **Distinción de fallos (BR1.3/Q4-A):** fallo transitorio de red → `TransientSessionError` (NO
  desloguea, conserva el handle); credencial inválida/None/indescifrable → `SessionUnrecoverableError`
  → 401 accionable. Sin reintentos internos (BR1.6).
- **Autoridad de estado en BD (BR1.5/NFR5):** la caché es best-effort (cache-aside); la BD gana en
  discrepancia. Lock por usuario con `SELECT ... FOR UPDATE`; idempotencia de `ensureSession` (BR1.2).
- **Frontera de seguridad (Q2-A):** `_resolve` es privada; el handle descifrado nunca cruza la
  frontera pública — `reauthenticate` devuelve la sesión reconstruida o `None`.
- **Degradación segura:** si `FUTMONDO_CRED_KEY` no está configurada, el backend arranca igual y
  degrada a 401 accionable (no crashea endpoints).
- **DB inyectable:** repos y servicio aceptan un DB inyectado para fakes de persistencia (SQLite en
  memoria); ningún test toca Neon (coste 0€, determinismo).

## Resumen de cobertura de tests

- **Comando por-unidad** (desde `backend/`):
  `pytest tests/test_durable_session_characterization.py tests/test_durable_session_repository.py tests/test_durable_session_service.py tests/test_durable_session_api.py -q`
- **Resultado**: **36 passed** (caracterización 3, repository 12, service 16 incl. test de concurrencia, api 5).
- **Suite completa del backend**: **90 passed, 1 warning** (baseline 54 → +36, **0 regresiones**, NFR4).
- **Lint**: `ruff` (config del repo) — All checks passed.
- Cobertura como referencia global (sin piso porcentual bloqueante adicional, decisión Q3); se exige
  cobertura de los caminos nuevos y de error de las piezas de durabilidad — satisfecho.

## Desviaciones respecto al plan

- **Desviación del ADR de seguridad (FR5.2) — requiere decisión humana en el gate:** el
  security-design aprobado (ADR) prescribía cifrar un *handle de re-auth token/refresh* derivado del
  login y rechazaba explícitamente cifrar la contraseña. Verificación objetiva sobre el código real:
  `backend/app/services/futmondo_client.py` NO expone un token/refresh reutilizable persistible —
  `FutmondoClient(email, password)` con `login()` como única vía (el payload envía siempre `mail`/`pwd`
  y `header.token="null"`; el `self.token`/cookies capturados no son reconstruibles sin re-login, no hay
  `set_token`/`from_token`/refresh). Por tanto el handle-token del ADR es **inviable a coste 0€** con la
  API de Futmondo. Se mantiene el cifrado del par `(email, password)` con Fernet/`FUTMONDO_CRED_KEY`:
  **sigue cumpliendo la regla dura** (nunca en claro en reposo, FR5.1/NFR1/BR1.4) y **FR5.2** (cifrado en
  reposo con clave gestionada como secret), pero es la alternativa que el ADR rechazó. `scheme` renombrado
  a `encrypted-credential+fernet-v1` (honesto). **El humano debe aceptar la desviación o pedir revisión
  del diseño** en el gate de la unidad.
- **Concurrencia (R-02, corregido tras revisión):** el `SELECT ... FOR UPDATE` liberaba el lock al
  cerrar la conexión, antes de la sección crítica de re-auth. Corregido con serialización intra-proceso
  por `user_id` en `SessionService.ensure_session` (registro de `threading.Lock` con double-check del
  caché dentro del lock, idempotencia BR1.2); la BD sigue siendo la autoridad (BR1.5) y `FOR UPDATE`
  queda como defensa entre instancias futura. Añadido `test_concurrent_ensure_session_reauthenticates_once`
  (dos `ensure_session` concurrentes → exactamente 1 re-auth); el test falla sin el lock (anti-tautología).
- **`unit-test-instructions.md` suelto:** el developer creó un `backend/unit-test-instructions.md`
  duplicado en la raíz del backend. Se eliminó para no dejar dos fuentes de verdad: las instrucciones
  de test aprobadas y autoritativas viven en el record dir
  (`.../code-generation/unit-test-instructions.md`). Sin impacto en la ejecución (el comando exacto
  está en el record y en este resumen).
- **Bug de precedencia de `token_store.is_refresh_token_valid`:** NO se corrige (fuera del alcance de
  la unidad); su comportamiento queda congelado en la caracterización para una corrección posterior
  trazable (C5).
- **Verificación en venv temporal:** la verificación local se hizo en un venv temporal
  (`pytest`/`cryptography` no están en el Python del sistema por PEP668). En CI (Python 3.12 +
  `requirements.txt`) el comando estándar funciona sin cambios.
- **Nota de entorno (no bloqueante):** `libsql-experimental` (backend Turso) no compila en Python
  3.14; irrelevante para los tests (usan fakes) y para producción (PG/Neon). CI usa 3.12.
