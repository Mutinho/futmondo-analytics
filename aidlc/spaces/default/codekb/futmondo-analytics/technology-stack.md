# Technology Stack

## Lenguajes

- **Python 3.12** — backend (`backend/app/`). `ruff` fija `target-version = "py312"`
  (hay `.pyc` cpython-314 en el entorno, pero el target de lint y despliegue es 3.12).
- **TypeScript** — frontend Angular (`angular-app/`).
- Node fijado en `.nvmrc` = `22.22.3`.

## Backend (FastAPI, `backend/requirements.txt`, pins reportados por esta pasada)

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `fastapi` | 0.141.1 | framework web / routers |
| `uvicorn[standard]` | 0.54.0 | servidor ASGI |
| `pydantic` | 2.13.5 | validación/serialización |
| `python-multipart` | 0.0.32 | form/multipart |
| `psycopg2-binary` | 2.9.13 | driver PostgreSQL (Neon); único engine productivo; fakes SQLite en tests |
| `requests` | 2.34.2 | HTTP (API Futmondo) |
| `curl_cffi` | 0.16.3 | HTTP con impersonación (API Sofascore) |
| `PyJWT` | 2.15.0 | JWT auth |
| `python-dotenv` | 1.2.3 | carga de `.env` |
| `google-genai` | 1.14.0 | LLM (asistente) |
| `groq` | 0.25.0 | LLM (asistente) |

> Base del patrón de ports: `typing.Protocol` (stdlib) y DTOs `dataclasses`
> (stdlib). `DataManagerV2` se apoya en stdlib + `psycopg2-binary` para todo su SQL;
> no introduce dependencias propias (coste 0 €). `requirements.txt` conserva rangos
> abiertos (deuda de pin); las versiones de arriba reflejan el entorno resuelto
> reportado por el scan.

### Test backend

| Librería | Versión |
|----------|---------|
| `pytest` | 9.1.1 |
| `pytest-cov` | 7.1.0 |
| `httpx` | 0.28.1 |

## Frontend (Angular, `angular-app/package.json`) — prosa preservada

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `@angular/*` | ^22.1.0 | framework (standalone, signals, PWA) |
| `@angular/material` | (línea 22) | UI Material |
| `chart.js` | ^4.5.1 | gráficos |
| `ng2-charts` | ^10.0.0 | wrapper Angular de Chart.js |
| `marked` | ^18.0.11 | render Markdown |
| `rxjs` | ~7.8.0 | programación reactiva |
| `vitest` / `@vitest/coverage-v8` | 4.1.11 | test + cobertura frontend |

## Tooling de calidad y despliegue

- `ruff` (lint backend, config `backend/ruff.toml`: `py312`, `line-length = 100`,
  `select = ["E","F","I"]`, `ignore = ["E501","E402"]`; `per-file-ignores` para el
  god-file). CI usa `ruff==0.16.9`. Ver `code-quality-assessment.md`.
- **Base de datos**: Neon PostgreSQL (serverless, Frankfurt).
- **Deploy**: Fly.io (región `cdg`) — dos apps (`futmondo-api`, `futmondo-app`).
- **CI/CD**: GitHub Actions (`ci.yml`, `fly-deploy.yml`, crons `daily-sync.yml` /
  `sofascore-sync.yml`); `pip-audit==2.10.1`.
- **Proxy**: nginx. **Restricción**: todo en tiers gratuitos (coste 0 €).
