# Team-Level Rules

> This team's affirmed practices and corrections. Loaded after `org.md` as
> strict-additive guidance; contradictions with broader policy are rejected.
> Populated by the practices-discovery affirmation gate. Edit at the gate,
> not directly.

## Way of Working

Mantenemos **trunk-based development** sobre `main` con ramas cortas y con prefijo
por tipo (`fix/...`, `chore/...`, `feat/...`). La integración pasa por Merge Request
con **gate de CI obligatorio** (`.github/workflows/ci.yml`, disparo `pull_request` →
`main`); el push directo a `main` re-ejecuta el gate en el job `verify` de
`fly-deploy.yml` antes de desplegar.

- **Estrategia de merge**: **squash-merge** a `main`. Cada MR aterriza como un único
  commit sobre la historia lineal de `main`. (Línea base afirmada; alineada con
  `org.md`.)
- **Base y destino de worktree**: base `main`, destino `main`.
- **Conventional Commits** con scope entre paréntesis y en castellano
  (`fix(backend)`, `test(backend)`, `refactor(backend)`, `chore(aidlc)`).
- **Matiz de este intent (premios) — Q1=A**: la mejora del cálculo de premios
  interviene sobre `data_sync_service.sync_prizes()` — un god-file de ~84 KB. El
  trabajo se hace como intervención acotada: **caracterizar primero** el
  comportamiento observable de `sync_prizes` (incluidos bugs conocidos si los
  hubiera), y **EXTRAER la fórmula a una función/módulo estrecho, puro y
  testeable** (sin I/O ni SQL) donde se corrige el cálculo, **sin engordar** el
  god-file `data_sync_service.py` ni el patrón SQL-en-router. `sync_prizes` pasa a
  **orquestar** (ingesta → cálculo puro → persistencia). No hay reescrituras
  grandes.

## Walking Skeleton

**No se ejecuta ceremonia de walking skeleton** para este intent (línea base OFF; el
sistema ya está en producción con pipeline Fly.io maduro, healthcheck `/health` y red de
tests de caracterización). El intent es una intervención acotada sobre código existente
(`sync_prizes` / `team_prizes`), no un producto nuevo: no hay nada que arrancar de cero.

## Testing Posture

- **Methodology**: test-after
- **Ordering**: caracterizar primero `data_sync_service.sync_prizes()` — congelar con
  tests su comportamiento observable actual en **TODAS las ramas (Q2=A)**: premio por
  puntos (`points_prize`, siempre), gating de ronda completa (`round_fully_played`),
  ranking flop/top, MVP, dream-team, jornada adelantada/negativa (pseudo-jornada) y el
  borrado defensivo `DELETE ... NOT IN`, **incluidos los bugs conocidos si los hubiera**
  — y solo después implementar la mejora del cálculo (sobre la función pura extraída) y
  escribir/ejecutar los tests del nuevo contrato (test-after); la suite existente debe
  permanecer en verde.

Detalle del orden de dos fases para este intent:

1. **Fase caracterización (characterization-first, antes de tocar `sync_prizes`)**:
   escribir tests que congelen la **PRODUCCIÓN** del premio en `sync_prizes` (hoy con
   **cobertura directa cero** — GAP CRÍTICO del RE), cubriendo TODAS las ramas de Q2. Es
   red de seguridad, no TDD: deben pasar contra el código actual. Se apoya en dobles/fakes
   de la API Futmondo y de la capa de persistencia (patrón `conftest.py`, almacén en
   memoria) para evitar `time.sleep()` real, llamadas de red y coste. El **CONSUMO** ya está
   caracterizado (`test_finance_characterization.py`); el hueco es la producción.
2. **Fase mejora (test-after)**: implementar la mejora de corrección/fiabilidad del cálculo
   sobre la **función pura extraída** (gating de ronda completa, jornadas adelantadas, modos
   de ranking) y después escribir los tests del *nuevo* contrato.
   **Q3=C — incertidumbre abierta**: **aún NO se sabe si hay bugs de cálculo a corregir**;
   se decide en el análisis de requisitos y la propia caracterización. Por tanto **no se
   afirma que los importes cambien ni que se conserven**. Si en requisitos se decide cambiar
   un comportamiento a propósito, los tests de fase 1 que describan ese comportamiento se
   **retiran/actualizan de forma deliberada y trazable**.

**Separación de responsabilidades al extraer (integrado del OBJECT de developer, aditivo).**
`sync_prizes` mezcla hoy tres responsabilidades: (a) **ingesta** desde la API Futmondo (I/O
con `time.sleep()`), (b) **cálculo puro** de los términos del premio + su gating, y (c)
**persistencia** (UPSERT `ON CONFLICT` + limpieza `DELETE ... NOT IN` sobre `team_prizes`).
La extracción de Q1 separa el **cálculo puro (sin I/O ni SQL)** de ingesta y persistencia,
dejando estas últimas como colaboradores inyectados. Esa separación es la que hace realizable
la caracterización a coste 0 €; sin ella "capa estrecha testeable" queda ambiguo. La mitad de
lectura ya existente (routers → `SELECT`/suma sobre `team_prizes`) **puede quedarse como está,
pero no debe crecer** ni introducir recálculo.

Notas y evidencia:

- **Cobertura**: el suelo del scope `feature` (80% líneas) queda como **referencia global**,
  no como piso bloqueante adicional. Se **exige** que existan tests cubriendo los **caminos
  nuevos y de error** de `sync_prizes` (producción del premio), **sin piso porcentual
  adicional bloqueante**. No existe `cov-fail-under`/`fail_under`/`coverageThreshold` en el
  repo (ratcheting diferido consciente).
- **Definición mínima de "hecho" (testing) del intent**: `sync_prizes` pasa de **0 tests de
  producción** a caracterizado *antes* del cambio, y con tests del nuevo contrato *después*.
  Sin esa red, el núcleo del intent no se fusiona.
- **Herramientas**: backend `pytest` (`backend/pytest.ini`: `testpaths = tests`,
  `pythonpath = .`, ejecutado desde `backend/`) + `pytest-cov`; frontend `ng test` con
  **Vitest** + `jsdom` vía builder `@angular/build:unit-test`.
- **Patrón de aislamiento reutilizable**: `backend/conftest.py` inyecta fakes de
  `DataManager`/conexión y factories para APIs externas; `test_finance_characterization.py`
  ya usa un doble de `DataManagerV2` + `get_db` falso. La caracterización de `sync_prizes`
  debe seguir el mismo patrón: **fake de la API Futmondo** (respuestas de ronda deterministas,
  sin red ni `sleep`) y **fake de la capa de persistencia** (almacén en memoria de
  `team_prizes`). Cada test crea y limpia su propio almacén; nunca comparte estado mutable.
- **Gate**: `pytest`, `ng test` y el escaneo de secretos (gitleaks) son **BLOQUEANTES** en
  CI (PR→`main`) desde el inicio; lint (ruff/ESLint) y auditorías de dependencias
  (pip-audit/npm audit) son **advisory** en la fase de saneamiento.
- **Hueco conocido — paridad `verify`↔gate-de-MR (Q5=A: DIFERIDO)**: el job `verify` de
  `fly-deploy.yml` (push→`main`) corre `pytest -q` **sin `--cov`**, mientras el gate de PR
  (`ci.yml`) sí mide cobertura con `--cov=app`. La **paridad de SEGURIDAD ya está cerrada**:
  gitleaks es BLOQUEANTE en ambos caminos (verificado por devsecops: `@v3` en PR, `@v2` en
  `verify`, ambos sin `continue-on-error`), y por tanto **lo único diferido es la señal de
  cobertura (`--cov`) en `verify`** — que es una decisión de calidad/pipeline, no de
  seguridad. Se **DIFIERE a un futuro diseño de pipeline**, fuera de alcance de este intent;
  queda registrado como deuda de pipeline, no cerrado por omisión.

## Change Control

<!-- Affirmed by the team. Mode: strict or relaxed. Strict here holds for every intent and cannot be changed from chat. -->

## Deployment

**Desplegamos on-merge a `main`** hacia Fly.io (región `cdg`), sin entorno de staging
separado: el smoke test contra `/health` (5 reintentos, HTTP 200) es la verificación del
release (`.github/workflows/fly-deploy.yml`).

- **Topología**: dos apps Fly.io — backend `futmondo-api` (puerto 8000, check `/health`) y
  frontend `futmondo-app` (nginx, puerto 80, check `/`). Base de datos **Neon PostgreSQL**
  (Frankfurt, tier free).
- **Orden de despliegue**: `verify` (gitleaks + pytest + ng test) → `deploy-backend` →
  `deploy-frontend` → `smoke-test`.
- **Crons de coste ~0**: `daily-sync.yml` (04:30 UTC) y `sofascore-sync.yml` (05:00 UTC) usan
  máquinas Fly one-shot que se crean, ejecutan y destruyen. **Nota de premios**: estos crons
  disparan el sync que ejecuta `sync_prizes`; cualquier cambio en la fórmula se ejercita en
  ese camino batch, no en la ruta de lectura.
- **Rollback**: runbook documentado (`docs/ROLLBACK.md`); el mecanismo Fly.io es redeploy de
  la release anterior.
- **Secretos**: siempre vía `secrets` de GitHub Actions / Fly.io, nunca literales en el
  workflow (el `JWT_SECRET` efímero de CI es solo un literal de arranque no productivo,
  exigido por el guard NFR1.1).
- **Restricción dura**: todo en **tiers gratuitos** (Neon free, Fly.io free allowance,
  GitHub Actions free) — coste 0 €.

## Code Style

Deferimos a las configuraciones del proyecto, en **modo escalonado (advisory → bloqueante)**:

- **Idioma en el código**: **identificadores, docstrings y comentarios en INGLÉS**; **texto
  de cara al usuario** (`HTTPException.detail`, prosa de UI) y **mensajes de commit** en
  **CASTELLANO**.
- **Backend (Python 3.12)**: `ruff` (`backend/ruff.toml`, `select = ["E","F","I"]`,
  `ignore = ["E501","E402","E722"]`, `line-length = 100`, `format` con comillas dobles). Hoy
  **advisory** en CI (`continue-on-error`); se pasará a bloqueante tras un formateo inicial en
  commit aislado.
- **Frontend (TypeScript/Angular 22)**: ESLint flat config
  (`angular-app/eslint.config.js`) **advisory**; `prettier ^3.8.1`.
- **Node**: versión fijada en `.nvmrc` = `22.22.3` (alineada con la línea Node 22 de CI);
  verificar build/tests del frontend en local o contenedor `node:<versión de .nvmrc>` antes
  de pushear cambios de devDependencies.
- **Persistencia y límites de capas (nota brownfield, refuerzo para premios)**: el nuevo
  código de premios debe implementarse tras una **capa de persistencia estrecha** (patrón
  `stores/` o funciones repositorio en `services/`), **sin ampliar** el patrón de SQL-en-router
  ni los god-files existentes (`data_manager_v2.py` ~166 KB, `data_sync_service.py` ~84 KB).
  La fórmula extraída de `sync_prizes` no debe engordar el god-file; **el cálculo puro se
  separa de ingesta y persistencia** (I/O y SQL fuera de la función de cálculo), agrupado por
  feature (p. ej. `services/prizes/` con su test adyacente).
- **Naming desambiguador de "puntos" (recomendación; Q6=A lo deja fuera de alcance de
  CAMBIO)**: aunque la deuda existente de la doble semántica de "puntos" y la resolución de
  identidad por nombre en `player_finances` quedan **fuera de alcance de este intent** (no se
  tocan, solo se documentan), el **código NUEVO** de premios debe desambiguar sin ambigüedad:
  reservar `*_points` para la métrica deportiva y `*_prize`/`*_amount` (sufijo monetario) para
  el importe. Es prevención directa de la clase de bug que la caracterización busca congelar,
  no cosmética.
- **Formateo brownfield**: NUNCA correr `ruff format` masivo sobre archivos brownfield ya
  modificados (infla diffs, expone avisos preexistentes e invalida el pase de revisión en
  vuelo). Formatear SOLO los archivos nuevos de la unidad, o de forma quirúrgica.
- **Imports**: preferir import estático a nivel de módulo salvo ciclo demostrable; evitar
  `__import__` dinámico.
- **Convenciones visibles**: código idiomático por lenguaje (snake_case Python, camelCase TS).
## Forbidden

<!-- Team-specific forbidden patterns -->

## Mandated

<!-- Team-specific mandates -->

## Corrections

<!-- Self-learning loop appends here. -->
