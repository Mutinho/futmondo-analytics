# Dependencias — Futmondo Analytics

> Reverse-engineering. Escaneo previo FULL preservado; rerun FOCUSED sobre
> `backend/app/services/` y `backend/tests/`. Dependencias externas (paquetes y
> servicios de terceros) y dependencias internas cross-package.

## Dependencias externas — servicios de terceros

| Servicio | Uso | Componente que depende | Riesgo |
|----------|-----|------------------------|--------|
| API Futmondo (oficial) | Autenticación y datos del campeonato | `integration clients` (`futmondo_client`), `auth`, `cron` | Disponibilidad/rate limits; token de sesión en memoria por usuario |
| API Sofascore (no oficial) | Ratings de jugadores | `integration clients` (`sofascore_client`) | Baneo de IP (exit code 2 en `sofascore-sync.yml`); sin API key |
| Gemini (`google-genai`) | Chat del asistente | `data services` (`assistant_service`) | Cuota/coste; debe respetar tier gratuito |
| Groq (`groq`) | Fallback del asistente | `data services` (`assistant_service`) | Cuota/coste |
| Neon PostgreSQL | Persistencia productiva | `backend`, `cron`, `scripts` | Tier gratuito (regla coste 0€) |
| Fly.io | Hosting de las 3 apps | despliegue | Free allowance; `min_machines_running=1` |
| GitHub Actions | CI/CD y crons programados | pipelines | Minutos gratuitos |

## Dependencias externas — paquetes

- **Backend** (`requirements.txt`): FastAPI, uvicorn, pydantic, PyJWT,
  psycopg2-binary, curl_cffi, libsql-experimental, requests, python-dotenv,
  python-multipart, google-genai, groq, pytest, pytest-cov, httpx. Versiones en
  `technology-stack.md`.
- **Frontend** (`package.json`): Angular 22 (core/material/cdk/router/forms/
  service-worker), chart.js, ng2-charts, marked, rxjs, typescript; test con
  Karma + Jasmine.
- **Notas**: `libsql-experimental` es dependencia heredada (backend Turso ya no en
  ruta activa). No hay `pyproject.toml`/`setup.py`: las dependencias Python viven
  solo en `requirements.txt`.

## Dependencia de test (foco del rerun)

- `backend/tests/` depende de `pytest` + `monkeypatch` (no de BD real). El
  fixture `analytics_service` de `test_analytics_service.py` sustituye
  `AnalyticsService.__init__` por un `fake_init` que inyecta un `StubDM` (fake de
  `DataManager`). Acoplamiento implícito: la fixture asume que los métodos
  públicos no dependen de estado inicializado en `__init__`, lo que NO se cumple
  (`_team_cache`/`_player_cache`). Ver `code-quality-assessment.md`.

## Dependencias internas cross-package

```mermaid
graph LR
    FE["angular-app"] -->|proxy /api,/auth| BE["backend"]
    PROXY["proxy (local)"] --> BE
    PROXY --> FE
    CRON["cron"] -->|reutiliza Dockerfile| BE
    SCRIPTS["backend/scripts"] --> SVC["data services"]
    SCRIPTS --> IC["integration clients"]
    EP["api endpoints"] --> SVC
    EP --> IC
    EP --> TM["task manager"]
    EP --> AUTH["auth"]
    AUTH --> IC
    SVC --> DB[("PostgreSQL")]
    IC --> EXT["APIs externas"]
    TESTS["backend/tests"] -->|StubDM fake| SVC
```

Fallback de texto: el frontend depende del backend en runtime (proxy). El `proxy`
local depende de backend y frontend. El `cron` reutiliza la imagen del backend.
Dentro del backend: los `api endpoints` dependen de `data services`,
`integration clients`, `task manager` y `auth`; `auth` depende de
`integration clients` (validación Futmondo); `data services` depende de
`PostgreSQL`; `integration clients` de las APIs externas. Los `backend/scripts`
dependen de `data services` e `integration clients`. La suite `backend/tests`
depende de `data services` (`AnalyticsService`) mediante fakes por fixture, sin
BD real.

## Acoplamientos de riesgo

- **`data services` como hub**: los "god files" (`data_manager_v2`,
  `data_sync_service`, `analytics_service`) concentran el fan-in de endpoints y
  scripts → alto riesgo de cambio.
- **Caracterización acoplada a estado privado**: `test_analytics_service.py`
  depende de detalles de `__init__` de `AnalyticsService`; cualquier cambio en la
  inicialización de caches o en el nombre de clave de salida rompe/altera la
  suite (foco del intent).
- **`task manager` in-memory**: acoplamiento implícito al ciclo de vida del
  proceso; reinicios Fly rompen tareas en curso.
- **Build**: frontend y backend son independientes en build; el acoplamiento es
  en runtime (HTTP) y en compose (`proxy`/`frontend` dependen de `backend`
  healthy).
