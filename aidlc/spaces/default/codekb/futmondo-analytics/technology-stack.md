# Technology Stack — futmondo-analytics

## Languages

- **TypeScript** `~6.0.2` — frontend Angular.
- **Python** `3.12` (`backend/ruff.toml` `target-version = "py312"`, `.python-version`).

## Frontend (angular-app)

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `@angular/*` (core, material, cdk) | `^22.2.1` | SPA/PWA: standalone components, signals, `OnPush`, rutas lazy. |
| `@angular/build` / `@angular/cli` | `^22.2.0` | Build (`@angular/build:application`), bundle PWA. |
| `@angular/service-worker` | `^22.2.1` | PWA (service worker, `ngsw-config.json`). |
| `chart.js` | `^4.5.1` | Gráficos. |
| `ng2-charts` | `^10.0.0` | Integración Angular de Chart.js. |
| `rxjs` | `~7.8.0` | Streams/async. |
| `marked` | `^18.0.11` | Render Markdown (asistente). |
| `vitest` | `4.1.11` | Runner de tests (`ng test`, builder `@angular/build:unit-test`). |
| `@vitest/coverage-v8` | `4.1.11` | Cobertura (pin exacto, emparejado con `vitest`). |
| `typescript` | `~6.0.2` | Lenguaje. |
| `jsdom`, `prettier` | dev | Entorno de test / formateo. |

- `packageManager: npm@11.12.1`; Node fijado en `.nvmrc` = `22.22.3`.

## Backend (backend)

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `fastapi` | `0.141.1` | Framework API HTTP. |
| `uvicorn` | `0.54.0` | ASGI server (`run.py`). |
| `pydantic` | `2.13.5` | Validación/serialización. |
| `PyJWT` | `2.15.0` | JWT (access/refresh). |
| `psycopg2-binary` | `2.9.13` | Driver Neon PostgreSQL. |
| `requests` | `2.34.2` | HTTP (Futmondo). |
| `curl_cffi` | `0.16.3` | HTTP para Sofascore. |
| `python-multipart`, `python-dotenv` | — | Multipart / `.env`. |
| `google-genai` | `1.14.0` | Asistente IA (Gemini). |
| `groq` | `0.25.0` | Asistente IA (Groq). |
| `pytest` | `9.1.1` | Tests backend. |
| `pytest-cov` | `7.1.0` | Cobertura backend. |
| `httpx` | `0.28.1` | Cliente HTTP de test. |

- **`requirements.txt` ya está pinneado a versión exacta (`==`)** — estado actual del
  código; los rangos abiertos descritos en `team.md` corresponden a un estado
  anterior ya resuelto (ver `code-quality-assessment.md`).

## Data & Infrastructure

- **Base de datos**: Neon PostgreSQL (serverless, Frankfurt, tier free).
- **Deploy**: Fly.io (región `cdg`) — dos apps (`futmondo-api` puerto 8000 check
  `/health`; `futmondo-app` nginx check `/`). CI/CD con GitHub Actions.
- **Proxy**: Nginx (local `proxy/`, prod `angular-app/nginx*.conf`).
- **Orquestación local**: Docker Compose.
- **Restricción**: todo en tiers gratuitos — coste 0 €.

## Sources

- `developer-scan.md`: Frameworks & Libraries, Build System, Test Coverage.
- `README.md`: tabla de stack, diagrama de producción.
- Versiones concretas en `dependencies.md`.
