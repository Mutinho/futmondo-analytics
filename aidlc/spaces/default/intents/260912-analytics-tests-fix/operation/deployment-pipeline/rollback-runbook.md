# Runbook de Rollback — Arreglo de tests de AnalyticsService

> Basado en el procedimiento existente `docs/ROLLBACK.md`. Este cambio es de muy
> bajo riesgo (solo un fichero de test), por lo que el rollback es directo.

## Disparadores de rollback
- `verify` falla tras el merge (no debería: la suite está en verde localmente).
- Smoke `/health` falla post-deploy.
- Regresión funcional detectada tras el despliegue.

## Procedimiento (pasos para revertir)
1. **Revert del commit** del arreglo en `main`:
   ```bash
   git revert <sha-del-merge> && git push origin main
   ```
   Esto vuelve a disparar `fly-deploy.yml` con el estado anterior.
2. **Alternativa directa (Fly)**: re-desplegar la release anterior:
   ```bash
   fly releases --app futmondo-api        # localizar release previa
   fly deploy --app futmondo-api --image <imagen-release-anterior>
   ```
   (Análogo para `futmondo-app` si aplica.) Ver `docs/ROLLBACK.md`.
3. **Verificar** `/health` tras el rollback.

## Notas
- Como el cambio no toca la BD ni el runtime, no hay rollback de datos ni de
  esquema. El revert del test es suficiente y seguro.
- Sin coste adicional (mismo pipeline y máquinas Fly existentes).

## Post-rollback
- Registrar causa raíz y, si procede, abrir un intent de seguimiento.
