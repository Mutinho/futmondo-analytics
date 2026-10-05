# Build Instructions — `data_manager_v2` decomposition

Backend-only refactor (Python 3.12 en CI; Fly.io + Neon). No hay build de
compilación: Python se ejecuta directamente. "Build" aquí = instalación de
dependencias + verificación de que la suite arranca.

## Instalación de dependencias

Desde `backend/`:

```bash
pip install -r requirements.txt
```

Versiones fijadas exactas (coste 0 €, todo OSS). En CI el runner usa **Python
3.12**. Para reproducir en local a coste 0 cuando el Python del sistema es más
nuevo que 3.12 (p. ej. 3.14), crear un venv efímero **excluyendo
`libsql-experimental`** (no compila fuera de 3.12 y los tests no lo ejercitan —
usan el fake SQLite de `conftest.py`):

```bash
cd backend
python3 -m venv .venv-bt && . .venv-bt/bin/activate
grep -v -i 'libsql' requirements.txt > /tmp/req.txt
pip install -r /tmp/req.txt pytest pytest-cov
```

## Configuración de entorno

- `JWT_SECRET`: requerido no-default en arranque (NFR1.1). En CI y en local es
  **efímero y no productivo** (p. ej. `bt-ephemeral-secret-not-a-real-one`).
  Nunca un secreto real (gitleaks escanea).
- `DATABASE_URL`: NO se necesita para los tests — usan el fake in-memory
  (`_FakeInMemoryDB`/`fake_db`), sin red ni BD real (NFR6).
- Ejecutar siempre **desde `backend/`** para que `from app...` resuelva
  (`pytest.ini` fija `pythonpath = .`).

## Comandos de build / verificación

```bash
# Verificar que la suite colecta (readiness del runner)
cd backend && python -m pytest tests/ --collect-only -q

# Suite completa con cobertura (el gate bloqueante usa --cov=app + piso 27)
cd backend && JWT_SECRET="bt-ephemeral-secret-not-a-real-one" \
  python -m pytest tests/ --cov=app -q
```

## Verificación del build

- La suite completa queda en **verde** (equivalencia estricta tras el refactor).
- El piso `--cov-fail-under=27` (en `pytest.ini`) **se mantiene o sube**; nunca
  se relaja (BR6.1/NFR2).
- `DataManagerV2` expone los **57 métodos** con firmas idénticas (fachada que
  sólo delega; no crece — BR1.4).

## Troubleshooting

- `No module named pytest`: el Python activo no tiene las deps; crear el venv
  efímero de arriba.
- Fallo de compilación de `libsql-experimental` fuera de 3.12: excluirlo del
  install (los tests no lo necesitan).
- `JWT_SECRET` ausente al arrancar `app.core.config`: exportar un valor efímero
  no productivo antes de correr.
- Si tras un run queda un venv efímero o `.coverage` en el árbol, limpiarlo
  (`git clean -fdx backend/.venv-bt backend/.coverage`) para no inflar el diff
  ni mover la fuente de cara a la revisión.
