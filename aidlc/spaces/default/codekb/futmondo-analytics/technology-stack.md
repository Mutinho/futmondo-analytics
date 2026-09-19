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
| `pytest-cov`, `httpx` | `>=5.0.0` / `>=0.27.0` | Cobertura (`--cov=app` en `ci.yml`) y `TestClient`. |

Nota del área de premios: la analítica y el cálculo de premios usan la librería estándar
`statistics` (media, pstdev) y SQL crudo (placeholders `?` adaptados con `adapt_params`);
no introducen dependencias nuevas. Cualquier doble/fake para caracterizar `sync_prizes` debe
apoyarse en `pytest` + fakes en memoria (patrón `conftest.py`), sin coste.

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
name `angular-app`, version `2.1.8`.

**Estado del tooling de test/cobertura (clave del intent activo)**:

- El runner es **Vitest** ejecutado por el builder `@angular/build:unit-test`
  (`angular.json` → `architect.test`: `runner: vitest`, `tsConfig: tsconfig.spec.json`,
  `buildTarget: angular-app:build:development`). `tsconfig.spec.json` declara
  `types: ["vitest/globals"]` e `include: src/**/*.spec.ts`.
- **NO existe `vitest.config.*`** en `angular-app/`; `angular.json` no declara opciones de
  `coverage`.
- **NO hay proveedor de cobertura instalado** (`@vitest/coverage-v8` ni `istanbul` en
  devDependencies) ni `coverage.thresholds`. `ng test` hoy ejecuta specs pero NO reporta ni
  exige cobertura.
- **NO quedan restos Karma/Jasmine** (`karma.conf.js`/`src/test.ts` ausentes): la migración
  a Vitest está completa; lo que falta es la capa de cobertura.
- **Dependencias de ESLint declaradas pero no instaladas**: `eslint.config.js` importa
  `angular-eslint`/`typescript-eslint`/`@eslint/js`, ausentes de devDependencies (lint sólo
  advisory best-effort).
- Añadir `@vitest/coverage-v8` (paquete OSS, coste 0 €) es la vía para medir cobertura;
  cambia `package.json`/`package-lock.json`, a verificar contra `npm ci` + `ng test` antes de
  pushear (ver `code-quality-assessment.md` y las reglas del proyecto).

## Infraestructura y Despliegue

- **Base de datos**: Neon PostgreSQL (Frankfurt, tier free) como modo productivo; fallback
  SQLite/Turso. Selección vía `DATABASE_URL` / `DATABASE_TYPE`.
- **Hosting**: Fly.io (región `cdg`), dos apps — `futmondo-api` (puerto 8000, check
  `/health`) y `futmondo-app` (nginx, puerto 80). Ambas `min=max=1`, `shared-cpu-1x`/256 MB.
- **CI/CD**: GitHub Actions (`ci.yml`, `fly-deploy.yml`, `daily-sync.yml`,
  `sofascore-sync.yml`); detalle en `code-quality-assessment.md`.
- **Build**: backend pip + `Dockerfile`/`nixpacks.toml`; frontend npm (`npm@11.12.1`) +
  Angular CLI (`@angular/build`).
- **Restricción dura**: todo en tiers gratuitos (Neon free, Fly.io free allowance, GitHub
  Actions free) — coste 0 €.
