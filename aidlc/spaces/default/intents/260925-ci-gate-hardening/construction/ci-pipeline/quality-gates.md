# Quality Gates — Intent 4 (gate CI/CD hardening)

> Criterios pass/fail de cada quality gate del pipeline endurecido, aplicables
> en AMBAS rutas hacia `main` (PR-gate `ci.yml` job `quality` + push-gate
> `fly-deploy.yml` job `verify`). Un rojo nunca llega a producción.

## Gates bloqueantes (tras este intent)

| Gate | Criterio pass/fail | Etapa | Presente en (tras el intent) |
|------|--------------------|-------|------------------------------|
| Secret scan (`gitleaks@v3`) | 0 secretos detectados en repo y tests; cualquier hallazgo → fail | Pre-todo | PR + verify (unificado a `@v3`) |
| Allowlist expiry | 0 entradas de la allowlist caducadas (`expiry >= hoy`); una caducada → fail | Pre-audit | PR + verify (nuevo) |
| Backend dependency audit (`pip-audit`) | 0 findings CON fix disponible fuera de la allowlist, sobre el entorno instalado; cualquiera → fail | Post-install | PR (promovido) + verify (nuevo) |
| Frontend dependency audit (`npm audit`) | 0 findings de severidad `high`+ fuera de la allowlist; cualquiera → fail | Post-install | PR (promovido) + verify (nuevo) |
| Backend lint (`ruff check`) | 0 violaciones no suprimidas (`per-file-ignores`/`# noqa` con rationale para deuda heredada); cualquiera → fail | Pre-test | PR (promovido) + verify (nuevo) |
| Backend coverage floor (`pytest --cov-fail-under`) | cobertura line total `>=` piso medido; por debajo → fail | Post-test | PR + verify (paridad `--cov` nueva) |
| Frontend coverage ratchet (`ng test` + `angular.json`) | cobertura `>=` umbrales por métrica; por debajo → fail (dentro de `ng test`) | Post-test | PR + verify (ya con paridad) |
| Release verification (`smoke-test` `/health`) | HTTP 200 en `/health` (5 reintentos); si no → release fallido | Post-deploy | verify chain (sin cambios) |

## Reglas de trinquete (invariantes)

- **El ratchet SÓLO sube**: ningún umbral/piso existente se relaja para pasar el
  gate (backend y frontend). Un flake se arregla en el test no-determinista,
  nunca bajando el piso ni añadiendo margen.
- **Severidad de audit SÓLO endurece**: npm audit `critical → high`, nunca al
  revés. pip-audit bloquea todo finding con fix; los sin fix van a la allowlist.
- **Sin `continue-on-error` permanente** en un check promovido; sin silenciar un
  audit borrándolo o bajando su nivel global. Findings sin fix → allowlist
  versionada con caducidad; una entrada caducada vuelve a bloquear.
- **Promoción escalonada**: cada gate se promueve a bloqueante en su propio
  commit `chore(ci)` aislado, con la deuda heredada saneada/silenciada
  quirúrgicamente ANTES de bloquear (nunca big-bang).

## Paridad PR ↔ push (FR17.3)

Todos los gates bloqueantes existen en AMBOS workflows tras el intent. El job
`verify` gana los pasos que hoy no tiene (allowlist expiry, pip-audit, npm
audit, ruff check, `pytest --cov` con piso) para que un push directo a `main` no
eluda el gate. La cadena `needs:` no se reordena; se refuerza el contenido de
`verify`.

## Reproducibilidad (NFR5.1)

- Tooling pinneado a versión exacta (`ruff`, `pip-audit`, `vitest`, gitleaks
  unificado a `@v3`): dos ejecuciones sobre el mismo commit dan el mismo
  veredicto.
- `pip-audit` sobre el entorno instalado (no rangos de `requirements.txt`):
  evita findings intermitentes.

## Coste 0 €

Todas las herramientas son OSS y caben en el free tier (GitHub Actions, Neon
free, Fly.io free allowance). El coste marginal dominante (medir cobertura
backend en dos jobs) se documenta en FR16; se acepta como coste de la paridad.

## Sources

- `./ci-config.md` (configuración accionable).
- `../infrastructure-design/cicd-pipeline.md`, `../nfr-design/security-design.md`, `../nfr-design/reliability-design.md`.
- `aidlc/spaces/default/memory/team.md` §Testing Posture / §Code Style / §Deployment.

## Assumptions & Open Questions

- El valor numérico del piso backend y los pins exactos se fijan al materializar; la política ya está afirmada.
