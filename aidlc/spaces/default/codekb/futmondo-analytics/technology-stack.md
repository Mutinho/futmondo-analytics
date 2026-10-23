# Technology Stack — Futmondo Analytics

> Refresco enfocado en latencia; stack sin cambios respecto al store previo.

| Capa | Tecnología | Versión / notas |
|---|---|---|
| Frontend | Angular + Material, signals, standalone, PWA | Angular 22 / Material 22 |
| Backend | FastAPI, Python | Python 3.12 (`ruff.toml` `py312`) |
| Auth | JWT (PyJWT, HS256) | access en memoria + refresh en cookie `HttpOnly` |
| Base de datos | Neon PostgreSQL (serverless, Frankfurt) | vía `DATABASE_URL`, `psycopg2` `ThreadedConnectionPool` (5-20) |
| Integración Futmondo | `requests` (`FutmondoClient`) | `_make_request` timeout 15 s, errores tipados |
| Integración Sofascore | `curl_cffi` (`SofascoreClient`) | ratings → `sofascore_cache` |
| Deploy | Fly.io (París, región `cdg`), GitHub Actions CI/CD | 2 apps: `futmondo-api` (8000), `futmondo-app` (nginx) |
| Lint/format | `ruff` (`select E,F,I`, line 100), ESLint (advisory), Prettier | `ruff check` bloqueante en ambos gates |
| Test | `pytest` + `pytest-cov` (backend, fakes in-memory `conftest.py`); Vitest `ng test` (frontend) | gate de CI bloqueante |

## Relevancia a la latencia

El coste dominante de `/market/today` y `/favorites/my` está en las llamadas
HTTP en vivo vía `requests`/`FutmondoClient` (timeout 15 s por llamada), no en
la capa `psycopg2`/Neon (reads agregados y pool reutilizado). Ninguna
dependencia de caché/TTL adicional está instalada (coste 0 €: cualquier mejora
usa stdlib o el camino read-from-sync ya existente).
