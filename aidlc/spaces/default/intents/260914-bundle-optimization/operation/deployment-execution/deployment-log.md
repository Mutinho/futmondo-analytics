# Deployment Log — Optimización del bundle inicial

> Stage 4.3 Deployment Execution · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield (fase Operation).
> Etapa final. Despliegue por deploy-on-merge; el despliegue real queda a cargo del usuario (acción de alto impacto en producción).

## Sources

- `operation/deployment-pipeline/deployment-strategy.md`, `cd-config.md`, `rollback-runbook.md`.
- `construction/build-and-test/test-results.md`.
- `.github/workflows/fly-deploy.yml`, `angular-app/fly.toml`, `angular-app/Dockerfile`.

## Estado del despliegue

**DESPLEGADO CON ÉXITO a producción (Fly.io).** El usuario hizo push + merge a `main`, y el pipeline (`fly-deploy.yml`) desplegó el frontend. Confirmado por la salida de `flyctl deploy`:

- **Build de producción en el pipeline**: `Initial total: 819.05 kB` (< 1 MB), pasa con `maximumError: 1MB`. NFR1 ✓
- **Chunks lazy verificados en el build del deploy**: `assistant-chat-component` (62.31 kB), `stats-component` (54.61 kB), `chunk-hE-eqeH-2.js` (chart.js, 208 kB) — todos fuera del chunk inicial. FR1.2/BR1.2, FR2.2/BR2.2 ✓
- **Imagen**: `registry.fly.io/futmondo-app:deployment-01M2G5K6YVY6J1V7XQT777ZXE5` (33 MB).
- **Rolling update**: máquina `1850356b030438` alcanzó estado `started`, smoke checks y health checks pasados, DNS verificado.
- **App en vivo**: https://futmondo-app.fly.dev/

El backend `futmondo-api` no cambió con este refactor.

> Nota de seguridad (backlog, fuera de scope): el build de producción usa `NODE_TLS_REJECT_UNAUTHORIZED=0` (visible en la salida del deploy). Señal ya anotada en reverse-engineering; no la introduce este refactor.

## Commit desplegado

- Rama: `fix/frontend-bundle-budget` → merge a `main`.
- Commit `8d71c88`: `refactor(frontend): bajar el bundle inicial por debajo de 1 MB` — 7 ficheros de código.
- El agente preparó el commit; el push, PR, merge y deploy los realizó el usuario (acciones de alto impacto).

## Cambios a desplegar

Solo frontend (`futmondo-app` en Fly.io), sin cambios en backend ni infraestructura:

| Fichero | Cambio |
|---|---|
| `angular-app/src/app/core/preloading/idle-preloading-strategy.ts` (+ `.spec.ts`) | Nueva estrategia de precarga con retardo |
| `angular-app/src/app/app.config.ts` | Fuera `provideCharts`/`PreloadAllModules`; entra `IdlePreloadingStrategy` |
| `angular-app/src/app/features/evolution/evolution.component.ts` | `provideCharts` a nivel de componente |
| `angular-app/src/app/features/stats/stats.component.ts` | `provideCharts` a nivel de componente |
| `angular-app/src/app/shared/components/assistant-fab.component.ts` | Chat diferido con `@defer` |
| `angular-app/angular.json` | Budget `initial` → `maximumError: 1MB`, `maximumWarning: 900kB` |

## Procedimiento de despliegue (a ejecutar por el usuario)

1. **Verificar en local/CI** (regla de proyecto C4): `npm ci` + `ng test` (o build en contenedor `node:22.22.3`). Ya verificado en Build and Test.
2. **Abrir PR** hacia `main` con los cambios del refactor. El gate `ci.yml` debe pasar (pytest + `ng test` + gitleaks bloqueantes).
3. **Merge a `main`** → `fly-deploy.yml` ejecuta: `verify` → `deploy-backend` → `deploy-frontend` (`flyctl deploy` con `ng build --configuration production`) → `smoke-test` `/health`.
4. El fail-closed del budget (`maximumError: 1MB`) protege NFR1 durante el `deploy-frontend`.

## Rollback

Ver `operation/deployment-pipeline/rollback-runbook.md`: `fly releases rollback <vN> --app futmondo-app` (solo frontend; backend no cambia). Rollback limpio (sin migración de datos).

## Verificación post-despliegue requerida

- Smoke test `/health` (automático en el pipeline).
- Verificación manual: gráficos (`evolution`, `stats`) renderizan tras carga lazy; chat del asistente abre y renderiza Markdown (BR5.1/FR1.3/FR2.3).
