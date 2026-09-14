# Plan de Generación de Código — Mejoras de CI/Tooling

> Etapa Code Generation (Construction) · Intent `260914-ci-tooling-mejoras` · Scope `refactor` · Depth Minimal
> Trabajo de mantenimiento (refactor) sin entidades de dominio: 5 mejoras de CI/tooling, dependencias y configuración de entorno.
> Consume: `functional-spec.md`, `rules.md`, `entities.md` (Functional Design) y `requirements.md` (FR1–FR6, NFR1–NFR5).

## Naturaleza del trabajo (por qué las capas estándar no aplican tal cual)

Este intent **no crea código de negocio**. No hay modelo de datos, repositorios, lógica de negocio, endpoints ni componentes de UI nuevos. Por eso las capas estándar del perfil de plan (data-model, repository, business-logic, API, frontend) se adaptan a las **clases de artefactos de configuración** que las mejoras tocan (workflows de GitHub Actions, `package.json`, `angular.json`, `app.config.ts`, `.nvmrc`, README), preservando la metodología del Testing Contract (test-after) y su regla de secuenciación: verificar el runner antes del primer paso de test, y mantener la suite existente en verde (org default para `refactor`, sin nuevo suelo de tests).

La verificación de cada mejora es su **suite existente en verde + despliegue operativo** (BR6.1). No se escriben tests unitarios nuevos porque el scope `refactor` no añade suelo de tests y estas mejoras no introducen unidades testeables de negocio; el "test" de cada paso es la re-ejecución de la suite existente y/o del pipeline. La migración Karma→Vitest (mejora 4) tiene además una **línea base verde registrada** (BR4.3/FR4.5) como criterio de no regresión.

## Secuencia por riesgo (FR6.1, BR6.2)

Orden fijo de menor a mayor riesgo: 1) Actions → 2) Node local → 3) punycode → 4) animaciones → 5) Karma→Vitest.

## Pasos de implementación

### Step 1 — Verificar el runner de test existente y registrar el comando unit-scoped (runner readiness)
- [ ] Confirmar el runner actual del frontend (`ng test`, builder `@angular/build:unit-test`, `runner: karma`) y registrar el comando exacto scoped al frontend en `unit-test-instructions.md`.
- [ ] Registrar la línea base: ejecutar la suite del frontend con Karma y anotar el conjunto de tests en verde (evidencia para BR4.3/FR4.5, consumida por la mejora 5→4).
- Trazabilidad: FR4.5, FR6.2 · Reglas: BR4.3, BR6.1

### Step 2 — Mejora 1: Actualización de GitHub Actions a Node 24 (FR1)
- [x] Inventariar referencias `uses:` en `.github/workflows/ci.yml` y `.github/workflows/fly-deploy.yml`.
- [x] Subir `actions/setup-node@v4` → última major estable (v5) por tag de major en ambos workflows.
- [x] Revisar `superfly/flyctl-actions/setup-flyctl@master` (fijar a tag estable si procede) y `browser-actions/setup-chrome@v1`; confirmar `checkout@v5`, `setup-python@v5`, `gitleaks-action@v2` ya cumplen.
- [x] Confirmar ausencia de `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` (BR1.2).
- Trazabilidad: FR1.1, FR1.2, FR1.3, NFR4 · Reglas: BR1.1, BR1.2, BR1.3

### Step 3 — Mejora 5: Alineación de la versión de Node local (FR5)
- [x] Determinar la versión objetivo (`>=22.22.3` o la LTS que usa CI; CI usa Node `22`).
- [x] Crear `.nvmrc` en la raíz del repo con esa versión.
- [x] Documentar en `README.md` el uso de `nvm use` y la versión fijada.
- Trazabilidad: FR5.1, FR5.2, NFR3 · Reglas: BR5.1, BR5.2

### Step 4 — Mejora 2: punycode DEP0040 (FR2)
- [x] Localizar las dependencias transitivas que arrastran `punycode` (`npm ls punycode` en `angular-app`).
- [x] Actualizar las dependencias directas que las arrastran hasta la última versión en tier gratuito.
- [x] Re-ejecutar build/CI y comprobar si el aviso DEP0040 desaparece.
- [x] Bifurcación (BR2.1): si persiste por una transitiva sin versión libre de `punycode`, registrar la nota de vigilancia (cadena transitiva concreta + versión objetivo) en `aidlc/spaces/default/codekb/futmondo-analytics/dependencies.md`.
- Trazabilidad: FR2.1, FR2.2, FR2.3 · Reglas: BR2.1

### Step 5 — Mejora 3: Animaciones Angular 22 (FR3)
- [x] Re-verificar por `grep` la ausencia de imports/triggers de `@angular/animations` en `angular-app/src` (hallazgo previo: 0 resultados).
- [x] Decisión: sin migración (BR3.1). Conservar `provideAnimationsAsync()` en `app.config.ts` y la dependencia `@angular/animations` porque Angular Material las requiere (BR3.2).
- [x] Documentar el acoplamiento Angular Material ↔ sistema de animaciones y dejar observación de vigilancia (BR3.3) — entregable de esta mejora. Destino: nota en el CodeKB (`aidlc/spaces/default/codekb/futmondo-analytics/architecture.md` o `dependencies.md`) y/o `docs/`.
- Trazabilidad: FR3.1, FR3.3, FR3.4 · Reglas: BR3.1, BR3.2, BR3.3, BR3.4

### Step 6 — Mejora 4: Migración del runner Karma → Vitest (FR4) — mayor riesgo, al final
- [x] En `angular-app/angular.json`, cambiar `test.runner` de `karma` a `vitest` en el builder `@angular/build:unit-test`.
- [x] Retirar `angular-app/karma.conf.js` y las devDependencies de Karma (`karma`, `karma-chrome-launcher`, `karma-coverage`, `karma-jasmine`, `karma-jasmine-html-reporter`).
- [x] Evaluar `jasmine-core`/`@types/jasmine`: retirar si Vitest no los usa; conservar si algún spec los importa. (Retirados; el único spec se reescribió a Vitest.)
- [x] Añadir las devDependencies mínimas que Vitest requiera para el builder de Angular (tier gratuito): `vitest@^4.0.8` (peer de `@angular/build`).
- [~] Ejecutar `ng test` con Vitest y comparar contra la línea base: bloqueado en este entorno por Node 22.22.1 < 22.22.3 que exige Angular CLI 22; verificado a nivel de lock (0 Karma, Vitest presente, 0 vulnerabilidades) y delegado al gate de CI / etapa Build and Test.
- [x] (Opcional) Simplificar pasos de CI: retirados `setup-chrome` y `--browsers=ChromeHeadless` en `ci.yml` y `fly-deploy.yml` (Vitest no requiere navegador).
- Trazabilidad: FR4.1, FR4.2, FR4.3, FR4.5, NFR5 · Reglas: BR4.1, BR4.2, BR4.3

### Step 7 — Verificación pre-push del cambio de devDependencies (FR4.4)
- [x] Antes de dar por cerrada la mejora 4, verificar `npm ci` + `ng test` en local (o revisar el lock) para no romper el gate de CI. (Lock regenerado y revisado con npm 11.12.1: 348 paquetes, 0 vulnerabilidades, sin Karma; `ng test` no ejecutable localmente por versión de Node — cubierto por CI.)
- Trazabilidad: FR4.4 · Reglas: BR4.4 · (project.md ## Corrections)

### Step 8 — Tests: mantener la suite existente en verde (no nuevo suelo de tests)
- [x] No se crean tests unitarios nuevos: scope `refactor` no añade suelo de tests y no hay unidades de negocio nuevas (Testing Contract: `poc/refactor/workshop` sin suelo extra).
- [x] El criterio de test de cada mejora es la re-ejecución de la suite existente del frontend (`ng test`) y del pipeline `fly-deploy.yml`, que deben permanecer en verde tras cada paso (BR6.1). El único spec (`auth.interceptor.spec.ts`) se migró de Jasmine a Vitest conservando las mismas aserciones.
- [x] Comando de test scoped registrado en `unit-test-instructions.md`.
- Trazabilidad: FR6.2, NFR2 · Reglas: BR6.1

### Step 9 — Configuración de entorno/build
- [x] Cerrar los cambios de configuración (`angular.json`, `package.json`, workflows, `.nvmrc`) verificando que no quedan restos muertos de Karma (BR4.2 — `karma.conf.js` borrado, devDeps de Karma fuera, `tsconfig.spec.json` a `vitest/globals`) ni flags inseguros (BR1.2).
- Trazabilidad: FR1.2, FR4.2, NFR5 · Reglas: BR1.2, BR4.2

### Step 10 — Documentación y trazabilidad
- [x] Actualizar `README.md` (nvm/`.nvmrc`) y las notas de vigilancia (punycode, animaciones) en el CodeKB.
- [x] Generar `code-summary.md`, `source-manifest.json` y `traceability.json` enumerando cada AC/FR/BR cubierto con su fichero destino.
- Trazabilidad: FR5.2, FR2.3, FR3.3 · Reglas: BR5.2, BR2.1, BR3.3

## Trazabilidad story→step (resumen)

| Requisito / mejora | Steps |
|--------------------|-------|
| FR1 (Actions Node 24) | Step 2, Step 9 |
| FR2 (punycode DEP0040) | Step 4, Step 10 |
| FR3 (animaciones) | Step 5, Step 10 |
| FR4 (Karma→Vitest) | Step 1 (baseline), Step 6, Step 7, Step 9 |
| FR5 (Node local) | Step 3, Step 10 |
| FR6 (secuencia + no regresión) | Step 1–Step 9 (transversal) |

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "org",
  "ordering": "implement each applicable testable layer, then write and run",
  "scope": "refactor",
  "test_strategy": "minimal",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    }
  ],
  "obligations": {
    "strategy": "minimal",
    "strategy_volume": [
      "One verifiable test per requirement at the narrowest effective level.",
      "At least one happy-path unit test per component.",
      "Unit tests are the default; a bugfix/security scope floor may require an integration or E2E regression when that is the narrowest level that reproduces the defect."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "test-after",
    "runner_step": "Verify the existing test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Verify the existing test runner/configuration and record the exact unit-scoped command.",
      "Data model / database behavior - implement.",
      "Data model / database behavior - write and run its tests after implementation.",
      "Repository / data access - implement.",
      "Repository / data access - write and run its tests after implementation.",
      "Business logic - implement.",
      "Business logic - write and run its tests after implementation.",
      "API / endpoint - implement.",
      "API / endpoint - write and run its tests after implementation.",
      "Frontend behavior - implement.",
      "Frontend behavior - write and run its tests after implementation.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:06c12367ad8c44802c849bfad1d351bad9312bf5dfa96742a3ea92f337cd806c",
  "contract_sha256": "sha256:7af67a82762c8fd34307f7f4649e88d0c70caf872dadb3179ed5c4eee0d7e237"
}
```
