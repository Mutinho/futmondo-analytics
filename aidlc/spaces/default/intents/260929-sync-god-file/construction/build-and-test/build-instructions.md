# Build Instructions — Backend (sync god-file refactor)

Refactor backend-only, Brownfield, coste 0 €. No hay build compilado: el backend es
Python (FastAPI) y el "build" es instalar dependencias y verificar que la suite
importa y corre. El frontend Angular no se toca en este intent.

## Instalación de dependencias

- Backend Python 3.12 (CI); local puede ser más nuevo (aquí 3.14) usando el
  workaround afirmado de coste 0 €:
  - Crear venv efímero: `python3 -m venv /tmp/bt-venv`
  - Excluir `libsql-experimental` de `requirements.txt` (no compila fuera de 3.12
    y no lo ejercitan los tests, que usan el fake SQLite):
    `grep -v 'libsql-experimental' backend/requirements.txt > /tmp/reqs.txt`
  - Instalar: `/tmp/bt-venv/bin/pip install -r /tmp/reqs.txt`
  - En CI (Python 3.12) se instala `requirements.txt` completo, sin exclusión.

## Configuración de entorno

- `JWT_SECRET` no-default requerido en arranque (NFR1.1); para tests basta un
  valor efímero no productivo: `JWT_SECRET="bt-ephemeral-not-a-real-secret"`.
- Sin BD real: los tests usan los fakes en memoria de `conftest.py`
  (`_FakeInMemoryDB`/`_FakeCursor` SQLite `:memory:`). Sin red, sin credenciales.

## Comandos de build / verificación

- Verificación de importación + suite: ejecutar desde `backend/`:
  `JWT_SECRET="…" python -m pytest -q --cov=app`
- Lint de los ficheros nuevos (sin `ruff format` masivo):
  `ruff check app/services/sync/ tests/test_sync_match_odds_characterization.py`

## Troubleshooting

- `libsql-experimental` falla al compilar en Python ≠ 3.12: excluirlo del venv
  local (no lo usan los tests); en CI 3.12 instala sin problema.
- `from app...` no resuelve: correr pytest DESDE `backend/` (`pythonpath = .` en
  `pytest.ini`).
- Arranque falla por `JWT_SECRET`: exportar un valor efímero no-default.
