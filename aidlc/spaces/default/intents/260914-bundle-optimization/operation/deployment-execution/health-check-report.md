# Health Check Report — Optimización del bundle inicial

> Stage 4.3 Deployment Execution · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield (fase Operation).

## Sources

- `angular-app/fly.toml` (health check config), `.github/workflows/fly-deploy.yml`.

## Health checks configurados (existentes, sin cambios)

| Componente | Check | Config |
|---|---|---|
| Frontend (`futmondo-app`) | HTTP `/` cada 30s (nginx sirve la SPA) | `angular-app/fly.toml` → `[checks.health]` |
| Backend (`futmondo-api`) | `/health` (smoke test post-deploy) | `fly-deploy.yml` job `smoke-test` |

Este refactor NO modifica los health checks: sigue sirviéndose la misma SPA por nginx en el frontend y el backend no cambia.

## Impacto del refactor en la salud del servicio

- **Positivo**: chunk inicial más pequeño (819 kB vs. techo previo 1.2 MB) → arranque más ligero, menor transferencia inicial.
- **Precarga diferida** (NFR4): los chunks lazy se precargan tras inactividad, reduciendo el pico de red posterior al arranque sin afectar a la disponibilidad.
- **Sin nuevos endpoints ni servicios**: no hay nuevas métricas de salud que definir.

## Validación tras el despliegue (a cargo del usuario)

1. `curl -sS https://futmondo-app.fly.dev/` → HTTP 200 (SPA servida).
2. `curl -sS https://futmondo-api.fly.dev/health` → HTTP 200 (backend sano, sin cambios).
3. Verificación funcional manual: gráficos y chat operativos (BR5.1).

## Estado

- Config de health checks: sin cambios, operativa.
- Validación en vivo: **PASADA**. La máquina del frontend (`1850356b030438`) pasó los machine/health checks del deploy y alcanzó `good state`; DNS verificado. App servida en https://futmondo-app.fly.dev/
- Pendiente (solo verificación funcional manual del usuario): confirmar que gráficos (`evolution`, `stats`) y el chat del asistente funcionan en la app desplegada (BR5.1/FR1.3/FR2.3).
