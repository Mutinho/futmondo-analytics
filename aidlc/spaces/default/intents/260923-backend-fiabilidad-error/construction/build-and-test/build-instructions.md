# Build Instructions — Construction (Fiabilidad backend FR3.2 + FR4)

Backend Python 3.12 (FastAPI) — intervención de fiabilidad acotada, sin build de
compilación (Python interpretado). La "verificación de build" es la resolución de
imports + el arranque del módulo; el gate real es la suite `pytest`. Coste 0 €.

## Dependencias

- Producción: `backend/requirements.txt` (FastAPI, uvicorn, pydantic, PyJWT,
  requests, curl_cffi, psycopg2-binary, libsql-experimental, …).
- Test: `pytest`, `pytest-cov`, `httpx` (ya en `requirements.txt`).

```bash
cd backend
pip install -r requirements.txt   # CI usa Python 3.12
```

**Repro local a coste 0 (Python del sistema > 3.12)**: crear un venv efímero
**excluyendo `libsql-experimental`** (no compila fuera de 3.12 y no lo ejercitan
los tests, que usan el fake SQLite de `conftest.py`) y fijar un `JWT_SECRET`
efímero (learning afirmado):

```bash
python3 -m venv /tmp/bt_venv
grep -v 'libsql-experimental' backend/requirements.txt > /tmp/reqs.txt
/tmp/bt_venv/bin/pip install -r /tmp/reqs.txt
```

## Entorno

- `JWT_SECRET` **no-default** obligatorio en arranque (NFR1.1). Para tests usar
  uno efímero; nunca un secreto real (gitleaks escanea).
- Sin red, sin DB real: los tests usan `_FakeInMemoryDB`/`_FakeCursor` de
  `conftest.py`.

## Verificación de build

```bash
cd backend
JWT_SECRET="x" python -c "import app.services.integration_errors, app.services.prizes.team_prizes_writer"
```

Resuelve imports del código nuevo/modificado sin errores.

## Troubleshooting

- `libsql-experimental` no compila → excluirlo del venv efímero (ver arriba).
- `ruff check` reporta `I` (orden de imports) en ficheros brownfield → **advisory**,
  NO se corrige con `ruff format`/`--fix` masivo (regla afirmada: no reformatear
  brownfield en masa).
