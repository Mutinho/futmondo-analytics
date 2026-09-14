# Functional Design — Preguntas (functional-design)

Intent: `260914-ci-tooling-mejoras` (scope refactor, profundidad Minimal).
Fuente: `requirements.md` (FR1-FR6), CodeKB e inspección del código actual.

La inspección del código ya resolvió casi todo el diseño (ver `memory.md`). Solo queda una decisión de diseño de alcance genuinamente abierta.

---

## Q1. Diseño de la mejora 3 (animaciones) a la luz de la inspección del código

Hallazgo verificado: el código **no tiene ninguna animación de la API antigua de `@angular/animations`** (0 imports, 0 triggers). El único uso es `provideAnimationsAsync()` en `app.config.ts`. Sin embargo, **Angular Material se usa en 37 ficheros** y su experiencia (ripples, menús, tooltips, overlays, expansion panels) depende del sistema de animaciones que ese provider habilita.

FR3.3 contemplaba retirar `provideAnimationsAsync()` "si nada la usa". Dado que Material sí lo necesita indirectamente, ¿cómo diseñamos FR3?

- A. **Sin acción de migración; conservar** `provideAnimationsAsync()` y `@angular/animations`. Documentar en el diseño que no hay animaciones propias de la API antigua que migrar y que el provider/dependencia se mantienen porque los requiere Angular Material. (Recomendada: es lo correcto y de menor riesgo.)
- B. Retirar `provideAnimationsAsync()` y `@angular/animations`, aceptando revisar/verificar que Material sigue funcionando (mayor riesgo de degradar la UX de Material).
- C. Sin acción ahora y **registrar como observación** para revisar cuando Angular publique una guía de migración de la dependencia de Material.
- X. Other (please specify)

[Answer]: A + matiz de C. Sin acción de migración: conservar provideAnimationsAsync() y @angular/animations porque los requiere Angular Material (0 animaciones propias de la API antigua). Además, documentar explícitamente en el diseño el estado de la dependencia de Material respecto al sistema de animaciones y dejar una observación de vigilancia para revisar si versiones más nuevas de Angular/Material cambian este acoplamiento o publican guía de migración.

---

## Consolidated Summary Confirmation

Resumen del diseño funcional antes de generar los artefactos (entities.md, rules.md, functional-spec.md, traceability.json):

- Naturaleza: 5 mejoras de CI/tooling/dependencias/config. No hay entidades de dominio ni lógica de negocio nuevas; entities.md lo documenta explícitamente (el "modelo" son artefactos de configuración: workflows, package.json/angular.json, .nvmrc). frontend-components.md (UI) no aplica.
- Mejora 1 (actions): objetivo real = subir `actions/setup-node@v4` -> última major (v5) en ci.yml y fly-deploy.yml; checkout/setup-python/gitleaks ya en Node 24; no existe ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION. Revisar también superfly/flyctl-actions/setup-flyctl@master y browser-actions/setup-chrome@v1.
- Mejora 2 (punycode DEP0040): actualizar dependencias transitivas que lo arrastran; rama "documentada" solo con nota de vigilancia (transitiva + versión objetivo).
- Mejora 3 (animaciones): sin migración (0 animaciones de API antigua); conservar provideAnimationsAsync()/@angular/animations por Angular Material (37 ficheros); documentar el acoplamiento Material<->animaciones y dejar observación de vigilancia para versiones futuras.
- Mejora 4 (Karma->Vitest): angular.json test builder pasa a runner: vitest; retirar karma.conf.js y devDependencies de Karma (karma, karma-chrome-launcher, karma-coverage, karma-jasmine, karma-jasmine-html-reporter); línea base verde registrada antes de migrar; suite verde local+CI; verificar npm ci + ng test local antes de pushear.
- Mejora 5 (Node local): crear .nvmrc (>=22.22.3 o LTS de CI) y documentar en README.
- Reglas de negocio (rules.md) = reglas técnicas verificables BRx.y por mejora + criterio transversal de no regresión (suite verde + fly-deploy operativo).
- Secuencia por riesgo: actions -> Node local -> punycode -> animaciones -> Karma->Vitest.
- Coste 0€.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
