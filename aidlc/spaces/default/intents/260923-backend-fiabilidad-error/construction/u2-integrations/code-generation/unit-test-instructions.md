# Unit Test Instructions — u2-integrations (Integraciones)

Estrategia **Standard** (5–8 tests por componente, unit + integración en fronteras
clave), metodología **test-after characterization-first**. Backend `pytest` desde
`backend/`, con las fixtures de `conftest.py`, sin red, sin DB real, sin
credenciales/tokens reales (`gitleaks` escanea los tests).

## Framework y configuración

- Runner: `pytest` (ya presente; `backend/pytest.ini` con `testpaths = tests`,
  `pythonpath = .`). Se ejecuta **desde `backend/`** para que `from app...`
  resuelva.
- Fixtures compartidas (`backend/conftest.py`): `_FakeInMemoryDB`/`_FakeCursor`
  (SQLite `:memory:` honrando el contrato de `db_connection`), `clean_jwt_env`,
  `fake_db`. No añadir dependencias nuevas (stdlib suficiente).
- Sin bootstrap de runner (brownfield): sólo verificar antes del primer test.

## Comando exacto para ESTA unidad (scoped)

Ejecutar los tests de u2-integrations por ruta explícita (NO `pytest` global):

```bash
cd backend && python -m pytest \
  tests/test_futmondo_client_characterization.py \
  tests/test_futmondo_client_typed_failures.py \
  tests/test_sync_integration_failure_effect.py \
  tests/test_team_prizes_atomic_replacement.py \
  -q
```

(El fichero de U1 `tests/test_integration_errors.py` sólo se re-ejecuta si el
Step 3a lo amplía de forma aditiva.) Build and Test ejecuta el comando de cada
unidad; por eso este comando va acotado por rutas, nunca `pytest` a secas.

## Cobertura

- `--cov` es **observabilidad-only, sin piso bloqueante** en este intent
  (`cov-fail-under` diferido). Se puede medir informativamente con
  `--cov=app`, pero NO se baja ningún umbral para pasar el gate; el trinquete
  sólo sube.

## Mocking / stubbing

- `_make_request`: monkeypatch de `self.session.post` para simular `Timeout`,
  `RequestException`, `JSONDecodeError` y `200 OK`; nunca red real.
- Punto de sync: usar un `ProgressSink` fake (patrón `conftest.py`) para aseverar
  que un paso queda `DEGRADED` (recuperable) o que la excepción se propaga (fatal).
- `team_prizes`: usar `_FakeInMemoryDB`/`_FakeCursor`; forzar el fallo dentro de
  la transacción de reemplazo y aseverar el estado resultante (todo-o-nada).
- Ninguna excepción/log debe contener password ni token (aserción explícita en
  los specs de tipo).

## Objetivo de cobertura

Cobertura significativa de las ramas nuevas de fallo (timeout/request/unparseable/
ban) y del reemplazo atómico (commit y rollback). Sin piso numérico bloqueante en
este intent; specs con aserciones reales de efecto (nunca `pytest.raises` sin
aserción de estado).

## Gestión de datos de test

- Datos en memoria construidos en cada test (sin estado compartido mutable).
- Sin credenciales/tokens reales: los dobles usan valores fake.
