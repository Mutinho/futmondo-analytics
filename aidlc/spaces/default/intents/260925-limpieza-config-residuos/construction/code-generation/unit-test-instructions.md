# Unit Test Instructions — Limpieza de configuración y residuos (FR14 + FR15)

Estrategia activa: **Minimal** (refactor). Test-after, characterization-first al
endurecer brownfield. Coste 0 €: `pytest` + fixtures fake in-memory, sin red, sin
BD real, sin credenciales.

## Framework y setup

- Backend: `pytest` desde `backend/`, con `conftest.py` compartido
  (`_FakeInMemoryDB`/`_FakeCursor` SQLite `:memory:` honrando el contrato de
  `db_connection`, `clean_jwt_env`, `fake_db`).
- Frontend: Vitest (`@angular/build:unit-test`) — este intent no toca código
  frontend salvo (posible) verificación de que no consume `/v1/matchdays`.
- Sin dependencias nuevas (stdlib suficiente). El fake de tests usa
  `db_type="sqlite"` in-memory, **independiente** de la rama SQLite de producción
  que se retira.

## Comandos de ejecución (scoped a esta unidad)

Runner-ready (correr antes del primer test para confirmar entorno):

```bash
cd backend && python -m pytest tests/test_db_engine_characterization.py -q
```

Tests de esta unidad (rutas exactas, no `pytest` global):

```bash
cd backend && python -m pytest \
  tests/test_db_engine_characterization.py \
  tests/test_config_hardcoded_ids.py \
  tests/test_matchdays_mount.py \
  -q
```

(Los dos últimos ficheros se crean en esta unidad; el primero ya existe y se
extiende con la caracterización del path Neon.)

Suite backend completa (verificación de no-regresión, baseline brownfield):

```bash
cd backend && python -m pytest -q
```

## Cobertura

- `--cov` se mantiene **observability-only, sin piso** (`cov-fail-under` diferido);
  no se introduce piso ni se relaja ninguno (ratcheting solo sube). NFR2/NFR4.
- Objetivo cualitativo: caracterización que ejercite el path PostgreSQL/Neon de
  `db_connection.py` (contrato del cursor/`adapt_sql`/`adapt_params`), de modo que
  "suite verde" pruebe la no-regresión del path que queda tras retirar SQLite/Turso
  (cierra R-03).

## Mocking / stubbing

- Usar las fixtures de `conftest.py` (`fake_db`, `_FakeInMemoryDB`, `clean_jwt_env`).
- Sin red, sin BD real, sin credenciales/tokens reales (gitleaks escanea los tests).
- Docstrings de caracterización con trazas a FR (patrón existente en la suite).

## Gestión de datos de test

- Datos en memoria vía el fake SQLite `:memory:`; nada persistente.
- Para el test de arranque sin IDs configurados (FR14.2), usar `monkeypatch`/env
  limpio para verificar el modo de fallo explícito (sin default legacy).
