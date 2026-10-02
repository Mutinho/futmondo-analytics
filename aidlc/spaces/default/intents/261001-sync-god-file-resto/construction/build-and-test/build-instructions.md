# Build Instructions — `261001-sync-god-file-resto`

> Backend FastAPI (Python 3.12 en CI). Refactor sin dependencias nuevas. Idioma:
> prosa en castellano; comandos literales.

## Dependencias

Desde `backend/`:

```bash
pip install -r requirements.txt
```

No se añaden dependencias nuevas en este intent (stdlib `typing.Protocol`
suficiente). `requirements.txt` no contiene `libsql-experimental`.

## Entorno

- Python 3.12 en CI (Fly.io/GitHub Actions). En local, si el Python del sistema
  es más nuevo que 3.12, crear un venv efímero e instalar `requirements.txt`
  (coste 0 €).
- `JWT_SECRET` no-default requerido en arranque (NFR1.1). Para tests, un secreto
  efímero no productivo basta (`export JWT_SECRET="ephemeral-..."`).
- Sin BD real: los tests usan los fakes en memoria de `conftest.py`.

## Build / verificación

Este refactor no tiene paso de compilación (Python). La verificación es la suite
de tests:

```bash
cd backend
pytest -q --cov=app --cov-fail-under=27
```

## Troubleshooting

- Si pytest no está disponible en el Python del sistema o la versión difiere de
  la de CI: crear venv efímero (`python3 -m venv /tmp/venv && /tmp/venv/bin/pip
  install -r requirements.txt`) y correr con `JWT_SECRET` efímero.
- Si falla el arranque por `JWT_SECRET`: exportar un secreto efímero no-default.
