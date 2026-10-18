# Technology Stack — Futmondo Analytics

Versiones tomadas de `backend/requirements.txt`, `angular-app/package.json`,
`backend/ruff.toml`, `backend/pytest.ini`, `.github/workflows/*.yml` y `.nvmrc`.

## Backend

| Área | Tecnología | Versión | Fuente |
|---|---|---|---|
| Lenguaje/runtime | Python | 3.12 | `pytest.ini`/CI `setup-python 3.12`, `ruff.toml` `target-version=py312` |
| Framework web | FastAPI | 0.141.1 | `requirements.txt` |
| ASGI server | uvicorn[standard] | 0.54.0 | `requirements.txt` |
| Validación | pydantic | 2.13.5 | `requirements.txt` |
| JWT | PyJWT | 2.15.0 | `requirements.txt` (HS256, `jwt_utils.py`) |
| HTTP client (Futmondo) | requests | 2.34.2 | `requirements.txt`, `futmondo_client.py` |
| HTTP client (Sofascore) | curl_cffi | 0.16.3 | `requirements.txt` |
| Driver DB | psycopg2-binary | 2.9.13 | `requirements.txt` |
| Multipart | python-multipart | 0.0.32 | `requirements.txt` |
| Env | python-dotenv | 1.2.3 | `requirements.txt`, `config.py` |
| AI (asistente) | google-genai / groq | 1.14.0 / 0.25.0 | `requirements.txt` |
| Tests | pytest / pytest-cov / httpx | 9.1.1 / 7.1.0 / 0.28.1 | `requirements.txt`, `pytest.ini` |
| Lint/format | ruff | 0.16.9 (pin en CI) | `ci.yml`/`fly-deploy.yml` (`pip install ruff==0.16.9`), `ruff.toml` |
| Dep audit | pip-audit | 2.10.1 (pin en CI) | `ci.yml`/`fly-deploy.yml` |

## Base de datos

| Área | Tecnología | Detalle | Fuente |
|---|---|---|---|
| Producción | Neon PostgreSQL (serverless) | Frankfurt, tier free; único engine soportado vía `DATABASE_URL` | `README.md`, `config.py`, `db_connection.py` |
| Local/tests | SQLite | ruta `db.db_type` para tests/local; fixtures fake in-memory | `db_connection.py`, `conftest.py` |

## Frontend

| Área | Tecnología | Versión | Fuente |
|---|---|---|---|
| Framework | Angular | ^22.2.1 (core/common/forms/router/...) | `package.json` |
| UI | Angular Material + CDK | ^22.2.1 | `package.json` |
| Build system | @angular/build + @angular/cli | ^22.2.0 | `package.json`, `angular.json` |
| Reactividad | RxJS | ~7.8.0 (+ Angular signals) | `package.json`, `auth.service.ts` |
| Charts | chart.js / ng2-charts | ^4.5.1 / ^10.0.0 | `package.json` |
| Markdown | marked | ^18.0.11 | `package.json` |
| Test runner | Vitest (builder `@angular/build:unit-test`, `runner: vitest`) | 4.1.11 | `package.json`, `angular.json` |
| Coverage | @vitest/coverage-v8 | 4.1.11 (pin exacto) | `package.json` |
| DOM test | jsdom | ^25.0.1 | `package.json` |
| Formato | prettier | ^3.8.1 | `package.json`, `.prettierrc` |
| Lint | ESLint (flat config, advisory/diferido) | — | `eslint.config.js`, `ci.yml` (advisory) |
| TypeScript | typescript | ~6.0.2 | `package.json` |
| Node (local) | Node | 22.22.3 (`.nvmrc`); CI usa `node-version: '22'` | `.nvmrc`, CI |
| Lenguaje de UI | PWA (service worker + manifest) | `@angular/service-worker` ^22.2.1 | `package.json`, `ngsw-config.json` |

## Infraestructura y CI/CD

| Área | Tecnología | Detalle | Fuente |
|---|---|---|---|
| Hosting | Fly.io | Apps `futmondo-api` + `futmondo-app` (nginx) | `README.md`, `fly-deploy.yml`, `fly.toml` |
| Reverse proxy | nginx | SPA + proxy `/api/*` y `/auth/*` | `nginx.prod.conf`, `README.md` |
| CI | GitHub Actions | `ci.yml` (PR→main), `fly-deploy.yml` (push→main) | `.github/workflows/` |
| Secret scan | gitleaks (action `@v3`, unificado ambos gates) | bloqueante | `ci.yml`, `fly-deploy.yml` |
| Orquestación local | docker-compose | `docker-compose.yml` | repo root |

## Relevancia para F1 (login nativo iOS)

El cliente nativo F1 es **Swift/SwiftUI** (nueva superficie, aún no en el repo) y
reutiliza este backend. No introduce coste ni dependencias de pago salvo la
excepción acotada de publicación de distribución nativa (Apple Developer
Program), documentada como excepción al mandato de coste 0 € en `team.md`. El
almacén seguro nativo previsto para el refresh token es iOS Keychain
(`@nativescript/secure-storage` se cita en reglas para una vía NativeScript; para
Swift nativo el equivalente es Keychain directo). PyJWT/HS256 del backend se
reutiliza sin cambios de criptografía.

## Sources

- `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`
- `angular-app/package.json`, `angular-app/angular.json`
- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`
- `.nvmrc`, `README.md`, `backend/app/core/config.py`, `backend/app/services/db_connection.py`

## Assumptions & Open Questions

- La versión exacta de nginx no está pineada en los ficheros leídos (viene de la
  imagen base del `Dockerfile`, no abierto línea a línea). El runner Swift/toolchain
  iOS de F1 no está en el repo todavía (hay un spike en `spikes/ios-xtool/`), así
  que su versión no se afirma aquí.
