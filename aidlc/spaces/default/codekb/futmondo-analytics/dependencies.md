# Dependencias — Futmondo Analytics

## Dependencias externas (servicios)

- **Neon PostgreSQL** — almacén de datos de producción (`DATABASE_URL`).
- **API Futmondo** — fuente de verdad del juego (credenciales por usuario).
- **API Sofascore** — ratings (vía `curl_cffi`).
- **Gemini / Groq** — asistente conversacional (`assistant_service.py`).
- **Fly.io** — hosting de las dos apps y crons.
- **GitHub Actions** — CI/CD.

> Versiones de librerías en `technology-stack.md`.

## Dependencias externas muertas / residuo (FR14, preservado)

- **Turso / libsql** (`libsql-experimental==0.0.55`) — cliente de la rama de BD
  muerta; sin uso en el flujo Neon; no lo ejercitan los tests (fake SQLite).
- **Railway/Nixpacks** (`nixpacks.toml`) — pipeline de deploy huérfano.

## Dependencias internas cross-paquete

```
api/v1/endpoints → services → db_connection → Neon
                 → auth      → stores → security
services → core (config/constants)
services → futmondo_client / sofascore_client / assistant_service (integraciones)
scripts → services, core
angular-app → API interna (/api/v1/*, /auth/*)
```

- `api/v1/endpoints` depende de `services` y `auth`.
- `services` depende de `core` (config/constants) y encapsula el acceso a BD
  (`db_connection`) e integraciones.
- `auth` depende de `stores` y `security`.
- `stores` depende de `db_connection` (rama PostgreSQL en producción).
- `scripts` dependen de `services`/`core` (incluidas las migraciones Turso
  muertas).
- El **frontend** depende del contrato REST del backend, incluido el doble
  prefijo `matchdays` (FR15).

## Acoplamiento interno relevante al intent (FR13 — god files)

- **Hub estrella `DataManagerV2`**: `data_sync_service` y `analytics_service`
  dependen de él vía `self.dm`, y 8 routers lo consumen directo. Extraerlo sin
  romper esos consumidores es la **restricción dura** — la fachada pública debe
  preservarse.
- **`assistant_service`** depende de `db_connection` directo (SQL inline en
  `_ctx_*`) además de Gemini/Groq.
- **Config module-level como dependencia oculta**: `data_sync_service` importa
  `CHAMPIONSHIP_ID`/`LEAGUE_ID`/`FUTMONDO_EMAIL/PASSWORD` de `app.core.config`;
  `assistant_service` importa `GEMINI_API_KEY`/`GROQ_API_KEY`;
  `_resolve_real_team_name` importa `LALIGA_TEAM_NAMES` de `constants`.
- **Precedente**: `sync_prizes` → paquete `prizes/` (dependencia ya
  desacoplada a módulo estrecho) — patrón a replicar. Detalle en
  `code-structure.md` y `code-quality-assessment.md`.

## Riesgo de acoplamiento previo (FR14, preservado — no re-verificado en este run)

Retirar la rama SQLite/Turso toca `config.py` (cascada) y `db_connection.py`
(`_init_turso`/`_init_sqlite`/`_TursoCursorWrapper` + ramas). Los consumidores
de `db_connection` dependen del contrato del cursor; characterization-first
antes de tocarlo. Detalle en `code-quality-assessment.md`.
