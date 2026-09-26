# Practices Discovery — Team Practices

**Collaborator:** aidlc-pipeline-deploy-agent

Intent 4 — `260925-ci-gate-hardening` (scope infra, brownfield). RE-RUN sobre
prácticas ya afirmadas: estas 5 secciones parten de la BASELINE de
`aidlc/spaces/default/memory/team.md` y ajustan el matiz al alcance de ESTE
intent (endurecimiento del gate CI/CD: FR11 cobertura backend bloqueante con
ratchet, FR12 linters/audits a bloqueante escalonado, FR17.3 gate de
verificación pre-deploy a coste 0 €, deuda diferida de paridad de cobertura
backend en `verify` y ratchet frontend, FR16 free-tier). **No** es un intent de
fiabilidad backend: el matiz de FR3.2/FR4 de intents previos no aplica aquí.
Las decisiones de la entrevista (Q1–Q6, todas la opción recomendada) están ya
integradas en las cinco secciones.

## Way of Working

Mantenemos **trunk-based development** sobre `main` con ramas cortas y con
prefijo por tipo (`fix/...`, `chore/...`, `feat/...`). La integración pasa por
Merge Request con **gate de CI obligatorio** (`.github/workflows/ci.yml`,
disparo `pull_request` → `main`, job `quality` como required status check); el
push directo a `main` re-ejecuta el gate en el job `verify` de
`fly-deploy.yml` antes de desplegar (los `needs:` no cruzan workflows, por eso
el gate se replica).

- **Estrategia de merge**: **squash-merge** a `main`. Cada MR aterriza como un
  único commit sobre la historia lineal de `main`. Base de worktree `main`,
  destino `main`. (Línea base afirmada; alineada con `org.md`.)
- **Conventional Commits** con scope entre paréntesis y en castellano
  (`chore(ci)`, `chore(backend)`, `test(frontend)`, `chore(aidlc)`).
- **Matiz de este intent (gate hardening, FR11/FR12/FR17.3)**: la intervención
  es **acotada y aditiva sobre configuración de CI/CD y tooling**, no toca
  lógica de negocio ni reescribe código de aplicación. Cada endurecimiento
  (piso de cobertura backend; promoción advisory→bloqueante de un linter/audit;
  unificación/pin de una versión de tooling) va en su **propio commit aislado**
  (`chore(ci)`) con el trinquete fijado explícitamente, de modo que un rollback
  quirúrgico sea trivial si el free tier o el ruido de la base heredada lo
  exigen. El orden respeta la secuenciación del scope: **audits de dependencias
  (pip-audit/npm audit) → lint (`ruff check` backend) → pisos de cobertura**,
  promoviendo lo de mayor señal de seguridad y menor ruido primero. **El piso de
  cobertura backend se fija al FINAL del escalón** (Q6), sobre la suite ya
  estabilizada por el saneamiento de la deuda de lint/audit.

## Walking Skeleton

**No se ejecuta ceremonia de walking skeleton** para este intent (línea base
OFF). El sistema ya está **en producción** con un pipeline Fly.io maduro
(región `cdg`, dos apps, healthcheck `/health`) y un **gate de CI bloqueante ya
operativo** (`gitleaks` + `pytest` + `ng test` en `ci.yml` y en el job `verify`
de `fly-deploy.yml`). El intent endurece un gate existente; no hay ningún
componente ni pipeline que arrancar de cero.

## Testing Posture

- **Methodology**: test-after
- **Ordering**: medir y congelar la señal de cobertura y el estado advisory del gate antes de subir cualquier umbral o promover un check a bloqueante; luego sanear/silenciar quirúrgicamente la deuda heredada que cada promoción reportaría, aplicar cada endurecimiento en su commit `chore(ci)` aislado con el trinquete fijado, y sólo al FINAL del escalón fijar el piso de cobertura backend (`--cov-fail-under`) al valor medido exacto sobre la suite ya estabilizada, verificando en verde en AMBOS gates (PR + job `verify`) sin escribir asserts espejo que pasen siempre.
- **Cobertura backend (FR11)**: hoy `--cov=app` es **observability-only, sin
  piso** (`ci.yml`; `pytest.ini` documenta cobertura como métrica informativa,
  activable con `--cov=app`). Este intent introduce un **piso bloqueante único
  `--cov-fail-under` en `pytest.ini`** (line-coverage total, dentro del mismo
  `addopts` de `pytest` — config, no un paso extra), fijado al **valor medido
  exacto SIN margen** (Q6; medición previa obligatoria) y que sube **sólo por
  trinquete**; nunca se relaja para pasar el gate. Si aparece flapping, se
  arregla el test no-determinista, NUNCA se baja el piso. El piso es
  **line-only** en este intent (no se añade `--cov-branch`); una eventual paridad
  de branch-coverage con el frontend queda fuera de alcance.
- **Paridad de la señal backend (asimetría a CREAR — FR17.3)**: `ci.yml` mide
  `--cov=app` mientras el job `verify` de `fly-deploy.yml` corre `pytest -q`
  **sin `--cov`**. Este intent **cierra la asimetría** llevando la misma
  invocación con cobertura y el mismo piso a `verify`, para que un rojo de
  cobertura no pueda colarse por el push directo a `main`. Esta paridad aterriza
  en el **mismo commit** que introduce el piso en `ci.yml`, o inmediatamente
  después (Q4), para que no exista una ventana en la que el piso viva sólo en el
  PR-gate.
- **Cobertura frontend (SÓLO ratchet — ya tiene paridad de enforcement)**: el
  enforcement vive DENTRO de `ng test` (builder `@angular/build:unit-test` +
  `@vitest/coverage-v8` pin `4.1.11`), con umbrales por métrica en `angular.json`
  (`coverageThresholds`: statements 15 / branches 15 / functions 13 / lines 14),
  y **ambos** workflows (PR-gate y push-gate) ya corren `ng test`. Es decir, el
  frontend **YA tiene paridad de enforcement** entre gates; su única tarea en
  este intent es **subir el ratchet** de esos cuatro umbrales al valor medido. No
  hay paridad frontend que crear (a diferencia del backend); no se debe inducir
  ese trabajo inexistente. `angular.json` es la fuente única de umbral (sin pasos
  extra ni `continue-on-error`).
- **Tooling y coste 0 €**: backend `pytest` + `pytest-cov` desde `backend/` con
  las fixtures fake in-memory de `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`
  SQLite `:memory:`, `clean_jwt_env`, `fake_db`) — sin red, sin BD real, sin
  credenciales/tokens reales (gitleaks escanea también los tests). No se prevén
  dependencias nuevas de test; cualquiera sería OSS y **fijada a versión
  exacta**. Un piso alto con aserciones débiles es peor que uno modesto con
  aserciones reales: la posture test-after se mantiene con specs que aseveran el
  efecto (payload/estado/modo de fallo), nunca `assert True` ni specs espejo.
- **Sin bajar cobertura para pasar el gate**: el ratchet (backend y frontend)
  **sólo sube**; nunca se relaja un umbral/piso existente para hacer pasar el
  gate.

## Deployment

**Desplegamos on-merge a `main`** hacia Fly.io (región `cdg`), sin entorno de
staging separado: el smoke test contra `/health` (5 reintentos, HTTP 200) es la
verificación del release (`.github/workflows/fly-deploy.yml`). Este intent
**endurece el gate de verificación pre-deploy (FR17.3)** pero **no cambia la
topología ni el orden de despliegue**.

- **Topología**: dos apps Fly.io — backend `futmondo-api` (puerto 8000, check
  `/health`) y frontend `futmondo-app` (nginx, check `/`). Base de datos **Neon
  PostgreSQL** (Frankfurt, tier free).
- **Orden de despliegue (cadena `needs:` intacta)**: `verify` (gitleaks +
  `pytest` + `ng test`) → `deploy-backend` → `deploy-frontend` → `smoke-test`
  (`/health`). El endurecimiento de FR17.3 refuerza el CONTENIDO del job
  `verify`, **no** reordena la cadena.
- **Paridad real de gate PR ↔ push a coste 0 € (FR17.3)**: el job `verify` HOY
  **no tiene ningún paso de audit ni de lint** (sólo gitleaks + `pytest -q` sin
  `--cov` + `ng test`). Cerrar la paridad NO es flipear un flag: exige **AÑADIR**
  a `verify` (i) la invocación de `pytest` con cobertura y el mismo piso que
  `ci.yml`, y (ii) los pasos de audit (`pip-audit`/`npm audit`) y lint
  (`ruff check` backend) que se vuelvan bloqueantes, para que un push directo a
  `main` no eluda el gate. Todo con acciones OSS gratuitas.
- **Gitleaks unificado y fijado en ambos gates (Q5)**: hoy `ci.yml` usa
  `gitleaks/gitleaks-action@v3` y `verify` usa `@v2` — dos versiones del mismo
  escáner de secretos hacia `main`. Este intent **unifica gitleaks a una única
  versión y la fija** en ambos workflows (cambio de config aislado, coste 0 €).
  El pin por SHA de las acciones de terceros mutables (`setup-flyctl@master`,
  etc.) se decide en **ci-pipeline**, no se cierra aquí.
- **Crons de coste ~0**: `daily-sync.yml` y `sofascore-sync.yml` (máquinas Fly
  one-shot); este intent **no** cambia el orden de deploy ni los crons.
- **Free tier (FR16, anexo opcional)**: se documenta el consumo dentro de los
  tiers gratuitos (GitHub Actions minutos, Neon free, Fly.io free allowance) y
  se identifican los umbrales que forzarían salir del free tier (p. ej. minutos
  de Actions por el coste añadido de medir cobertura y correr audits/lint en dos
  jobs).
- **Rollback**: runbook documentado (`docs/ROLLBACK.md`); el mecanismo Fly.io es
  redeploy de la release anterior. Cada endurecimiento del gate va en commit
  aislado para rollback quirúrgico.
- **Secretos**: siempre vía `secrets` de GitHub Actions / Fly.io; en CI el
  `JWT_SECRET` es efímero y no productivo (`ci-ephemeral-secret-not-a-real-one`).
- **Restricción dura**: todo en **tiers gratuitos** — coste 0 €.

## Code Style

Deferimos a las configuraciones del proyecto, en **modo escalonado (advisory →
bloqueante)**. Este intent añade sólo lo relevante al endurecimiento del gate.

- **Idioma en el código**: **identificadores, docstrings y comentarios en
  INGLÉS**; **texto de cara al usuario** (`HTTPException.detail`, prosa de UI) y
  **mensajes de commit** en **CASTELLANO**.
- **Promoción escalonada de linters/audits (FR12) — alcance afirmado (Q1)**: hoy
  `ruff check` backend, `pip-audit` y `npm audit` corren en **advisory**
  (`continue-on-error: true`). Este intent los promueve a **bloqueante de forma
  escalonada**: **primero los audits de dependencias**, **luego el lint**
  (`ruff check` backend, como último paso del escalón). **ESLint frontend queda
  EXCLUIDO de este intent como deuda diferida**: hoy `angular-eslint`,
  `@typescript-eslint/*` y `eslint` **no están instalados** como devDependencies
  y `ci.yml` corre `npx ng lint || echo …` (tolerante a su ausencia); volverlo
  bloqueante obligaría a instalar+pinnar esas devDependencies, tocar
  `package.json`/lockfile y disparar la verificación `npm ci` + `ng test` en
  `node:22.22.3`. Para no ampliar la superficie del frontend en un intent infra,
  **NO se tocan las devDependencies del frontend**: su única acción es subir el
  ratchet de cobertura. Cada promoción es un cambio de configuración aislado en
  su propio commit `chore(ci)`, con la deuda de la base heredada saneada o
  silenciada quirúrgicamente ANTES de bloquear.
- **Audits de dependencias (Q2/Q3/Q5)**:
  - **npm audit** bloquea en **`high`** (no critical-only): `high` incluye
    clases explotables (prototype pollution, ReDoS, RCE en transitivas) que
    `critical`-only dejaría pasar. Si `high` genera demasiado ruido heredado de
    golpe, se promueve primero en `critical`, se sanea, y se endurece a `high`
    en un commit posterior — el **trinquete de severidad SÓLO endurece**
    (critical→high), nunca se relaja.
  - **pip-audit** bloquea **todo finding CON fix disponible**; no se intenta un
    corte por severidad numérica (la señal CVSS es inconsistente en las fuentes
    de pip-audit). Los findings **SIN fix** se gobiernan por **allowlist
    versionada** (ver abajo), nunca silenciando el gate.
  - **Auditar el entorno instalado, no los rangos**: `pip-audit` se ejecuta
    **sobre el venv resuelto tras `pip install` (sin `-r`)**, para que el gate
    refleje exactamente lo que se despliega y no findings intermitentes por lo
    que resuelva pip ese día. `requirements.txt` tiene rangos abiertos
    (`requests>=`, `fastapi>=`, `psycopg2-binary>=`, `curl_cffi>=`, `pytest>=`);
    pinnar esa deuda es parte natural del endurecimiento.
  - **Findings sin fix → allowlist versionada y auditada** (Q3): commiteada en
    el repo con ID del advisory/CVE, dependencia+versión, motivo (sin fix
    upstream), fecha y **fecha de caducidad/revisión**, vía
    `pip-audit --ignore-vuln <ID>` y el equivalente versionado en npm. **NUNCA**
    `continue-on-error` permanente ni borrar/silenciar el audit; una entrada
    **caducada vuelve a bloquear**.
- **`ruff` backend** (`backend/ruff.toml`, `target-version = "py312"`,
  `line-length = 100`, `select = ["E","F","I"]`, `ignore = ["E501","E402"]`;
  `E722`/bare-except **ya re-habilitado como advisory** de intents previos;
  `[lint.per-file-ignores]` para `tests/**` y `conftest.py`). La promoción de
  `ruff check` a bloqueante es un cambio de **una sola línea** en `ci.yml`
  (quitar su `continue-on-error: true`), en su propio commit `chore(ci)`, y es el
  **último** paso del escalón de FR12.
- **Deuda de lint pre-bloqueo — cómo se sanea (Q1 OBJECT desarrollador)**: la
  deuda que `ruff check` reporte hoy en advisory se sanea **POR FICHERO de forma
  quirúrgica** o se suprime con **`per-file-ignores` / `# noqa` puntual con
  rationale** ANTES de bloquear. **NUNCA** se acalla ampliando ni reescribiendo
  los god-files (`data_sync_service.py`, `data_manager_v2.py`,
  `assistant_service.py`) ni los routers SQL-en-endpoint, y **NUNCA** con un
  `ruff check --fix` de repo entero. La promoción es config, no refactor de
  oportunidad.
- **Formateo brownfield (regla afirmada, arrastrada)**: **NUNCA** reformatear en
  masa con `ruff format` / Prettier los ficheros heredados; formatear **sólo**
  los ficheros nuevos o de forma quirúrgica, para no inflar diffs, no exponer
  avisos preexistentes ni invalidar el pase de revisión en vuelo. La reviewer
  sólo corre `ruff check` (no `ruff format`). Promover `ruff check` a bloqueante
  **no** implica correr `ruff format` ni `--fix` masivo.
- **Pin de versiones OSS en el gate bloqueante (Q5)**: cualquier dependencia de
  tooling del gate se fija a **versión exacta EN EL PASO QUE LA INSTALA**, no
  sólo se enuncia. En concreto este intent: **pinnar `ruff` y `pip-audit`** (hoy
  `ci.yml` hace `pip install ruff` sin pin) y **pinnar `vitest`** (hoy rango
  abierto `^4.0.8` frente al pin de su plugin `@vitest/coverage-v8 == 4.1.11`,
  que el runner debe emparejar). Un tooling flotante puede introducir reglas
  nuevas que rompan el gate de forma no determinista. Nada de rangos abiertos en
  un check bloqueante (patrón ya seguido con `@vitest/coverage-v8 == 4.1.11` y
  `PyJWT == 2.9.0`).
- **Node**: versión fijada en `.nvmrc` = `22.22.3`. Este intent no toca
  devDependencies del frontend; si un futuro intent lo hiciera, se verifica
  `npm ci` + `ng test` en contenedor `node:22.22.3` antes de pushear.
- **Ubicación de tests / convenciones visibles**: tests backend bajo
  `backend/tests/`; snake_case Python, camelCase TS. Sin árbol de tests paralelo
  nuevo.
