# Quality Gates — Construcción (FR3.2 + FR4)

Las quality gates que el CI aplica antes de fusionar a `main` y desplegar. Sin
cambios estructurales en este intent; se documentan tal cual y se confirma que
aplican los comandos de build/test que registró Build and Test.

## Gates bloqueantes (un rojo NO llega a `main`/producción)

| Gate | Comando | Dónde | Bloqueante |
|---|---|---|---|
| Secretos | `gitleaks` | `ci.yml` (PR) + `verify` (push) | Sí |
| Tests backend | `pytest` (`--cov=app` en `ci.yml`; `pytest -q` en `verify`) | `ci.yml` + `verify` | Sí |
| Tests frontend | `ng test` (Node 22, Vitest) | `ci.yml` + `verify` | Sí |
| Smoke de release | `/health` HTTP 200 (5 reintentos) | `fly-deploy.yml` `smoke-test` | Sí (marca release fallida) |

Estos gates aplican exactamente los comandos que Build and Test ejecutó y
registró en `test-results.md` (suite 203 passed, 0 failed).

## Gates advisory (reportan, no bloquean)

| Gate | Comando | Nota |
|---|---|---|
| Lint backend | `ruff check` (`select = E,F,I`; `ignore = E501,E402`) | **Advisory**; `E722` re-habilitado por trinquete (reporta bare-except). NO se corre `ruff format`. |

## Cobertura

- `--cov=app` en `ci.yml` es **observabilidad-only, sin piso bloqueante**
  (`cov-fail-under` diferido). NUNCA se baja un umbral para pasar el gate; el
  trinquete sólo sube.
- **Deuda de pipeline diferida** (fuera de alcance): la asimetría de la señal de
  cobertura — `verify` corre `pytest -q` **sin `--cov`** mientras `ci.yml` mide
  `--cov=app` — queda registrada como deuda; este intent no la cierra.

## Política de promoción

- On-merge a `main` → Fly.io (región `cdg`); sin staging separado. El smoke test
  `/health` es la verificación de release. Rollback manual (`docs/ROLLBACK.md`).

## Assumptions & Open Questions

None.
