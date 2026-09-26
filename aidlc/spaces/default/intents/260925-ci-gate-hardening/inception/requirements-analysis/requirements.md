# Requirements — Intent 4: Endurecimiento del gate CI/CD

Intent `260925-ci-gate-hardening` (scope `infra`, brownfield). Derivado del plan
de análisis `260911-analisis-mejoras` (agrupado en `docs/BACKLOG-plan-intents.md`,
Intent 4) y de las prácticas afirmadas en practices-discovery de este intent
(decisiones Q1–Q6).

## Sources

- `[desc]` Initial description: `<record>/project-description.json` (endurecimiento
  del gate CI/CD: FR11 + FR12 + FR17.3 + deuda diferida de pipeline; FR16 anexo).
- `[scope]` Workflow-selected scope: `infra`.
- `docs/BACKLOG-plan-intents.md` (Intent 4: FR11/FR12/FR17.3 + deuda diferida; FR16).
- `aidlc/spaces/default/intents/260911-analisis-mejoras/inception/requirements-analysis/requirements.md` (origen de FR11/FR12/FR16/FR17.x).
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/practices-discovery/team-practices.md` (decisiones Q1–Q6, evidencia del repo).
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/practices-discovery/evidence.md` (estado real de `ci.yml`, `fly-deploy.yml`, `pytest.ini`, `ruff.toml`, `angular.json`, `requirements.txt`).
- `aidlc/spaces/default/codekb/futmondo-analytics/business-overview.md`, `architecture.md`, `code-structure.md`.
- `[memory:M1]` `aidlc/spaces/default/memory/project.md` (ALWAYS/NEVER afirmados 2026-09-25).

## Intent analysis

El sistema ya está en producción con un gate de CI **parcialmente** bloqueante:
`gitleaks` + `pytest` (con `--cov=app` observability-only, sin piso) + `ng test`
bloquean, mientras `ruff check`, `pip-audit` y `npm audit` corren en advisory
(`continue-on-error: true`). El objetivo del intent es **endurecer esa red de
seguridad** — sin cambiar lógica de negocio ni topología de despliegue — para que
un rojo real (cobertura por debajo del piso, CVE con fix, secreto, lint roto)
nunca llegue a `main` ni por PR ni por push directo, todo a **coste 0 €**. Es una
intervención config-only de CI/CD, aditiva y con cada endurecimiento en su propio
commit aislado para rollback quirúrgico.

## Functional requirements

### FR11 — Piso de cobertura backend bloqueante
- **FR11.1**: Introducir un único `--cov-fail-under=<N>` en `backend/pytest.ini`
  (dentro del `addopts` de `pytest`), como piso **line-coverage total** (line-only;
  sin `--cov-branch`).
- **FR11.2**: `<N>` se fija al **valor medido exacto** de la suite estabilizada,
  sin margen de holgura; la medición previa es obligatoria y el piso se fija al
  **final** del escalón FR12 (sobre la suite ya saneada).
- **FR11.3**: El piso sube **solo por trinquete**; nunca se relaja para pasar el
  gate. Un flapping se resuelve arreglando el test no-determinista, no bajando el
  piso.
- Given la suite backend en verde, When se mide `pytest --cov=app`, Then el piso
  se fija a ese porcentaje exacto y el gate falla si una ejecución posterior cae
  por debajo.

### FR12 — Promoción escalonada de linters/audits advisory → bloqueante
- **FR12.1**: Orden escalonado: **audits de dependencias primero** (pip-audit
  backend, npm audit frontend), **`ruff check` backend después** como último paso.
  Cada promoción en su propio commit `chore(ci)` aislado.
- **FR12.2**: `npm audit` bloquea en severidad **`high`** (no critical-only). Si
  `high` genera demasiado ruido heredado de golpe, se promueve primero en
  `critical`, se sanea y se endurece a `high` en commit posterior (el trinquete de
  severidad solo endurece).
- **FR12.3**: `pip-audit` bloquea **todo finding con fix disponible**; los findings
  **sin fix** se gobiernan por allowlist (FR12.5), nunca silenciando el gate.
- **FR12.4**: `pip-audit` se ejecuta sobre el **entorno instalado/resuelto tras
  `pip install`** (sin `-r requirements.txt`), para un gate reproducible.
- **FR12.5**: Los findings sin fix se registran en una **allowlist versionada y
  auditada**, commiteada (ID CVE/advisory, dependencia+versión, motivo, fecha y
  fecha de caducidad/revisión), vía `pip-audit --ignore-vuln <ID>` y el
  equivalente versionado en npm; una entrada caducada vuelve a bloquear. Nunca
  `continue-on-error` permanente ni borrar el audit.
- **FR12.6**: La deuda de lint que `ruff check` reporte se sanea **por fichero de
  forma quirúrgica** o se suprime con `per-file-ignores`/`# noqa` puntual con
  rationale, ANTES de bloquear. Nunca `ruff check --fix` de repo entero, `ruff
  format` masivo, ni ampliar/reescribir los god-files ni los routers SQL.
- **FR12.7** (Out of scope, deuda diferida): ESLint frontend NO se promueve a
  bloqueante en este intent (hoy sus devDependencies no están instaladas).

### FR13 — Cierre de deuda de tooling del gate (pins y unificación)
- **FR13.1**: Unificar `gitleaks` a una única versión y fijarla en **ambos** gates
  (`ci.yml` `@v3` vs `verify` `@v2`).
- **FR13.2**: Fijar a versión exacta, **en el paso que la instala**, `ruff` y
  `pip-audit` (hoy `pip install ruff` sin pin).
- **FR13.3**: Fijar `vitest` a versión exacta (hoy `^4.0.8`), emparejada con el pin
  de su plugin `@vitest/coverage-v8 == 4.1.11`.
- **FR13.4** (Out of scope): el pin de acciones de terceros por SHA
  (`setup-flyctl@master`, etc.) se decide en ci-pipeline.

### FR14 — Paridad real de gate PR ↔ push directo (origen FR17.3)
- **FR14.1**: Llevar al job `verify` de `fly-deploy.yml` la misma invocación de
  `pytest` **con `--cov` y el mismo piso** que `ci.yml`, aterrizándolo en el mismo
  commit (o inmediatamente después) que introduce el piso en `ci.yml`.
- **FR14.2**: **Añadir** al job `verify` los pasos de audit (`pip-audit`/`npm
  audit`) y lint (`ruff check` backend) que se vuelvan bloqueantes — hoy `verify`
  no tiene ninguno; es añadir pasos, no flipear un flag.
- **FR14.3**: La cadena `needs:` de `fly-deploy.yml` (`verify` → `deploy-backend`
  → `deploy-frontend` → `smoke-test`) **no** se reordena; el endurecimiento
  refuerza el contenido de `verify`, no su topología.

### FR15 — Ratchet de cobertura frontend
- **FR15.1**: Subir los umbrales de `angular.json` (`coverageThresholds`:
  statements/branches/functions/lines) al valor medido actual. El ratchet solo
  sube.
- **FR15.2**: `angular.json` es la **fuente única** del umbral frontend, con el
  enforcement dentro de `ng test` (sin pasos extra ni `continue-on-error`). El
  frontend ya tiene paridad de enforcement en ambos workflows: su única tarea es
  subir el ratchet, no crear paridad; no se tocan devDependencies.

### FR16 — Documentación de consumo y umbrales de free tier
- **FR16.1**: Documentar el consumo actual dentro de los tiers gratuitos (minutos
  de GitHub Actions, Neon free, Fly.io free allowance).
- **FR16.2**: Identificar los umbrales que forzarían salir del free tier, con
  atención al coste añadido de medir cobertura y correr audits/lint en dos jobs
  (PR + `verify`). Entregable como documento.

## Non-functional requirements

- **NFR1 — Coste 0 €**: todo en tiers gratuitos (Neon free, Fly.io free allowance,
  GitHub Actions free); ninguna dependencia o servicio de pago. Cualquier tooling
  OSS nuevo se fija a versión exacta.
- **NFR2 — Aislamiento por commit**: cada endurecimiento (piso de cobertura,
  promoción advisory→bloqueante, unificación/pin de versión) en su propio commit
  `chore(ci)` con el trinquete fijado, para rollback quirúrgico.
- **NFR3 — No reformateo brownfield**: nunca `ruff format`/Prettier en masa sobre
  ficheros heredados; solo ficheros nuevos o cambios quirúrgicos. La reviewer solo
  corre `ruff check`.
- **NFR4 — Secretos**: siempre vía `secrets` de GitHub Actions / Fly.io; en CI el
  `JWT_SECRET` es efímero y no productivo; los tests usan fakes/dobles, nunca
  credenciales reales (gitleaks escanea también los tests).
- **NFR5 — Reproducibilidad del gate**: el gate no debe producir rojos
  intermitentes; de ahí auditar el entorno instalado (FR12.4) y pinnar el tooling
  (FR13).
- **NFR6 — Idioma**: identificadores/docstrings/comentarios en inglés; texto de
  usuario y mensajes de commit (Conventional Commits con scope) en castellano.

## Constraints

- Stack fijo: Angular 22 + FastAPI (Python 3.12) + Neon PostgreSQL + Fly.io + GitHub Actions.
- No ampliar los god-files (`data_sync_service.py`, `data_manager_v2.py`, `assistant_service.py`) ni el patrón SQL-en-router; intent config-only de CI/CD.
- Node fijado en `.nvmrc` = `22.22.3`; si un cambio tocara devDependencies del frontend, verificar `npm ci` + `ng test` en contenedor `node:22.22.3` antes de pushear.

## Assumptions

- La medición de cobertura backend y de umbrales frontend se realiza en
  ci-pipeline / nfr-requirements sobre la suite ya estabilizada; los valores
  numéricos exactos del piso (FR11.2) y del ratchet frontend (FR15.1) se fijan
  entonces.
- El estado advisory/bloqueante actual del gate es el descrito en la evidencia de
  practices-discovery (verificado contra `ci.yml` y `fly-deploy.yml`).

## Out of scope

- ESLint frontend a bloqueante (FR12.7 — deuda diferida; no se tocan devDependencies del frontend).
- Pin de acciones de terceros por SHA (FR13.4 — se decide en ci-pipeline).
- Branch-coverage backend (`--cov-branch`); el piso es line-only.
- SAST/DAST dedicado (CodeQL/Semgrep/ZAP) — deuda documentada, no alcance.
- Cualquier refactor de los god-files o de los routers SQL-en-endpoint.

## Open questions

- Valor numérico exacto del piso de cobertura backend (FR11.2) — se mide en ci-pipeline/nfr-requirements.
- Delta por métrica del ratchet de cobertura frontend (FR15.1) — se mide en ci-pipeline/nfr-requirements.

## Assumptions & Open Questions

- Los valores numéricos del piso backend y del ratchet frontend quedan diferidos a la medición en ci-pipeline/nfr-requirements (política ya afirmada; falta solo el número).
