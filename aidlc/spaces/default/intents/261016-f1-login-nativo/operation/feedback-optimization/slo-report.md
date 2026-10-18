# SLO Report — F1: Login nativo end-to-end

> Fase: operación (feedback-optimization). Perspectiva de operations engineer. Idioma: castellano;
> tokens técnicos verbatim en inglés. Sin SLO formal con error budget / burn-rate (de pago,
> NO-APLICA a coste 0 €): se reporta el **SLI informal** definido en `slo-config.md`, con la
> evidencia reunida en operación.

## Cumplimiento del SLI informal (post-F1)

| SLI | Objetivo indicativo | Evidencia | Estado |
|-----|---------------------|-----------|--------|
| Disponibilidad del backend | `/health` → 200 | HTTP 200 verificado en vivo (deployment-execution, performance-validation, 2026-10-18) | ✅ |
| Éxito de login nativo | `POST /auth/login` 200 + `refresh_token` en body | validado en el iPhone 13 Pro; 401 correcto con credencial inválida | ✅ |
| Éxito de refresh / auto-login | `POST /auth/refresh` renueva sesión | auto-login al reabrir la app (Keychain) | ✅ |
| Ausencia de errores de auth | sin picos de 4xx/5xx inesperados en `/auth/*` | sin anomalías observadas en `fly logs` tras el release de D-01 | ✅ |

## Error budget / burn-rate

- **NO-APLICA**: no hay SLO formal con error budget ni alertas por burn-rate (requieren métricas
  gestionadas de pago). El "presupuesto de error" no se cuantifica; la señal práctica de
  degradación es el smoke `/health` en rojo + picos en `fly logs` (ver `alarms.md`).

## Conclusión

Tras el despliegue de F1, todos los SLI informales están en verde. D-01 (transporte del refresh
token) no ha degradado la disponibilidad ni introducido errores de auth observables.

## Sources

- [consumes] slo-config.md, dashboards.md, alarms.md (observability-setup); deployment-log.md;
  test-results.md (performance-validation); incident-plan.md.
- [memory] aidlc-shared/operation-fly-stack.md (SLI informal; SLO de pago NO-APLICA); project.md
  (coste 0 €).

## Assumptions & Open Questions

None.
