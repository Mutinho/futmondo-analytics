# Entities — Mejoras de CI/Tooling

> Etapa Functional Design (Construction) · Intent `260914-ci-tooling-mejoras` · Scope refactor
> Consume: `requirements.md`. Diseño de dominio de facto: estructura de código existente (CodeKB).

## Nota sobre el modelo de dominio

Este intent **no introduce entidades de dominio ni lógica de negocio nuevas**. Son 5 mejoras de CI/tooling, dependencias y configuración de entorno. No hay modelo de datos, ni persistencia, ni agregados de negocio que diseñar.

Para no dejar el artefacto vacío y mantener la trazabilidad, el "modelo" relevante aquí es el conjunto de **artefactos de configuración** que las mejoras modifican. Se listan como entidades de configuración (no de negocio) para anclar las reglas técnicas de `rules.md` y la especificación de `functional-spec.md`.

```yaml
domain_entities: []   # No hay entidades de dominio de negocio en este intent.

config_artifacts:
  - name: GitHubWorkflow
    description: Ficheros de workflow de GitHub Actions que definen CI y despliegue.
    instances:
      - path: .github/workflows/ci.yml
        role: CI Gate (lint advisory, tests bloqueantes, secret scan bloqueante)
      - path: .github/workflows/fly-deploy.yml
        role: Verify + deploy a Fly.io + smoke test /health
    attributes:
      - name: action_refs
        description: Referencias `uses:` a actions de GitHub, cada una con su tag de versión.
        constraint: cada action referenciada debe usar runtime Node 24 (última major estable por tag de major)
      - name: unsafe_node_flag
        description: Variable ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION.
        constraint: no debe estar presente
    afecta_a: [FR1]

  - name: FrontendPackageManifest
    description: Manifiesto de dependencias del frontend Angular.
    instances:
      - path: angular-app/package.json
    attributes:
      - name: dependencies
        description: Dependencias de runtime (incluye @angular/animations, @angular/material).
      - name: devDependencies
        description: Dependencias de desarrollo (incluye el set de Karma).
      - name: engines
        description: Campo engines (ausente actualmente; fuera de alcance modificarlo — ver requirements Out of Scope).
    afecta_a: [FR2, FR3, FR4]

  - name: AngularBuildConfig
    description: Configuración de build/test de Angular.
    instances:
      - path: angular-app/angular.json
    attributes:
      - name: test.builder
        value_actual: "@angular/build:unit-test"
      - name: test.runner
        value_actual: karma
        value_objetivo: vitest
    afecta_a: [FR4]

  - name: NodeVersionPin
    description: Fichero de versión de Node del proyecto para nvm.
    instances:
      - path: .nvmrc
        estado_actual: ausente
        estado_objetivo: presente, fijando >=22.22.3 (o LTS de CI)
    afecta_a: [FR5]

  - name: AppProvidersConfig
    description: Configuración de providers del bootstrap Angular.
    instances:
      - path: angular-app/src/app/app.config.ts
    attributes:
      - name: provideAnimationsAsync
        estado: presente
        decision: conservar (requerido por Angular Material; sin animaciones propias de la API antigua)
    afecta_a: [FR3]
```

## Resumen

No hay entidades de dominio. Las mejoras operan sobre 5 clases de artefactos de configuración: workflows de GitHub Actions, el manifiesto de dependencias del frontend, la configuración de build/test de Angular, el pin de versión de Node y la configuración de providers de la app. Las relaciones entre ellos son de configuración, no de datos: `AngularBuildConfig.test.runner` y `FrontendPackageManifest.devDependencies` (Karma) cambian juntos en la mejora 4; `AppProvidersConfig.provideAnimationsAsync` y `FrontendPackageManifest.dependencies` (@angular/animations) se conservan juntos en la mejora 3.

Las reglas técnicas verificables por artefacto están en `rules.md`; los flujos de aplicación de cada mejora, en `functional-spec.md`.
