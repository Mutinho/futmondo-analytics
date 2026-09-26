# Rollback Runbook — Intent 4 (gate CI/CD hardening)

> Fase Operation. El mecanismo de rollback de release **no cambia** en este
> intent config-only. Este runbook **reutiliza y referencia** el runbook
> existente como fuente única, y añade el matiz del rollback quirúrgico por
> commit `chore(ci)` propio del endurecimiento del gate.

## Fuente única del rollback de release: `docs/ROLLBACK.md`

El procedimiento de rollback de producción es el ya documentado y vigente en
**[`docs/ROLLBACK.md`](../../../../../../docs/ROLLBACK.md)** (NFR2.2, rollback
manual Fly.io). No se modifica. Resumen (la fuente autoritativa es ese fichero):

- **Cuándo**: el smoke test post-deploy `/health` falla, o se detecta un fallo
  funcional/disponibilidad en producción tras un merge a `main`.
- **Cómo**: `fly releases rollback <vN> --app futmondo-api` (y `futmondo-app` si
  aplica), o redeploy explícito de la imagen previa; verificar con
  `curl https://futmondo-api.fly.dev/health` → HTTP 200.
- **Limitación aceptada**: el estado en memoria (`TaskManager`, syncs en curso)
  se pierde en el redeploy/rollback; relanzar los syncs tras el rollback.
- **Post-rollback**: abrir un PR con el fix real (nunca push directo a `main`);
  el gate de CI debe pasar antes de fusionar.

## Matiz de este intent: rollback quirúrgico del endurecimiento del gate

Además del rollback de release (arriba), el endurecimiento del gate introduce un
segundo eje de reversibilidad, **distinto y complementario**:

- Cada endurecimiento (unificar gitleaks, pinnar tooling, allowlist + expiry,
  promover pip-audit, promover npm audit, promover ruff check, piso de cobertura
  + paridad, ratchet frontend) aterriza en su **propio commit `chore(ci)`
  aislado** con el trinquete fijado.
- Si un cambio concreto del gate rompe el pipeline o resulta demasiado ruidoso
  para el free tier / la base heredada, el rollback es **revertir ese único
  commit `chore(ci)`** (`git revert <sha>` vía PR), sin arrastrar los demás
  endurecimientos.
- Este rollback quirúrgico es de **configuración de CI/CD**, no de release de
  producción: no dispara un redeploy de la app; solo ajusta el gate.

### Escenarios y respuesta

| Escenario | Rollback | Mecanismo |
|-----------|----------|-----------|
| Release en producción rojo (`/health` ≠ 200) | Rollback de release | `docs/ROLLBACK.md` (`fly releases rollback`) |
| Un endurecimiento de gate rompe el pipeline | Rollback quirúrgico de config | `git revert <sha del commit chore(ci)>` vía PR |
| `npm audit high` mete demasiado ruido heredado | Endurecer primero en `critical` | Ajuste del nivel en su commit; el trinquete solo endurece después |
| Entrada de allowlist caducada bloquea | Renovar/retirar la entrada | Editar `.pip-audit-allowlist` (con nueva fecha/caducidad o eliminando el ignore si hay fix) |

## Guardrail Operation (rollback obligatorio documentado)

- Todo cambio de este intent tiene ruta de reversa: release → `docs/ROLLBACK.md`;
  config de gate → revert del commit `chore(ci)`.
- La verificación de éxito del deploy sigue siendo el smoke test `/health`
  (health check definido).

## Escalado (single-maintainer)

- No hay rotación on-call formal (single-maintainer). El canal de aviso es la
  notificación de GitHub Actions (gate/deploy rojo). Ante un rollback de
  release, si `/health` sigue rojo tras revertir, detener la máquina
  (`fly machine stop`) mientras se diagnostica, según `docs/ROLLBACK.md`.

## Sources

- `docs/ROLLBACK.md` (fuente única del rollback de release, sin cambios).
- `./cd-config.md`, `./deployment-strategy.md` (este stage).
- `../../construction/ci-pipeline/ci-config.md` (secuencia de commits `chore(ci)`).
- `aidlc/spaces/default/memory/team.md` §Deployment (rollback quirúrgico por commit aislado).

## Assumptions & Open Questions

- None.
