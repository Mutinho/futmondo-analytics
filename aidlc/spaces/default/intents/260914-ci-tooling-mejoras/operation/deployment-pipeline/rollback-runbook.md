# Runbook de Rollback — Mejoras de CI/Tooling

> Etapa Deployment Pipeline (Operation) · Intent `260914-ci-tooling-mejoras` · Scope `refactor` · Brownfield.
> Rollback nativo de Fly.io (tier gratuito). Documenta cómo revertir tanto un despliegue como los cambios de CI/tooling de este intent.

## Triggers de rollback

- El smoke test `/health` falla tras el deploy (el job `smoke-test` termina en rojo).
- Regresión detectada en producción (errores 5xx, la app no carga).
- El gate de CI falla tras el cambio de tooling (regresión de tests o build).

## Rollback del despliegue (Fly.io, tier gratuito)

Fly.io mantiene el historial de releases. Reversión sin coste adicional:

```bash
# Listar releases (identificar el anterior estable)
fly releases --app futmondo-api      # backend
fly releases --app futmondo-app      # frontend

# Revertir al release anterior (redeploy de la imagen previa)
fly deploy --app futmondo-api --image <imagen-release-anterior>
fly deploy --app futmondo-app --image <imagen-release-anterior>

# Verificar salud tras el rollback
curl -f https://futmondo-api.fly.dev/health
```

Alternativa por máquina (si aplica): `fly machine update <machine-id> --image <imagen-anterior>`.

## Rollback de los cambios de CI/tooling de este intent (git)

Al ser trunk-based con squash-merge, cada mejora/lote es revertible por commit:

| Mejora | Reversión |
|--------|-----------|
| 1 · Actions Node 24 | Revertir el cambio `setup-node@v5`→`@v4` en `ci.yml`/`fly-deploy.yml` (reintroduce el aviso de Node 20, sin romper el deploy). |
| 4 · Karma→Vitest | `git revert` del commit de migración: restaura `runner: karma`, `karma.conf.js`, devDeps de Karma, el spec Jasmine y el paso `setup-chrome`/`--browsers=ChromeHeadless`. **Requiere `npm ci` + `ng test` local (o revisar el lock) antes de pushear** (BR4.4). |
| 5 · .nvmrc | Borrar `.nvmrc` (solo afecta al entorno local). |
| 2 · punycode | Sin acción de rollback específica: la resolución fue consecuencia de la mejora 4; revertir la 4 reintroduce la cadena `dom-serialize→ent→punycode`. |
| 3 · animaciones | Sin cambios de código (solo documentación); nada que revertir. |

## Consideraciones

- **Base de datos**: este intent no toca esquema ni datos (Neon PostgreSQL); no hay rollback de datos.
- **No hay blue/green**: el rollback es un redeploy de la release anterior; ventana breve de indisponibilidad durante el reemplazo de máquina.
- **Verificación post-rollback**: siempre confirmar `/health` (backend) y carga del frontend antes de dar el rollback por bueno.

## Post-rollback

Registrar la causa (qué mejora o deploy causó la regresión) y, si aplica, abrir corrección antes de reintentar el despliegue. Coste 0€ en todo el procedimiento.
