# Evidencia inspeccionada — Practices Discovery

> Versión integrada por el lead (aidlc-pipeline-deploy-agent). Registro de qué
> inspeccionó/infirió cada participante, las decisiones de la entrevista humana y la
> incertidumbre no resuelta (deuda consciente).

## Qué inspeccionó/infirió cada participante

### Lead (aidlc-pipeline-deploy-agent)

- **Inspeccionado**: `git log --oneline -30`, `git branch -a`, HEAD `8d71c88`;
  `.github/workflows/{ci,fly-deploy,daily-sync,sofascore-sync}.yml`; `backend/fly.toml`,
  `angular-app/fly.toml`, `docker-compose.yml`; `backend/ruff.toml`, `backend/pytest.ini`,
  `angular-app/eslint.config.js`, `.nvmrc`; `project.md`, `org.md`.
- **Observado/inferido**: trunk-based sobre `main` con ramas cortas prefijadas e
  integración vía MR; Conventional Commits en castellano; gate escalonado
  (gitleaks/pytest/ng test bloqueantes desde el inicio; ruff/ESLint/pip-audit/npm audit
  advisory); deploy on-merge a Fly.io `cdg` sin staging, smoke `/health` con 5 reintentos;
  crons one-shot; coste 0 €; sin walking skeleton para brownfield acotado.
- **Divergencia detectada (resuelta en entrevista)**: se observó un merge commit de PR #1,
  frente al default squash-merge de `org.md`.

### aidlc-quality-agent (calidad)

- **Inspeccionado**: `backend/pytest.ini`, `backend/conftest.py`, `backend/tests/`,
  `.github/workflows/{ci,fly-deploy}.yml`, `angular-app/angular.json`,
  `code-quality-assessment.md`.
- **Confirmado**: Methodology test-after + characterization-first; `conftest.py` declara
  explícitamente "congelar el comportamiento ACTUAL antes de refactorizar"; no existe piso
  de cobertura (`cov-fail-under`/`fail_under`/`coverageThreshold` ausentes); gate de PR con
  gitleaks+`pytest`+`ng test` bloqueantes; hueco crítico: **0 tests de
  `SessionStore`/`TaskManager`**.
- **Aportado**: orden de dos fases (caracterización→durabilidad), patrón de fakes de
  `conftest.py` reutilizable para la capa de persistencia, definición mínima de "hecho"
  de testing.

### aidlc-developer-agent (desarrollo)

- **Inspeccionado**: `backend/app/` (auth, services, api) y CodeKB.
- **Confirmado**: nombrado idiomático y consistente; trunk-based; test-after +
  characterization-first; coste 0 €; estilo escalonado.
- **Aportado/corregido**: docstrings y comentarios reales en **inglés** (solo `detail` de
  `HTTPException` y commits en castellano); ausencia de capa de persistencia (SQL crudo en
  auth/routers, DDL de dominio en `auth/token_store.py`); god-files
  `data_manager_v2.py` (~166 KB) y `data_sync_service.py` (~84 KB); imports diferidos y
  `__import__` dinámico en `refresh` como antipatrón.

### aidlc-devsecops-agent (seguridad)

- **Inspeccionado**: `.github/workflows/ci.yml`, `backend/ruff.toml`,
  `angular-app/eslint.config.js`, `code-quality-assessment.md`.
- **Confirmado**: gitleaks bloqueante con `fetch-depth: 0`; lint/format advisory;
  pip-audit/npm audit advisory; FR5 credenciales en claro en memoria.
- **Aportado**: encuadre de que lint ≠ SAST; propuesta (no afirmada) de orden de
  preferencia FR5; modelo de amenaza mínimo (STRIDE) para la durabilidad.

## Decisiones de la entrevista humana (autoritativas)

- **Q1 — Way of Working**: trunk-based; ramas cortas desde `main` + MR con gate de CI;
  **squash-merge** a `main` al fusionar. (Resuelve la divergencia observada.)
- **Q2 — Walking Skeleton**: **OFF** (sistema en producción; nada que bootstrapear).
- **Q3 — Testing Posture**: `Methodology: test-after`; `Ordering` caracterización primero
  (congelar comportamiento actual, incl. bugs conocidos) → durabilidad (test-after). El
  suelo 80% del scope `feature` es referencia global; se exigen tests de caminos nuevos y
  de error de `SessionStore`/`TaskManager`, sin piso porcentual adicional bloqueante.
- **Q4 — Code Style**: identificadores, docstrings y comentarios en **inglés**; texto de
  usuario y mensajes de commit en **castellano**.
- **Q5 — Credenciales (FR5)**: solo la **prohibición dura** (NEVER contraseña en claro en
  memoria o BD); el orden de preferencia re-auth vs. cifrado se decide en diseño.
- **Heredadas mantenidas**: coste 0 € (solo tiers gratuitos); `JWT_SECRET` no-default;
  gate de CI bloqueante (tests + gitleaks) antes de merge.

## Incertidumbre no resuelta / deuda consciente (no son reglas afirmadas)

- **Asimetría del re-verify de deploy**: el job `verify` de `fly-deploy.yml` corre
  `pytest -q` **sin `--cov`** y **sin gitleaks**, a diferencia del gate de PR. Un secreto
  introducido en un push directo a `main` solo lo detendría el gate de MR (relevante a
  FR5). Se apoya en branch protection; formalizar replicación de gitleaks queda para diseño
  de pipeline.
- **Ausencia de SAST/DAST**: no hay paso SAST ni DAST en ningún workflow. Deuda de
  seguridad consciente y aceptable en coste 0 €; opciones futuras de coste 0 €:
  `semgrep` OSS / `bandit` advisory, familia `S` de ruff, hook pre-commit de gitleaks,
  pinning de acciones por SHA, SBOM (Syft/Trivy). No se afirman como reglas hoy.
- **Deuda de seguridad de código** (registrada como tradeoffs, no como práctica): `except
  Exception: pass` en migraciones y auto-detección (enmascara fallos); bug de precedencia
  en `token_store.is_refresh_token_valid` (posible fallo de validación de expiración de
  refresh tokens); `NODE_TLS_REJECT_UNAUTHORIZED=0` en el `ng build` de producción
  (desactiva verificación TLS en el build). Recomendado caracterizar el bug de expiración
  antes de tocar auth; el resto queda fuera del foco del intent salvo registro.
- **Divergencia de runtime Python 3.12/3.11**: la documentación/stack declara Python 3.12
  (ruff `py312`) pero existen indicios de divergencia entre 3.12 y 3.11 en el entorno de
  ejecución/CI. A confirmar y unificar en diseño/infra; no bloquea esta etapa.
- **Migraciones ad-hoc sin versionado** (`CREATE TABLE IF NOT EXISTS` + `ALTER` en
  `try/except: pass`): al introducir persistencia cifrada de sesión/estado, el cambio de
  esquema debe hacerse de forma controlada; el `try/except: pass` puede ocultar un fallo
  de migración.

## Sources

- `git log --oneline -30`, `git branch -a`, `git rev-parse HEAD` (= `8d71c88`).
- `.github/workflows/{ci,fly-deploy,daily-sync,sofascore-sync}.yml`.
- `backend/fly.toml`, `angular-app/fly.toml`, `docker-compose.yml`.
- `backend/ruff.toml`, `backend/pytest.ini`, `backend/conftest.py`,
  `angular-app/eslint.config.js`, `angular-app/angular.json`, `.nvmrc`.
- `backend/app/` (auth, services, api).
- `aidlc/spaces/default/codekb/futmondo-analytics/{technology-stack,code-quality-assessment,
  architecture,business-overview,code-structure,dependencies}.md`.
- `aidlc/spaces/default/memory/{project,org}.md`.
- `contributions/aidlc-{quality,developer,devsecops}-agent.md`.
- `practices-discovery-questions.md` (Q1–Q5 + confirmación consolidada).
