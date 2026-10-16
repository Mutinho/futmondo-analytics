# Technology Stack — futmondo-analytics

> Versiones tomadas del scan de este run. Frontend con rangos `^`/`~` de
> `package.json`; backend con pins exactos de `requirements.txt`.

## Lenguajes

- **TypeScript** `~6.0.2` (frontend) — Angular 22.
- **Python** `3.12` (backend) — FastAPI. Node fijado en `.nvmrc` = `22.22.3`.

## Frontend (`angular-app`, `version: 2.2.0`)

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `@angular/{core,common,router,forms,animations,compiler,platform-browser,service-worker}` | `^22.2.1` | Framework Angular + PWA |
| `@angular/cdk`, `@angular/material` | `^22.2.1` | UI Material (DOM-dependiente) |
| `chart.js` | `^4.5.1` | Gráficos (`<canvas>`) |
| `ng2-charts` | `^10.0.0` | Wrapper Angular de Chart.js (lazy/`@defer`) |
| `marked` | `^18.0.11` | Markdown del asistente (diferido) |
| `rxjs` | `~7.8.0` | Reactividad |
| `tslib` | `^2.3.0` | Helpers de TS |

**devDependencies frontend**: `@angular/build` + `@angular/cli` `^22.2.0`,
`typescript` `~6.0.2`, `vitest` **`4.1.11`** (pin exacto) + `@vitest/coverage-v8`
**`4.1.11`**, `jsdom` `^25.0.1`, `prettier` `^3.8.1`. `packageManager:
npm@11.12.1`. **ESLint** flat config presente (`eslint.config.js`) pero sus
devDependencies NO instaladas (lint frontend advisory/diferido).

## Backend (`backend`, `version: 2.0.0`) — pins exactos

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `fastapi` | `0.141.1` | Framework web |
| `uvicorn[standard]` | `0.54.0` | ASGI server |
| `pydantic` | `2.13.5` | Validación/modelos |
| `requests` | `2.34.2` | HTTP cliente (Futmondo) |
| `python-dotenv` | `1.2.3` | Config `.env` |
| `python-multipart` | `0.0.32` | Form/multipart |
| `psycopg2-binary` | `2.9.13` | Driver PostgreSQL (Neon) |
| `curl_cffi` | `0.16.3` | Cliente HTTP para Sofascore |
| `PyJWT` | `2.15.0` | JWT |
| `google-genai` | `1.14.0` | LLM Gemini |
| `groq` | `0.25.0` | LLM fallback |

**Test backend**: `pytest` `9.1.1`, `pytest-cov` `7.1.0`, `httpx` `0.28.1`.

## Base de datos y despliegue

- **BD**: Neon PostgreSQL (serverless, Frankfurt / free tier).
- **Empaquetado**: Docker (`docker-compose.yml` local; Dockerfiles por servicio).
- **Deploy**: Fly.io (región `cdg`), apps `futmondo-api` y `futmondo-app`;
  `backend/fly.toml`, `angular-app/fly.toml`, `cron/fly.toml`.
- **CI/CD**: GitHub Actions (`ci.yml`, `fly-deploy.yml`, crons). Ver detalle en
  `code-quality-assessment.md`.

## Relevancia para el intent (viabilidad nativa)

El stack de **presentación** web (Angular Material, Chart.js/`<canvas>`,
PWA/service worker) es DOM-dependiente y no porta a NativeScript; servicios RxJS
y modelos sí. Ver dependencias cruzadas en `dependencies.md` y riesgos en
`code-quality-assessment.md`.
