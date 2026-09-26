# Deployment Strategy — Intent 4 (gate CI/CD hardening)

> Fase Operation. Estrategia de despliegue REAL del stack (Fly.io + Neon, coste
> 0 €), adaptada de las guardrails que asumen blue-green/canary/SLO de pago.
> Este intent no cambia la estrategia; la documenta y encuadra el efecto del
> gate endurecido.

## Estrategia de despliegue (real)

| Facet | Elección | Rationale |
|-------|----------|-----------|
| Modelo | **Redeploy on-merge** a `main` → Fly.io (`flyctl deploy`) | Deploy continuo a producción; línea base afirmada. |
| Entornos | **Único entorno de producción**, sin dev/staging separado (Q5) | Coste 0 €; el smoke test `/health` es la verificación de release. |
| Traffic shifting | **Ninguno gradual** (no blue-green, no canary) — NO-APLICA | Blue-green/canary exigen doble infraestructura o traffic-splitting gestionado = coste. Fly.io hace redeploy directo de la app. |
| Promoción de entorno | **Implícita**: merge a `main` → deploy (Q5) | No hay pipeline de promoción multi-entorno; el "gate de promoción" es el gate de CI bloqueante + smoke test. |
| Migraciones de BD | Fuera de alcance de este intent (no toca esquema) | El intent es config-only de CI/CD; sin cambios de datos. |
| Feature flags | No se introducen en este intent | Sin features nuevas; endurecimiento de gate. |

## Criterio de éxito / aborto del deploy

- **Gate de promoción (pre-deploy)**: el job `verify` bloqueante (gitleaks +
  pip-audit + npm audit + ruff check + allowlist expiry + `pytest --cov` con
  piso + `ng test`). Si CUALQUIER paso falla, los jobs `deploy-*` no se ejecutan
  (cadena `needs:`). Un rojo nunca llega a producción (Q2).
- **Verificación de release (post-deploy)**: smoke test contra `/health`, 5
  reintentos esperando HTTP 200. Si no responde 200, el release se marca
  fallido y se procede al rollback (ver `rollback-runbook.md`).
- **Criterio de aborto**: fallo de `verify` (aborta antes de desplegar) o fallo
  del smoke test (release fallido → rollback manual).

## SLIs / SLOs (informal, coste 0 €)

- **SLO formal con burn-rate alerting**: **NO-APLICA** en este intent (exige
  servicios de pago). Alternativa gratuita documentada: SLI informal.
- **SLI de release (informal)**: `/health` devuelve 200 tras el deploy (smoke
  test). Métrica de salud existente; sin ventana de burn-rate formal.
- **SLI de gate (informal)**: reproducibilidad (mismo commit → mismo veredicto)
  y ausencia de flapping; observable en el log de GitHub Actions.
- **Observabilidad de runtime** (guardrail Operation: cada componente con una
  métrica de salud): `/health` (healthcheck de `futmondo-api`), `/` (healthcheck
  de `futmondo-app`), `fly status` y `fly logs`. Sin cambios en este intent.

> Nota (guardrail Operation): las guardrails piden SLOs cuantificados con
> ventana temporal. En este stack a coste 0 € no hay motor de SLO/burn-rate; se
> documenta la alternativa gratuita (SLI informal `/health` 200 por release) en
> vez de inventar infraestructura de SLO inexistente. Es una limitación aceptada
> y trazada (learned 2026-09-16).

## Blue-green / canary — criterios de traffic-shifting y aborto (guardrail Operation)

**NO-APLICA**: no se usa blue-green ni canary (coste). No hay traffic-shifting
gradual que documentar. El equivalente de "abort condition" es el smoke test
`/health`: si falla, rollback manual de la release previa. Documentado en vez de
diseñar una estrategia de pago inexistente.

## Efecto del endurecimiento del gate en la estrategia

- El endurecimiento **refuerza el criterio de promoción** (más razones para que
  `verify` bloquee el deploy) sin cambiar el modelo de despliegue ni el
  mecanismo de aborto.
- Cada endurecimiento va en commit `chore(ci)` aislado: si un cambio de gate
  rompe el pipeline, el rollback es revertir ese commit (rollback quirúrgico),
  independiente del rollback de release de Fly.io.

## Sources

- `./cd-config.md`, `./rollback-runbook.md` (este stage).
- `../../construction/nfr-design/reliability-design.md`, `observability-design.md`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (mapeo AWS→gratuito, SLI informal).
- `aidlc/spaces/default/memory/project.md` §Corrections (adaptación Operation coste 0 €).

## Assumptions & Open Questions

- SLO formal con burn-rate queda como deuda documentada (de pago); fuera de alcance por coste 0 €.
