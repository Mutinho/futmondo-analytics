# Unit Test Instructions — U1 `u1-error-layer`

## Framework y configuración

`pytest` desde `backend/` con las fixtures compartidas de `conftest.py`
(`_FakeInMemoryDB`/`_FakeCursor` SQLite `:memory:`, `clean_jwt_env`, `fake_db`).
Sin red, sin DB real, sin credenciales. Sin dependencias nuevas (stdlib).

## Comando exacto de esta unidad (scoped a U1)

```bash
cd backend && python -m pytest tests/test_integration_errors.py tests/test_error_layer_hardening.py -q
```

(Los dos ficheros de test de U1; NO un `pytest` global — Build and Test corre el
comando de cada unidad, un comando global re-ejecutaría toda la suite por unidad.)

## Cobertura

- Estrategia standard: 5-8 tests por componente.
- Piso `feature`: 80% de línea (medido con `--cov=app`, observabilidad-only en el
  job `verify`; no se baja ningún umbral para pasar).
- Suite existente en verde.

## Guía de mocking/stubbing

- Dobles/fakes en memoria para cualquier fallo de integración; nunca golpear una
  API real ni provocar un baneo.
- Para el spec de defensa NFR3: construir la excepción pasando credenciales de
  prueba conocidas en el contexto y aseverar su ausencia en `str/repr/args`.

## Datos de test

- Valores de prueba y credenciales falsas; gitleaks escanea los `*.py` de tests.

## Tests previstos (U1)

- `tests/test_integration_errors.py`: construcción de cada subtipo, clasificación
  recuperable/fatal por tipo, re-parentado de `SofascoreIPBanError`, spec de
  defensa NFR3 (sin secretos en `str/repr/args`).
- `tests/test_error_layer_hardening.py`: caracterización + reclasificación de las
  capturas de arranque/migraciones/`db_connection.py`, aseverando el EFECTO
  (recuperable sigue/degrada; fatal propaga), sin `pytest.raises` sin aserción.
