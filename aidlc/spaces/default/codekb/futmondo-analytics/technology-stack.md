# Technology Stack — Futmondo Analytics

> Merge CURRENT; stack **sin cambios** respecto al store previo. El intent
> `261023-sync-jugador-completo` es un refactor/enriquecimiento del sync de
> jugadores: no introduce dependencias nuevas (stdlib + capa DDD existente).

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

## Relevancia al intent (sync completo de jugadores)

- La persistencia usa `psycopg2` (Postgres/Neon) y la rama SQLite en los
  adapters (`db.db_type`), con UPSERT batch (`execute_values` / `executemany`).
  Cualquier columna nueva debe respetar ambas ramas y la DDL de
  `schema_lifecycle`.
- La ingesta usa `requests` vía `FutmondoClient` (timeout 15 s, errores
  tipados). Si el enriquecimiento exige una llamada por jugador
  (`/1/player/summary` o `/1/player/fullprofile`), el coste HTTP del sync crece
  linealmente — a evaluar en Functional Design (coste 0 €, sin tooling de pago).
- No se instalan dependencias nuevas: el patrón DDD (puerto + adapter +
  servicio) y la capa `sync_read` ya existen.
