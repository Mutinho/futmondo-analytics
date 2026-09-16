# Build Instructions — Durabilidad del estado

> Etapa Build and Test (Construction). Instrucciones de construcción del backend `futmondo-api`
> (FastAPI, Python 3.12) tras la durabilidad de sesión (u1) y de tareas de sync (u2). Coste 0 €.
> El frontend Angular no se toca en este intent (backend-only), así que estas instrucciones cubren
> el backend; el gate de CI ejecuta además `ng test` sin cambios funcionales de frontend.

## Prerrequisitos

- **Python 3.12** (línea que usa CI; ver `backend/Dockerfile` / `nixpacks.toml`). El runtime local
  puede ser más nuevo (p. ej. 3.14), pero `libsql-experimental==0.0.55` no compila en 3.14; ese
  paquete solo lo usa el backend Turso y **no** lo ejercitan los tests (usan el fake SQLite de
  `conftest.py`). Para ejecutar la suite en un entorno con 3.14, excluir `libsql-experimental` al
  instalar (ver más abajo). En CI (3.12) se instala el `requirements.txt` completo.
- **Neon PostgreSQL** solo para runtime productivo; **no** se requiere para los tests (fakes de
  persistencia en memoria).

## Instalación de dependencias

Desde `backend/`:

```bash
# Entorno productivo / CI (Python 3.12): requirements completo
pip install -r requirements.txt
```

```bash
# Entorno local con Python 3.14 (coste 0, sin Neon): venv efímero excluyendo libsql-experimental
python3 -m venv /tmp/futmondo-bt-venv
/tmp/futmondo-bt-venv/bin/pip install --upgrade pip
grep -v '^libsql-experimental' requirements.txt > /tmp/req-no-libsql.txt
/tmp/futmondo-bt-venv/bin/pip install -r /tmp/req-no-libsql.txt
```

## Configuración de entorno

- **`JWT_SECRET`** — obligatorio y no-default en el arranque del servicio web (guard NFR1.1,
  endurecido en `test_jwt_startup.py`). En producción SIEMPRE via secret de Fly.io; en test/CI un
  literal efímero no productivo de arranque es aceptable (permitido por el guard, ver `team.md`):

  ```bash
  export JWT_SECRET="ci-ephemeral-test-secret-not-production"
  ```

- **`FUTMONDO_CRED_KEY`** — clave Fernet para el cifrado en reposo de credenciales (FR5.2, u1). En
  producción via secret de Fly.io; en test se fija una clave efímera por fixture. No es necesaria
  para la recolección de la suite.
- **`DATABASE_URL`** — solo runtime productivo (Neon). Los tests no la usan.

## Comandos de build / verificación

El backend es Python interpretado; el "build" es la instalación de dependencias y la verificación de
importabilidad + arranque. Desde `backend/`:

```bash
# Verificación de importabilidad del árbol de la app (con JWT_SECRET de arranque)
JWT_SECRET="ci-ephemeral-test-secret-not-production" python -c "import app.main"
```

- Nuevos módulos de durabilidad: `app/stores/task_repository.py`, `app/services/task_service.py`
  (u2) y `app/stores/session_repository.py`, `app/security/credential_protection.py`,
  `app/services/session_service.py` (u1).
- Esquema durable creado de forma idempotente en el arranque (`ensure_durable_*_schema`), sin
  migración manual.

## Verificación del build

1. La instalación de dependencias termina sin errores (excluyendo `libsql-experimental` en 3.14).
2. `import app.main` no lanza (con `JWT_SECRET` de arranque fijado).
3. La suite de tests recolecta sin errores de import (ver `test-results.md`).

## Troubleshooting

- **`RuntimeError: FATAL: JWT_SECRET must be set...`** en la recolección de tests: exportar
  `JWT_SECRET` de arranque efímero antes de `pytest` (el import a nivel de módulo de
  `test_analytics_service.py` evalúa `app.core.config`).
- **Fallo de compilación de `libsql-experimental` en Python 3.14**: excluirlo del install local; no
  lo ejercitan los tests. CI usa 3.12 y lo instala normalmente.
- **`StarletteDeprecationWarning` de httpx en TestClient**: warning conocido, no relacionado con la
  durabilidad; no rompe la suite.
