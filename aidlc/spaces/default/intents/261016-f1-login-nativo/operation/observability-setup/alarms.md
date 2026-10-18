# Alarms — F1: Login nativo end-to-end

> Fase: operación (observability-setup). Idioma: castellano; tokens técnicos verbatim en inglés.
> Sin CloudWatch Alarms / SNS / PagerDuty (de pago). El "alerting" gratuito de este stack son el
> gate bloqueante, el smoke test y las notificaciones de GitHub Actions al mantenedor único.

## Alertas efectivas (gratuitas)

| Alerta | Disparador | Canal | Severidad | Acción |
|--------|------------|-------|-----------|--------|
| Release fallido | `smoke-test` `/health` != 200 tras 5 reintentos en `fly-deploy.yml` | Notificación de GitHub Actions (workflow en rojo) al mantenedor | Alta | Rollback (ver `rollback-runbook.md`) |
| Gate de CI rojo | cualquier job bloqueante (gitleaks/pip-audit/ruff/pytest/npm audit/ng test) falla | GitHub Actions (PR check / `verify` en rojo) | Alta | No fusionar / no desplegar; arreglar |
| Caída de backend | `/health` != 200 (comprobación manual o puntual) | `fly logs`/`fly status` (pull) | Alta | Diagnóstico + rollback/`fly machine stop` |
| Errores de auth | pico de 4xx/5xx en `/auth/*` observable en `fly logs` | pull manual por el mantenedor | Media | Diagnóstico de D-01 / transporte del token |

## Escalado (single-maintainer)

El escalado es al **mantenedor único** vía las notificaciones de GitHub Actions (email/UI). No hay
rotación on-call ni PagerDuty (equipo de una persona, coste 0 €). El runbook de respuesta vive en
la etapa siguiente (Incident Response) y en `docs/ROLLBACK.md`.

## Umbrales

- Smoke `/health`: binario (200 vs no-200), 5 reintentos con 10 s entre ellos (ya configurado en
  `fly-deploy.yml`).
- Sin umbrales de burn-rate (requieren SLO formal gestionado = NO-APLICA de pago). Ver
  `slo-config.md` para el SLI informal.

## NO-APLICA (de pago)

| CloudWatch/stage | Estado |
|---|---|
| CloudWatch Alarms + SNS topics | NO-APLICA; sustituido por gate `verify` + smoke + notificación GitHub Actions |
| PagerDuty / rotación on-call | NO-APLICA (single-maintainer, coste 0 €) |
| Alarmas por burn-rate de SLO | NO-APLICA (SLO formal de pago) |

## Sources

- [consumes] reliability-design.md, monitoring-design.md — NO existen (etapas `skipped`);
  derivado de la app desplegada.
- [code] `.github/workflows/fly-deploy.yml` (job `smoke-test`), `docs/ROLLBACK.md`.
- [memory] aidlc-shared/operation-fly-stack.md (CloudWatch Alarms → gate+smoke); phases/operation.md
  (umbrales de alerta bajo el SLO); project.md (coste 0 €).

## Assumptions & Open Questions

None.
