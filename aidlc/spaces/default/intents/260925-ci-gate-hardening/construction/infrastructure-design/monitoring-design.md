# Monitoring Design — Intent 4 (gate CI/CD hardening)

> Monitoreo específico de plataforma que implementa la estrategia de
> `observability-design.md`, adaptado al stack real (GitHub Actions + Fly.io) y
> al mandato coste 0 €. Tabular donde es posible.

## Metrics & KPIs

| Metric | Source | Threshold | Why it matters |
|--------|--------|-----------|----------------|
| Resultado por check bloqueante (pass/fail) | Log de GitHub Actions (paso con nombre: `pip-audit`, `npm audit`, `ruff check`, `coverage floor`, `allowlist expiry`, `gitleaks`) | Cualquier fail bloquea el merge/deploy | Localiza la causa del rojo sin leer todo el log (NFR-OBS.2, Q1/Q3 NFR Design). |
| Cobertura backend (line) | `pytest --cov` en `ci.yml` y `verify` | `< --cov-fail-under` bloquea | Señal de cobertura visible en ambas rutas hacia `main` (NFR-OBS.1). |
| Cobertura frontend (4 métricas) | `ng test` + `angular.json` `coverageThresholds` | `< umbral` bloquea | Ratchet frontend, ya con paridad; solo sube. |
| Findings de audit | `pip-audit` / `npm audit` | Finding con fix (pip) / `high`+ (npm) no allowlisted bloquea | Supply-chain: CVE explotable con parche no llega a producción. |
| Caducidad de la allowlist | Script `check-allowlist-expiry` | Entrada con `expiry < hoy` bloquea | Una excepción caducada vuelve a bloquear (NFR-SEC.3). |
| Minutos de GitHub Actions consumidos/mes | Panel de billing de Actions (free tier) | Umbral documentado en FR16 (margen del allowance) | Observabilidad de coste; sustituye Cost Explorer (NFR6.1). |
| Salud de release | `smoke-test` `/health` (5 reintentos) | HTTP ≠ 200 marca release fallido | Verificación de release intacta (NFR-OBS.4). |
| Salud de runtime | `fly status` + `fly logs` + `/health` | — (observación pull) | Observabilidad de runtime gratuita existente; sin cambios. |

## Alerts

| Alert | Condition | Severity | Routes to |
|-------|-----------|----------|-----------|
| Gate PR rojo | Job `quality` (`ci.yml`) falla en un PR | Bloqueante (no merge) | Notificación de GitHub Actions al autor del PR |
| Gate push rojo | Job `verify` (`fly-deploy.yml`) falla en push a `main` | Bloqueante (no deploy) | Notificación de GitHub Actions al maintainer |
| Release fallido | `smoke-test` `/health` ≠ 200 tras deploy | Bloqueante (release marcado fallido) | Notificación de Actions; rollback manual `docs/ROLLBACK.md` |
| Allowlist caducada | Script de expiry falla | Bloqueante | El mismo canal del gate; el `::error::` nombra el CVE/dep/fecha |

Escalado: **single-maintainer**; el canal de escalado es la notificación nativa
de GitHub Actions. Sin PagerDuty/SNS (de pago) — NO-APLICA.

## SLIs / SLOs (informal, coste 0 €)

| SLI | SLO target | Measurement window |
|-----|-----------|--------------------|
| Reproducibilidad del gate | Mismo commit → mismo veredicto (100 %) | Por ejecución |
| Determinismo (sin flapping) | 0 rojos intermitentes atribuibles a no-determinismo | Continuo; un flake se arregla en el test, no bajando el piso |
| Cobertura de rutas hacia `main` | 100 % (PR + push aplican el mismo conjunto de checks) | Por cambio de workflow |
| Salud de release | `/health` 200 tras cada deploy | Por release |

No hay SLO formal con burn-rate alerting (de pago) — **NO-APLICA/diferido**; el
SLI es informal y observable con el log de Actions + `fly logs`.

## Logs & Tracing

- **Agregación de logs**: el log de GitHub Actions (por job/step) es la fuente
  primaria para el gate; `fly logs` para runtime. Sin agregador gestionado (de
  pago) — NO-APLICA.
- **Tracing distribuido**: NO-APLICA (de pago). Sustituto gratuito: correlación
  por log estructurado + `task_id` en `fly logs` (contexto de runtime, sin
  cambios en este intent).
- **Dashboards**: no se crean dashboards dedicados (de pago); el "dashboard" es
  la vista de checks del PR/commit en GitHub y el panel de billing de Actions.

## Mapeo AWS→gratuito (resumen)

| Herramienta asumida | Equivalente gratuito | Estado |
|---------------------|----------------------|--------|
| CloudWatch metrics/dashboards | pasos con nombre en Actions + `fly logs` + `/health` | Aplica (pull) |
| CloudWatch Alarms / SNS / PagerDuty | gate bloqueante + smoke test + notificación de Actions | Aplica (parcial) |
| X-Ray / tracing | log estructurado + `task_id` | Diferido |
| Anomaly Detection (ML) | barreras deterministas (allowlist con caducidad, piso, pins) | Sustituido |
| Cost Explorer / Trusted Advisor | minutos de Actions documentados + coste 0 € | Sustituido |
| AWS Config drift detection | diff de git sobre `fly.toml` y workflows versionados | Aplica |

## Trazabilidad

- NFR-OBS.1 → Metrics (cobertura en ambos gates); NFR-OBS.2 → Metrics (pasos con
  nombre) + Alerts; NFR-OBS.3 → allowlist auditable + expiry; NFR-OBS.4 →
  release health; NFR6.1 → minutos de Actions.

## Sources

- `../nfr-design/observability-design.md` (estrategia que este artefacto implementa).
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (mapeo AWS→gratuito).

## Assumptions & Open Questions

- El umbral concreto de minutos de free tier se cuantifica en FR16 (ci-pipeline).
