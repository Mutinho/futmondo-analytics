# Informe de Validación de Salud — Backend Security Hardening

> Scope `security-patch`, fase Operation. Documenta los health checks vigentes y
> su validación para este release. Stack real: Fly.io + Neon, coste 0 €.

## Health checks definidos

| Componente | App Fly.io | Check | Puerto | Config |
|-----------|-----------|-------|--------|--------|
| Backend | `futmondo-api` | `GET /health` | 8000 | `interval=30s`, `timeout=5s`, `force_https=true` |
| Frontend | `futmondo-app` | `GET /` (nginx) | 80 | check de disponibilidad |

- Región: `cdg`. Máquinas `min=max=1`, `shared-cpu-1x` / 256 MB.
- Base de datos: Neon PostgreSQL (Frankfurt, tier free).

## Métrica de salud y de error (fase Operation)

- **Métrica de salud**: disponibilidad del endpoint `/health` del backend
  (HTTP 200 = sano). Es la señal que Fly.io usa para el routing y la que el
  smoke test post-deploy valida.
- **Métrica de error**: respuestas no-200 de `/health` y 5xx del backend,
  observables vía `fly logs` (logging estructurado). No hay SLO formal con
  burn-rate ni tracing distribuido: exigirían servicios de pago y contradicen el
  mandato de coste 0 € — se documenta la alternativa gratuita en su lugar
  (NO-APLICA/diferido), coherente con la práctica del proyecto para etapas de
  Operation sobre stack Fly.io + Neon.

## Validación para este release

- El arranque del backend valida el guard de `JWT_SECRET` no-default (NFR1.1):
  un secreto ausente/por-defecto impide el arranque y `/health` no daría 200.
  El health check, por tanto, actúa como verificación indirecta de esa
  precondición de seguridad en cada release.
- Las cinco correcciones no alteran el contrato de `/health` ni la topología.

## Implicaciones de seguridad (revisión de fase Operation)

- No se añaden ni eliminan controles de seguridad en el despliegue.
- No se tocan IAM, red ni cifrado (Fly.io gestiona TLS con `force_https`).
- FR8 elimina `SSL_VERIFY=0` de `docker-compose.yml` (solo entorno local):
  refuerza la postura, no la debilita.

## Rollback

Si el health check / smoke test falla tras el deploy, ejecutar el runbook de
rollback (`deployment-pipeline/rollback-runbook.md`): `fly releases rollback` de
la release previa y verificación con `curl /health`.
