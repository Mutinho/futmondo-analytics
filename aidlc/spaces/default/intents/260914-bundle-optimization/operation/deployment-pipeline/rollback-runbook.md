# Rollback Runbook — Optimización del bundle inicial

> Stage 4.1 Deployment Pipeline · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield (fase Operation).
> Complementa `docs/ROLLBACK.md` (runbook general del proyecto) con las particularidades de este refactor.

## Sources

- `docs/ROLLBACK.md` — procedimiento general de rollback en Fly.io.
- `.github/workflows/fly-deploy.yml` — smoke test post-deploy.

## Cuándo revertir este refactor

- El build de producción del frontend falla en el deploy (p. ej. el bundle supera 1 MB por un efecto no previsto) → el deploy se detiene solo (fail-closed); no llega a producción, no hace falta rollback, solo corregir y re-desplegar.
- Tras el deploy: un gráfico (`evolution`/`stats`) no renderiza, o el chat del asistente no abre/renderiza Markdown (regresión funcional de la carga diferida).
- La navegación entre rutas lazy se rompe (efecto de la nueva estrategia de precarga).

## Procedimiento de rollback

Al ser un cambio de **solo código frontend** (sin migración de datos ni de esquema), el rollback es limpio: revertir al release anterior de la app `futmondo-app`.

### 1. Identificar la release previa

```bash
fly releases --app futmondo-app
```

Anota la versión (`vN`) anterior al deploy de este refactor.

### 2. Revertir

```bash
fly releases rollback <vN> --app futmondo-app
```

(El backend `futmondo-api` NO cambia con este refactor; no necesita rollback.)

### 3. Verificar tras el rollback

- `curl -sS https://futmondo-app.fly.dev/` responde 200 (nginx sirve la SPA).
- Verificación manual: gráficos y chat vuelven a funcionar como antes.

### 4. Alternativa (revertir el merge)

Si se prefiere revertir en el código: abrir un PR que revierta el commit del refactor (nunca push directo a `main`), dejar pasar el gate de CI, y mergear. El deploy automático restaura el estado previo.

## Limitaciones conocidas

- El estado en memoria (sesiones de sync en curso) se pierde en cada redeploy/rollback (limitación aceptada del modelo de un único entorno; ver `docs/ROLLBACK.md`).
- No hay staging: la verificación es el smoke test `/health` más la comprobación manual de gráficos y chat.

## Post-rollback

- Diagnosticar la causa (referencia rota por `@defer`, registro de charts, o la estrategia de precarga), corregir en un PR con el gate de CI verde, y re-desplegar.
