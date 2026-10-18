# Health Check Report — F1: Login nativo end-to-end

> Fase: operación (deployment-execution). Idioma: castellano; tokens técnicos verbatim en inglés.
> Estado de salud del entorno tras el despliegue de F1. Observación pull con herramientas
> gratuitas (`curl /health`, `fly status`/`fly logs`); coste 0 €.

## Health checks tras el despliegue

| Componente | Health check | Estado | Última verificación |
|------------|--------------|--------|---------------------|
| Backend `futmondo-api` | `GET /health` → 200 `{"status":"healthy"}` | ✅ healthy (0.47 s) | 2026-10-18 (en vivo desde el agente) |
| Frontend `futmondo-app` | `GET /` (nginx) | ✅ sin cambios en F1 | release encadenado verde |
| Base de datos Neon | conexión TLS desde el backend (implícita en `/health` 200) | ✅ alcanzable | 2026-10-18 |
| App iOS `FutmondoApp` | validación manual del flujo F1 en el iPhone 13 Pro | ✅ funcional | validada por el propietario |

## Señales de salud (SLI informal)

Sin SLO formal con burn-rate (sería de pago; NO-APLICA a coste 0 €). SLI informal del backend:

- **Disponibilidad**: `/health` devuelve 200.
- **Ausencia de errores de auth**: sin picos de 4xx/5xx en `/auth/login` y `/auth/refresh`
  observables vía `fly logs` (pull manual por el mantenedor; no hay dashboard gestionado).
- **Métrica de salud mínima** (guardarraíl de la fase operación): el endpoint `/health` cumple la
  exigencia de "al menos una métrica de salud" para el servicio.

## Adaptación de observabilidad (AWS → gratuito)

| Herramienta AWS | Equivalente gratuito | Estado |
|---|---|---|
| CloudWatch dashboards/metrics | `fly status` + `fly logs` + `/health` | Aplica (pull) |
| CloudWatch Alarms / SNS / PagerDuty | gate `verify` + smoke `/health` + notificación de GitHub Actions | Aplica (parcial) |
| Health checks gestionados | healthcheck `/health` de Fly.io (ya configurado) | Aplica |

La configuración detallada de observabilidad es trabajo de la etapa siguiente (Observability
Setup); aquí solo se reporta el estado de salud post-despliegue.

## Rollback disponible

Si un health check fallara, el rollback está documentado en `rollback-runbook.md` (backend:
`fly releases rollback`; iOS: reinstalar build previo). No ha sido necesario: todos los checks en
verde.

## Sources

- [consumes] deployment-log.md, smoke-test-results.md; environment-inventory.md,
  validation-report.md.
- [code] verificación en vivo `curl /health`; `.github/workflows/fly-deploy.yml`.
- [memory] phases/operation.md (métrica de salud + error rate; health check de verificación);
  aidlc-shared/operation-fly-stack.md (SLI informal, sin SLO de pago); project.md (coste 0 €).

## Assumptions & Open Questions

None.
