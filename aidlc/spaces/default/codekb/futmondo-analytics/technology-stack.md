# Stack Tecnológico — Futmondo Analytics

> Reverse-engineering. Escaneo previo FULL preservado; rerun FOCUSED sobre
> `backend/app/services/` y `backend/tests/`. Lenguajes, frameworks y librerías
> con versiones, según `backend/requirements.txt`, `angular-app/package.json` y
> los ficheros de build leídos.

## Lenguajes y runtimes

| Lenguaje / runtime | Versión | Ubicación |
|--------------------|---------|-----------|
| Python | 3.12 (`python:3.12-slim`) | `backend/`, `cron/`, `backend/scripts/` |
| TypeScript | `~6.0.2` | `angular-app/` |
| Node/npm | `npm@11.12.1` | build frontend |

## Backend — frameworks y librerías

| Librería | Versión | Propósito |
|----------|---------|-----------|
| FastAPI | `>=0.104.0` | framework de la API |
| uvicorn[standard] | `>=0.24.0` | servidor ASGI |
| pydantic | `>=2.5.0` | modelos y validación |
| PyJWT | `==2.9.0` | firma/verificación JWT (HS256) |
| psycopg2-binary | `>=2.9.9` | PostgreSQL (`ThreadedConnectionPool` 5-20) |
| curl_cffi | `>=0.16.0` | cliente Sofascore con impersonación TLS |
| libsql-experimental | `==0.0.55` | backend Turso/libSQL (embedded replica, heredado) |
| requests | `>=2.31.0` | cliente API Futmondo |
| python-dotenv | `>=1.0.0` | carga de `.env` |
| python-multipart | `>=0.0.6` | parsing multipart |
| google-genai | `==1.14.0` | asistente IA (Gemini) |
| groq | `==0.25.0` | asistente IA (fallback Groq) |
| pytest | `>=8.0.0` | testing backend (runner de la suite de caracterización) |
| pytest-cov | `>=5.0.0` | cobertura (sin piso bloqueante) |
| httpx | `>=0.27.0` | requerido por `TestClient` |

Nota del rerun: la suite de `backend/tests/` se ejecuta con `pytest` +
`monkeypatch` desde `backend/` (`pythonpath = .` en `pytest.ini`) para que
`from app...` resuelva. En este entorno no se pudo ejecutar pytest (módulo no
instalado; regla coste 0€, scope Minimal); la ejecución real corresponde al
stage `build-and-test`.

## Frontend — frameworks y librerías

| Librería | Versión | Propósito |
|----------|---------|-----------|
| Angular (core, material, cdk, router, forms, service-worker) | `^22.1.0` | framework SPA/PWA |
| chart.js | `^4.5.1` | gráficos |
| ng2-charts | `^10.0.0` | binding Angular de Chart.js |
| marked | `^18.0.11` | render Markdown en el chat IA |
| rxjs | `~7.8.0` | programación reactiva |
| typescript | `~6.0.2` | lenguaje |
| Karma + Jasmine | (config) | testing frontend |
| @angular/build:application | Angular CLI 22 | builder |

`package.json` del frontend en versión `2.1.7`; `main.py` reporta la API en
versión `2.0.0`.

## Infraestructura y build

- **Persistencia**: Neon PostgreSQL (serverless, Frankfurt). Capa de abstracción
  con soporte adicional a SQLite y Turso/libSQL (ramas heredadas).
- **Contenedores**: Docker (`backend/Dockerfile` sobre `python:3.12-slim`),
  Docker Compose para orquestación local.
- **Despliegue**: Fly.io (`flyctl deploy` por app: `futmondo-api`,
  `futmondo-app`, `futmondo-cron`).
- **CI/CD**: GitHub Actions (4 workflows).
- **Residuos de plataforma**: `backend/nixpacks.toml` (Railway) y scripts de
  migración a Turso — heredados, ya no en la ruta activa (Neon).

## Integraciones externas

- API oficial de Futmondo (autenticación y datos del campeonato).
- API no oficial de Sofascore (ratings de jugadores).
- Gemini (`google-genai`) + Groq (`groq`) para el asistente conversacional.
