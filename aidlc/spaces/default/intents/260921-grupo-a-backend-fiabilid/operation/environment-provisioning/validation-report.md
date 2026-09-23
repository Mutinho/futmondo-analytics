# Informe de validación del entorno — Fiabilidad de la sync

> Conversation language: Spanish. Fase Operation. Perspectivas inline:
> platform (lead), devsecops y compliance (support). Valida que el entorno de
> producción existente soporta el intent. Coste 0 €.

## Veredicto: VÁLIDO para el despliegue del intent

El entorno de producción actual (Fly.io + Neon) soporta el cambio de fiabilidad
sin reprovisionar ni modificar infraestructura. El intent es backend-only,
aditivo y sin cambios de esquema.

## Validación de infraestructura

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Apps provisionadas y sanas | OK | `futmondo-api` (`/health` 200), `futmondo-app` (`/` 200) |
| BD accesible | OK | Neon (Frankfurt) vía `DATABASE_URL` TLS; sin migración por este intent |
| CD operativa | OK | `fly-deploy.yml` (`verify → deploy → smoke`); ver `cd-config.md` |
| Sin recursos nuevos requeridos | OK | inventario sin cambios (código en app existente) |

## Postura de seguridad (devsecops)

| Comprobación | Resultado | Nota |
|---|---|---|
| Secretos no en claro | OK | Fly/GitHub secrets; gitleaks bloqueante en PR y `verify` |
| `JWT_SECRET` no-default en arranque | OK | NFR1.1; endurecido en `test_jwt_startup.py` |
| Conexión a BD cifrada | OK | TLS a Neon |
| Validación de entrada reforzada | OK | techo de `price` (NFR5) desplegado en `futmondo-api` |
| Manejo de errores sin fugas | OK | `except` acotados (FR3.2): fatales se propagan con contexto, no se silencian |

## Compliance / residencia de datos

| Comprobación | Resultado | Nota |
|---|---|---|
| Residencia de datos | OK (sin cambios) | Neon en Frankfurt (UE); el intent no mueve ni añade datos personales |
| Sin datos personales nuevos | OK | el estado `degraded` en `progress` es metadato técnico (status/reason), no PII |
| Auditoría de despliegue | OK | historial de releases Fly.io + logs de GitHub Actions |
| Contraseña Futmondo nunca en claro | OK (sin regresión) | el intent no toca el manejo de credenciales |

## NO-APLICA / diferido (servicios de pago)

- SLOs formales con burn-rate, tracing distribuido, anomaly detection ML:
  requieren servicios de pago; se difieren. El equivalente gratuito (Fly logs,
  healthcheck, logging estructurado del nuevo helper `record_degraded_step`)
  cubre la observabilidad del intent.
- AWS Secrets Manager, VPC/SG/NACL, cross-account: inexistentes en este stack.

## Sources

- `environment-inventory.md`, `operation/deployment-pipeline/cd-config.md`,
  `inception/requirements-analysis/requirements.md` (NFR1.1, NFR5),
  `construction/sync-reliability/functional-design/*`, `project.md`
  (adaptación de stack Operation + coste 0 €), `README.md` (auth/multi-usuario).

## Assumptions & Open Questions

None.
