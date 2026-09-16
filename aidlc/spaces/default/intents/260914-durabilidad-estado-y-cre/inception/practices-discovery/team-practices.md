# Prácticas del equipo — Futmondo Analytics

> Versión integrada por el lead (aidlc-pipeline-deploy-agent) a partir de la
> evidencia real del repositorio (**brownfield**), las tres contribuciones de
> soporte (calidad, desarrollo, seguridad) y las decisiones de la entrevista
> humana. Cinco secciones con encabezados exactos del protocolo.

## Way of Working

Trabajamos con **trunk-based development** sobre `main`. Las ramas de trabajo son
cortas y con prefijo por tipo (`fix/...`, `chore/...`), como muestra el historial
(`fix/frontend-bundle-budget`, `chore/ci-tooling-mejoras`). La integración a `main`
pasa por Merge Request con **gate de CI obligatorio** (`.github/workflows/ci.yml`,
disparo `pull_request` → `main`); el push directo a `main` re-ejecuta el gate en el
job `verify` antes de desplegar.

- **Estrategia de merge (decisión humana Q1)**: **squash-merge** a `main` al fusionar.
  Cada MR aterriza como un único commit sobre la historia lineal de `main`, alineado
  con el default de `org.md`. (Se resuelve así la divergencia observada del merge
  commit de PR #1 en el historial.)
- **Base y destino de worktree**: base `main`, destino `main`.
- Los mensajes de commit siguen **Conventional Commits** (`feat`, `fix`, `chore`,
  `test`, `ci`, `docs`, `refactor`) con scope entre paréntesis (`fix(frontend)`,
  `test(backend)`), en castellano.
- El versionado del producto se refleja en el frontend (`angular-app` `version 2.1.7`)
  y en mensajes de commit (`v2.1.x`); no hay tags de release automatizados observados.

## Walking Skeleton

**No se ejecuta ceremonia de walking skeleton** para este intent (decisión humana Q2:
OFF). El sistema ya está en producción (pipeline Fly.io maduro, healthcheck `/health`,
red de seguridad de tests de caracterización): no hay nada que arrancar de cero. El
intent `260914-durabilidad-estado-y-cre` es una intervención acotada sobre código
existente (`SessionStore`/`TaskManager`), no un producto nuevo.

## Testing Posture

- **Methodology**: test-after
- **Ordering**: caracterización primero (congelar con tests el comportamiento
  observable actual de `SessionStore`/`TaskManager`, **incluidos los bugs conocidos**,
  antes de refactorizar) y, a continuación, implementar la durabilidad y escribir y
  ejecutar los tests de cada capa (test-after). La suite existente debe permanecer en
  verde.

Detalle del orden de dos fases para este intent (integrado de la contribución de calidad):

1. **Fase caracterización** (antes de tocar `SessionStore`/`TaskManager`): escribir
   tests que congelen el comportamiento actual, *incluido el de fallo* (p. ej. reinicio
   pierde sesión → 403, tarea de sync huérfana tras redeploy, y la divergencia
   comentario↔comportamiento de `_helpers.get_user_futmondo_client`, y el bug de
   precedencia de `is_refresh_token_valid`). Es red de seguridad, no TDD: deben pasar
   contra el código actual.
2. **Fase durabilidad (test-after)**: implementar la persistencia y después escribir los
   tests del *nuevo* contrato (sesión reconstruida tras reinicio, idempotencia de tarea,
   no reintroducir `password` en claro). Los tests de la fase 1 que describían el *fallo*
   se actualizan/retiran de forma deliberada y trazable cuando el comportamiento esperado
   cambia a propósito.

Notas y evidencia adicional:

- **Cobertura (decisión humana Q3)**: el suelo del scope `feature` (80% líneas) queda
  como **referencia global**, no como piso bloqueante adicional. Se **exige** que existan
  tests cubriendo los **caminos nuevos y de error** de las piezas de durabilidad
  (`SessionStore`/`TaskManager`), **sin piso porcentual adicional bloqueante**. La
  cobertura es hoy una métrica consciente (ratcheting diferido), no una omisión: no existe
  `cov-fail-under` / `fail_under` / `coverageThreshold` en el repo.
- **Definición mínima de "hecho" (testing) del intent**: `SessionStore` y `TaskManager`
  pasan de 0 tests a cubiertos en caracterización *antes* del refactor, y con tests del
  nuevo contrato de durabilidad *después*. Sin esa red, el núcleo del intent no se fusiona.
- **Herramientas**: backend `pytest` (`backend/pytest.ini`: `testpaths = tests`,
  `pythonpath = .`, ejecutado desde `backend/`) + `pytest-cov`; frontend `ng test` con
  **Vitest** + `jsdom` vía builder `@angular/build:unit-test`.
- **Patrón de aislamiento reutilizable**: `backend/conftest.py` inyecta fakes de
  `DataManager`/conexión y factories para APIs externas, y la fixture `clean_jwt_env`
  aísla variables de entorno de arranque. El diseño de durabilidad debe seguir el mismo
  patrón: **fakes de la capa de persistencia** (almacén en memoria en el test) en lugar
  de BD Neon real, para tests rápidos, deterministas y sin coste. Cada test crea y limpia
  su propio almacén; nunca comparte estado mutable entre tests.
- **Gate**: los tests (`pytest`, `ng test`) y el escaneo de secretos (gitleaks) son
  **BLOQUEANTES** en CI desde el inicio; lint (ruff/ESLint) y auditorías de dependencias
  (pip-audit/npm audit) son **advisory** en la fase de saneamiento.
- **Hueco/nota conocida (a resolver en diseño de CI, no bloquea esta etapa)**: el job
  `verify` de `fly-deploy.yml` (push→`main`) **no es idéntico** al gate de PR — corre
  `pytest -q` **sin `--cov`** y **sin gitleaks**. Es defensa en profundidad razonable (el
  MR ya gateó), pero implica que un secreto introducido por un push directo a `main` solo
  lo detendría el gate de MR (relevante a FR5). Se apoya en branch protection para forzar
  MRs; formalizar si `verify` debe replicar gitleaks queda para diseño de pipeline.

## Deployment

**Desplegamos on-merge a `main`** hacia Fly.io (región `cdg`), sin entorno de staging
separado: el smoke test contra `/health` es la verificación del release
(`.github/workflows/fly-deploy.yml`).

- **Topología**: dos apps Fly.io — backend `futmondo-api` (puerto 8000, check `/health`)
  y frontend `futmondo-app` (nginx, puerto 80, check `/`). Ambas `min=max=1` máquina,
  `shared-cpu-1x` / 256 MB. Base de datos **Neon PostgreSQL** (Frankfurt, tier free).
- **Orden de despliegue**: `verify` (pytest + ng test) → `deploy-backend` →
  `deploy-frontend` → `smoke-test`. El smoke test reintenta 5 veces contra `/health`
  esperando HTTP 200.
- **Crons de coste ~0**: `daily-sync.yml` (04:30 UTC) y `sofascore-sync.yml` (05:00 UTC)
  usan máquinas Fly one-shot que se crean, ejecutan y destruyen; nunca quedan corriendo.
- **Rollback**: runbook documentado (`docs/ROLLBACK.md`); el mecanismo Fly.io es redeploy
  de la release anterior.
- **Secretos**: los secretos productivos SIEMPRE via `secrets` de GitHub Actions / Fly.io,
  nunca literales en el workflow (el `JWT_SECRET` efímero de `ci.yml` es solo un literal de
  arranque no productivo, exigido por el guard NFR1.1).
- **Restricción dura**: todo se mantiene en **tiers gratuitos** (Neon free, Fly.io free
  allowance, GitHub Actions free) — coste 0 €.

## Code Style

Deferimos a las configuraciones del proyecto, en **modo escalonado (advisory → bloqueante)**:

- **Idioma en el código (decisión humana Q4)**: **identificadores, docstrings y
  comentarios en INGLÉS**; **texto de cara al usuario** (`detail` de `HTTPException`,
  prosa de UI) y **mensajes de commit** en **CASTELLANO**. (Corrige la afirmación previa
  del borrador de "comentarios en castellano": el código real tiene docstrings/comentarios
  en inglés y solo el texto de usuario en castellano.)
- **Backend (Python 3.12)**: `ruff` (`backend/ruff.toml`, `select = ["E", "F", "I"]`,
  `ignore = ["E501", "E402", "E722"]`, `line-length = 100`, `format` con comillas dobles).
  Hoy **advisory** en CI (`continue-on-error`); se pasará a bloqueante tras un formateo
  inicial en commit aislado. Al endurecer, considerar por trinquete la familia `S`
  (flake8-bandit) de ruff para banderas de seguridad de coste 0 € (`assert` en prod,
  `subprocess`/`eval` inseguros, `try/except/pass`).
- **Frontend (TypeScript/Angular 22)**: ESLint flat config (`angular-app/eslint.config.js`,
  `typescript-eslint` + `angular-eslint`, reglas base degradadas a `warn`) — **advisory**;
  `prettier ^3.8.1`. Selectores: directivas prefijo `app` camelCase, componentes prefijo
  `app` kebab-case.
- **Node**: versión fijada en `.nvmrc` = `22.22.3` (alineada con la línea Node 22 de CI);
  verificar build/tests del frontend en local o en contenedor `node:<versión de .nvmrc>`
  antes de pushear cambios de devDependencies.
- **Persistencia y límites de capas (nota brownfield)**: el código actual dispersa SQL
  crudo en auth y routers (`token_store.py`, `routes._auto_detect_championships`,
  `_helpers.get_championship_config`) sin capa repositorio. El nuevo estado durable debe
  implementarse tras una capa de persistencia estrecha (módulo tipo `stores/` o funciones
  repositorio en `services/`), sin ampliar el patrón de SQL-en-router ni los god-files
  existentes (`data_manager_v2.py` ~166 KB, `data_sync_service.py` ~84 KB).
- **Imports**: preferir import estático a nivel de módulo salvo ciclo demostrable; evitar
  `__import__` dinámico (observado en `refresh`).
- **Convenciones visibles**: código idiomático por lenguaje (snake_case Python,
  camelCase TS).

## Sources

- Historial git: `git log --oneline -30`, `git branch -a`, HEAD `8d71c88`.
- CI/CD: `.github/workflows/ci.yml`, `fly-deploy.yml`, `daily-sync.yml`,
  `sofascore-sync.yml`.
- Deploy: `backend/fly.toml` (`futmondo-api`, región `cdg`), `angular-app/fly.toml`
  (`futmondo-app`), `docker-compose.yml`.
- Calidad/estilo: `backend/ruff.toml`, `backend/pytest.ini`, `backend/conftest.py`,
  `angular-app/eslint.config.js`, `.nvmrc`.
- Contribuciones: `contributions/aidlc-{quality,developer,devsecops}-agent.md`.
- Entrevista: `practices-discovery-questions.md` (Q1–Q5).
- CodeKB: `aidlc/spaces/default/codekb/futmondo-analytics/` — `technology-stack.md`,
  `code-quality-assessment.md`, `architecture.md`, `business-overview.md`,
  `code-structure.md`, `dependencies.md`.
- Reglas: `aidlc/spaces/default/memory/project.md` (coste 0 €, CI frontend),
  `aidlc/spaces/default/memory/org.md` (`## Way of Working`, `## Testing Posture`,
  `## Deployment`).
