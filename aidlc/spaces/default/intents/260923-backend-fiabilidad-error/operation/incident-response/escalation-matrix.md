# Escalation Matrix — Operación (FR3.2 + FR4)

Matriz de escalado single-maintainer, coste 0 €. El "canal de escalado" es la
notificación nativa de GitHub Actions + la inspección de `fly logs`. No hay
on-call rotativo ni PagerDuty (NO-APLICA).

## Severidades y respuesta

| Severidad | Definición | Ejemplos | Respuesta / ruta |
|---|---|---|---|
| **P1** | Producción rota o caída | Release fallida (`/health` ≠ 200); backend no responde | Rollback inmediato (`rollback-runbook.md`); atención del maintainer al recibir la notificación de GitHub |
| **P2** | Degradación parcial sin caída | Baneo Sofascore (RB-1); fallo fatal en escritura recuperado por rollback de transacción (RB-3); cron sistemático fallido | Diagnóstico en la ventana de trabajo del maintainer; runbook correspondiente |
| **P3** | Informativo / transitorio | `DEGRADED` puntual recuperable (RB-2); cron fallido puntual reintentado por la siguiente ejecución | Registrar; actuar sólo si se repite |

## Contacto / notificación

- **Maintainer único**: la señal llega por (a) email/notificación de GitHub
  Actions ante deploy/cron en rojo, y (b) inspección manual de `fly logs` /
  `fly status` / `/health`.
- **Post-mortem**: obligatorio para P1/P2 (guardarraíl de fase Operation);
  registrado como issue/nota en el repo.

## NO-APLICA (coste 0 €)

- PagerDuty / Opsgenie / on-call rotativo / SNS → **NO-APLICA**. Alternativa
  gratuita: notificación de GitHub Actions + inspección manual. Documentado, no
  inventado.

## Assumptions & Open Questions

None.
