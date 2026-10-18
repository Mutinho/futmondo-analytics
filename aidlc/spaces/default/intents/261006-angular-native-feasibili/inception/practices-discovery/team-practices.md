# Prácticas del Equipo — Integración final (re-run brownfield, intent de análisis)

> Integración final del lead (pipeline-deploy) para la etapa Practices Discovery
> del intent `261006-angular-native-feasibili` (scope `classic`). Re-run
> brownfield: recoge la **línea base durable y transversal** del equipo, no las
> reglas de intents previos específicas de CI gate-hardening o refactor de
> god-files, que **no aplican** a un intent de ANÁLISIS de viabilidad (sin código
> de aplicación, sin cambios de CI, sin trinquete de cobertura). Incorpora las
> tres contribuciones de apoyo (quality, developer, devsecops) y las decisiones de
> la entrevista humana (Q1=B, Q2=B, Q3=C).

## Way of Working

Mantenemos **trunk-based development** sobre `main` con ramas cortas y con
prefijo por tipo (`fix/...`, `chore/...`, `feat/...`, `docs/...`). La integración
pasa por Pull Request con **gate de CI obligatorio**
(`.github/workflows/ci.yml`, disparo `pull_request` → `main`, job `quality` como
required status check); el push directo a `main` re-ejecuta el gate en el job
`verify` de `fly-deploy.yml` antes de desplegar (los `needs:` no cruzan
workflows, por eso el gate se replica).

- **Estrategia de merge**: **squash-merge** a `main`. Cada PR aterriza como un
  único commit sobre la historia lineal de `main`. Base de worktree `main`,
  destino `main`. (Línea base durable, alineada con `org.md`.)
- **Conventional Commits** con scope entre paréntesis y en castellano
  (`chore(aidlc)`, `docs(feasibility)`, `chore(ci)`…).
- **Matiz de ESTE intent (análisis de viabilidad)**: los entregables son
  **documentos de análisis** (viabilidad de Angular Native/NativeScript, menú
  inferior iOS, widgets, ruta de implementación), **no** código de aplicación ni
  cambios de CI/CD. No hay refactor, ni promoción de linters/audits, ni trinquete
  de cobertura en este intent. Las ramas y commits de documentación siguen la
  misma política trunk-based + squash-merge; el gate de CI aplica igual aunque el
  cambio sea sólo documental.

## Walking Skeleton

**No se ejecuta ceremonia de walking skeleton** para este intent (línea base
OFF). El sistema ya está **en producción** con un pipeline Fly.io maduro (región
`cdg`, dos apps `futmondo-api` + `futmondo-app`, healthcheck `/health`) y un
**gate de CI bloqueante ya operativo** (gitleaks + `ruff check` + `pytest` +
`pip-audit` + `ng test` + `npm audit`). Además, al ser un intent de **análisis**,
no hay ningún componente ni pipeline que arrancar de cero: no se produce software
ejecutable que un esqueleto deba validar.

## Testing Posture

- **Methodology**: test-after
- **Ordering**: este intent entrega **documentos de análisis** (no capas de
  software testeable), así que no introduce ningún piso de cobertura ni tests
  nuevos; la única obligación de testing es que la **suite existente siga en
  verde** (backend `pytest` + `pytest-cov` desde `backend/` con fixtures fake
  in-memory de `conftest.py`; frontend `ng test` con Vitest). Un intent de
  análisis no modifica código de aplicación, por lo que no debería disparar
  fallos de la suite; pero el gate de CI corre igual en el PR documental y dentro
  de `ng test` el enforcement de cobertura (`coverageThresholds` en
  `angular.json`) es **bloqueante**: si un rojo aparece por **flapping** de
  cobertura ajeno al cambio, se **arregla el test no-determinista**, NUNCA se baja
  un umbral/piso ni se añade `continue-on-error` (coherente con el invariante del
  trinquete). Se conserva la metodología test-after del equipo para cuando se
  produzca código.
- **Línea base durable (para cuando SÍ haya código)**: posture **test-after**;
  tests como entregable de primera clase que **aseveran el efecto**
  (payload/estado/modo de fallo), nunca `assert True` ni specs espejo; fixtures
  fake in-memory sin red, sin BD real y sin credenciales/tokens reales (gitleaks
  escanea también los tests). El trinquete de cobertura (backend
  `--cov-fail-under` en `pytest.ini`; frontend `coverageThresholds` en
  `angular.json`) **sólo sube**, nunca se relaja para pasar el gate; el flapping
  se arregla en el test no-determinista, no bajando el piso.
- **Portabilidad de la posture al target nativo (riesgo a documentar en
  feasibility, no obligación de este intent)**: la suite frontend actual (15
  `*.spec.ts` sobre `@angular/build:unit-test`, builder Vitest `4.1.11` +
  `@vitest/coverage-v8` + `jsdom`) **no porta tal cual** a NativeScript: no hay
  DOM/`jsdom`, el runner Angular CLI de Vitest no aplica y los specs que montan
  componentes Material/CDK no portan; los specs de servicios/RxJS/signals son
  portables casi 1:1. Una migración nativa implicaría **rehacer el arnés de test
  de frontend** y **re-basar** el umbral de cobertura sobre un runner distinto
  (suelo nuevo bajo tooling distinto, no un trinquete que suba), y añade una
  dimensión **E2E/dispositivo** (iPhone 13 Pro / Samsung A17) hoy inexistente. El
  **backend no cambia** por una migración de UI nativa (ni `pytest` ni el piso
  `--cov-fail-under`), para que nadie induzca trabajo backend inexistente.
- **No aplica en este intent**: los valores concretos de piso de cobertura
  medidos en intents previos (backend `--cov-fail-under=27`; frontend
  statements 19 / branches 19 / functions 17 / lines 18) son estado heredado del
  repo que este intent **no modifica**; no se induce trabajo de ratchet ni de
  paridad de señal, propio de los intents de CI gate-hardening.

## Deployment

**Desplegamos on-merge a `main`** hacia Fly.io (región `cdg`), sin entorno de
staging separado: el smoke test contra `/health` (5 reintentos, HTTP 200) es la
verificación del release (`.github/workflows/fly-deploy.yml`,
`verify → deploy-backend → deploy-frontend → smoke-test`). **Este intent es de
análisis y no despliega nada**: no toca la topología, el orden de despliegue, los
crons ni el gate `verify`. La política de despliegue se documenta como línea base
durable, no como trabajo a ejecutar.

- **Topología**: dos apps Fly.io — backend `futmondo-api` (puerto 8000, check
  `/health`) y frontend `futmondo-app` (nginx, check `/`). Base de datos **Neon
  PostgreSQL** (Frankfurt, tier free).
- **Secretos**: siempre vía `secrets` de GitHub Actions / Fly.io; en CI el
  `JWT_SECRET` es efímero y no productivo (`ci-ephemeral-secret-not-a-real-one`).
- **Rollback**: runbook documentado (`docs/ROLLBACK.md`); el mecanismo Fly.io es
  redeploy de la release anterior.
- **Restricción dura (durable) y su excepción acotada (Q1=B)**: todo en **tiers
  gratuitos** — coste 0 € — para infraestructura, servicios y dependencias
  recurrentes del proyecto. **Excepción aceptada y acotada**: el **coste de
  publicación de distribución nativa** (Apple Developer Program ~99 €/año; Google
  Play Developer, pago único) es una excepción conocida y bounded a ese mandato
  **sólo** para habilitar la distribución de una app nativa (iPhone 13 Pro /
  Samsung A17). El análisis de viabilidad **documenta ese coste de distribución
  como coste recurrente** y procede; el mandato de coste 0 € sigue durable y sin
  relajar para todo lo demás.

## Code Style

Deferimos a las configuraciones del proyecto. **Este intent produce prosa de
análisis**, así que la mayor parte del estilo de código aplica sólo si/cuando se
genere código; se documenta como línea base durable.

- **Idioma en el código (durable)**: **identificadores, docstrings y comentarios
  en INGLÉS**; **texto de cara al usuario** (`HTTPException.detail`, prosa de UI)
  y **mensajes de commit** en **CASTELLANO**. En este intent, los **documentos de
  análisis** son prosa de cara al usuario → en castellano, conservando verbatim
  en inglés los nombres de framework (`NativeScript`, `Angular`, `FastAPI`),
  rutas, claves/enums YAML y tokens preservados.
- **Linter/formato (durable, estado del repo)**: backend `ruff` (`ruff.toml`,
  `py312`, `line-length = 100`, `select = ["E","F","I"]`). La **fuente de verdad
  del estado del gate es `ci.yml`**: `ruff check` corre **bloqueante** (`ruff`
  pinned, sin `continue-on-error`) en ambos gates (`ci.yml` job `quality` y
  `fly-deploy.yml` job `verify`). El comentario de cabecera de
  `backend/ruff.toml` quedó **stale** (aún describe modo advisory): se anota como
  **deuda de documentación**, **sin editar ese fichero en este intent de
  análisis**. **NUNCA** `ruff format` en masa ni `--fix` de repo entero sobre
  ficheros brownfield (infla diffs, expone avisos preexistentes e invalida el
  pase de revisión en vuelo) — formatear sólo ficheros nuevos o de forma
  quirúrgica. Frontend: ESLint flat config presente pero advisory/diferido
  (devDependencies no instaladas); Prettier `3.8.1`.
- **No aplica en este intent**: la promoción escalonada advisory→bloqueante de
  linters/audits, el saneamiento de deuda de lint por fichero y el pin de
  versiones de tooling del gate son trabajo de los intents de CI gate-hardening
  (FR11/FR12/FR17.3), **no** de un intent de análisis. No se toca
  `ci.yml`/`fly-deploy.yml`, `ruff.toml`, `pytest.ini` ni `angular.json`.
