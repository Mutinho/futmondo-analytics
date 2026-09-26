# Deployment Log — Intent 4 (gate CI/CD hardening)

> Fase Operation. Este intent es **config-only**: no hay artefacto de aplicación
> nuevo que desplegar. El "despliegue" es el **push a `main` de los commits
> `chore(ci)`** que endurecen el gate. Este log documenta el **procedimiento y el
> estado esperado** de ese despliegue; **no** registra un push ya ejecutado (no
> se ha realizado en esta etapa). La verificación real ocurre al pushear cada
> commit y observar el gate en verde.

## Naturaleza del despliegue (Q1=A)

- **Artefacto desplegado**: cambios de configuración de CI/CD y tooling
  versionados (`ci.yml`, `fly-deploy.yml`, `pytest.ini`, `angular.json`,
  `requirements.txt`, `scripts/check-allowlist-expiry.sh`,
  `backend/.pip-audit-allowlist`).
- **Sin código de aplicación nuevo**: no se despliega runtime; el CD de la app
  (`deploy-backend`/`deploy-frontend`) se dispara igual que siempre cuando los
  commits aterrizan en `main`.
- **Migraciones de BD (Q2=A)**: **ninguna**. No se toca esquema ni datos de Neon;
  no se delega ejecución de migración al developer.

## Secuencia de despliegue (Q4=A) — escalonada, verde antes de continuar

Los 8 commits `chore(ci)` se pushean **en orden**, cada uno debe pasar el gate
(PR + `verify`) en **verde** antes del siguiente; rollback quirúrgico por commit
si uno rompe. Sin ventana de freeze especial (deploy on-merge, single-maintainer).

| # | Commit `chore(ci)` | Estado esperado del gate | Rollback |
|---|--------------------|--------------------------|----------|
| 1 | unificar gitleaks a `@v3` en ambos gates | Verde (mismo escaneo, versión unificada) | `git revert` del commit |
| 2 | pinnar `ruff`, `pip-audit`, `vitest` a versión exacta | Verde (sin cambio de comportamiento, solo pin) | `git revert` |
| 3 | añadir allowlist versionada + expiry check en ambos gates | Verde (allowlist vacía → expiry no bloquea) | `git revert` |
| 4 | `pip-audit` sobre entorno instalado, bloqueante (PR + verify) | Verde tras sanear/allowlistear findings con fix | `git revert` |
| 5 | `npm audit --audit-level=high` bloqueante (PR + verify) | Verde tras sanear; si ruido alto, primero `critical` | `git revert` |
| 6 | sanear deuda de lint + `ruff check` bloqueante (PR + verify) | Verde tras saneo quirúrgico/`per-file-ignores` | `git revert` |
| 7 | piso `--cov-fail-under` en `pytest.ini` + paridad `--cov` en `verify` | Verde con el piso al valor medido exacto | `git revert` |
| 8 | subir ratchet de cobertura frontend en `angular.json` | Verde con umbrales al valor medido | `git revert` |

## Estado del despliegue

| Campo | Valor |
|-------|-------|
| Estado | **Planificado / documentado** (no ejecutado en esta etapa) |
| Mecanismo | push a `main` (deploy on-merge); cadena `verify → deploy-backend → deploy-frontend → smoke-test` |
| Ejecutor | maintainer, vía PR (gate PR) o push directo (gate `verify`) |
| Verificación de cada commit | gate en verde (PR + `verify`) + smoke test `/health` tras el deploy |
| Cambios de runtime | Ninguno (config-only) |

## Seguridad del despliegue (guardrail Operation)

- El despliegue **añade** controles de seguridad al gate pre-deploy; **no retira
  ni elude** ninguno. Sin cambios de IAM/red/cifrado → sin risk assessment de
  infraestructura.
- Secretos vía `secrets` de GitHub Actions / Fly.io; `JWT_SECRET` efímero en CI.
- Todo commit pasa por el gate bloqueante antes de fusionar; un rojo nunca llega
  a producción.

## Rollback

Ver `../deployment-pipeline/rollback-runbook.md`: rollback de release vía
`docs/ROLLBACK.md` (Fly.io), y rollback quirúrgico de config vía `git revert`
del commit `chore(ci)` concreto.

## Sources

- `../deployment-pipeline/cd-config.md`, `deployment-strategy.md`, `rollback-runbook.md`.
- `../environment-provisioning/environment-inventory.md`.
- `../../construction/ci-pipeline/ci-config.md` (secuencia de commits).
- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`.

## Assumptions & Open Questions

- La ejecución real (push de los commits y observación del gate en verde) es una acción posterior del maintainer; esta etapa documenta el procedimiento y el estado esperado, sin fabricar un push no realizado.
