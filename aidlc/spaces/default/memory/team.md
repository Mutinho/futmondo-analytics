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
  commit sobre la historia lineal de `main`. Base de worktree `main`, destino `main`.
  (Línea base afirmada; alineada con `org.md`.)
- **Conventional Commits** con scope entre paréntesis y en castellano
  (`fix(backend)`, `test(backend)`, `chore(ci)`, `chore(aidlc)`).
- **Matiz de este intent (fiabilidad backend, FR3.2 + FR4)**: la intervención es
  **acotada y aditiva**, no una reescritura. Sigue la secuenciación de dependencia
  del scope-document: **capa de errores (FR3.2) → clientes (FR4) → estado degradado**,
  priorizando dentro de FR4 los puntos de corrupción de datos. El código nuevo vive
  **tras una capa/función estrecha y testeable**; NO se amplían los god-files
  (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router. El
  cambio de contrato de `futmondo_client.py` (de `None`/`bool` a excepción tipada
  propagada) tiene **blast radius alto**: hay que mapear a sus llamadores antes de
  tocarlo.

## Walking Skeleton

**No se ejecuta ceremonia de walking skeleton** para este intent (línea base OFF; el
sistema ya está en producción con pipeline Fly.io maduro, healthcheck `/health` y un
gate de CI bloqueante ya operativo con `pytest` + `ng test`). El intent es una
intervención acotada de fiabilidad sobre código backend existente
(`futmondo_client.py`, `db_connection.py`, `main.py`, migraciones, `sync_step_status.py`),
no un producto nuevo: no hay nada que arrancar de cero.

## Testing Posture

- **Methodology**: test-after
- **Ordering**: caracterizar primero (characterization-first) cada captura brownfield que se vaya a endurecer y el contrato de `futmondo_client._make_request` ANTES de cambiarlo — entregando un **inventario verificable de llamadores** de `_make_request` (Q4) —, luego implementar la taxonomía recuperable/fatal con excepciones tipadas propagadas (migrando el núcleo: `_make_request` + los llamadores donde un `None` no detectado corrompe datos; el resto de llamadores queda como deuda), y sólo después escribir specs significativas que **aseveren el EFECTO** por modo de fallo (recuperable → paso marcado `DEGRADED` y la operación NO falla; fatal → excepción tipada propagada Y sin datos a medias escritos) — nada de `pytest.raises` sin aserción de estado (Q1) —, replicando el patrón de referencia `SofascoreIPBanError` ya caracterizado, con la suite existente en verde en cada paso.
- **Cobertura/tooling (Q5-quality)**: `--cov` se mantiene **observabilidad-only, sin piso** (`cov-fail-under`) en este intent — el ratcheting de cobertura backend sigue diferido. La asimetría de la señal de cobertura entre `ci.yml` (`--cov=app`) y el job `verify` de `fly-deploy.yml` (`pytest -q` sin `--cov`) queda registrada como **deuda diferida**; este intent no introduce piso ni cierra la asimetría.

Detalle del encuadre para este intent (aditivo sobre la posture afirmada):

1. **Marco general — test-after con specs significativas.** Se mantiene la posture
   afirmada del equipo: test-after, specs con aserciones reales (payload, estado,
   modo de fallo), nunca el anti-patrón `expect(true).toBe(true)` / `assert True`.
2. **Characterization-first al endurecer brownfield.** El mandato ya afirmado cubre
   `sync_prizes`, `SessionStore` y `TaskManager`; **se extiende** el mismo principio
   a: (a) cualquier `except Exception` / `except: pass` de la primera oleada FR3.2
   que se vaya a reclasificar (arranque `main.py`, migraciones `scripts/migrate_*`,
   `db_connection.py`), y (b) el **contrato de `futmondo_client._make_request`**
   antes de convertir su `None`/`bool` en excepción tipada — el cambio toca muchos
   llamadores del god-file de sync, así que se congela el comportamiento actual con
   dobles/fakes en memoria antes de tocarlo, **entregando un inventario verificable
   de llamadores** de `_make_request` como artefacto previo a la migración (Q4). La
   migración de contrato cubre el **núcleo** (`_make_request` + los llamadores donde
   un `None` no detectado corrompe datos); el resto de llamadores queda como **deuda**.
2bis. **Floor de aserción significativa por modo de fallo (Q1).** Un spec de fallo NO
   basta con `pytest.raises`: debe aseverar el EFECTO. Recuperable → el paso se marca
   `DEGRADED` vía `sync_step_status.py` **y** la operación no falla; fatal → la
   excepción tipada se propaga **y** no quedan datos a medias escritos (estado de la
   caché/tabla verificado tras el fallo). El anti-patrón prohibido es el spec espejo
   que captura la excepción sin aseverar el efecto lateral (o su ausencia).
3. **Herramientas y coste 0 €.** Backend `pytest` + `pytest-cov` desde `backend/`,
   con las fixtures compartidas de `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`
   SQLite `:memory:` honrando el contrato de `db_connection`, `clean_jwt_env`,
   `fake_db`): **sin red, sin DB real, sin credenciales**. No se prevén dependencias
   nuevas (stdlib suficiente); cualquiera sería OSS y fijada a versión exacta.
4. **Sin bajar cobertura para pasar el gate.** No existe piso de cobertura
   bloqueante backend hoy (`cov-fail-under` diferido); el ratcheting sólo sube y
   nunca se relaja para hacer pasar el gate.
5. **Enforcement de bare-except (`E722`) — decisión afirmada (Q2).** `E722` está hoy
   en `ignore` en `backend/ruff.toml` y `ruff check` es advisory. Este intent
   **re-habilita `E722` como ADVISORY por trinquete**: se quita del `ignore` para que
   `ruff check` lo reporte, **sin** promover ruff a bloqueante. El cambio va en su
   **propio commit aislado** (`chore(ci)`), **sin `--fix` ni `ruff format`**, aislando
   el reflow de la regla afirmada de NO reformatear brownfield en masa. La reviewer
   corre `ruff check` (no `ruff format`).

## Change Control

<!-- Affirmed by the team. Mode: strict or relaxed. Strict here holds for every intent and cannot be changed from chat. -->

## Deployment

**Desplegamos on-merge a `main`** hacia Fly.io (región `cdg`), sin entorno de staging
separado: el smoke test contra `/health` (5 reintentos, HTTP 200) es la verificación del
release (`.github/workflows/fly-deploy.yml`). Línea base afirmada; ESTE intent **no cambia
la topología ni el orden de despliegue**, sólo endurece el manejo de errores/contratos
del backend previos al deploy.

- **Topología**: dos apps Fly.io — backend `futmondo-api` (puerto 8000, check `/health`)
  y frontend `futmondo-app` (nginx, puerto 80, check `/`). Base de datos **Neon PostgreSQL**
  (Frankfurt, tier free); fallback SQLite/Turso.
- **Orden de despliegue**: `verify` (gitleaks + `pytest` + `ng test`) → `deploy-backend` →
  `deploy-frontend` → `smoke-test`. Este intent **no cambia la cadena `needs:`**.
- **Taxonomía recuperable/fatal como principio de release**: un fallo **recuperable**
  degrada y continúa (marcado en `StepStatus.DEGRADED` vía `sync_step_status.py`, sin
  corromper datos); un fallo **fatal** aborta limpio, sin dejar datos a medias. El punto
  de corrupción tras commit (`DELETE FROM team_prizes ... NOT IN (...)` que traga el fallo)
  se endurece hacia el patrón de reemplazo transaccional atómico ya caracterizado.
- **Crons de coste ~0**: `daily-sync.yml` (04:30 UTC) y `sofascore-sync.yml` (05:00 UTC)
  usan máquinas Fly one-shot; ejercitan las rutas de sync que este intent endurece, pero
  **no** cambian el orden de deploy.
- **Rollback**: runbook documentado (`docs/ROLLBACK.md`); el mecanismo Fly.io es redeploy
  de la release anterior.
- **Secretos**: siempre vía `secrets` de GitHub Actions / Fly.io, nunca literales en el
  workflow; los specs de fiabilidad usan fakes/dobles, nunca credenciales ni tokens reales
  (gitleaks escanea también los tests).
- **Restricción dura**: todo en **tiers gratuitos** (Neon free, Fly.io free allowance,
  GitHub Actions free) — coste 0 €.
- **Deuda de pipeline DIFERIDA (fuera de alcance)**: la asimetría de la señal de cobertura
  de backend — `verify` corre `pytest -q` **sin `--cov`** mientras `ci.yml` mide `--cov=app`
  — queda registrada como deuda; este intent no la cierra.

## Code Style

Deferimos a las configuraciones del proyecto, en **modo escalonado (advisory → bloqueante)**.
Línea base afirmada; ESTE intent añade sólo lo relevante al manejo de errores/contratos del
backend.

- **Idioma en el código**: **identificadores, docstrings y comentarios en INGLÉS**; **texto
  de cara al usuario** (`HTTPException.detail`, prosa de UI) y **mensajes de commit** en
  **CASTELLANO**. Los tests nuevos llevan docstrings de caracterización con trazas a FR/BR
  (patrón ya usado en `sync_step_status.py`, `task_service.py`, `sofascore_client.py`).
- **Excepciones tipadas propagadas, no swallow silencioso (FR4)**: el patrón de fallo de
  integración es una **excepción tipada por modo de fallo, propagada**, con
  `except <Typed>: raise` ANTES del `except Exception` genérico; **nunca `return None`
  silencioso** como señal de fallo.
- **Módulo dedicado de errores de integración (Q3)**: las excepciones de integración viven
  en un **módulo estrecho y testeable `integration_errors`** con una **raíz común
  `IntegrationError`**, del que heredan los subtipos por modo de fallo de Sofascore y de
  Futmondo — fuera de los god-files. (Los nombres/subtipos exactos son decisión de
  functional-design; aquí se afirma la práctica de raíz común + módulo dedicado.)
- **Idioma de las excepciones (Q3, aclaración)**: los **mensajes de las excepciones de
  integración internas van en INGLÉS** (son diagnóstico de desarrollador, como el resto de
  identificadores/docstrings); el **texto de cara al usuario** (`HTTPException.detail` en el
  borde HTTP, prosa de UI) va en **CASTELLANO**.
- **Formateo brownfield (regla afirmada, arrastrada)**: NUNCA reformatear en masa con
  `ruff format` los ficheros brownfield ya modificados; formatear SÓLO los ficheros nuevos
  o de forma quirúrgica, para no inflar diffs, no exponer avisos preexistentes ni invalidar
  el pase de revisión en vuelo (la reviewer sólo corre `ruff check`).
- **Backend (Python 3.12)**: `ruff` (`backend/ruff.toml`, `select = ["E","F","I"]`,
  `ignore = ["E501","E402","E722"]`) — advisory en CI. Este intent **re-habilita `E722`
  (bare-except) como ADVISORY por trinquete (Q2)**: se quita `E722` del `ignore` para que
  `ruff check` lo reporte, **sin** promover ruff a bloqueante. El cambio es de **una sola
  línea de config**, en su **propio commit aislado** (`chore(ci)`), **sin `--fix` ni
  `ruff format`**, para aislar el reflow y mantener estable el binding de la fuente reclamada
  de la reviewer.
- **Ubicación de tests**: bajo `backend/tests/` como la suite existente; sin árbol de tests
  paralelo nuevo.
- **Node**: versión fijada en `.nvmrc` = `22.22.3`. Este intent no toca devDependencies del
  frontend, pero la regla afirmada de verificar `npm ci` + `ng test` en `node:22.22.3` antes
  de pushear cualquier cambio de esas dependencias sigue vigente.
- **Convenciones visibles**: código idiomático por lenguaje (snake_case Python, camelCase TS).## Forbidden

<!-- Team-specific forbidden patterns -->

## Mandated

<!-- Team-specific mandates -->

## Corrections

<!-- Self-learning loop appends here. -->
