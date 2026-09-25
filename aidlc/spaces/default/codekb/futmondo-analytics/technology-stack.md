# Stack Tecnológico — futmondo-analytics

## Lenguajes y Runtimes

- **Python 3.12** (backend). Nota: `libsql-experimental==0.0.55` sólo compila en 3.12.
- **TypeScript** (frontend, `typescript ~6.0.2`).
- **Node.js 22.22.3** (fijado en `.nvmrc` de RAÍZ — no existe `.nvmrc` dentro de
  `angular-app/`; alineado con la línea Node 22 de CI, que usa `node-version: '22'`).

## Frameworks y Librerías

Versiones tal como aparecen en `backend/requirements.txt` y `angular-app/package.json`; el
mapa de dependencias externas/internas está en `dependencies.md`.

### Backend

| Librería | Versión | Propósito |
|---|---|---|
| `fastapi` | `>=0.104.0` | Framework web / API. |
| `uvicorn[standard]` | `>=0.24.0` | Servidor ASGI. |
| `pydantic` | `>=2.5.0` | Validación/serialización de modelos (DTOs en `models.py`). |
| `PyJWT` | `==2.9.0` | Emisión/verificación de JWT. |
| `requests` | `>=2.31.0` | Cliente HTTP (proxy Futmondo, fotos). Sus `Timeout`/`RequestException` son las excepciones que `futmondo_client._make_request` traga a `None` (hueco FR4). |
| `curl_cffi` | `>=0.16.0` | Cliente HTTP para Sofascore (fingerprint TLS, impersonate chrome, throttle 750 ms). Sobre él se implementa `SofascoreIPBanError` (patrón recuperable-vs-fatal de referencia). |
| `psycopg2-binary` | `>=2.9.9` | Driver PostgreSQL (Neon). Pool `ThreadedConnectionPool` (5-20) con retry x3 en `db_connection`. |
| `libsql-experimental` | `==0.0.55` | Driver Turso/libSQL (fallback; sólo Python 3.12). |
| `python-dotenv` | — | Carga de `.env`. |
| `google-genai` | `==1.14.0` | Integración LLM (assistant; fuera del área del intent activo). |
| `groq` | `==0.25.0` | Integración LLM (assistant; fuera del área del intent activo). |
| `pytest` | `>=8.0.0` | Framework de test backend. |
| `pytest-cov` | `>=5.0.0` | Cobertura (`--cov=app` en `ci.yml`). |
| `httpx` | `>=0.27.0` | `starlette.testclient.TestClient`. |

Nota del área de fiabilidad (intent activo): las dos integraciones externas usan clientes
HTTP distintos — `requests` (Futmondo) y `curl_cffi` (Sofascore) — con contratos de fallo
divergentes; la caracterización usa `pytest` + fakes en memoria (`conftest.py`:
`_FakeInMemoryDB`/`_FakeCursor` SQLite `:memory:` que honra el contrato de `db_connection`,
`clean_jwt_env`, `fake_db`), sin red ni DB real ni credenciales, coste 0 €.

### Frontend

| Librería | Versión | Propósito |
|---|---|---|
| `@angular/*` (animations, cdk, common, compiler, core, forms, material, platform-browser, router, service-worker) | `^22.1.0` | Framework SPA/PWA + Material + service worker. |
| `chart.js` | `^4.5.1` | Gráficos (evolución, analytics, finanzas). |
| `ng2-charts` | `^10.0.0` | Wrapper Angular de Chart.js. |
| `marked` | `^18.0.11` | Render de Markdown (assistant). |
| `rxjs` | `~7.8.0` | Programación reactiva. |
| `tslib` | `^2.3.0` | Runtime de TypeScript. |
| `@angular/build` | `^22.1.2` (dev) | Builder (esbuild/vite) para `ng build`/`ng test`. |
| `@angular/cli` | `^22.1.2` (dev) | CLI (`ng`). |
| `@angular/compiler-cli` | `^22.1.0` (dev) | Compilación AOT. |
| `vitest` | `^4.0.8` (dev) | Test runner frontend (`architect.test.runner: vitest` vía `@angular/build:unit-test`). |
| `jsdom` | `^25.0.1` (dev) | Entorno DOM para los tests Vitest. |
| `typescript` | `~6.0.2` (dev) | Compilador TS. |
| `prettier` | `^3.8.1` (dev) | Formateo. |

**Gestor de paquetes**: `npm@11.12.1` (`packageManager` en `package.json`). `package.json`
name `angular-app`.

El estado detallado del tooling de test/cobertura del frontend (proveedor, thresholds,
migración a Vitest) vive en `code-quality-assessment.md`, área propietaria de aquel intent.

## Infraestructura y Despliegue

- **Base de datos**: Neon PostgreSQL (Frankfurt, tier free) como modo productivo; fallback
  SQLite/Turso. Selección vía `DATABASE_URL` / `DATABASE_TYPE`.
- **Hosting**: Fly.io (región `cdg`), dos apps — `futmondo-api` (puerto 8000, check
  `/health`) y `futmondo-app` (nginx, puerto 80). Ambas `min=max=1`, `shared-cpu-1x`/256 MB.
- **CI/CD**: GitHub Actions (`ci.yml`, `fly-deploy.yml`, `daily-sync.yml`,
  `sofascore-sync.yml`); detalle en `code-quality-assessment.md`.
- **Build**: backend pip + `Dockerfile`/`nixpacks.toml` (sin poetry); frontend npm
  (`npm@11.12.1`) + Angular CLI (`@angular/build`).
- **Restricción dura**: todo en tiers gratuitos (Neon free, Fly.io free allowance, GitHub
  Actions free) — coste 0 €.
