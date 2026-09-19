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
  commit sobre la historia lineal de `main`. (Línea base afirmada; alineada con `org.md`.)
- **Base y destino de worktree**: base `main`, destino `main`.
- **Conventional Commits** con scope entre paréntesis y en castellano
  (`feat(frontend)`, `test(frontend)`, `chore(ci)`, `chore(aidlc)`).
- **Matiz de este intent (cobertura de frontend + pipeline)**: la intervención es
  **acotada y aditiva sobre configuración y specs**, no una reescritura. Retira
  `skipTests: true` de los schematics de lógica en `angular.json` (FR10.1), declara la
  cobertura y sus umbrales en el **target `test` de `angular.json`** (opciones del
  builder `@angular/build:unit-test`, FR10.2), añade el proveedor OSS
  `@vitest/coverage-v8` a versión fijada, siembra specs de la capa `core/` crítica más
  un componente `features/*` de alto valor, y cablea el umbral corrigiendo el comando
  `ng test` en el gate de CI (`ci.yml`) y en el job `verify` (`fly-deploy.yml`, FR17.1).
  NO se reescriben componentes ni servicios de negocio; el objetivo es que la cobertura
  sea **medible y creciente (ratcheting)**, no perfecta de golpe.

## Walking Skeleton

**No se ejecuta ceremonia de walking skeleton** para este intent (línea base OFF; el
sistema ya está en producción con pipeline Fly.io maduro, healthcheck `/health` y un
gate de CI bloqueante ya operativo con `ng test`). El intent es una intervención
acotada sobre infraestructura de tests/pipeline existente (`angular.json`, `ng test`,
`ci.yml`, `fly-deploy.yml`), no un producto nuevo: no hay nada que arrancar de cero.

## Testing Posture

- **Methodology**: test-after
- **Ordering**: sembrar specs de la capa `core/` crítica (servicios + `auth.guard` + `auth.interceptor`) más el componente de puja del mercado -> configurar cobertura en el target `test` de `angular.json` con `coverage.all: true` + `coverage.include: src/app/**` + excludes y umbrales por métrica -> medir la línea base y fijar el umbral inicial por debajo -> cablear el gate corrigiendo el comando `ng test` en `ci.yml` Y en el job `verify`; la suite existente permanece en verde.

Detalle del orden y del encuadre para este intent (aditivo sobre la posture afirmada):

1. **Encuadre — NO es characterization-first.** La posture afirmada previa era
   backend/`sync_prizes`-específica (congelar la producción del premio de un god-file).
   ESTE intent es distinto: **añadir infraestructura de cobertura** a un frontend que
   hoy casi no tiene specs (**2 specs sobre 71 fuentes `*.ts`**, cifra medida por la
   revisión de calidad), no congelar el comportamiento de un artefacto único. El marco
   es **test-after** con un orden seguro de siembra.

2. **Denominador de cobertura (Q1=A — resuelve la objeción principal de calidad).**
   El `tsconfig.spec.json` actual solo incluye `*.spec.ts`, así que la cobertura V8 por
   defecto mediría **únicamente los ficheros ya probados**: un umbral así es
   engañosamente alto y **caería** al sembrar más specs (crece el denominador),
   rompiendo el trinquete. Fijamos el universo de cobertura desde el día 1 en el target
   `test` de `angular.json`:
   - `coverage.all: true`
   - `coverage.include: src/app/**`
   - `coverage.exclude` explícito: `*.spec.ts`, `main.ts`, `*.config.ts`, `environments/*`,
     `*.d.ts`, mocks y barrels.
   El umbral mide el código de la app **completo** desde el principio, para que el
   ratchet sea honesto y no descienda al añadir specs.

3. **Fase siembra (Q4=B — antes de activar el umbral bloqueante).** Escribir specs para
   las piezas transversales críticas primero, replicando el patrón Vitest +
   `@angular/*/testing` ya establecido por los 2 specs existentes
   (`core/interceptors/auth.interceptor.spec.ts`,
   `core/preloading/idle-preloading-strategy.spec.ts`). Alcance de fase 1:
   - **`core/` crítica**: los 10 servicios HTTP de `core/services/*`
     (`analytics`, `assistant`, `auth`, `budget`, `championship`, `evolution`,
     `favorites`, `roster`, `stats`, `sync`), el guard `core/guards/auth.guard.ts`
     (hoy SIN spec) y el interceptor `core/interceptors/auth.interceptor.ts`.
   - **más un componente `features/*` de alto valor**: el **diálogo de puja del mercado**
     (bid-dialog), para validar el patrón de test de componente standalone + signals +
     `HttpClient` antes de que el trinquete empuje a más componentes.
   Prioridad fina (por valor/coste, determinista y sin red): P0 `auth.guard.ts` y
   `auth.service.ts`; P1 servicios HTTP CRUD (`HttpTestingController`); P2
   `assistant.service.ts` (posible no-determinismo por streaming). El resto de
   `features/*` y `shared/*` entra en rondas posteriores del trinquete.

4. **Fase infraestructura + umbral (Q2=A, Q3=A, ratcheting).** Añadir
   `@vitest/coverage-v8` como devDependency **a versión fijada** (cambio de
   `package.json`/`package-lock.json`), declarar `coverage.provider` y
   `coverage.thresholds` en el target `test` de `angular.json`, y fijar un umbral
   **por métrica** (`lines`, `branches`, `functions`, `statements`), NO un único número
   global. El valor inicial se **mide tras la siembra** y se fija **ligeramente por
   debajo** de la línea base medida (colchón de 2–5 puntos para absorber la variabilidad
   de la instrumentación V8), redondeando hacia abajo. `branches`/`functions` detectan
   los tests-espejo sin aserciones (la propia brecha de meaningfulness de FR17.1). El
   umbral es **trinquete manual por MR** (Q3=A): solo sube, revisado a mano cuando la
   cobertura real lo supera; nunca se baja para hacer pasar el gate.

5. **Fase gate (Q5=A — FR17.1, significatividad).** La cobertura **no se hereda sola**:
   hoy `ci.yml` (PR) y el job `verify` de `fly-deploy.yml` (push→`main`) corren
   `ng test --watch=false` **sin** flag de cobertura. Hay que **fijar el comando exacto
   en ambos** para que ejerciten el umbral (p. ej. el flag de cobertura del builder o su
   default en el target `test`), con una **única fuente de umbral** en `angular.json`.
   La brecha de FR17.1 es de **meaningfulness**, no de ejecución: hoy los tests corren
   pero no imponen cobertura ni verifican aserciones significativas. Orden obligado:
   **FR10 → FR17.1**. Los specs sembrados deben tener aserciones reales (payload,
   headers, estado), nunca el anti-patrón `expect(true).toBe(true)`.

Notas y evidencia:

- **Herramientas**: frontend `ng test` con **Vitest** (`^4.0.8`) + `jsdom` (`^25.0.1`)
  vía el builder `@angular/build:unit-test` (`angular.json` → `architect.test.runner:
  vitest`). Proveedor de cobertura a añadir: `@vitest/coverage-v8` (OSS, coste 0 €),
  **fijado a versión exacta y casado en major con `vitest` 4.x** (un mismatch de major
  rompe la instrumentación). Node `22.22.3` (`.nvmrc`, alineado con la línea Node 22 de
  CI). Backend inalterado: `pytest` + `pytest-cov` desde `backend/`.
- **La config de cobertura vive en `angular.json`, no en un `vitest.config` suelto**
  (corrección mecánica de developer O1): el builder `@angular/build:unit-test` lee la
  cobertura y sus umbrales de las `options` del target `test`; un `vitest.config` a mano
  podría quedar fuera del flujo del builder. Fuente única de umbral.
- **Umbral inicial (valor exacto → implementación).** El valor de arranque
  (líneas/ramas/funciones/statements) NO se afirma aquí; se mide tras la siembra de la
  fase 1 y se fija por debajo de la línea base real. Debe ser un piso que la línea base
  ya supere para no romper el gate bloqueante de inmediato.
- **Sin `cov-fail-under` heredado.** Como en backend, no existe piso de cobertura
  bloqueante hoy; el umbral del frontend se introduce como trinquete consciente.
- **Definición mínima de "hecho" (testing) del intent**: `angular.json` deja de nacer
  código de lógica sin spec (`skipTests` retirado de los schematics relevantes),
  `ng test` mide y exige cobertura por métrica contra un umbral con denominador estable,
  y ese umbral bloquea en `ci.yml` y en `verify`; los specs llevan aserciones
  significativas.
- **Gate**: `pytest`, `ng test` (ahora **con cobertura por métrica**) y el escaneo de
  secretos (gitleaks) son **BLOQUEANTES** en CI (PR→`main`) y en `verify` (push→`main`);
  lint (ruff/ESLint) y auditorías de dependencias (pip-audit/npm audit) siguen
  **advisory**. Cualquier paso adicional de reporte de cobertura es **solo
  observabilidad** y nunca lleva `continue-on-error` que sustituya al enforcement dentro
  de `ng test` (guardarraíl de devsecops).
- **Deuda de pipeline DIFERIDA (Q8=A — no cerrada por omisión).** Dos huecos quedan
  fuera del alcance de este intent y se registran como deuda:
  (1) la paridad de la señal de cobertura de **backend** (`--cov`) en el job `verify`
  (hoy `pytest -q` sin `--cov`, mientras `ci.yml` mide con `--cov=app`);
  (2) **SAST/DAST del frontend** (no hay análisis estático de seguridad más allá de
  ESLint advisory). Ambos son preexistentes y se difieren a un futuro diseño de
  pipeline. OJO: la paridad de cobertura del **frontend** SÍ queda cerrada por este
  intent, porque el umbral vive dentro de `ng test` y ese comando corre en ambos
  caminos; la paridad de secretos ya está cerrada (gitleaks bloqueante `@v3` en PR y
  `@v2` en `verify`, sin `continue-on-error`).

## Change Control

<!-- Affirmed by the team. Mode: strict or relaxed. Strict here holds for every intent and cannot be changed from chat. -->

## Deployment

**Desplegamos on-merge a `main`** hacia Fly.io (región `cdg`), sin entorno de staging
separado: el smoke test contra `/health` (5 reintentos, HTTP 200) es la verificación del
release (`.github/workflows/fly-deploy.yml`). Línea base afirmada; ESTE intent **no cambia
la topología ni el orden de despliegue**, solo endurece la señal de calidad previa al deploy.

- **Topología**: dos apps Fly.io — backend `futmondo-api` (puerto 8000, check `/health`) y
  frontend `futmondo-app` (nginx, puerto 80, check `/`). Base de datos **Neon PostgreSQL**
  (Frankfurt, tier free).
- **Orden de despliegue**: `verify` (gitleaks + pytest + `ng test`) → `deploy-backend` →
  `deploy-frontend` → `smoke-test`. Con este intent, `verify` gana la exigencia de cobertura
  del frontend vía el umbral de `ng test` (FR17.1) sin cambiar la cadena `needs:`.
- **Crons de coste ~0**: `daily-sync.yml` (04:30 UTC) y `sofascore-sync.yml` (05:00 UTC) usan
  máquinas Fly one-shot; **no** afectan al frontend ni a su cobertura.
- **Rollback**: runbook documentado (`docs/ROLLBACK.md`); el mecanismo Fly.io es redeploy de
  la release anterior.
- **Secretos**: siempre vía `secrets` de GitHub Actions / Fly.io, nunca literales en el
  workflow (el `JWT_SECRET` efímero de CI es solo un literal de arranque no productivo,
  exigido por el guard NFR1.1). Los specs de auth sembrados usan fakes/dobles, nunca
  secretos ni tokens reales (gitleaks escanea también los `*.spec.ts`).
- **Restricción dura**: todo en **tiers gratuitos** (Neon free, Fly.io free allowance,
  GitHub Actions free) — coste 0 €. El proveedor de cobertura elegido es OSS
  (`@vitest/coverage-v8`), sin servicio de pago (no Codecov/Coveralls); el reporte se
  genera y consume dentro de `ng test` en el runner free-tier.

## Code Style

Deferimos a las configuraciones del proyecto, en **modo escalonado (advisory → bloqueante)**.
Línea base afirmada; ESTE intent añade solo lo relevante a specs y tooling de frontend.

- **Idioma en el código**: **identificadores, docstrings y comentarios en INGLÉS**; **texto
  de cara al usuario** (`HTTPException.detail`, prosa de UI) y **mensajes de commit** en
  **CASTELLANO**. Los specs nuevos llevan docstrings de caracterización con trazas a FR/BR
  (patrón ya usado en los 2 specs existentes).
- **Código nuevo nace con spec (Q6=A / FR10.1)**: se retira `skipTests` de los schematics
  de `service`, `guard`, `interceptor`, `class`, `component` (donde vive el
  comportamiento — HTTP, auth/refresh, estado con signals); se **mantiene**
  `skipTests: true` en `pipe`, `resolver`, `directive` (specs a menudo triviales; en este
  repo hay 1 pipe trivial `money.pipe.ts` y no hay resolvers). Retirar el flag NO genera
  specs retroactivos: solo afecta a ficheros NUEVOS; la deuda de los ~69 ficheros sin spec
  se cubre por la **siembra** de la fase 1, no por el flag.
- **Frontend (TypeScript/Angular 22)**: ESLint flat config (`angular-app/eslint.config.js`)
  **advisory**; `prettier ^3.8.1`. Los specs nuevos siguen el patrón Vitest +
  `@angular/*/testing` de `auth.interceptor.spec.ts` (`TestBed.configureTestingModule` con
  `provideHttpClient(withInterceptors([...]))` + `provideHttpClientTesting()`, mocks por
  `useValue` con `vi.fn()`, `HttpTestingController.expectOne(...).flush(...)` y
  `httpMock.verify()`) e `idle-preloading-strategy.spec.ts` (`vi.useFakeTimers()`). El
  guard `CanActivateFn` se invoca dentro de `TestBed.runInInjectionContext(...)`.
- **Backend (Python 3.12)**: `ruff` (`backend/ruff.toml`) — inalterado por este intent.
- **Node**: versión fijada en `.nvmrc` = `22.22.3` (alineada con la línea Node 22 de CI, que
  usa `node-version: '22'`; `packageManager: npm@11.12.1`). **Verificar `npm ci` + `ng test`
  en local o contenedor `node:22.22.3` antes de pushear** cualquier cambio de
  devDependencies del frontend (añadir `@vitest/coverage-v8` cambia
  `package.json`/`package-lock.json`).
- **Formateo brownfield (matiz frontend, aditivo)**: NUNCA reformatear en masa con
  Prettier/ESLint ficheros existentes al sembrar specs; formatear SOLO los ficheros nuevos
  o de forma quirúrgica, para no inflar diffs ni invalidar el pase de revisión en vuelo
  (equivalente frontend de la regla ya afirmada para `ruff format` en backend).
- **Ubicación de specs**: adyacentes a su fuente (`*.spec.ts` junto al `*.ts`), como los
  specs existentes. No introducir un árbol de tests separado.
- **Umbral de cobertura**: vive en el target `test` de `angular.json` (no disperso, no en
  `vitest.config`); es por métrica y es trinquete (solo sube).
- **Convenciones visibles**: código idiomático por lenguaje (camelCase TS, snake_case Python).
## Forbidden

<!-- Team-specific forbidden patterns -->

## Mandated

<!-- Team-specific mandates -->

## Corrections

<!-- Self-learning loop appends here. -->
