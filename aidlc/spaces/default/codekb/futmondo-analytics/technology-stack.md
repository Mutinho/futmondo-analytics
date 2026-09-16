# Technology Stack — Futmondo Analytics

> Artefacto CodeKB (architect). Base: `developer-scan.md`. Store STALE. Las versiones del backend reflejan lo **verificado en este run** (`backend/requirements.txt`); las del frontend se preservan del análisis previo (fuera del foco de este run).

## Lenguajes

- **Python 3.12** — backend y cron (Dockerfile `python:3.12-slim`; `ruff.toml` `target-version = py312`). **Divergencia**: `nixpacks.toml` (Railway heredado) fija `python311`.
- **TypeScript** — frontend (`angular-app`).

## Backend (`backend/requirements.txt`, Python 3.12) — verificado este run

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `fastapi` | `>=0.104.0` | Framework web/API |
| `uvicorn[standard]` | `>=0.24.0` | Servidor ASGI (`uvicorn app.main:app`) |
| `pydantic` | `>=2.5.0` | Modelos/validación (`app.auth.models`) |
| `PyJWT` (`jwt`) | `==2.9.0` | Firma/verificación JWT HS256 |
| `psycopg2-binary` | `>=2.9.9` | Cliente PostgreSQL (Neon) + `ThreadedConnectionPool` |
| `libsql-experimental` | `==0.0.55` | Backend Turso/LibSQL (ruta alternativa; ver deuda técnica) |
| `requests` | `>=2.31.0` | HTTP del `FutmondoClient` (`requests.Session`) |
| `curl_cffi` | `>=0.16.0` | Cliente HTTP para Sofascore (impersonación de navegador) |
| `python-dotenv` | `>=1.0.0` | Carga `.env` |
| `python-multipart` | `>=0.0.6` | Form/multipart |
| `google-genai` | `==1.14.0` | IA (assistant; fuera de foco) |
| `groq` | `==0.25.0` | IA (assistant; fuera de foco) |
| `pytest` | `>=8.0.0` | Runner de tests |
| `pytest-cov` | `>=5.0.0` | Cobertura (informativa, sin piso bloqueante) |
| `httpx` | `>=0.27.0` | `TestClient` de Starlette |

- **Linter/formato backend**: `ruff` (`backend/ruff.toml`, `select = [E, F, I]`, `ignore = [E501, E402, E722]`, `line-length = 100`) — **advisory** en CI.

## Frontend (`angular-app`, `version 2.1.7`) — preservado del análisis previo

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `@angular/*` (`core`, `common`, `compiler`, `forms`, `router`, `platform-browser`, `service-worker`, `animations`) | `22.1.x` | Framework Angular 22 (standalone, signals) + PWA |
| `@angular/material` | `22.1.6` | UI Material 22 |
| `@angular/cdk` | `22.1.6` | CDK |
| `chart.js` | `4.5.1` | Gráficos |
| `ng2-charts` | `10.0.0` | Wrapper Angular de Chart.js |
| `marked` | `18.0.13` | Render de Markdown del chat del asistente |
| `rxjs` | `7.8.2` | Reactividad |
| `tslib` | `2.8.1` | Runtime TypeScript |

devDependencies frontend (preservado): `@angular/build`/`@angular/cli` `22.1.x`, `vitest ^4.0.8` + `jsdom ^25` (runner vía `@angular/build:unit-test`), `prettier ^3.8.1`. **Engines**: `node: ^22.22.3 || ^24.15.0 || >=26.0.0`; raíz fija `.nvmrc` = `22.22.3`. ESLint (flat config) en modo advisory; devDeps de eslint aún no instaladas.

## Infraestructura / build / deploy

| Tecnología | Uso |
|------------|-----|
| Neon PostgreSQL | Base de datos serverless (Frankfurt), tier free |
| Fly.io (`flyctl`) | Deploy de `angular-app`, `backend` (región `cdg`), `cron`; free allowance |
| Docker | `python:3.12-slim` (backend); multi-stage `node`→`nginx:alpine` (frontend) |
| nginx (`nginx:alpine`) | Servido de SPA y reverse proxy local |
| GitHub Actions | CI/CD (tier free) |
| `nixpacks.toml` | Config Railway heredada (`target python311`); ver deuda técnica |

## Referencias cruzadas

- Relaciones de dependencia (externas e internas): `dependencies.md`.
- Señales de deuda por versión/tooling: `code-quality-assessment.md`.
