# Deployment Execution Log — refactor DDD del asistente

Intent `260929-assistant-god-file`, scope `refactor` (Minimal), fase Operation. Registra el plan de
ejecución del despliegue y su estado. **El sistema ya está en producción**; este refactor no cambia
el comportamiento observable ni el artefacto desplegado.

## Estado del despliegue

- **Verificación local (pre-merge)**: COMPLETA y en verde. Suite 244 passed / 3 xfailed
  (preexistentes), cobertura 33.82% ≥ piso 27, `ruff check` del paquete nuevo limpio, import
  histórico del endpoint OK. Ver `construction/build-and-test/test-results.md`.
- **Despliegue a producción**: **PENDIENTE del merge a `main`**. La ejecución real la realiza el
  pipeline `.github/workflows/fly-deploy.yml` on-merge; **no la ejecuta el agente** (desplegar a un
  sistema en vivo es una acción de alto impacto que corresponde al merge del usuario). El código
  refactorizado y los artefactos AI-DLC están en el árbol de trabajo sin fusionar.

## Plan de ejecución (on-merge a `main`)

Cuando el usuario abra el PR y fusione a `main`, el pipeline ejecuta la cadena `needs:` intacta:

1. **`verify`** (gate bloqueante): gitleaks → allowlist expiry → pip-audit (entorno instalado) →
   `ruff check .` → `pytest --cov=app` con piso → npm audit (high) → `ng test`. Un rojo aborta el
   despliegue (los deploy dependen de `verify`).
2. **`deploy-backend`**: `flyctl deploy` de `futmondo-api` (el backend con el paquete DDD nuevo).
3. **`deploy-frontend`**: `flyctl deploy` de `futmondo-app` (nginx; sin cambios en este intent).
4. **`smoke-test`**: `curl` a `/health`, 5 reintentos, HTTP 200 — verificación de release.

## Migraciones de BD

- **Ninguna**. El refactor no toca esquema (OOS5); el `CREATE TABLE IF NOT EXISTS` idempotente se
  preserva en el adaptador. No hay paso de migración que ejecutar. (El soporte del desarrollador
  para ejecución de migraciones no se invoca: no aplica.)

## Pasos manuales para el usuario (fuera del agente)

1. Revisar los 32+ cambios sin commitear bajo el workspace (paquete `assistant/`, tests, shim, y el
   árbol `aidlc/`), commitear con Conventional Commits en castellano (p. ej.
   `refactor(backend): descompone assistant_service en paquete DDD`).
2. Abrir MR a `main`; el gate de CI (`ci.yml`) debe pasar (required status check).
3. Fusionar (squash-merge). El pipeline `fly-deploy.yml` despliega y ejecuta el smoke test.
4. Verificar `/health` 200 post-deploy; ante fallo, seguir `rollback-runbook.md`.

## NO-APLICA (equivalentes AWS de pago)

- CodeDeploy canary/blue-green, CloudWatch alarms de deploy, rollback automático por métricas:
  sustituidos por recreate/rolling de Fly.io + smoke `/health` + rollback manual (coste 0 €).
