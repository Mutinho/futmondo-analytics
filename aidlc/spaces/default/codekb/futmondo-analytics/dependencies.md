# Dependencias — Futmondo Analytics

## Dependencias externas (servicios)

- **Neon PostgreSQL** — almacén de datos de producción (`DATABASE_URL`).
- **API Futmondo** — fuente de verdad del juego (credenciales por usuario).
- **API Sofascore** — ratings (vía `curl_cffi`).
- **Gemini / Groq** — asistente conversacional.
- **Fly.io** — hosting de las dos apps y crons.
- **GitHub Actions** — CI/CD.

> Versiones de librerías en `technology-stack.md`.

## Dependencias externas muertas / residuo (FR14)

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

## Riesgo de acoplamiento relevante al intent

Retirar la rama SQLite/Turso toca `config.py` (cascada) y `db_connection.py`
(`_init_turso`/`_init_sqlite`/`_TursoCursorWrapper` + ramas en
`get_connection`/`adapt_sql`/`adapt_params`/`get_last_insert_id`/`sync`). Los
consumidores de `db_connection` (vía `services`/`stores`) dependen del contrato
del cursor; **characterization-first** antes de tocarlo. Detalle en
`code-quality-assessment.md`.
