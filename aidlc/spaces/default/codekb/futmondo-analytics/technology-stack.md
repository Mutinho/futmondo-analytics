# Technology Stack — futmondo-analytics

Versiones tomadas de los pins exactos del handoff (`backend/requirements.txt`,
`angular-app/package.json`, `.nvmrc`). Evidencia de configuración en
`code-quality-assessment.md`.

## Lenguajes

- **Python 3.12** (backend `futmondo-api`; `ruff.toml` `target-version = py312`).
- **TypeScript** (frontend Angular).
- SQL crudo embebido (PostgreSQL / SQLite en tests vía `adapt_params`).

## Backend — frameworks y librerías (pins exactos)

- `fastapi==0.141.1` — framework web/API.
- `uvicorn[standard]==0.54.0` — servidor ASGI.
- `pydantic==2.13.5` — validación/serialización de modelos.
- `psycopg2-binary==2.9.13` — driver PostgreSQL (Neon).
- `curl_cffi==0.16.3` — cliente HTTP para Sofascore.
- `PyJWT==2.13.0` — JWT (auth).
- `requests==2.34.2` — cliente HTTP (Futmondo).
- `google-genai==1.14.0` — LLM Gemini (fallback del asistente).
- `groq==0.25.0` — LLM Groq (`openai/gpt-oss-120b`, primario del asistente).
- `python-dotenv==1.2.3` — carga de entorno.
- `python-multipart==0.0.32` — parsing multipart.

### Backend — test

- `pytest==9.1.1`, `pytest-cov==7.1.0`, `httpx==0.28.1`.

## Frontend — frameworks y librerías

- **Angular 22** + **Material 22** (PWA; signals, standalone components).
- Chart.js / ng2-charts (gráficos).
- `@vitest/coverage-v8==4.1.11` (proveedor de cobertura, pin exacto; `vitest`
  aún en rango abierto `^4.0.8` — señalado como deuda de pin en
  `code-quality-assessment.md`).
- **Node** fijado en `.nvmrc` = `22.22.3`.

## Infra / plataforma (coste 0 €)

- **Neon PostgreSQL** (Frankfurt, tier free) — base de datos.
- **Fly.io** (región `cdg`, tier free allowance) — dos apps: `futmondo-api`
  (puerto 8000, check `/health`) y `futmondo-app` (nginx, check `/`).
- **GitHub Actions** (tier free) — CI (`ci.yml`) y deploy (`fly-deploy.yml`).
- **Docker** — `docker-compose.yml` (local), `Dockerfile` por app.

## Notas de política

Pin a versión exacta en el paso que instala cada dependencia de tooling del gate
bloqueante; nada de rangos abiertos en checks bloqueantes (regla afirmada).
Cualquier dependencia nueva sería OSS y fijada (no se prevé ninguna para el
intent activo).
