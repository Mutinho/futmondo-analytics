# Instrucciones de Build — Reemplazo transaccional de la caché de Sofascore

> Intent: `260911-sofascore-cache-atomica` · Scope: `bugfix` · Estrategia de
> test: Minimal · Backend FastAPI (Python) sobre Neon PostgreSQL / SQLite (tests).

## Prerrequisitos

- Python 3.12 (producción/CI). El entorno de ejecución local de esta sesión
  tiene Python 3.14 gestionado por el SO (PEP 668); se usa un venv aislado.
- Los tests NO requieren `libsql-experimental` (Turso), que necesita toolchain
  de Rust y no compila en Python 3.14; los tests usan SQLite en memoria.

## Instalación de dependencias

Desde `backend/`, en un entorno virtual aislado:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Si `libsql-experimental` falla al compilar en el entorno local (Python 3.14 sin
Rust), instalar el subconjunto necesario para build/test (no usa Turso):

```bash
pip install requests python-dotenv fastapi pydantic python-multipart \
  psycopg2-binary curl_cffi PyJWT pytest pytest-cov httpx
```

## Configuración de entorno

- `JWT_SECRET` es obligatorio para importar `app.core.config`. En tests basta un
  valor no-default: `export JWT_SECRET="test-secret-not-default-000"`.
- No se requiere `DATABASE_URL` para los tests (usan fakes de `db` / SQLite).
- Ninguna variable nueva se añade en este bugfix.

## Comandos de build

El backend es Python interpretado: no hay paso de compilación/bundling. La
"verificación de build" equivale a comprobar que los módulos importan/parsean:

```bash
python -m py_compile app/core/constants.py \
  app/services/sofascore_client.py \
  app/api/v1/endpoints/sofascore_sync.py \
  tests/test_sofascore_sync_characterization.py
```

Lint (opcional, config en `backend/ruff.toml`):

```bash
ruff check app tests
```

## Verificación de build

- `py_compile` de los 4 ficheros tocados debe salir con código 0.
- La colección de pytest (`pytest --collect-only`) no debe reportar errores de
  importación.

## Troubleshooting

- **`ModuleNotFoundError: app`** → ejecutar pytest DESDE `backend/`
  (`pytest.ini` fija `pythonpath = .`).
- **`libsql-experimental` no compila** → no es necesario para los tests;
  instalar el subconjunto de dependencias indicado arriba.
- **`JWT_SECRET` no definido** → exportarlo antes de importar `app.core.config`.
