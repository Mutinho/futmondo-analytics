# Deployment Strategy — recreate on-merge con verificación por healthcheck

Intent: `sync-god-file` · scope `refactor` · Operation. Refleja el comportamiento
real del pipeline; el refactor no lo cambia.

## Estrategia

**Recreate on-merge a `main`** hacia Fly.io, sin entorno de staging separado. Cada
merge a `main` (o push directo, que replica el gate en `verify`) despliega la
release. No es blue/green ni canary: Fly.io recrea las máquinas de cada app con la
imagen nueva; la **verificación de release** es el smoke test `/health`.

- **Orden de despliegue** (cadena `needs:` intacta): `verify` → `deploy-backend`
  → `deploy-frontend` → `smoke-test`. Backend primero para que el frontend (nginx
  proxy) apunte a un backend ya desplegado.
- **Sin blue/green/canary**: no hay staging ni doble entorno (coste 0 €). El
  healthcheck `/health` sustituye al análisis de métricas de canary.

## Criterios de verificación y aborto

- **Gate pre-deploy (bloqueante)**: `verify` debe pasar (gitleaks + pip-audit +
  ruff + pytest con cobertura y piso + npm audit + ng test). Un rojo aborta la
  cadena antes de cualquier deploy — **un rojo nunca llega a producción**.
- **Verificación post-deploy (smoke test)**: `curl` a `/health`, 5 reintentos con
  10 s de espera, éxito en HTTP 200 y `{"status":"healthy"}`. Un smoke test
  fallido marca el release en rojo y es el **trigger de rollback** (ver
  `rollback-runbook.md`).
- **Criterio de aborto**: `verify` rojo → no se despliega. Smoke test rojo tras el
  deploy → rollback manual a la release anterior.

## Migraciones de esquema

- Este refactor **no cambia el esquema** de Neon (equivalencia estricta,
  out-of-scope de cambios de BD). No hay paso de migración en el pipeline para
  este intent. Si un intent futuro tocara el esquema, aplicaría el patrón
  expand-contract (cambios backward-compatible primero), fuera de alcance aquí.

## Rollback (resumen; detalle en `rollback-runbook.md`)

- Mecanismo Fly.io: `fly releases rollback <vN>` (o redeploy explícito de la
  imagen previa). Documentado en `docs/ROLLBACK.md` y resumido en el runbook de
  esta etapa. Cada endurecimiento del gate va en commit aislado para rollback
  quirúrgico.

## Adaptación al stack real

- Blue/green gestionado, canary con CloudWatch alarms y feature flags de pago:
  **NO-APLICA** en este stack (coste 0 €, sin staging). La alternativa gratuita es
  recreate + healthcheck `/health` + gate bloqueante, ya operativa.
- SLO formal con burn-rate: diferido (de pago); el SLI informal es `/health` 200 +
  ausencia de pasos `degraded` inesperados en `fly logs`.
