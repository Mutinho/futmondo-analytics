# Alarms — Intent 4 (gate CI/CD hardening)

> Fase Operation. Conocimiento CloudWatch Alarms/SNS/PagerDuty **adaptado a coste
> 0 €**. Escalado single-maintainer vía notificación nativa de GitHub Actions
> (Q4=A). Alertas sobre síntomas, no causas.

## Alarmas (gratuitas)

| Alarma | Condición | Severidad | Canal / acción |
|--------|-----------|-----------|----------------|
| Gate PR rojo | Job `quality` (`ci.yml`) falla en un PR | Bloqueante (no merge) | Notificación de GitHub Actions al autor del PR |
| Gate push rojo | Job `verify` (`fly-deploy.yml`) falla en push a `main` | Bloqueante (no deploy) | Notificación de Actions al maintainer |
| Release fallido | `smoke-test` `/health` ≠ 200 tras deploy | Bloqueante (release fallido) | Notificación de Actions; rollback (`docs/ROLLBACK.md`) |
| Allowlist caducada | Script de expiry falla (entrada con `expiry < hoy`) | Bloqueante | Notificación de Actions; el `::error::` nombra CVE/dep/fecha |
| Finding de audit nuevo | `pip-audit` (con fix) / `npm audit` (`high`) no allowlisted | Bloqueante | Notificación de Actions; sanear o allowlistear con caducidad |

## Filosofía de alertas

- **Alertar sobre síntomas**: gate rojo, release fallido, allowlist caducada —
  todos user/main-impacting, no métricas de recurso.
- **Sin alert fatigue**: no se alerta sobre CPU/memoria; las alarmas son eventos
  bloqueantes discretos del gate/deploy.
- **Umbral bajo el SLO**: como no hay SLO formal con burn-rate (de pago), la
  "alarma" es el propio fallo bloqueante, que precede al impacto en producción
  (un rojo nunca llega a `main`).

## Escalado (single-maintainer)

| Nivel | Responsable | Canal |
|-------|-------------|-------|
| Gate/deploy rojo | maintainer | Notificación de GitHub Actions (email/UI) |
| Release fallido en producción | maintainer | Notificación de Actions + rollback manual |

No hay rotación on-call ni IC formal (single-maintainer). No aplica matriz de
escalado multinivel.

## NO-APLICA (de pago) — documentado

- **CloudWatch Alarms / SNS / PagerDuty / OpsCenter**: NO-APLICA (coste).
  Sustituidos por las notificaciones nativas de GitHub Actions.
- **Composite alarms / auto-remediation Lambda**: NO-APLICA (coste + no hay
  Lambda). El rollback es manual (`docs/ROLLBACK.md`).

## Sources

- `../../construction/infrastructure-design/monitoring-design.md`, `../../construction/nfr-design/reliability-design.md`.
- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`.

## Assumptions & Open Questions

- None.
