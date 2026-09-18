# Stack Tecnológico — futmondo-analytics

## Lenguajes y Runtimes

- **Python 3.12** (backend). Nota: `libsql-experimental==0.0.55` sólo compila en 3.12.
- **TypeScript** (frontend, `typescript ~6.0.2`).
- **Node.js 22.22.3** (fijado en `.nvmrc`, alineado con la línea Node 22 de CI).

## Frameworks y Librerías

Versiones tal como aparecen en `backend/requirements.txt` y `angular-app/package.json`; el
mapa de dependencias externas/internas está en `dependencies.md`.

### Backend

| Librería | Versión | Propósito |
|---|---|---|
| `fastapi` | `>=0.104.0` | Framework web / API. |
| `uvicorn[standard]` | — | Servidor ASGI. |
| `pydantic` | `>=2.5.0` | Validación/serialización de modelos (DTOs en `models.py`). |
| `PyJWT` | `==2.9.0` | Emisión/verificación de JWT. |
| `requests` | `>=2.31.0` | Cliente HTTP (proxy Futmondo, fotos). |
| `curl_cffi` | `>=0.16.0` | Cliente HTTP para Sofascore (fingerprint TLS). |
| `psycopg2-binary` | — | Driver PostgreSQL (Neon). |
| `libsql-experimental` | `==0.0.55` | Driver Turso/libSQL (fallback; sólo Python 3.12). |
| `python-dotenv` | — | Carga de `.env`. |
| `google-genai`, `groq` | — | Integraciones LLM (assistant). |
| `pytest` | `>=8.0.0` | Framework de test backend. |
| `pytest-cov`, `httpx` | — | Cobertura y `TestClient`. |

Nota del área analizada: la analítica y el cálculo de premios usan la librería estándar
`statistics` (media, pstdev) y SQL crudo (placeholders `?` adaptados con `adapt_params`);
no introducen dependencias nuevas. Cualquier doble/fake para caracterizar `sync_prizes` debe
apoyarse en `pytest` + fakes en memoria (patrón `conftest.py`), sin coste.

### Frontend

| Librería | Versión | Propósito |
|---|---|---|
| `@angular/*` | `^22.1.0` | Framework SPA/PWA. |
| Angular Material | `22` | Componentes UI (`MatTable`, `MatDialog`, signals). |
| `chart.js`, `ng2-charts` | — | Gráficos (evolución, analytics, finanzas). |
| `marked` | — | Render de Markdown. |
| `rxjs` | `~7.8.0` | Programación reactiva. |
| `vitest` | `^4.0.8` (dev) | Test runner frontend (vía `@angular/build:unit-test`). |
| `jsdom`, `prettier` | `^3.8.1` (dev) | Entorno de test / formateo. |

## Infraestructura y Despliegue

- **Base de datos**: Neon PostgreSQL (Frankfurt, tier free) como modo productivo; fallback
  SQLite/Turso. Selección vía `DATABASE_URL` / `DATABASE_TYPE`.
- **Hosting**: Fly.io (región `cdg`), dos apps — `futmondo-api` (puerto 8000, check
  `/health`) y `futmondo-app` (nginx, puerto 80). Ambas `min=max=1`, `shared-cpu-1x`/256 MB.
- **CI/CD**: GitHub Actions (`ci.yml`, `fly-deploy.yml`, crons); detalle en
  `code-quality-assessment.md`.
- **Build**: backend pip + `Dockerfile`/`nixpacks.toml`; frontend npm (`npm@11.12.1`) +
  Angular CLI.
- **Restricción dura**: todo en tiers gratuitos (Neon free, Fly.io free allowance, GitHub
  Actions free) — coste 0 €.
