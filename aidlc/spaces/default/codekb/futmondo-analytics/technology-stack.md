# Stack Tecnológico — Futmondo Analytics

## Lenguajes

- **Python 3.12** (backend).
- **TypeScript / Angular** (frontend).

## Backend

| Componente | Versión | Propósito |
|------------|---------|-----------|
| FastAPI | (rango abierto en `requirements.txt`) | framework web/API |
| uvicorn[standard] | rango abierto | servidor ASGI |
| pydantic | v2 | validación/serialización |
| PyJWT | `2.9.0` (pin) | JWT auth |
| psycopg2-binary | rango abierto | driver PostgreSQL (Neon) |
| curl_cffi | rango abierto | cliente HTTP para Sofascore |
| libsql-experimental | `0.0.55` (pin) | cliente Turso — **dead-path**, no compila fuera de 3.12, no ejercitado por tests (FR14) |
| google-genai | pin | asistente (Gemini) |
| groq | pin | asistente (Groq) |
| python-dotenv | rango abierto | carga de `.env` |

> Detalle exhaustivo de versiones en `backend/requirements.txt`. Varias
> dependencias van con rango abierto (deuda de pinning, ver
> `code-quality-assessment.md`).

## Frontend

| Componente | Versión | Propósito |
|------------|---------|-----------|
| Angular | 22.1.x | framework SPA/PWA |
| Angular Material | 22 | UI |
| chart.js + ng2-charts | 4.5 / 10 | gráficos |
| marked | 18 | render Markdown |
| rxjs | 7.8 | reactividad |
| @vitest/coverage-v8 | `4.1.11` (pin) | cobertura (gate) |

> Detalle en `angular-app/package.json`. Node fijado en `.nvmrc` = `22.22.3`.

## Base de datos

- **Neon PostgreSQL** (Frankfurt, tier free) — vía `DATABASE_URL` (producción).
- Fallback SQLite / Turso — **muerto en operación** (código presente, FR14).

## Infraestructura / despliegue

- **Docker** (`python:3.12-slim`) + **Fly.io** (región `cdg`), check `/health`.
- **GitHub Actions** (CI + deploy + crons).
- `nixpacks.toml` (`python311`) — **residuo Railway**, incoherente con 3.12 y
  con Fly.io/Docker (ver deuda).
- Coste 0 € (Neon free, Fly.io free allowance, GitHub Actions free).
