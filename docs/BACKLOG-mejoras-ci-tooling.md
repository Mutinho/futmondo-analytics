# Mejoras técnicas pendientes — CI / Tooling

> Registro de mejoras detectadas al desbloquear el gate de CI (intent
> `260912-analytics-tests-fix`, 2026-09-14). Son ajenas a ese bugfix y no
> bloquean el despliegue (el pipeline `fly-deploy.yml` pasa en verde). Se anotan
> aquí, fuera de los artefactos de intents ya cerrados, para abordarlas más
> adelante — idealmente como un intent propio de mejoras de CI/tooling.

## Origen
Warnings observados en la ejecución de GitHub Actions tras arreglar los tests de
`AnalyticsService` y sincronizar el frontend. Relacionadas con el trabajo del
intent de análisis (`260911-analisis-mejoras`), pero registradas aparte para no
modificar sus artefactos.

## Backlog

### 1. Node 20 deprecado en GitHub Actions (prioridad: media)
- Los runners avisan: "Node 20 is being deprecated. This workflow is running with
  Node 24 by default." Algunas `actions/*@v4` aún usan el runtime Node 20.
- **Acción**: actualizar las actions a versiones sobre Node 24 (p. ej.
  `actions/setup-node`, `actions/checkout` a sus últimas majors) en `ci.yml` y
  `fly-deploy.yml`. Evitar `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` salvo como
  parche temporal.
- **Impacto**: bajo esfuerzo; coste 0€.

### 2. `punycode` DeprecationWarning (DEP0040) (prioridad: baja)
- `The punycode module is deprecated`. Proviene de dependencias transitivas de Node.
- **Acción**: se resuelve al actualizar las dependencias que lo arrastran; no
  requiere acción directa. Vigilar al subir majors.
- **Impacto**: bajo; sin efecto funcional.

### 3. `@angular/animations` deprecado en Angular 22 (prioridad: media)
- Aviso: "@angular/animations is deprecated. Use `animate.enter` and
  `animate.leave` instead." (https://v22.angular.dev/guide/animations).
- **Acción**: migrar las animaciones a la nueva API cuando se toque la UI.
- **Impacto**: medio esfuerzo si hay animaciones en uso; coste 0€.

### 4. Migrar el runner de tests de frontend: Karma → Vitest (prioridad: media)
- Karma está en modo mantenimiento; el ecosistema Angular avanza hacia Vitest.
- Estado actual: el frontend usa el builder `@angular/build:unit-test` con
  `runner: karma` y `ChromeHeadless`. `karma.conf.js` quedó en el repo pero el
  builder nuevo NO lo lee (se dejó como referencia).
- **Acción**: evaluar `@angular/build:unit-test` con `runner: vitest`; retirar
  `karma.conf.js` y las devDependencies de Karma si la migración se completa.
- **Impacto**: medio esfuerzo; coste 0€ (solo tooling de test).

### 5. Versión de Node local desalineada (prioridad: baja)
- Aviso `EBADENGINE`: entorno local Node v22.22.1 < requerido `^22.22.3` por
  algunos paquetes de Angular 22. No afecta a CI (usa Node más nuevo).
- **Acción**: alinear Node local a ≥22.22.3 (o la LTS que use CI) vía nvm.
- **Impacto**: bajo; solo entorno de desarrollo.

## Notas
- Ninguna de estas mejoras bloquea el despliegue actual.
- Al abordarlas, respetar la regla de proyecto de coste 0€ (solo tiers gratuitos).
- Si se convierten en trabajo formal, abrir un intent AI-DLC (scope `refactor` o
  similar) que las priorice y las trace.

## Relacionado
- Estado verificado de FR10 (cobertura frontend) y FR17 (fiabilidad del
  pipeline): ver `docs/BACKLOG-cobertura-frontend-y-pipeline.md` (2026-09-18).
  El punto nº4 de arriba (Karma → Vitest) ya quedó resuelto según esa
  verificación.
