# Instrucciones de Test — Backend Security Hardening

> Scope `security-patch`, test strategy **Minimal** (una prueba verificable por
> FR, en el nivel más estrecho que reproduce el defecto; camino de error donde
> aplique). Metodología **test-after** con caracterización primero para FR9.
> Sin piso de cobertura porcentual bloqueante adicional (decisión de equipo);
> la suite existente debe permanecer en verde.

## Framework y Configuración

- **Runner**: `pytest` (+ `pytest-cov` disponible), ejecutado **desde `backend/`**.
- **Config**: `backend/pytest.ini` → `testpaths = tests`, `pythonpath = .`.
- **Arranque JWT**: cada módulo de test fija un secreto efímero no productivo con
  `os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")` antes de
  importar `app.*` (patrón existente en `test_auth_characterization.py` y
  `test_db_admin_guard.py`). Es un literal de arranque, no una credencial real.
- **Entorno local a coste 0**: si el Python del sistema es más nuevo que el de
  CI (3.12), crear un venv efímero excluyendo `libsql-experimental` (no compila
  fuera de 3.12 y no lo ejercitan los tests, que usan el fake SQLite).

## Aislamiento (mocking / stubbing)

- **Nunca** BD real: usar los fakes de `backend/conftest.py`
  (`fake_db` → `_FakeInMemoryDB`) o, para `token_store`, el `patch_db`/`_FakeDB`
  de `test_auth_characterization.py` (doble de conexión que devuelve la fila).
- **Nunca** llamadas de red reales: parchear `get_user_futmondo_client` con un
  doble espía para FR6.
- Cada test crea y limpia su propio estado; sin estado mutable compartido.

## Comando de readiness (ejecutable antes del primer test)

Desde `backend/`:

```bash
python -m pytest -q --collect-only
```

## Comandos de ejecución por FR (scoped, NO project-wide)

Cada comando está acotado a los ficheros de esta unidad de trabajo. Ejecutar
desde `backend/`.

- **FR9 — corrección + caracterización de `is_refresh_token_valid`**:
  ```bash
  python -m pytest tests/test_auth_characterization.py -q
  ```
  Casos clave: aware futuro → `True` (contrato corregido), aware pasado →
  `False`, naive futuro → `True`, naive pasado → `False`, revocado → `False`,
  ausente → `False`.

- **FR6 — validación de `price` en `place_bid`**:
  ```bash
  python -m pytest tests/test_market_bid_validation.py -q
  ```
  Casos: `price=0` → 422 y cliente Futmondo no invocado; `price<0` → 422;
  `price>0` → cliente invocado (happy path).

- **FR7 — exposición del endpoint de fotos**:
  ```bash
  python -m pytest tests/test_photos_exposure.py -q
  ```
  Casos: `/api/v1/photos` no está en `AUTH_EXCLUDED_PATHS`; petición sin token a
  ruta `/api/v1/*` no excluida → 401; `/static/photos` fuera del prefijo
  protegido (público a propósito).

- **FR8 — verificación TLS (sin `verify=False`)**:
  ```bash
  python -m pytest tests/test_tls_verification.py -q
  ```
  Casos: `SSL_VERIFY` ausente de `docker-compose.yml`; ningún cliente HTTP de
  `backend/app/**` usa `verify=False`.

- **FR18 — guarda de administración de BD**:
  ```bash
  python -m pytest tests/test_db_admin_guard.py -q
  ```
  Casos: 404 por defecto, 404 con valor no afirmativo, 200 con
  `ENABLE_DB_ADMIN=1` (doble de `DataManagerV2`).

## Suite completa (verificación de no regresión, NFR4)

Tras aplicar todas las correcciones y tests, confirmar verde global desde
`backend/`:

```bash
python -m pytest -q
```

## Objetivos de cobertura

- **Minimal**: al menos una prueba verificable por FR (5 FRs → ≥5 casos
  dirigidos, más los casos de error donde aplica). Sin umbral porcentual
  bloqueante adicional; la suite existente permanece en verde.
