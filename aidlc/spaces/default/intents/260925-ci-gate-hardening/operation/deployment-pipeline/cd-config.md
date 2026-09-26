# CD Config — Intent 4 (gate CI/CD hardening)

> Fase Operation. Este intent es **config-only** y endurece el **gate pre-deploy**
> (contenido del job `verify`), sin cambiar la topología ni el orden de
> despliegue. Este documento describe el CD existente y el delta del
> endurecimiento; el "cómo" del gate ya está en `../../construction/ci-pipeline/ci-config.md`.

## CD existente (línea base, SIN cambios)

- **Workflow**: `.github/workflows/fly-deploy.yml`, disparo `push` → `main` (+
  `workflow_dispatch`).
- **Cadena `needs:` (intacta)**: `verify → deploy-backend → deploy-frontend →
  smoke-test`.
- **Jobs de deploy**:
  - `deploy-backend`: `flyctl deploy` en `./backend` (app `futmondo-api`),
    `needs: verify`.
  - `deploy-frontend`: `flyctl deploy` en `./angular-app` (app `futmondo-app`),
    `needs: deploy-backend`.
  - `smoke-test`: `curl` a `/health` (5 reintentos, HTTP 200),
    `needs: [deploy-backend, deploy-frontend]`.
- **Secretos**: `FLY_API_TOKEN` vía `secrets`; `JWT_SECRET` efímero en `verify`.
- **Región/topología**: Fly.io `cdg`, dos apps; Neon PostgreSQL (Frankfurt).
- **Crons** (`daily-sync.yml`, `sofascore-sync.yml`): máquinas Fly one-shot,
  fuera de la cadena de deploy; **no cambian**.

## Delta de este intent (gate pre-deploy endurecido)

Lo único que cambia es el **CONTENIDO del job `verify`** (el gate que precede al
deploy), ya especificado en `ci-config.md`:

| Aspecto | Antes | Después | Efecto en CD |
|---------|-------|---------|--------------|
| gitleaks en `verify` | `@v2` | `@v3` (unificado) | Mismo bloqueo, versión unificada |
| pip-audit en `verify` | ausente | añadido, bloqueante | `verify` puede fallar por CVE con fix |
| npm audit en `verify` | ausente | añadido (`high`), bloqueante | `verify` puede fallar por finding `high`+ |
| ruff check en `verify` | ausente | añadido, bloqueante | `verify` puede fallar por lint |
| allowlist expiry en `verify` | ausente | añadido | `verify` puede fallar por entrada caducada |
| pytest en `verify` | `pytest -q` (sin `--cov`) | `pytest -q --cov=app --cov-fail-under=<piso>` | `verify` puede fallar por cobertura |

La cadena `needs:` **no se reordena**: `deploy-backend` sigue dependiendo de
`verify`, así que cualquier fallo nuevo de `verify` impide el deploy — la
defensa en profundidad se refuerza, el mecanismo es el mismo.

## Qué NO cambia (invariantes de fase Operation)

- Topología de dos apps Fly.io + Neon.
- Orden de deploy (`verify → deploy-backend → deploy-frontend → smoke-test`).
- Deploy on-merge a `main`; sin entorno de staging separado.
- Smoke test `/health` como verificación de release.
- Crons de sync.
- Secretos vía `secrets` de GitHub Actions / Fly.io.

## Seguridad del cambio (guardrail Operation)

- El endurecimiento **no retira ni elude** ningún control de seguridad existente;
  **añade** controles al gate pre-deploy (implicación de seguridad: mayor
  cobertura de supply-chain antes de producción).
- No toca IAM/red/cifrado (Fly.io gestiona routing/TLS; Neon TLS): sin cambios
  que requieran risk assessment de infraestructura.

## Sources

- `.github/workflows/fly-deploy.yml` (estado real).
- `../../construction/ci-pipeline/ci-config.md`, `../../construction/ci-pipeline/quality-gates.md`.
- `../../construction/infrastructure-design/cicd-pipeline.md`, `infrastructure-specification.md`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`.

## Assumptions & Open Questions

- Los valores de pin y del piso se materializan en los commits `chore(ci)` (ci-config.md); la topología de CD no depende de ellos.
