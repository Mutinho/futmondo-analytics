# Build Instructions — refactor DDD de `assistant_service.py`

Intent `260929-assistant-god-file`, scope `refactor` (Minimal), zero-Unit. Refactor sin cambio
de comportamiento observable sobre el backend FastAPI/Python 3.12. Coste 0 €: solo tooling
existente (`pytest` + `pytest-cov`), sin dependencias nuevas.

## Instalación de dependencias y entorno

- **Backend** desde `backend/`. En CI (`ci.yml`, job `quality`) el entorno es Python de la línea
  3.12; en local, cuando el Python del sistema es más nuevo (p. ej. 3.14), se reproduce a coste 0
  con un **venv efímero** desde `backend/requirements.txt` **excluyendo `libsql-experimental`**
  (no compila fuera de 3.12 y no lo ejercitan los tests, que usan el fake SQLite in-memory) y un
  `JWT_SECRET` efímero de arranque:
  ```bash
  python3 -m venv /tmp/venv && . /tmp/venv/bin/activate
  grep -viE 'libsql-experimental' backend/requirements.txt > /tmp/reqs.txt
  pip install -r /tmp/reqs.txt
  export JWT_SECRET="ci-ephemeral-secret-not-a-real-one"
  ```
- **Sin dependencias nuevas** en este intent: el refactor usa solo stdlib + el `pytest`/
  `pytest-cov` ya presentes. `requirements.txt` no se toca (regla afirmada: cualquier dependencia
  nueva sería OSS y fijada a versión exacta).
- **Secretos**: `JWT_SECRET` no-default exigido en arranque (NFR1.1 del servicio); en CI es
  efímero y no productivo. Nunca credenciales reales (gitleaks escanea también los tests).

## Comandos de build y verificación

- **Build backend**: no hay paso de compilación (Python interpretado); la "build" efectiva es
  que el paquete importe sin errores y el import histórico siga resolviendo:
  ```bash
  cd backend && python -c "from app.services.assistant_service import get_assistant_service; get_assistant_service()"
  ```
- **Lint quirúrgico** (solo ficheros nuevos del paquete; NUNCA `ruff format`/`--fix` masivo sobre
  brownfield):
  ```bash
  cd backend && ruff check app/services/assistant/
  ```
- **Verificación de la suite** (ver `test-results.md`):
  ```bash
  cd backend && pytest --cov=app -q            # suite completa + cobertura (piso --cov-fail-under=27)
  cd backend && pytest tests/test_assistant_*.py -q   # unit-scoped del asistente
  ```
- El gate de CI bloqueante (gitleaks + `pytest` + `ng test`) es la verificación de release; un
  rojo nunca llega a `main`.

## Troubleshooting

- **`module 'psycopg2' has no attribute 'pool'`** al importar: aviso preexistente del fallback de
  pool de conexiones; no afecta a los tests (usan el fake in-memory) ni al refactor.
- **`libsql-experimental` no compila** en Python > 3.12: excluirlo del venv efímero como arriba;
  no lo ejercita ningún test.
- **Cobertura por debajo del piso**: NUNCA se relaja el piso `--cov-fail-under=27`; si aparece
  flapping se arregla el test no-determinista. El trinquete solo sube.
