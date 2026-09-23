# Instrucciones de build — Fiabilidad de la sync (backend)

> Conversation language: Spanish. Intent backend-only, aditivo, coste 0 €.
> Lead: aidlc-quality-agent; perspectiva de seguridad: aidlc-devsecops-agent.
> El intent NO toca el frontend (`angular-app/`) ni su build; toda la
> intervención vive en `backend/app/`.

## Dependencias

- Python **3.12** (línea de CI; el sistema local puede ser más nuevo).
  `.nvmrc`/Node no aplican a esta unidad (backend puro).
- Instalación: `pip install -r backend/requirements.txt`.
- Nota de coste 0 €: si el Python del sistema es > 3.12 y `libsql-experimental`
  no compila, usar el contenedor `python:3.12` (los tests usan el fake SQLite de
  `conftest.py`, no `libsql`).

## Entorno

- `JWT_SECRET` **no-default** obligatorio en arranque (NFR1.1). Para build/test
  local basta un literal efímero no productivo:
  `export JWT_SECRET=test-secret-not-default-000`.
- Sin BD ni red reales para los tests: fakes/dobles del task manager y del
  cliente Futmondo.

## Comandos de build

El backend es Python (sin paso de compilación/bundling). La "verificación de
build" es la comprobación de import/compilación y el arranque de la app:

```bash
cd backend
python -m compileall app        # compila todos los módulos (detecta SyntaxError)
python -c "import app.main"      # la app importa sin error (requiere JWT_SECRET)
```

Contenedor a coste 0 € (recomendado cuando el Python local ≠ 3.12):

```bash
docker run --rm -v "$PWD":/repo -w /repo/backend \
  -e JWT_SECRET=test-secret-not-default-000 -e PYTHONDONTWRITEBYTECODE=1 \
  python:3.12 bash -c "pip install --quiet -r requirements.txt; python -m compileall app"
```

## Verificación de build

- `compileall` termina sin error → sin fallos de sintaxis en `app/`.
- `import app.main` sin excepción → wiring de routers/servicios correcto.
- La suite `pytest` arranca la app vía `TestClient` (cubre el import de arranque).

## Troubleshooting

- **`libsql-experimental` no compila**: usar `python:3.12` o un venv efímero que
  la excluya (los tests no la ejercitan).
- **`JWT_SECRET` no-default**: el arranque falla adrede si falta o es default
  (NFR1.1). Exportar el literal efímero de arriba.
- **Bytecode residual (`__pycache__/*.pyc`)**: fijar `PYTHONDONTWRITEBYTECODE=1`
  al correr pytest para no ensuciar el árbol de trabajo.

## Sources

- `construction/sync-reliability/code-generation/code-summary.md`,
  `build-instructions` derivadas del stack real del backend.
- `inception/requirements-analysis/requirements.md` (NFR1.1 arranque JWT).

## Assumptions & Open Questions

None.
