# Unit Test Instructions — u1-durable-session

> Etapa Code Generation (Construction). Instrucciones de test para ESTA unidad. Estrategia
> **Standard** (5–8 tests por componente). Metodología test-after con caracterización primero.
> Backend `pytest` desde `backend/`. Coste 0€: fakes de la capa de persistencia, nunca Neon real.

## Framework y configuración

- **Framework**: `pytest` + `pytest-cov` (ya en el backend).
- **Config existente**: `backend/pytest.ini` (`testpaths = tests`, `pythonpath = .`); ejecutar
  siempre desde el directorio `backend/`.
- **Aislamiento**: reutilizar `backend/conftest.py` — fakes de `DataManager`/conexión y la fixture
  `clean_jwt_env`. Añadir un **fake de la capa de persistencia** (almacén en memoria) para
  `SessionRepository`/`ProtectedCredential`, de modo que ningún test toque Neon real.
- **Regla de aislamiento**: cada test crea y limpia su propio almacén en memoria; nunca se comparte
  estado mutable entre tests.

## Cómo ejecutar los tests DE ESTA UNIDAD (comando exacto, scoped)

Los archivos de test de esta unidad viven bajo `backend/tests/` con prefijo `test_durable_session_`.
Comando exacto por-unidad (NO usar un `pytest` global):

```bash
# desde backend/
pytest tests/test_durable_session_characterization.py \
       tests/test_durable_session_repository.py \
       tests/test_durable_session_service.py \
       tests/test_durable_session_api.py -q
```

Con cobertura (referencia global, sin piso bloqueante adicional):

```bash
# desde backend/
pytest tests/test_durable_session_characterization.py \
       tests/test_durable_session_repository.py \
       tests/test_durable_session_service.py \
       tests/test_durable_session_api.py \
       --cov=app.services.session_service \
       --cov=app.security.credential_protection \
       --cov=app.stores -q
```

> El runner debe estar listo (Step 2 del plan) antes del primer test. Para test-after, se implementa
> cada capa y luego se escriben/ejecutan sus tests con estos comandos.

## Alcance de tests por componente (Standard: 5–8 por componente)

- **Caracterización** (`test_durable_session_characterization.py`): congelan el comportamiento
  ACTUAL antes de refactorizar (deben pasar contra el código de hoy): reinicio pierde sesión → 403
  opaco; divergencia comentario↔comportamiento de `_helpers.get_user_futmondo_client`; bug de
  precedencia de `is_refresh_token_valid`.
- **SessionRepository / stores** (`test_durable_session_repository.py`): upsert idempotente por
  `user_id`; purga perezosa de fila expirada; nunca persiste el
  password en claro. (La serialización de la sección crítica de rehidratación NO recae en el
  `SELECT ... FOR UPDATE` del repositorio —el lock de fila se libera al cerrar la conexión antes del
  re-auth—, sino en el lock por usuario de `SessionService`; su test vive en
  `test_durable_session_service.py`.)
- **CredentialProtection / SessionService** (`test_durable_session_service.py`): `ensureSession`
  idempotente; sesión reconstruida tras "reinicio" (caché vacío); credencial inválida/None → 401
  accionable; fallo transitorio NO desloguea (error tipado); el password/handle NUNCA aparece en
  claro; `__repr__`/`__str__` de `ReauthMaterial` redactado; **serialización por usuario**: dos
  `ensureSession(user_id)` concurrentes del mismo usuario producen UNA sola re-autenticación
  (`login_calls == 1`), cerrando el hueco de R-02/R-03.
- **API / endpoints** (`test_durable_session_api.py`): `/auth/refresh` rehidrata; primer uso tras
  reinicio reconstruye o devuelve 401 (no 403 opaco); idempotencia venga del disparador que venga.

## Objetivos de cobertura

- Referencia global del scope `feature`: 80% líneas (NO piso bloqueante adicional, decisión Q3).
- **Exigido**: tests que cubran los **caminos nuevos y de error** de las piezas de durabilidad; sin
  piso porcentual bloqueante adicional. No existe `cov-fail-under` en el repo (ratcheting diferido).

## Mocking / stubbing

- **Fakes de persistencia** (almacén en memoria) en lugar de Neon. No mockear a nivel de driver SQL;
  inyectar un `SessionRepository`/almacén falso por el mismo patrón que `conftest.py`.
- **API Futmondo**: usar las factories existentes de `conftest.py` para simular el re-auth (éxito,
  credencial inválida, fallo transitorio 5xx/timeout).
- **`FUTMONDO_CRED_KEY`**: en test, fijar una clave efímera vía fixture (nunca un secreto real).

## Gestión de datos de test

Cada test construye su propio almacén en memoria y lo descarta al terminar; sin fixtures de datos
compartidos mutables. La caracterización usa el código actual sin tablas nuevas; los tests del nuevo
contrato usan el fake de persistencia con las 2 tablas simuladas.
