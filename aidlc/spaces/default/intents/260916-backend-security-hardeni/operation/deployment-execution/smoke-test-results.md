# Resultados de Smoke Test — Backend Security Hardening

> Scope `security-patch`, fase Operation. El smoke test post-deploy es la
> verificación de release (no hay staging separado). Coste 0 €.

## Definición del smoke test

Job `smoke-test` de `fly-deploy.yml`: tras `deploy-backend` y `deploy-frontend`,
hace `curl` contra el healthcheck del backend con **5 reintentos**, esperando
**HTTP 200**.

- **Endpoint**: `https://futmondo-api.fly.dev/health`
- **Respuesta esperada**: HTTP 200 con cuerpo `{"status":"healthy"}`
- **Reintentos**: 5 (cubre el arranque de la máquina Fly `min=max=1`)
- **Criterio de éxito**: al menos una respuesta 200 dentro de los reintentos.
- **Criterio de abort/fallo**: 5 reintentos sin 200 → workflow en rojo → señal
  para ejecutar el rollback manual (ver `deployment-pipeline/rollback-runbook.md`).

## Cobertura del smoke test para este release

Las cinco correcciones son de bajo riesgo de despliegue y no cambian el contrato
de arranque del servicio. El smoke test verifica que:

- El backend arranca correctamente tras el deploy (incluye el guard de
  `JWT_SECRET` no-default de NFR1.1: si faltara el secreto, el arranque fallaría
  y `/health` no daría 200 — el smoke test lo detectaría).
- La corrección de auth (FR9) no rompe el arranque ni el healthcheck.

## Ejecución

El smoke test se ejecuta automáticamente en GitHub Actions al desplegar (tras el
merge a `main`). No se ejecuta desde esta etapa de documentación; su resultado
efectivo se observa en el run del workflow de despliegue.

## Verificación funcional adicional (post-merge, recomendada)

Más allá del smoke test automático de `/health`, tras el despliegue conviene una
comprobación manual rápida de los caminos tocados (coste 0, opcional):

- Login + refresh de token (FR9): iniciar sesión y refrescar; un refresh token
  válido debe seguir funcionando.
- Puja con `price<=0` (FR6): debe devolver 422 sin efecto lateral.
- `/api/v1/photos` sin token (FR7): debe requerir autenticación.
- Endpoints admin de BD (FR18): 404 salvo `ENABLE_DB_ADMIN`.

Estas comprobaciones ya están cubiertas por la suite (135 passed); la
verificación manual es defensa en profundidad, no un gate.
