# Estrategia de Despliegue — Backend Security Hardening

> Scope `security-patch`, fase Operation, brownfield. Documenta la estrategia de
> despliegue vigente y su idoneidad para este release de seguridad.

## Estrategia: redeploy on-merge (recreate), entorno único

- **Modelo**: `deploy on merge` a `main` → Fly.io. Cada máquina es
  `min=max=1`; Fly reemplaza la máquina con la nueva release (efectivamente
  *recreate* con un breve corte, aceptable para esta app de un solo entorno).
- **Sin staging separado**: la verificación de release es el **smoke test**
  post-deploy contra `/health` (5 reintentos, HTTP 200 esperado). Es el
  health check definido por fase de Operation (procedimiento con verificación
  de éxito).
- **No blue/green ni canary**: no aplican en `min=max=1` de tier gratuito; su
  adopción tendría coste (doble máquina) y contradiría el mandato de coste 0 €.
  Documentado como decisión consciente, no omisión.

## Criterios de promoción y abort

- **Promoción a producción**: automática al pasar `verify` (gitleaks + pytest +
  ng test) en push→`main`. El gate humano previo es la aprobación del MR
  (branch protection + required status check).
- **Condición de abort/fallo**: si `smoke-test` no obtiene HTTP 200 de `/health`
  tras 5 reintentos, el workflow queda en rojo → señal para ejecutar el rollback
  manual (ver `rollback-runbook.md`).

## Migración de datos

Ninguna. Este patch no cambia el esquema de Neon; no hay pasos
expand/contract ni backfill.

## Idoneidad para este release

Las cinco correcciones son de bajo riesgo de despliegue (validación de entrada,
corrección de lógica de auth, documentación, eliminación de una variable de
entorno local, consolidación de test). La estrategia vigente —redeploy on-merge
con smoke test `/health` y rollback manual— es adecuada sin cambios.

## Implicaciones de seguridad del despliegue (revisión de fase Operation)

- No se añaden ni eliminan controles de seguridad en el despliegue.
- No se tocan IAM, red ni cifrado (Fly.io gestiona TLS con `force_https`).
- El único cambio de config es quitar `SSL_VERIFY=0` de `docker-compose.yml`
  (solo local); refuerza la postura de seguridad, no la debilita.
