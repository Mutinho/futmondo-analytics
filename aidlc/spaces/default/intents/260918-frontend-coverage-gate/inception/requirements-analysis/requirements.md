# Análisis de Requisitos — Frontend Coverage Gate

Intent: `260918-frontend-coverage-gate` (scope `classic`, brownfield). Deriva de FR10 y FR17.1 del plan de mejoras del intent `260911-analisis-mejoras`, con estado base verificado en `docs/BACKLOG-cobertura-frontend-y-pipeline.md` (2026-09-18).

## Fuentes

- `[desc]` Descripción autorizada del proyecto (`project-description.json`): abordar FR10 (cobertura de tests del frontend Angular) y FR17.1 (job `verify` del pipeline con tests significativos); orden FR10 → FR17.1; mantener stack (Angular 22 + Vitest + FastAPI + Neon + Fly.io); sin reescrituras grandes; coste 0 €.
- Estado base verificado: `docs/BACKLOG-cobertura-frontend-y-pipeline.md` (2026-09-18) y el `code-quality-assessment.md` de la ingeniería inversa (artefacto propietario del estado de cobertura del frontend y pipeline).
- Visión de negocio: `business-overview.md` — el intent no añade comportamiento de dominio; su valor es de **protección** (evitar que una regresión en lógica cubierta llegue a producción).
- Arquitectura y estructura: `architecture.md` (flujo build/test + CI/CD `verify`) y `code-structure.md` (estructura de `angular-app/`, schematics, workflows).
- Prácticas afirmadas: `team-practices.md` (Testing Posture test-after; denominador `coverage.all` + `include src/app/**`; umbral por métrica; ratcheting manual solo-arriba; config en `angular.json`; `skipTests` retirado en service/guard/interceptor/class/component; reglas duras; deuda diferida).
- Decisiones de la entrevista de esta etapa (`requirements-analysis-questions.md`): Q1=A, Q2=C, Q3=A, Q4=A, Q5=A.

## Análisis de Intención

El equipo quiere **blindar el frontend Angular con tests significativos y medibles** de forma que el pipeline impida que una regresión en lógica cubierta (p. ej. `auth.interceptor`, servicios `core/*`, `auth.guard`) llegue a producción. No es un producto nuevo ni una reescritura: es una intervención **acotada y aditiva** sobre configuración (`angular.json`), tooling de test (Vitest + proveedor de cobertura) y workflows de CI/CD (`ci.yml`, `fly-deploy.yml`). El objetivo es que la cobertura sea **medible y creciente (ratcheting)**, no perfecta de golpe, y todo a coste 0 €.

Orden obligado: **FR10 → FR17.1** (la significatividad del gate depende de que exista primero la infraestructura de cobertura).

## Requisitos Funcionales

### FR10 — Cobertura de tests del frontend Angular

**FR10.1 — El código de lógica nuevo nace con spec.**
El sistema (schematics de `angular-app/angular.json`) deja de generar código de lógica sin spec: se retira `skipTests: true` de los schematics `service`, `guard`, `interceptor`, `class` y `component`; se **mantiene** `skipTests: true` en `pipe`, `resolver` y `directive` (bajo valor).
- Criterio de aceptación (Given/When/Then):
  - Given `angular.json` con `skipTests: true` global,
    When se retira el flag de los schematics de lógica indicados,
    Then `ng generate service|guard|interceptor|class|component` crea el `*.spec.ts` adyacente, y `ng generate pipe|resolver|directive` no lo crea.
  - Given los ficheros existentes sin spec,
    When se aplica FR10.1,
    Then NO se generan specs retroactivos (el flag solo afecta a ficheros nuevos); la deuda existente se cubre por la siembra (FR10.3), no por el flag.

**FR10.2 — `ng test` mide y exige cobertura por métrica con denominador estable.**
El sistema añade infraestructura de cobertura configurada en el target `test` de `angular.json` (opciones del builder `@angular/build:unit-test`), con el proveedor OSS `@vitest/coverage-v8` a versión fijada (pin exacto, casado en major con `vitest` 4.x).
- FR10.2.1 — Denominador estable: `coverage.all: true` + `coverage.include: src/app/**` + `coverage.exclude` explícito (`*.spec.ts`, `main.ts`, `*.config.ts`, `environments/*`, `*.d.ts`, mocks, barrels). La cobertura mide el código de la app completo desde el día 1.
- FR10.2.2 — Umbral **por métrica** (`lines`, `branches`, `functions`, `statements`) declarado en `angular.json`, NO un único número global.
- FR10.2.3 — Umbral **ratcheting** manual por MR: solo sube; se revisa a mano cuando la cobertura real lo supera; nunca se baja para hacer pasar el gate. El valor inicial se mide tras la siembra (FR10.3) y se fija ligeramente por debajo de la base medida (colchón 2–5 pts). No se afirma un número concreto: el requisito es que exista, sea por métrica y bloquee.
- Criterio de aceptación:
  - Given el proveedor y la config de cobertura en `angular.json`,
    When se ejecuta `ng test` (no-watch),
    Then reporta cobertura por métrica sobre `src/app/**` y falla si alguna métrica cae por debajo de su umbral.
  - Given un intento de bajar un umbral para pasar el gate,
    When se revisa la MR,
    Then se rechaza (ratcheting solo-arriba, regla dura afirmada).

**FR10.3 — Siembra de specs de la capa crítica (habilita un umbral no trivial).**
El sistema siembra specs replicando el patrón Vitest + `@angular/*/testing` existente (`auth.interceptor.spec.ts`, `idle-preloading-strategy.spec.ts`), con aserciones reales (payload, headers, estado), antes de activar el umbral bloqueante.
- FR10.3.1 — **Mínimo duro (P0)**: `core/guards/auth.guard.ts` y `core/services/auth.service.ts` DEBEN tener spec con aserciones significativas antes de activar el umbral bloqueante.
- FR10.3.2 — **Guía priorizada (P1/P2)**: el resto de la fase 1 —los demás servicios HTTP de `core/services/*` (`analytics`, `assistant`, `budget`, `championship`, `evolution`, `favorites`, `roster`, `stats`, `sync`), el `core/interceptors/auth.interceptor.ts` y el componente de puja del mercado (bid-dialog)— se siembra por prioridad y lo empuja el ratcheting en rondas posteriores; no es requisito duro para esta entrega.
- Criterio de aceptación:
  - Given los specs P0 sembrados,
    When se ejecuta `ng test`,
    Then pasan con aserciones reales (no `expect(true).toBe(true)`) y la suite existente permanece en verde.

### FR17.1 — El gate de pipeline exige cobertura significativa del frontend

**FR17.1 — El umbral de cobertura bloquea en ambos caminos de CI.**
El sistema cablea el umbral de `ng test` para que ejerza en `ci.yml` (PR→`main`) **y** en el job `verify` de `fly-deploy.yml` (push→`main`), corrigiendo el comando exacto en ambos (hoy ambos corren `ng test --watch=false` sin flag de cobertura). Fuente única de umbral en `angular.json`.
- FR17.1.1 — Significatividad: la cobertura por métrica (especialmente `branches`/`functions`) actúa como proxy automático contra tests-espejo sin aserciones; se complementa con revisión humana en MR de que los specs llevan aserciones reales. No se añade tooling de lint nuevo (Q1=A).
- FR17.1.2 — Cualquier paso adicional de reporte de cobertura es solo observabilidad y nunca lleva `continue-on-error` que sustituya al enforcement dentro de `ng test`.
- Criterio de aceptación:
  - Given un cambio que rompe lógica cubierta,
    When se abre una PR o se hace push a `main`,
    Then `ng test` falla por métrica de cobertura en `ci.yml` (PR) y en `verify` (push), y el cambio no llega a `deploy-*`.
  - Given el umbral activado,
    When se inspecciona la configuración,
    Then existe una única fuente de umbral en el target `test` de `angular.json`, referenciada por ambos comandos.

## Requisitos No Funcionales

- **NFR1 — Coste 0 €**: toda la solución vive en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free). El proveedor de cobertura es OSS (`@vitest/coverage-v8`); nada de servicios de pago (no Codecov/Coveralls); el reporte se genera y consume dentro de `ng test` en el runner free-tier.
- **NFR2 — Sin reescrituras / cambio acotado**: no se reescriben componentes ni servicios de negocio; la intervención es aditiva sobre `angular.json`, tooling y workflows. Nunca reformatear en masa ficheros existentes al sembrar specs (formateo solo de ficheros nuevos o quirúrgico).
- **NFR3 — Estabilidad del gate**: la suite existente permanece en verde; el umbral inicial arranca por debajo de la base medida para no romper el gate bloqueante de inmediato.
- **NFR4 — Determinismo de tests**: los specs sembrados no usan red ni `sleep`; usan `HttpTestingController`/fakes. Los tests de auth usan fakes/dobles, nunca secretos ni tokens reales (gitleaks escanea `*.spec.ts`).
- **NFR5 — Reproducibilidad de tooling**: verificar `npm ci` + `ng test` en local o contenedor `node:22.22.3` (`.nvmrc`, alineado con la línea Node 22 de CI) antes de pushear cambios de devDependencies del frontend.

## Restricciones

- **C1** — Stack fijo: Angular 22 + Vitest (`^4.0.8`) + `jsdom` (`^25.0.1`) vía builder `@angular/build:unit-test`; FastAPI + Neon + Fly.io. No se cambia la topología ni el orden de despliegue.
- **C2** — La config de cobertura vive en el target `test` de `angular.json`, no en un `vitest.config` suelto (el builder lee la cobertura de las `options` del target).
- **C3** — El proveedor de cobertura se fija a versión exacta y casado en major con `vitest` 4.x (un mismatch de major rompe la instrumentación).
- **C4** — `gitleaks` + `pytest` + `ng test` (ahora con cobertura por métrica) son BLOQUEANTES en CI (PR→`main`) y en `verify` (push→`main`); lint (ruff/ESLint) y auditorías (pip-audit/npm audit) siguen advisory.
- **C5** — Orden obligado FR10 → FR17.1.

## Supuestos

- **A1** `[assumption]` — La línea base de cobertura medida tras la siembra P0 será suficiente para fijar un umbral por métrica que la base ya supere; se validará al medir en implementación.
- **A2** `[assumption]` — El builder `@angular/build:unit-test` de Angular 22 soporta declarar `coverage.provider`, `coverage.all`, `coverage.include/exclude` y `coverage.thresholds` en las `options` del target `test`; la sintaxis exacta se valida al cablear (principio de fuente única ya afirmado).
- **A3** `[assumption]` — Activar el umbral dentro de `ng test` propaga el enforcement a `ci.yml` y `verify` sin tocar la cadena `needs:` del pipeline.

## Fuera de alcance

- Paridad de la señal de cobertura de **backend** (`--cov`) en el job `verify` (hoy `pytest -q` sin `--cov`): deuda de pipeline diferida (Q8=A), no cerrada por omisión.
- **SAST/DAST del frontend**: fuera de alcance; deuda de pipeline diferida.
- Refactor de god-files backend, cálculo de premios, doble semántica de "puntos", resolución de identidad en `player_finances`: fuera de alcance (intents distintos).
- Reescritura o reformateo masivo de componentes/servicios existentes.
- Objetivo de cobertura a medio plazo (p. ej. 80%): puede documentarse como aspiración no bloqueante, pero no es requisito de esta entrega.

## Assumptions & Open Questions

- El valor numérico exacto del umbral inicial por métrica se determina en implementación tras medir la base post-siembra (por diseño, no es un número afirmado aquí).
- La sintaxis precisa de la opción de cobertura del builder Angular 22 (flag CLI vs `options` del target) se confirma al cablear el gate.
- El coste del harness de test del componente bid-dialog (standalone + Material + signals) puede ajustar el orden dentro de la fase 1 (guía P1/P2), sin afectar el mínimo duro P0.
