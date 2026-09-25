# Build and Test Summary — FR14 + FR15

Intent: `260925-limpieza-config-residuos` · Scope: `refactor` (Minimal) · zero-Unit.

## Estado general y prerequisitos

- Build backend: OK (importable, sin `ImportError` tras la poda del dead-path).
- Prerequisito de arranque: `JWT_SECRET` no-default (NFR1.1). BD única: Neon
  PostgreSQL (`DATABASE_URL`). En tests, fakes in-memory (sin red/BD/credenciales).

## Inventario de tipos de test

Test Strategy **Minimal** → no se generan ficheros de instrucciones de test
adicionales (integration/performance/security). Los unit tests se cubren en
code-generation. Ficheros producidos por esta etapa: `build-instructions.md`,
`build-and-test-summary.md`, `test-results.md`, `cross-unit-traceability.md`.

## Expectativas de cobertura

- Backend: suite `pytest` verde (208 passed, 3 xfailed). `--cov`
  observability-only, sin piso (NFR2). Ratcheting solo sube.
- Frontend: no tocado; `ng test` se ejercita en el gate de CI real.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| T-SUITE | NFR1 (requirements.md) | suite existente verde | 208 passed, 3 xfailed, 0 failed | `test-results.md` (pytest -q) | build-and-test | Met |
| T-COV | NFR2 (requirements.md) | ningún umbral relajado | `--cov` sin piso, intacto | `ruff.toml`/CI sin cambio de floor | build-and-test | Met |
| T-DIFF | NFR4 (requirements.md) | diffs quirúrgicos, sin `ruff format` masivo | solo ficheros de la poda; ruff advisory sin `--fix` | `git status`, `code-summary.md` | build-and-test | Met |
| T-DEADPATH | FR14.1 | sin refs vivas al dead-path | 0 refs vivas (excl. comentario god-file) | grep en `backend/app` | build-and-test | Met |
| T-NOFRONTEND | FR15 | frontend intacto | `git status angular-app/` vacío | git status | build-and-test | Met |
| T-CI-REAL | NFR2 (gate CI) | gitleaks + pytest(3.12) + ng test verdes | pendiente en CI real | pipeline `.github/workflows/ci.yml` | deployment-execution | Unverified (deferred: requires CI env) |

Nota: T-CI-REAL requiere el entorno de CI (Python 3.12 + gitleaks + `ng test`) y
lo posee la fase de despliegue; localmente se verificó el equivalente backend en
venv efímero (Python 3.14 sin `libsql-experimental`, learning afirmado). No
bloquea el gate de esta etapa: la verificación local es verde y el gate de CI es
la puerta previa al merge/deploy, no de esta etapa.

## Readiness

- **Build-ready**: sí.
- **Test-ready**: sí (suite verde, sin regresiones).
- **Deployment-ready**: sí, sujeto al gate de CI real antes del merge a `main`.

## Limitaciones / pendientes

- Verificación local en Python 3.14 (CI real 3.12); tests usan fakes, no BD real.
- Deuda diferida registrada: `DATABASE_PATH` conservada, comentario stale en
  god-file, asimetría `--cov` `ci.yml`/`verify` (todas fuera de alcance).
