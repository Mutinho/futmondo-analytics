# Requisitos — Mejoras de CI/Tooling (`260914-ci-tooling-mejoras`)

> Fase INCEPTION · Etapa Requirements Analysis · Scope `refactor` · Profundidad Minimal
> Fuentes: `docs/BACKLOG-mejoras-ci-tooling.md` (backlog origen), CodeKB de `futmondo-analytics`
> (`business-overview.md`, `architecture.md`, `code-structure.md`), y las respuestas del usuario
> en `requirements-analysis-questions.md`.

## Sources

- Initial description: intent `260914-ci-tooling-mejoras` (`aidlc-state.md#Project`) — las 5 mejoras técnicas de CI/tooling a acometer en un mismo intent, coste 0€, ninguna bloquea el despliegue.
- `[desc]` Backlog origen: `docs/BACKLOG-mejoras-ci-tooling.md` (mejoras 1-5, prioridades, acciones e impacto).
- `[Q1]`–`[Q5]` Respuestas de clarificación: `requirements-analysis-questions.md`.
- CodeKB (brownfield): `architecture.md` (workflows, stack, flujos), `code-structure.md` (builder `@angular/build:unit-test`, `karma.conf.js` huérfano, `app.config.ts` con `provideAnimationsAsync()`), `business-overview.md` (restricción coste 0€).
- `[memory:M1]` Regla de proyecto: coste 0€ (solo tiers gratuitos). `[memory:M2]` Regla de proyecto: verificar `npm ci` + `ng test` en local (o el lock) antes de pushear tras cambiar devDependencies del frontend.

## Análisis de intent (qué se quiere lograr)

El objetivo es **saldar deuda técnica de CI/tooling** del proyecto Futmondo Analytics eliminando avisos de deprecación y modernizando el tooling de test del frontend, **sin cambiar el dominio de negocio ni la funcionalidad de la aplicación** y **sin coste recurrente**. El éxito se mide por la desaparición de los avisos identificados y por que, tras cada cambio, la suite de tests siga en verde y el pipeline de despliegue (`fly-deploy.yml`) siga operativo. Es trabajo de mantenimiento (`refactor`): la suite existente debe permanecer verde y no se añaden funcionalidades.

## Requisitos funcionales

### FR1 — Actualización de GitHub Actions al runtime Node 24
- **FR1.1**: El sistema de CI debe usar versiones de `actions/*` cuyo runtime sea Node 24 en `.github/workflows/ci.yml` y `.github/workflows/fly-deploy.yml`, actualizando cada action a su **última major estable** fijada por tag de major (p. ej. `actions/checkout`, `actions/setup-node`). `[Q1]` `[desc]`
- **FR1.2**: No debe existir la variable `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` en los workflows; si estuviera presente, debe eliminarse. `[Q1]`
- **FR1.3**: Tras la actualización, los workflows deben ejecutarse sin el aviso "Node 20 is being deprecated". `[desc]`
- **Criterio de aceptación**
  - Given los workflows `ci.yml` y `fly-deploy.yml`, When se ejecutan en GitHub Actions tras la actualización, Then ninguna step emite el aviso de deprecación de Node 20 y ninguna action referenciada usa runtime Node 20.
  - Given `fly-deploy.yml`, When se dispara un despliegue, Then el pipeline completa el despliegue en verde (no regresión).

### FR2 — Resolución/vigilancia del DeprecationWarning `punycode` (DEP0040)
- **FR2.1**: El proyecto debe eliminar o, si no es posible sin coste/riesgo, dejar documentada y vigilada la causa del aviso `The punycode module is deprecated (DEP0040)`, que proviene de dependencias transitivas de Node. `[desc]`
- **FR2.2**: La resolución se aborda mediante la actualización de las dependencias que lo arrastran; no requiere reemplazar código propio. `[memory:M1]`
- **FR2.3**: La rama "documentada" solo es admisible cuando se cumplan las dos condiciones: (a) se ha ejecutado la actualización de dependencias que arrastran `punycode` hasta la última versión disponible en tier gratuito, y (b) el aviso persiste por una transitiva que aún no ofrece una versión libre de `punycode`. En ese caso debe registrarse en `dependencies.md` (o en una nota del intent) la cadena transitiva concreta que lo introduce y la versión objetivo que lo eliminaría cuando exista.
- **Criterio de aceptación**
  - Given la ejecución de CI y del build local, When se ejecutan tras el trabajo de dependencias, Then el aviso DEP0040 no aparece; **o bien** aparece y existe la nota de vigilancia de FR2.3 identificando la transitiva responsable y la versión objetivo. En ambos casos sin efecto funcional.

### FR3 — Migración de animaciones a la API de Angular 22 (condicional)
- **FR3.1**: Debe verificarse si la aplicación usa la API antigua de `@angular/animations` (triggers/`transition`/`animate`) más allá del `provideAnimationsAsync()` presente en `app.config.ts`. `[Q2]` `code-structure.md`
- **FR3.2 (si hay animaciones de la API antigua)**: Todas ellas deben migrarse a la nueva API `animate.enter` / `animate.leave` de Angular 22, y `@angular/animations` (y `provideAnimationsAsync()` si ya no se usa) debe retirarse. `[Q2]` `[desc]`
- **FR3.3 (si no hay animaciones de la API antigua)**: La mejora se cierra documentando "sin acción" en los artefactos; adicionalmente, `provideAnimationsAsync()` puede retirarse si ningún componente lo necesita. `[Q2]`
- **FR3.4**: Tras el cambio (migración o retirada), el frontend no debe emitir avisos de deprecación de `@angular/animations`. Nota: el aviso concreto ("@angular/animations is deprecated") figura en el backlog pero no está confirmado en el estado actual (el CodeKB solo registra `provideAnimationsAsync()`); por tanto el criterio se formula como "no introducir ni conservar ningún aviso de deprecación de `@angular/animations`", verificándose contra la salida real de build/test. `[desc]` `code-structure.md`
- **Criterio de aceptación**
  - Given el código del frontend, When se compila/ejecuta tras el trabajo de animaciones, Then la salida de build/test no contiene ningún aviso de deprecación de `@angular/animations` y la suite de tests permanece en verde.
  - Given que no existan animaciones de la API antigua, When se completa la verificación, Then queda registrado "sin acción" con la evidencia de la verificación.

### FR4 — Migración del runner de tests del frontend de Karma a Vitest
- **FR4.1**: El builder `@angular/build:unit-test` del frontend debe configurarse con `runner: vitest` en lugar de `runner: karma`. `[Q3]` `code-structure.md`
- **FR4.2**: Deben retirarse `angular-app/karma.conf.js` y las devDependencies de Karma del frontend. `[Q3]` `[desc]`
- **FR4.3**: Tras la migración, **toda la suite de tests del frontend debe pasar en verde** tanto en local como en CI. `[Q3]`
- **FR4.4**: Antes de pushear el cambio (que toca devDependencies del frontend), debe verificarse `npm ci` + `ng test` en local (o revisarse el lock) para no romper el gate de CI. `[Q3]` `[memory:M2]`
- **FR4.5**: Antes de iniciar la migración debe establecerse y registrarse la **línea base**: ejecutar la suite de tests del frontend con el runner actual (Karma) y confirmar que está en verde. La migración solo se acepta si tras ella la suite pasa al menos el mismo conjunto de tests en verde (no regresión respecto a esa línea base). `[Q3]` `[Q5]`
- **Criterio de aceptación**
  - Given `angular-app`, When se ejecuta `ng test` tras la migración, Then los tests corren con Vitest y la suite pasa en verde, sin residuos de Karma (`karma.conf.js` ni devDependencies de Karma presentes).
  - Given la línea base registrada (suite en verde con Karma), When se compara con el resultado tras migrar a Vitest, Then no hay tests que pasaban antes y fallen después (no regresión).
  - Given un push tras el cambio, When se ejecuta el gate de CI, Then el gate pasa (no regresión respecto a la línea base verde).

### FR5 — Alineación de la versión de Node local
- **FR5.1**: El repositorio debe incluir/actualizar un `.nvmrc` que fije la versión de Node del proyecto en `>=22.22.3` (o la LTS que utilice CI), de modo que `nvm use` alinee el entorno local y elimine el aviso `EBADENGINE`. `[Q4]` `[desc]`
- **FR5.2**: El README debe documentar el uso de `.nvmrc`/nvm para el entorno de desarrollo. `[Q4]`
- **Criterio de aceptación**
  - Given un entorno de desarrollo con nvm, When el desarrollador ejecuta `nvm use` en la raíz del repo, Then Node queda en la versión declarada (`>=22.22.3` o LTS de CI) y no se emite el aviso `EBADENGINE` al instalar/usar los paquetes de Angular 22.

### FR6 — Secuenciación y criterio transversal de no regresión
- **FR6.1**: Las mejoras deben acometerse en orden de menor a mayor riesgo: 1) GitHub Actions (FR1) → 2) Node local (FR5) → 3) punycode (FR2) → 4) animaciones (FR3) → 5) Karma→Vitest (FR4). `[Q5]` `[desc]`
- **FR6.2**: Tras cada mejora, la suite de tests existente debe permanecer en verde y el pipeline `fly-deploy.yml` debe seguir desplegando correctamente. `[Q5]`
- **Criterio de aceptación**
  - Given cada una de las 5 mejoras aplicada de forma incremental, When se ejecutan tests y despliegue, Then no se introduce ninguna regresión (suite verde + despliegue operativo) en ningún paso.

## Requisitos no funcionales

- **NFR1 — Coste**: Ninguna mejora puede introducir gasto recurrente; solo se admiten soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free). `[memory:M1]`
- **NFR2 — No regresión funcional**: El comportamiento de la aplicación (autenticación, mercado, sync, finanzas, analítica) no debe cambiar como consecuencia de estas mejoras; son cambios de CI/tooling y test-runner. `[desc]`
- **NFR3 — Reproducibilidad de entorno**: La versión de Node del proyecto debe quedar declarada de forma versionada (`.nvmrc`) para que local y CI sean coherentes. `[Q4]`
- **NFR4 — Seguridad de CI**: No debe habilitarse el uso de runtimes inseguros de Node en las actions (`ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` prohibido salvo parche temporal explícito, que este intent elimina). `[Q1]`
- **NFR5 — Mantenibilidad del tooling de test**: Tras FR4, el tooling de test del frontend queda en un runner con soporte activo (Vitest), sin ficheros de configuración muertos (`karma.conf.js`). `[desc]`

## Restricciones

- **C1**: Trunk-based, cambios pequeños que se integran a `main`; cada mejora debe dejar `main` en estado desplegable. (Way of Working del proyecto.)
- **C2**: El stack fijo no cambia: Angular 22 / FastAPI / Neon / Fly.io. Estas mejoras operan sobre CI, dependencias de test y configuración de entorno, no sobre la arquitectura.
- **C3**: Coste 0€ (ver NFR1). `[memory:M1]`

## Asunciones

- **A1**: El pipeline `fly-deploy.yml` está actualmente en verde y desplegando (según backlog: "el pipeline pasa en verde"); es la línea base de no regresión. `[desc]`
- **A2**: Existe una versión de cada `action/*` con runtime Node 24 disponible por tag de major en el momento de la implementación. `[assumption]`
- **A3**: La suite de tests del frontend actual pasa en verde con Karma antes de migrar a Vitest. Esta asunción queda **elevada a paso verificable** en FR4.5 (registrar la línea base antes de migrar), no permanece como asunción sin comprobar.
- **A4**: `punycode` (DEP0040) proviene únicamente de dependencias transitivas y no de código propio del proyecto. `[desc]`

## Fuera de alcance

- Cambios funcionales en la aplicación (nuevas features, cambios de negocio).
- `NODE_TLS_REJECT_UNAUTHORIZED=0` en el build de producción (señal de seguridad señalada en `architecture.md`, ajena a estas 5 mejoras).
- Retirada de restos heredados no relacionados (`libsql-experimental`, `nixpacks.toml`), salvo que resulten directamente implicados por la resolución de dependencias de FR2.
- Migración del runner de tests del backend (pytest) — solo aplica al frontend.
- Endurecer `engines` en `package.json` y/o la versión de Node de CI (descartado en Q4 para no arriesgar el pipeline; FR5 se limita a `.nvmrc` + README).
- Agrupación en PRs/commits (decisión de entrega, se resuelve en fases posteriores).

## Preguntas abiertas

- **OQ1** (para Construcción): ¿Existen realmente animaciones basadas en la API antigua de `@angular/animations`? Resuelve la bifurcación FR3.2 vs FR3.3. Se verificará al ejecutar la mejora 3.
- **OQ2** (para Construcción): ¿La migración Karma→Vitest requiere reescribir algún test (p. ej. APIs específicas de Jasmine/Karma) o la suite pasa sin cambios de tests? Afecta al esfuerzo de FR4, no a su definición de "hecho".

## Assumptions & Open Questions

Las asunciones A1–A4 y las preguntas abiertas OQ1–OQ2 anteriores permanecen con su estado epistémico hasta confirmarse en fases posteriores. `None` adicional.
