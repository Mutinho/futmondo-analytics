# Practices Discovery — Evidence

**Collaborator:** aidlc-pipeline-deploy-agent

Qué inspeccioné y qué inferí para redactar `team-practices.md` y
`discovered-rules.md` de este RE-RUN (Intent 4, scope infra, brownfield). El
foco es CI/CD gate hardening (FR11/FR12/FR17.3 + deuda diferida + FR16), no
fiabilidad backend.

Hallazgos que fijaron cada sección:

- **Gate de CI real** (`.github/workflows/ci.yml`, disparo `pull_request → main`,
  job `quality`): `gitleaks` + `pytest --cov=app` + `ng test` son **BLOQUEANTES**;
  `ruff check`, ESLint (`npx ng lint || echo …`), `pip-audit -r requirements.txt`
  y `npm audit --audit-level=high` corren **advisory** (`continue-on-error:
  true`). Esto confirma el punto de partida de FR12 (advisory→bloqueante
  escalonado) y de FR11 (cobertura backend hoy medida pero sin piso).
- **Gate de push→main** (`.github/workflows/fly-deploy.yml`, job `verify`):
  corre `gitleaks` + `pytest -q` (**SIN `--cov`**) + `ng test`, **sin ningún paso
  de audit ni de lint**, y de él dependen `deploy-backend` → `deploy-frontend` →
  `smoke-test` (`/health`, 5 reintentos). Confirma verbatim la **asimetría de
  cobertura backend** a cerrar (FR17.3), que la paridad de audit/lint en `verify`
  exige AÑADIR pasos (no flipear un flag), y la cadena `needs:` que NO debe
  reordenarse.
- **Config de cobertura backend**: `backend/pytest.ini` declara cobertura como
  métrica informativa, activable con `--cov=app`, **sin piso** — no hay
  `cov-fail-under`. Es el hueco exacto de FR11.
- **Config de cobertura frontend**: `angular-app/angular.json` (target `test`,
  builder `@angular/build:unit-test`) define `coverageThresholds` = statements
  15 / branches 15 / functions 13 / lines 14; enforcement dentro de `ng test`, y
  AMBOS workflows corren `ng test` → el frontend ya tiene **paridad de
  enforcement**; su tarea es sólo subir el ratchet. Fuente única del umbral.
- **Lint backend**: `backend/ruff.toml` (`py312`, `line-length = 100`,
  `select = ["E","F","I"]`, `ignore = ["E501","E402"]`; `E722` ya re-habilitado
  como advisory en un intent previo; `[lint.per-file-ignores]` para `tests/**` y
  `conftest.py`). Advisory hoy; último paso del escalón FR12. `ci.yml` hace
  `pip install ruff` **sin pin**.
- **ESLint frontend no instalado**: `eslint.config.js` declara explícitamente que
  `angular-eslint`, `@typescript-eslint/*` y `eslint` **aún no son
  devDependencies**; volverlo bloqueante ampliaría la superficie del frontend.
- **Pins OSS existentes / drift**: `@vitest/coverage-v8 == 4.1.11` pero `vitest`
  en rango abierto `^4.0.8` (angular-app); `PyJWT == 2.9.0`, `google-genai ==
  1.14.0`, `groq == 0.25.0` pinneados frente a rangos abiertos (`requests>=`,
  `fastapi>=`, `psycopg2-binary>=`, `curl_cffi>=`, `pytest>=`) en
  backend/requirements.txt; gitleaks `@v3` (ci.yml) vs `@v2` (verify);
  `setup-flyctl@master`. Confirma la práctica afirmada de pin exacto en checks
  bloqueantes y la deuda de tooling a cerrar (gitleaks/ruff/pip-audit/vitest) vs
  la que se difiere a ci-pipeline (SHA de acciones).
- **God-files confirmados (tamaños reales)**: `data_sync_service.py` ~84,6 KB,
  `data_manager_v2.py` ~166,2 KB, `assistant_service.py` ~51,7 KB; routers
  SQL-en-endpoint grandes bajo `app/api/v1/endpoints/`. Justifica la regla de
  sanear la deuda de lint por fichero/`# noqa`, nunca ampliando esos ficheros.
- **Topología / cadencia de deploy**: inferida de `fly-deploy.yml` + codekb —
  dos apps Fly.io (`futmondo-api`, `futmondo-app`), Neon PostgreSQL free
  (Frankfurt), on-merge a `main` sin staging, smoke `/health` como verificación
  de release. Justifica walking skeleton OFF (sistema ya en producción).
- **Baseline afirmada**: leí las 5 secciones de `memory/team.md` y los
  ALWAYS/NEVER de `memory/project.md` como línea base y ajusté el matiz al gate
  hardening (descartando el matiz de fiabilidad backend de intents previos).
- **Entrevista Q1–Q6**: todas resueltas con la opción recomendada; ver
  ## Assumptions & Open Questions (sección Resueltas).

## Sources

- `.github/workflows/ci.yml`
- `.github/workflows/fly-deploy.yml`
- `.github/workflows/daily-sync.yml`, `.github/workflows/sofascore-sync.yml` (crons Fly one-shot, coste ~0)
- `backend/pytest.ini`
- `backend/ruff.toml`
- `backend/requirements.txt`
- `angular-app/angular.json` (target `test` → `coverageThresholds`)
- `angular-app/package.json` (devDependencies, pin `@vitest/coverage-v8 == 4.1.11`, `vitest ^4.0.8`)
- `angular-app/eslint.config.js` (ESLint no instalado; `npx ng lint || echo …`)
- `backend/app/services/data_sync_service.py`, `data_manager_v2.py`, `assistant_service.py` (god-files, tamaños)
- `backend/app/api/v1/endpoints/` (routers SQL-en-endpoint)
- `aidlc/spaces/default/codekb/futmondo-analytics/code-quality-assessment.md`
- `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md`
- `aidlc/spaces/default/codekb/futmondo-analytics/dependencies.md`
- `aidlc/spaces/default/codekb/futmondo-analytics/code-structure.md`
- `aidlc/spaces/default/codekb/futmondo-analytics/architecture.md`
- `aidlc/spaces/default/codekb/futmondo-analytics/business-overview.md`
- `aidlc/spaces/default/memory/team.md` (baseline afirmada, 5 secciones)
- `aidlc/spaces/default/memory/project.md` (ALWAYS/NEVER afirmados)
- `aidlc/spaces/default/memory/org.md` (defaults de framework)
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/project-description.json`
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/aidlc-state.md` (scope infra, stages a ejecutar/omitir)
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/practices-discovery/practices-discovery-questions.md` (respuestas Q1–Q6)
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/practices-discovery/contributions/aidlc-quality-agent.md`
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/practices-discovery/contributions/aidlc-developer-agent.md`
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/practices-discovery/contributions/aidlc-devsecops-agent.md`

## Assumptions & Open Questions

### Resueltas en la entrevista (Q1–Q6)

- **Q1 — Alcance de ESLint frontend (FR12)**: RESUELTA (A). ESLint frontend
  EXCLUIDO de este intent (deuda diferida); a bloqueante sólo audits + `ruff
  check` backend; no se tocan las devDependencies del frontend; el frontend sólo
  sube el ratchet de cobertura. Resuelve el OBJECT del desarrollador.
- **Q2 — Severidad que bloquea en audits (FR12)**: RESUELTA (A). npm audit
  bloquea en `high`; pip-audit bloquea todo finding CON fix; sin-fix → allowlist
  (Q3); si `high` produce ruido de golpe, promover primero en `critical` y
  endurecer a `high` (trinquete de severidad sólo endurece).
- **Q3 — Findings sin fix en free tier (FR12)**: RESUELTA (A). Allowlist
  versionada y auditada, commiteada (ID CVE/advisory, dependencia+versión,
  motivo, fecha y caducidad), vía `pip-audit --ignore-vuln <ID>` y equivalente
  npm; nada de `continue-on-error` permanente; entrada caducada vuelve a
  bloquear.
- **Q4 — Paridad de audits/lint/cobertura en el job `verify` (FR17.3)**:
  RESUELTA (A). `verify` recibe la señal de cobertura backend CON piso (paridad
  con `ci.yml`) Y los pasos de audit/lint bloqueantes (AÑADIR pasos, no flipear
  flag); la paridad de cobertura aterriza en el mismo commit (o inmediatamente
  después) que introduce el piso en `ci.yml`.
- **Q5 — Deuda de tooling y drift de versiones**: RESUELTA (A). Unificar y fijar
  gitleaks en ambos gates; pinnar `ruff`/`pip-audit` en el paso que los instala;
  pinnar `vitest`; auditar el entorno instalado (no `-r`). El pin de acciones de
  terceros por SHA (`setup-flyctl@master`, etc.) se decide en ci-pipeline.
- **Q6 — Granularidad y holgura del piso backend (FR11)**: RESUELTA (A).
  Line-coverage total (único `--cov-fail-under` en `pytest.ini`), piso = valor
  medido exacto SIN margen; flapping → arreglar el test no-determinista, nunca
  bajar el piso; el piso se fija al FINAL del escalón FR12 sobre la suite ya
  estabilizada.

### Abiertas (mediciones numéricas, dependen de ci-pipeline / nfr-requirements)

- **Valor numérico exacto del piso backend (FR11)**: el piso `--cov-fail-under`
  se fija al porcentaje medido de `pytest --cov=app` sobre la suite ya
  estabilizada al FINAL del escalón FR12. La política está afirmada (valor
  medido exacto, sin margen, line-only, sólo trinquete); el número concreto se
  mide en ci-pipeline / nfr-requirements, no en esta etapa.
- **Delta exacto del ratchet frontend**: subir los umbrales de `angular.json`
  (statements/branches/functions/lines) al valor medido actual; el delta
  numérico concreto por métrica se decide con la medición en ci-pipeline.
