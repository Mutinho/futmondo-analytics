# Rollback Runbook — calculadora-mejora

## Triggers de rollback

- Smoke test `/health` falla tras el deploy (no HTTP 200 en 5 reintentos).
- Regresión funcional observada en la Calculadora (p. ej. el saldo futuro
  calcula mal, la lista no se reconstruye, error de render) tras el release.

## Procedimiento (Fly.io, frontend-only)

1. Identificar la release anterior sana del frontend:
   ```bash
   fly releases --app futmondo-app
   ```
2. Revertir al release anterior:
   ```bash
   fly releases rollback --app futmondo-app
   ```
   (o `fly deploy` del commit anterior si se prefiere redeploy explícito).
3. Verificar: `fly status --app futmondo-app` y comprobar `/` (frontend) y
   `/health` (vía backend) responden.

## Datos / migraciones

- **Nada que revertir**: el cambio no toca backend, esquema ni datos. El estado
  del toggle vive en `localStorage` del navegador de cada usuario; un rollback
  del bundle simplemente deja de leer/escribir la clave `futmondo_calc_include_onsale`
  (los navegadores que la tengan guardada no sufren error: el código revertido
  la ignora).

## Post-rollback

- Registrar causa raíz; si fue regresión funcional, añadir el caso al spec de
  `calculator.component.spec.ts` antes de re-desplegar (práctica: todo defecto
  tiene su test).

## Referencias

- `docs/ROLLBACK.md` (runbook general del proyecto).
- Mecanismo Fly.io: redeploy de la release anterior.

## Sources

- `team.md` → `## Deployment` (rollback por redeploy); `docs/ROLLBACK.md`.

## Assumptions & Open Questions

None.
