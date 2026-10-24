# Deployment Strategy — Enriquecimiento del sync de jugadores

## Estrategia

- **Deploy-on-merge** a `main` → Fly.io, sin entorno de staging separado (línea
  base del equipo). El redeploy de Fly.io es **rolling con healthcheck**
  (`/health`); no se introduce blue/green ni canary (no aplican al tier free y
  no hay necesidad para un cambio backend acotado).
- **Orden crítico (migración antes que código):** la migración de esquema se
  aplicó **manualmente a Neon ANTES** del deploy del código. Esto evita la
  ventana en la que el código nuevo consultaría columnas inexistentes. Como las
  columnas ya están, el `deploy-backend` es seguro en cualquier momento.

## Compatibilidad hacia atrás

- El `ALTER` es **aditivo y no destructivo**: el código ANTERIOR (en producción
  ahora) ignora las columnas nuevas; el código NUEVO las lee. Por tanto:
  - Desplegar el código nuevo con las columnas ya presentes → correcto.
  - Si hubiera que revertir el código → el esquema con columnas extra no rompe
    el código viejo (no las referencia). Sin rollback de esquema necesario.

## Población de datos tras el deploy

- Las columnas arrancan con su default (`0`/`NULL`/`''`). Se completan en el
  **primer sync de jugadores** (periódico y bajo demanda), que ya extrae los 6
  campos. `favorites/my` degrada con los defaults hasta entonces (por diseño,
  BR5.2) — sin "null" crudos en el front.
- **Opcional (acelerar):** lanzar un sync manual tras el deploy para poblar de
  inmediato. No es bloqueante.

## Verificación post-deploy

- `smoke-test` del pipeline (`/health`).
- Manual: `GET /api/v1/favorites/my?championship_id=<id>` con token válido tras
  un sync → los favoritos muestran points/change/team/logo/medias reales.
