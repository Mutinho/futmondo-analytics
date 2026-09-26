# Dashboards — Intent 4 (gate CI/CD hardening)

> Fase Operation. Conocimiento CloudWatch/Grafana **adaptado al stack real
> (coste 0 €)**. Sin dashboards dedicados de pago; las "vistas" son las
> herramientas gratuitas existentes (Q3=A).

## Vistas de observabilidad (gratuitas)

| Vista | Qué muestra | Dónde | Estado |
|-------|-------------|-------|--------|
| **Checks del PR/commit en GitHub** | Estado del gate por paso (gitleaks, pip-audit, npm audit, ruff, cobertura, expiry, tests) — pass/fail | Pestaña Checks del PR / commit en GitHub | Existente / reforzado por el intent |
| **Billing de GitHub Actions** | Minutos consumidos/mes y margen del free tier (observabilidad de coste) | Settings → Billing → Actions | Existente |
| **`fly status`** | Estado de las apps `futmondo-api` / `futmondo-app` (running, health) | CLI `fly status` | Existente |
| **`fly logs`** | Logs de runtime (estructurados: `sync_step`, `reason`, `task_id`) | CLI `fly logs` | Existente |
| **Historial de releases Fly** | Releases y su estado (para rollback) | `fly releases` | Existente |

## Layout recomendado (qué mirar y cuándo)

- **Tras abrir un PR**: la vista de Checks — cada paso del gate con nombre propio;
  un rojo señala la causa sin abrir el log completo.
- **Tras un push a `main`**: el job `verify` en Actions + la cadena de deploy +
  el `smoke-test` `/health`.
- **Salud continua**: `fly status` + `curl /health`; `fly logs` para detalle.
- **Coste**: panel de billing de Actions, revisado periódicamente (FR16).

## NO-APLICA (de pago) — documentado

- **CloudWatch dashboards / Grafana**: NO-APLICA (coste). Sustituidos por las
  vistas gratuitas anteriores.
- **Dashboards de SLO con burn-rate**: NO-APLICA (ver `slo-config.md`).

## Sources

- `../../construction/infrastructure-design/monitoring-design.md`, `../../construction/nfr-design/observability-design.md`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`.

## Assumptions & Open Questions

- None.
