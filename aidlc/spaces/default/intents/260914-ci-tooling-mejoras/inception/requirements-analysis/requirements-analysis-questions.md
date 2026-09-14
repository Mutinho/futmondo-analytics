# Requirements Analysis — Preguntas de clarificación

Intent: `260914-ci-tooling-mejoras` (scope refactor, profundidad Minimal)
Fuente principal: `docs/BACKLOG-mejoras-ci-tooling.md` + CodeKB de `futmondo-analytics`.

Las 5 mejoras (actions GitHub, punycode DEP0040, animaciones Angular 22, Karma→Vitest, Node local) están bien definidas en el backlog. Estas preguntas resuelven decisiones abiertas que fijan el alcance verificable de cada requisito.

---

## Q1. Criterio de "actualizado" para las GitHub Actions (mejora 1)

El backlog pide subir las `actions/*` a majors sobre Node 24 en `ci.yml` y `fly-deploy.yml` (p. ej. `actions/checkout`, `actions/setup-node`). ¿Qué criterio de versión debe cumplir el requisito para considerarse "hecho"?

- A. Subir cada action a su **última major estable** disponible (la que use runtime Node 24), fijada por tag de major (p. ej. `@v5`).
- B. Subir solo lo mínimo para **eliminar el warning de Node 20**, sin forzar la última major si una intermedia ya usa Node 24.
- C. Fijar las actions a **SHA de commit** (pinning por hash) además de subir la major, por seguridad de cadena de suministro.
- D. Igual que A, pero además **eliminar cualquier `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION`** si existiera.
- X. Other (please specify)

[Answer]: D. Igual que A (última major estable por tag de major, runtime Node 24), y además eliminar cualquier ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION si existiera.

---

## Q2. Alcance de la migración de animaciones a la API de Angular 22 (mejora 3)

El backlog pide migrar de `@angular/animations` a `animate.enter` / `animate.leave`. En `app.config.ts` hay `provideAnimationsAsync()`. ¿Cuál es el alcance del requisito?

- A. Migrar **todas** las animaciones existentes a la nueva API y **retirar** `@angular/animations` (y `provideAnimationsAsync()`) si ya no se usa.
- B. Migrar las animaciones a la nueva API pero **conservar** `provideAnimationsAsync()`/dependencia si algún componente aún la necesita.
- C. Solo **eliminar el warning de deprecación** con el cambio mínimo, difiriendo migraciones complejas.
- D. **Descartar** esta mejora en este intent si no hay animaciones reales en uso (verificar primero y, si no las hay, documentar como "sin acción").
- X. Other (please specify)

[Answer]: D. Verificar primero si hay animaciones basadas en la API antigua de @angular/animations. Si NO hay, documentar como "sin acción" (y retirar provideAnimationsAsync()/dependencia si nada la usa). Si SÍ hay, aplicar A: migrar todas a animate.enter/animate.leave y retirar @angular/animations.

---

## Q3. Definición de "hecho" para Karma → Vitest (mejora 4, la de mayor riesgo)

Estado actual: builder `@angular/build:unit-test` con `runner: karma` y `ChromeHeadless`; `karma.conf.js` quedó huérfano. ¿Qué debe cumplir el requisito para cerrarse?

- A. Cambiar a `runner: vitest`, **retirar `karma.conf.js` y las devDependencies de Karma**, y que **toda la suite de tests siga en verde** en local y CI.
- B. Igual que A, pero **conservar `karma.conf.js`** temporalmente como referencia hasta confirmar estabilidad.
- C. Migrar a Vitest **solo si** la suite pasa sin cambios en los tests; si algún test requiere reescritura significativa, **dejar la migración a medias documentada** y no romper CI.
- D. Igual que A, y además **verificar `npm ci` + `ng test` en local (o el lock)** antes de pushear, conforme a la regla de proyecto para no romper el gate de CI.
- X. Other (please specify)

[Answer]: D. Cambiar a runner: vitest, retirar karma.conf.js y las devDependencies de Karma, con toda la suite en verde en local y CI, y verificar npm ci + ng test en local (o el lock) antes de pushear (regla de proyecto).

---

## Q4. Alcance de la mejora de Node local (mejora 5) y secuenciación

El backlog dice alinear Node local a ≥22.22.3 vía nvm (aviso `EBADENGINE`; no afecta a CI). ¿Cómo tratamos esta mejora dentro del intent?

- A. Incluirla como requisito formal: **añadir/actualizar `.nvmrc`** (y documentar en README) para fijar la versión de Node del proyecto; el desarrollador la aplica con nvm.
- B. Incluirla solo como **documentación** (nota en README/CONTRIBUTING) sin `.nvmrc`.
- C. **Alinear también `engines` en package.json** y CI para que local y CI usen la misma versión (reproducibilidad).
- D. Tratarla como **acción manual del desarrollador** fuera del alcance de código (solo se documenta en los requisitos como recomendación, sin artefacto).
- X. Other (please specify)

[Answer]: A. Requisito formal: añadir/actualizar .nvmrc fijando la versión de Node del proyecto (>=22.22.3, o la LTS que use CI) y documentar en README; el desarrollador la aplica con nvm.

---

## Q5. Secuenciación y criterio transversal de "no regresión"

El backlog sugiere secuenciar por riesgo dejando Karma→Vitest al final. ¿Confirmas la secuencia y el criterio transversal de éxito?

- A. Sí: orden **1) actions GitHub → 2) Node local → 3) punycode (verificación) → 4) animaciones → 5) Karma→Vitest**, con el criterio transversal de que **la suite existente permanezca en verde y el pipeline `fly-deploy.yml` siga desplegando** tras cada mejora.
- B. Sí a la secuencia, pero **agrupar en 2-3 PRs/commits** en lugar de uno por mejora.
- C. Prefiero **otra secuencia** (indícala en Other).
- D. Sin preferencia de orden; aplica el criterio de riesgo por defecto (Karma→Vitest al final).
- X. Other (please specify)

[Answer]: A. Orden 1) actions GitHub -> 2) Node local -> 3) punycode (verificación) -> 4) animaciones -> 5) Karma->Vitest, con criterio transversal de que la suite existente permanezca en verde y el pipeline fly-deploy.yml siga desplegando tras cada mejora.

---

## Consolidated Summary Confirmation

Resumen de las decisiones antes de generar los requisitos:

- Mejora 1 (GitHub Actions): subir `actions/*` a su última major estable (runtime Node 24, tag de major) en `ci.yml` y `fly-deploy.yml`; eliminar cualquier `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` si existiera.
- Mejora 2 (punycode DEP0040): resolver/vigilar el warning vía dependencias transitivas; verificación, sin acción directa forzada.
- Mejora 3 (animaciones Angular 22): verificar primero si hay animaciones de la API antigua `@angular/animations`; si las hay, migrar todas a `animate.enter`/`animate.leave` y retirar la dependencia; si no, documentar "sin acción" (y retirar `provideAnimationsAsync()` si nada la usa).
- Mejora 4 (Karma→Vitest): cambiar el builder a `runner: vitest`, retirar `karma.conf.js` y las devDependencies de Karma, con la suite en verde en local y CI; verificar `npm ci` + `ng test` en local (o el lock) antes de pushear.
- Mejora 5 (Node local): añadir/actualizar `.nvmrc` (>=22.22.3 o LTS de CI) y documentar en README.
- Secuencia por riesgo: actions → Node local → punycode → animaciones → Karma→Vitest, dejando la de mayor riesgo al final.
- Criterio transversal de no regresión: tras cada mejora, la suite existente permanece en verde y `fly-deploy.yml` sigue desplegando.
- Restricción global: coste 0€ (solo tiers gratuitos).

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
