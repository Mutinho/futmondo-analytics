# Rollback Runbook — Enriquecimiento del sync de jugadores

Se apoya en el runbook existente `docs/ROLLBACK.md` (redeploy de la release
Fly.io anterior). Este documento añade las particularidades de ESTE cambio.

## Cuándo revertir

- `favorites/my` devuelve errores tras el deploy, o el sync de jugadores falla
  por el nuevo mapeo.

## Procedimiento

1. **Código:** redeploy de la release Fly.io anterior de `futmondo-api`
   (mecanismo estándar del runbook). El pipeline no cambia.
2. **Esquema:** **no hace falta revertir.** La migración fue aditiva y no
   destructiva; las 6 columnas extra en `players` son ignoradas por el código
   anterior (no las referencia). Dejarlas no causa ningún problema.
3. **Datos:** sin rollback de datos. El sync anterior simplemente no rellenaba
   esas columnas; quedarán con su default hasta que vuelva a desplegarse el
   código nuevo.

## Reversión opcional del esquema (NO recomendada / innecesaria)

Solo si por política se quisiera dejar `players` exactamente como antes:

```sql
ALTER TABLE players DROP COLUMN IF EXISTS points;
ALTER TABLE players DROP COLUMN IF EXISTS change;
ALTER TABLE players DROP COLUMN IF EXISTS home_average;
ALTER TABLE players DROP COLUMN IF EXISTS away_average;
ALTER TABLE players DROP COLUMN IF EXISTS matches;
ALTER TABLE players DROP COLUMN IF EXISTS status;
```

`DROP COLUMN` SÍ es destructivo (pierde los valores poblados); no es necesario
para un rollback de código y no se recomienda.

## Verificación post-rollback

- `smoke-test` `/health`; `favorites/my` responde con el contrato previo.
