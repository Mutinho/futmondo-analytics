# CD Config — F1: Login nativo end-to-end

> Fase: operación (deployment-pipeline). Perspectiva de release engineer. Idioma: castellano;
> identificadores, rutas y claves YAML verbatim en inglés. F1 **no introduce** pipelines nuevos:
> reutiliza el CD on-merge a Fly.io ya operativo para el ajuste de backend (D-01) y documenta el
> flujo de distribución de la app iOS por firma gratuita con `xtool`. Coste 0 € salvo la excepción
> acotada de publicación nativa (diferida en F1).

## Dos canales de despliegue en F1

F1 tiene dos entregables con rutas de despliegue distintas:

| Entregable | Canal de despliegue | Estado en F1 |
|------------|---------------------|--------------|
| Ajuste de backend (D-01: transporte del refresh token) | CD automático on-merge a Fly.io (`fly-deploy.yml`) | **Aplica** — ya desplegado a `futmondo-api` |
| App nativa iOS (`ios/`, `FutmondoApp`) | Instalación manual por firma gratuita con `xtool` desde WSL | **Aplica (manual)** — sin publicación en App Store (B-09 diferido) |

## Canal 1 — Backend D-01: CD automático a Fly.io (reutilizado, sin cambios)

Fuente de verdad: `.github/workflows/fly-deploy.yml` (disparo `push` → `main`). F1 **no modifica**
este workflow. Cadena existente:

```
verify → deploy-backend → deploy-frontend → smoke-test
```

- **`verify`**: replica el gate bloqueante del PR (gitleaks + pip-audit + `ruff check` + `pytest`
  con cobertura y piso + `npm audit` + `ng test`). Incluye los 8 tests nuevos de
  `test_auth_refresh_transport.py`. Un rojo nunca llega a producción (regla durable).
- **`deploy-backend`**: `flyctl deploy` en `./backend` → app `futmondo-api` (región `cdg`, puerto
  8000). `needs: verify`.
- **`deploy-frontend`**: `flyctl deploy` en `./angular-app` → app `futmondo-app` (nginx). F1 no
  cambia el frontend, pero el workflow lo redespliega igualmente por su `needs:` encadenado.
- **`smoke-test`**: `curl` contra `/health` (5 reintentos, HTTP 200) como verificación de release.

Secretos: `FLY_API_TOKEN` vía GitHub Actions secrets; `JWT_SECRET` no-default en producción (nunca
en claro). D-01 es aditivo y no añade secretos nuevos.

## Canal 2 — App iOS: instalación por firma gratuita con `xtool` (manual)

No hay CD de la app nativa en F1 (coste 0 € + alcance). El despliegue al dispositivo lo ejecuta el
propietario con `ios/scripts/install-app.sh` desde WSL:

1. Pone `xtool` (AppImage) y la toolchain Swift 6.4.0 en PATH.
2. Resuelve el relay de `usbmuxd` (gateway WSL `:27015`) y verifica que el iPhone es visible.
3. `xtool dev run` desde `ios/`: build → sign → package → install → launch (product `FutmondoApp`,
   bundleID `com.futmondo.app`).
4. Primer arranque tras (re)firmar: confiar el perfil en Ajustes del iPhone.

Objetivo de despliegue: **iPhone 13 Pro** del propietario. Backend prod apuntado desde la app:
`https://futmondo-api.fly.dev` (hardcoded en `FutmondoApp.swift`).

**Validez de la firma gratuita: ~7 días** (limitación de Apple free-signing). Re-desplegar = volver
a ejecutar el script. La publicación en App Store (Apple Developer Program ~99 €/año) es la
**excepción acotada** de coste y queda **diferida (B-09)**, fuera de alcance de F1.

## Artefactos de infraestructura consumidos — no disponibles (documentado)

La etapa declara consumir `infrastructure-specification.md` y `cicd-pipeline.md` por unidad de
construcción. En F1 la etapa **infrastructure-design se reportó `skipped`** en los 3 bolts (sin
infraestructura nueva: D-01 es aditivo sobre apps Fly.io ya existentes y la app iOS no provisiona
nada). Por tanto esos artefactos **no existen** y no se inventan (regla: diseñar solo contra
evidencia que existe). La topología real se toma de `fly-deploy.yml`, `team.md` → `## Deployment` y
`aidlc-shared/operation-fly-stack.md`.

## Mapeo de adaptación (AWS → gratuito), específico de este CD

| Herramienta AWS del stage | Equivalente gratuito en este stack | Estado |
|---|---|---|
| CodePipeline / CodeDeploy | GitHub Actions `fly-deploy.yml` on-merge | Aplica |
| Promoción dev → staging → prod | Entorno único prod; sin staging; smoke `/health` es la verificación | Sustituido |
| Aprobación manual de producción | Gate de CI bloqueante + revisión de PR (single-maintainer) | Sustituido |
| Feature flags (AppConfig / Evidently) | No se usan en F1; D-01 es aditivo y la precedencia cookie→header→body hace el cambio retrocompatible sin flag | NO-APLICA |
| Registry de artefactos gestionado | Registry de Fly.io para la imagen backend; la app iOS no publica artefacto (firma local) | Aplica (parcial) |

## Sources

- [consumes] ci-config.md, quality-gates.md (construction/ci-pipeline).
- [consumes] infrastructure-specification.md, cicd-pipeline.md — NO existen (infrastructure-design
  reportada `skipped` en los 3 bolts); no se inventan.
- [code] `.github/workflows/fly-deploy.yml`, `ios/scripts/install-app.sh`, `docs/ROLLBACK.md`.
- [memory] team.md `## Deployment`; aidlc-shared/operation-fly-stack.md; project.md (coste 0 € +
  excepción acotada de publicación nativa).

## Assumptions & Open Questions

None.
