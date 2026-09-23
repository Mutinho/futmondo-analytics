# Operation sobre stack Fly.io + Neon (coste 0 €) — Mapeo de adaptación

> Conocimiento de equipo (`aidlc-shared`): lo leen todos los agentes en cada
> intent del espacio. Documenta cómo adaptar las etapas de fase **Operation**
> (cuyo conocimiento embebido asume AWS/CloudWatch) al stack real de este
> proyecto, sin re-derivarlo intent a intent.
>
> Este documento es guía reutilizable; NO sustituye a las reglas de memoria de
> `memory/` (que solo se escriben por el ritual de learnings). La corrección
> base ya afirmada vive en `project.md` → `## Corrections` (learned 2026-09-16).

## Contexto del stack real

- **Hosting**: Fly.io (región `cdg`) — backend `futmondo-api` (puerto 8000,
  check `/health`) y frontend `futmondo-app` (nginx, puerto 80, check `/`).
- **BD**: Neon PostgreSQL (Frankfurt, tier free).
- **CI/CD**: GitHub Actions (`ci.yml` en PR→`main`; `fly-deploy.yml` job
  `verify` en push→`main`), free tier.
- **Operación**: single-maintainer.
- **Mandato duro**: **coste 0 €** — solo tiers gratuitos; descartar toda mejora
  o dependencia con gasto recurrente.

## Regla de adaptación

En cualquier etapa de Operation cuyo conocimiento asuma AWS, **mapear cada
herramienta a su equivalente gratuito** y marcar el resto **NO-APLICA/diferido**,
documentando la alternativa gratuita en vez de inventar infraestructura
inexistente. No proponer nada con gasto recurrente.

## Tabla de mapeo (AWS → equivalente gratuito en este stack)

| Herramienta AWS del stage | Equivalente gratuito | Estado |
|---|---|---|
| CloudWatch dashboards / metrics | `fly status` + `fly logs` + healthcheck `/health` | Aplica (observación pull) |
| CloudWatch Alarms / SNS / PagerDuty | gate `verify` bloqueante + `smoke-test` `/health`; escalado single-maintainer por notificación de GitHub Actions | Aplica (parcial) |
| X-Ray / tracing distribuido | correlación por log estructurado + `task_id` en `fly logs` | Diferido (tracing de pago NO-APLICA) |
| CloudWatch Anomaly Detection (ML) | barreras deterministas (validación de entrada) + estados explícitos (p. ej. `degraded`) | Sustituido (ML NO-APLICA) |
| AWS Config drift detection | diff de git sobre `fly.toml` y workflows versionados | Aplica |
| Cost Explorer / Trusted Advisor | mandato coste 0 € (tiers gratuitos), verificado por diseño | Sustituido |
| SSM Automation / AWS Backup / DR multi-región | rollback manual `flyctl` (`fly releases rollback`); RPO = datos en Neon | Diferido |
| VPC / subnets / security groups / NACL / Secrets Manager | Fly.io gestiona red/routing; secretos vía `fly secrets` / GitHub Actions secrets; TLS a Neon | NO-APLICA (términos AWS) |

## Notas de observabilidad y despliegue

- **Despliegue**: on-merge a `main`; cadena `verify → deploy-backend →
  deploy-frontend → smoke-test`. Un rojo nunca llega a producción. Sin staging;
  el smoke test `/health` (5 reintentos, HTTP 200) es la verificación de release.
- **Rollback**: manual, `docs/ROLLBACK.md`. El estado en memoria (`TaskManager`,
  syncs en curso) se pierde en el redeploy — limitación aceptada.
- **SLO/SLI**: sin SLO formal con burn-rate (de pago); SLI informal = `/health`
  200 + ausencia de pasos `degraded` inesperados en `fly logs`.
- **Logging**: preferir logs estructurados (campos como `sync_step`, `reason`,
  `task_id`) para que `fly logs` + `grep` sustituyan a las consultas gestionadas.

## Secretos y coste (guardarraíles siempre)

- Secretos nunca en claro; `gitleaks` es bloqueante en CI (PR) y `verify`
  (push). `JWT_SECRET` no-default exigido en arranque (NFR1.1).
- Nunca introducir un servicio de pago para cubrir una necesidad de Operation:
  documentar la alternativa gratuita o marcar la deuda como diferida.

## Deuda de pipeline diferida conocida (fuera de alcance por defecto)

- Paridad de la señal de cobertura `--cov` de backend en el job `verify`.
- SAST/DAST del frontend más allá de ESLint advisory.
