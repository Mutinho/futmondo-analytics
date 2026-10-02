# Technology Stack

## Lenguajes

- **Python 3.12** — backend (`backend/app/`).
- **TypeScript** — frontend Angular (`angular-app/`).
- Node fijado en `.nvmrc` = `22.22.3`.

## Backend (FastAPI, `backend/requirements.txt`)

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `fastapi` | 0.141.1 | framework web (sync router) |
| `uvicorn[standard]` | 0.54.0 | servidor ASGI |
| `pydantic` | 2.13.5 | validación/serialización |
| `PyJWT` | 2.15.0 | JWT auth |
| `psycopg2-binary` | 2.9.13 | driver PostgreSQL (Neon); fakes SQLite en tests |
| `requests` | 2.34.2 | HTTP (API Futmondo) |
| `curl_cffi` | 0.16.3 | HTTP con impersonación (API Sofascore) |
| `google-genai` | 1.14.0 | LLM (asistente) |
| `groq` | 0.25.0 | LLM (asistente) |
| `python-dotenv` | 1.2.3 | carga de `.env` |
| `python-multipart` | 0.0.32 | form/multipart |

> Nota: `requirements.txt` tiene rangos abiertos (deuda de pin); las versiones de
> arriba reflejan el entorno resuelto reportado por el scan. Base del patrón de
> ports: `typing.Protocol` (stdlib) y DTOs `dataclasses` `frozen=True` (stdlib).

### Test backend

| Librería | Versión |
|----------|---------|
| `pytest` | 9.1.1 |
| `pytest-cov` | 7.1.0 |
| `httpx` | 0.28.1 |

## Frontend (Angular, `angular-app/package.json`)

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `@angular/*` | ^22.1.0 | framework (standalone, signals, PWA) |
| `@angular/material` | (línea 22) | UI Material |
| `chart.js` | ^4.5.1 | gráficos |
| `ng2-charts` | ^10.0.0 | wrapper Angular de Chart.js |
| `marked` | ^18.0.11 | render Markdown |
| `rxjs` | ~7.8.0 | programación reactiva |

### Test frontend

| Librería | Versión |
|----------|---------|
| `vitest` | 4.1.11 |
| `@vitest/coverage-v8` | 4.1.11 |
| `jsdom` | (presente) |

## Tooling de calidad

- `ruff` (lint backend; sin pin en la instalación de CI, config en
  `backend/ruff.toml`: `target-version = "py312"`, `line-length = 100`,
  `select = ["E","F","I"]`, `ignore = ["E501","E402"]`). Ver
  `code-quality-assessment.md` para la configuración de calidad y CI/CD.
- ESLint frontend: deuda diferida (no instalado como devDependency).

## Datos y despliegue

- **Base de datos**: Neon PostgreSQL (serverless, Frankfurt).
- **Deploy**: Fly.io (región `cdg`) — dos apps (`futmondo-api`, `futmondo-app`).
- **CI/CD**: GitHub Actions (`ci.yml`, `fly-deploy.yml`, crons).
- **Proxy**: nginx.
- **Restricción**: todo en tiers gratuitos (coste 0 €).
