# Instrucciones de Build — Backend Security Hardening

> Scope `security-patch`, test strategy Minimal, brownfield. El «build» de este
> patch es la verificación de la suite de tests del backend (Python/FastAPI) y,
> en CI, del frontend Angular; no hay compilación nueva. Coste 0 €.

## Prerrequisitos

- Python **3.12** en CI (línea de producción). En local, si el Python del
  sistema es más nuevo, usar un venv efímero (ver más abajo).
- `backend/requirements.txt` para el backend; Node `22.22.3` (`.nvmrc`) para el
  frontend.

## Instalación de dependencias (backend)

Desde `backend/`:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

### Nota de reproducción local a coste 0 (Python > 3.12)

Si el Python del sistema es más nuevo que 3.12, `libsql-experimental==0.0.55`
no compila. Los tests usan el fake SQLite de `conftest.py`, así que se excluye
sin afectar la validez:

```bash
python3 -m venv /tmp/bt-venv && . /tmp/bt-venv/bin/activate
grep -viE 'libsql-experimental' requirements.txt > /tmp/req.txt
pip install -r /tmp/req.txt
export JWT_SECRET="ephemeral-not-default-000"   # literal de arranque no productivo (guard NFR1.1)
```

## Setup de entorno

- `JWT_SECRET`: obligatorio y no-default (guard `resolve_jwt_secret`, NFR1.2).
  En tests se fija un literal efímero no productivo; en producción SIEMPRE via
  secrets de Fly.io / GitHub Actions.
- Los tests NO tocan Neon: usan fakes de conexión (`conftest.py`,
  `test_auth_characterization.py`).

## Comandos de build/verificación

Desde `backend/`:

```bash
python -m pytest -q            # suite completa del backend
```

Frontend (en CI, o local con Node 22.22.3):

```bash
cd angular-app && npm ci && npm run test   # ng test (Vitest + jsdom)
```

## Verificación del build

- La suite del backend debe terminar en verde (135 passed en la ejecución de
  esta etapa).
- El gate de CI bloqueante (`.github/workflows/ci.yml`) exige además
  **gitleaks** y **ng test** verdes antes de fusionar a `main`.

## Troubleshooting

- `ModuleNotFoundError: app...` → ejecutar desde `backend/` (pytest.ini fija
  `pythonpath=.`).
- Fallo de compilación de `libsql-experimental` en Python > 3.12 → excluirlo del
  venv efímero (ver arriba); no afecta a los tests.
- `JWT_SECRET must not be default` al arrancar → exportar un `JWT_SECRET`
  no-default (comportamiento esperado del guard NFR1.2, no un bug).
