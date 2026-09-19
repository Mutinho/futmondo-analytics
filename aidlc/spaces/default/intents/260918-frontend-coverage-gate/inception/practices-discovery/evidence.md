# Evidencia — Practices Discovery (RE-RUN) del intent `260918-frontend-coverage-gate`

> Qué inspeccionó cada participante (lead + quality + developer + devsecops), qué se
> infirió, las 8 decisiones de la entrevista y las incertidumbres residuales. Documento
> de integración final del lead pipeline/deploy tras la ronda ciega y la entrevista humana.

## Fuentes inspeccionadas por participante

### Lead (pipeline/deploy)

Línea base afirmada (punto de partida del RE-RUN):
- `aidlc/spaces/default/memory/team.md` — Way of Working (trunk-based, squash a `main`, gate
  de CI bloqueante), Walking Skeleton (OFF), Testing Posture (previa, backend/`sync_prizes`),
  Deployment (on-merge a Fly.io + smoke `/health`), Code Style (escalonado advisory→bloqueante,
  `.nvmrc` 22.22.3, no `ruff format` masivo).
- `aidlc/spaces/default/memory/project.md` — Mandated/Forbidden ya afirmados.
- `aidlc/spaces/default/memory/org.md` y `phases/inception.md` — defaults del framework.

Reverse-engineering codekb (refrescado esta sesión):
- `code-quality-assessment.md` — fuente propietaria del estado de cobertura del frontend:
  FR10.1 (`skipTests: true` global en `angular.json`), FR10.2 (sin config de cobertura ni
  proveedor ni umbrales), FR17.1 (el job `verify` YA corre `ng test --watch=false`
  bloqueante — la brecha es de meaningfulness), secuenciación obligada FR10 → FR17.1.
- `component-inventory.md`, `technology-stack.md`, `architecture.md`, `code-structure.md`,
  `business-overview.md`, `dependencies.md` — inventario del frontend y stack.

Configuración de CI/deploy y build:
- `.github/workflows/ci.yml` (PR→`main`, job `quality`): gitleaks@v3 (BLOQUEANTE) → pytest
  `--cov=app` (BLOQUEANTE) → `npm ci` + `ng test --watch=false` (BLOQUEANTE); ruff/ESLint/
  audits advisory.
- `.github/workflows/fly-deploy.yml` (push→`main`, job `verify`): gitleaks@v2 (BLOQUEANTE) →
  pytest `-q` **sin `--cov`** (BLOQUEANTE) → `npm ci` + `ng test --watch=false` (BLOQUEANTE) →
  deploys → smoke `/health`.
- `angular-app/angular.json`: `skipTests: true` en los 8 schematics; `architect.test` con
  `@angular/build:unit-test`, `runner: vitest`, `tsConfig: tsconfig.spec.json`. Sin bloque
  `coverage`.
- `angular-app/package.json`: sin `@vitest/coverage-v8` ni `istanbul`; `vitest ^4.0.8`,
  `jsdom ^25.0.1`; script `test` = `ng test`.
- `git rev-parse HEAD` → `b2b5a38628339800af210e3ede6698c09f8d2f96`; rama
  `fix/matchday-prizes-tie-split`.

### Support — aidlc-quality-agent (lente de calidad)

Verificó contra evidencia primaria (`ci.yml`, `fly-deploy.yml`, `angular.json`,
`package.json`, `tsconfig.spec.json`, `code-quality-assessment.md`). Aportes integrados:
- **Cifras de partida medidas**: **10** servicios HTTP en `core/services/*`, **1** guard
  (`auth.guard.ts`, sin spec), **1** interceptor (con spec), **2** specs sobre **71** fuentes
  `*.ts`. (Cierra la horquilla "11 servicios / ~71-90 fuentes" del borrador previo.)
- **HUECO CRÍTICO del denominador** (objeción principal): `tsconfig.spec.json` solo incluye
  `*.spec.ts`, por lo que la cobertura por defecto mediría solo lo probado y CAERÍA al
  sembrar → hay que fijar `coverage.all: true` + `coverage.include: src/app/**` + excludes.
- Umbral **por métrica** (`lines`/`statements`/`functions`/`branches`), con arranque asimétrico;
  procedimiento de derivación segura (medir tras siembra, fijar N puntos por debajo).
- Prioridad de siembra P0/P1/P2 y anti-patrón de tests-espejo (aserciones significativas).

### Support — aidlc-developer-agent (lente developer / mecánica)

Aportes integrados:
- **O1 (corrección mecánica de peso)**: la cobertura NO vive en un `vitest.config` suelto;
  este stack usa el builder `@angular/build:unit-test`, y la config va en las `options` del
  **target `test` de `angular.json`**. Un `vitest.config` a mano es frágil.
- **O2**: la cobertura **no se hereda sola**; hay que pasar el flag de cobertura en el comando
  `ng test` de `ci.yml` Y de `verify` (hoy corren `ng test --watch=false` sin cobertura).
- **O3**: `skipTests` de grano fino — retirar en `service`/`guard`/`interceptor`/`class`/
  `component`; conservar en `pipe`/`resolver`/`directive` (specs triviales).
- Confirmación del patrón de test a replicar (`TestBed` + `provideHttpClient(withInterceptors)`
  + `provideHttpClientTesting`; `runInInjectionContext` para el guard; fake timers).
- Verificar que `@vitest/coverage-v8` case en major con `vitest ^4.0.8`.

### Support — aidlc-devsecops-agent (lente seguridad / cadena de suministro)

Aportes integrados:
- **G1**: fijar `@vitest/coverage-v8` a versión exacta (o casada con `vitest` 4.x); un rango
  abierto en la herramienta que mide un gate bloqueante es superficie de suministro innecesaria.
  Paquete oficial del scope `@vitest` ya confiado (menor riesgo de typosquat que `istanbul`).
- **G2**: SAST/DAST del frontend quedan DIFERIDOS y deben registrarse como deuda de pipeline
  (no cerrados por omisión), igual que la paridad `--cov` de backend en `verify`.
- **G3**: los specs de auth NUNCA fijan/loggean secretos ni tokens reales (gitleaks escanea
  `*.spec.ts`); usar fakes/dobles.
- Confirmó que el diseño PRESERVA el gate (añade señal a `ng test`, ya bloqueante; no toca
  gitleaks/pytest) y que gitleaks sigue bloqueante en ambos caminos (@v3 PR / @v2 verify, sin
  `continue-on-error`). Advirtió que un paso de reporte con `continue-on-error` no debe
  sustituir al enforcement dentro de `ng test`.

## Inferencias (consolidadas)

- La brecha real de FR17.1 NO es "el frontend no se prueba antes de producción" (ya se corre
  `ng test` bloqueante en `verify`), sino que esos tests **no imponen cobertura** ni verifican
  aserciones significativas. El umbral vive dentro de `ng test` (config única en `angular.json`)
  y se propaga a `ci.yml` y `verify` **solo si el flag de cobertura queda cableado en el comando
  de ambos**.
- El orden seguro es siembra → denominador estable + proveedor + umbral por métrica bajo → gate,
  porque un umbral por encima de la cobertura real rompería el gate BLOQUEANTE de inmediato.
- Sin denominador estable (`coverage.all` + `include`) el trinquete no es medible: caería al
  sembrar. Es la corrección que resuelve la objeción principal de calidad.

## Decisiones de la entrevista (source of truth)

- **Q1=A** — Denominador: `coverage.all: true` + `coverage.include: src/app/**` + `coverage.exclude`
  explícito (specs, `main.ts`, `*.config.ts`, environments, mocks). Mide toda la app desde el
  principio; el ratchet es honesto.
- **Q2=A** — Umbral **por métrica** (`lines`, `branches`, `functions`, `statements`), medido tras
  la siembra, arrancando ligeramente por debajo de la línea base.
- **Q3=A** — Ratcheting **manual por MR**, revisado; solo sube.
- **Q4=B** — Siembra fase 1: `core/` crítica (servicios + `auth.guard` + `auth.interceptor`)
  **más** el componente de puja del mercado (bid-dialog) para validar el patrón standalone +
  signals + `HttpClient`.
- **Q5=A** — Config en el target `test` de `angular.json`; corregir el comando `ng test` en
  `ci.yml` Y en `verify` para que ambos ejerciten el umbral; fuente única de umbral.
- **Q6=A** — Retirar `skipTests` en `service`, `guard`, `interceptor`, `class`, `component`;
  conservarlo en `pipe`, `resolver`, `directive`.
- **Q7=A,B,C,D,E** — Afirmadas las cinco reglas duras (ver `discovered-rules.md`).
- **Q8=A** — Deferidos y documentados como deuda de pipeline: (1) paridad `--cov` de backend en
  `verify`; (2) SAST/DAST del frontend. No cerrados por omisión.
- **Consolidated Summary Confirmation** — "Looks correct".

## Incertidumbre residual (medible en implementación)

1. **Valores exactos del umbral inicial por métrica**: NO se fijan aquí; se miden corriendo
   `ng test` con cobertura tras la siembra de fase 1 y se fijan por debajo de la base
   (colchón 2–5 pts). Cualquier número afirmado a ciegas sería especulación.
2. **Sintaxis exacta del flag/opción de cobertura del builder Angular 22**: confirmar en
   implementación cómo `@angular/build:unit-test` declara `coverage`/umbrales en el target
   `test` y qué flag pasa `ng test` en CI. El espíritu (config única en `angular.json`) está
   afirmado; la sintaxis exacta se valida al cablear.
3. **Coste de la siembra del bid-dialog**: componente standalone con Material/diálogo; su
   harness es más caro que los servicios HTTP y puede ajustar el orden dentro de la fase 1.

## Deuda de pipeline explícitamente diferida (Q8=A — no cerrada por omisión)

- Paridad de la señal de cobertura de **backend** (`--cov`) en el job `verify` de
  `fly-deploy.yml` (hoy `pytest -q` sin `--cov`).
- **SAST/DAST del frontend** (sin análisis estático de seguridad más allá de ESLint advisory).

La paridad de cobertura del **frontend** SÍ queda cerrada por este intent (umbral dentro de
`ng test`, que corre en ambos caminos). La paridad de escaneo de secretos ya está cerrada
(gitleaks bloqueante @v3 en PR y @v2 en `verify`).
