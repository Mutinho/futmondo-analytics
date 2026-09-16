# Entities — Optimización del bundle inicial (frontend Angular)

> Stage 3.1 Functional Design · Intent `260914-bundle-optimization` · scope refactor · Minimal.
> Fuente: `requirements.md` (FR1–FR4, NFR1–NFR4) y `codekb/futmondo-analytics/architecture.md` (composición del bundle) como diseño de dominio de facto.
> Este refactor NO introduce entidades de datos de negocio. Las "entidades" aquí son los objetos de **configuración de carga** del frontend que gobiernan qué entra en el chunk inicial. Técnica-agnóstico a nivel de diseño (los nombres de fichero son referencias al código existente, no implementación).

## Sources

- `requirements.md` — FR1 (charts eager→lazy), FR2 (diferir chat/marked), FR3 (precarga con retardo), FR4 (budget), NFR1–NFR4.
- `codekb/futmondo-analytics/architecture.md` — subgrafo de composición del bundle inicial.

```yaml
entities:
  - name: AppBootstrapConfig
    description: >
      La configuración de arranque de la aplicación (ApplicationConfig, hoy en
      app.config.ts), evaluada de forma eager en bootstrapApplication. Determina
      qué providers se cargan en el chunk inicial.
    attributes:
      - name: chartRegistration
        logical_type: enum
        required: true
        allowed_values: [eager-global, lazy-per-route]
        constraints: "Debe ser lazy-per-route tras el refactor (FR1)."
      - name: preloadingStrategy
        logical_type: enum
        required: true
        allowed_values: [preload-all, delayed-idle, no-preload]
        constraints: "Debe ser delayed-idle tras el refactor (FR3, Q2=C)."
      - name: animationsProvider
        logical_type: enum
        required: true
        allowed_values: [async-animations]
        constraints: "Se conserva sin cambios (dependencia de Angular Material)."
    entity_level_constraints:
      - "No debe registrar librerías de gráficos de forma global/eager (invariante del refactor)."
    relationships:
      - "AppBootstrapConfig 1--1 PreloadingPolicy (define su estrategia de precarga)."
      - "AppBootstrapConfig 1--N LazyLoadBoundary (declara las fronteras de carga diferida por ruta)."

  - name: LazyLoadBoundary
    description: >
      Una frontera de carga diferida: un punto donde código y sus dependencias
      pesadas se cargan bajo demanda en lugar de en el arranque. Cada frontera
      corresponde a una ruta lazy o a un componente diferido.
    attributes:
      - name: boundaryId
        logical_type: identifier
        required: true
        unique: true
        constraints: "Ej.: assistant-chat, feature-evolution, feature-stats."
      - name: trigger
        logical_type: enum
        required: true
        allowed_values: [route-navigation, user-action-open-chat, idle-preload]
      - name: deferredDependencies
        logical_type: list
        required: true
        constraints: "Librerías/código que salen del chunk inicial (chart.js, ng2-charts, marked, código del chat)."
      - name: functionalContract
        logical_type: text
        required: true
        constraints: "El comportamiento observable debe ser idéntico al actual tras la carga (NFR2)."
    relationships:
      - "LazyLoadBoundary N--1 AppBootstrapConfig."
      - "LazyLoadBoundary 1--N DeferredLibrary (las dependencias que difiere)."

  - name: DeferredLibrary
    description: >
      Una librería pesada que hoy está en el chunk inicial de forma eager y que
      el refactor mueve a carga diferida. No se sustituye ni se elimina (coste
      0 €, sin cambio funcional): solo cambia CUÁNDO se carga.
    attributes:
      - name: name
        logical_type: string
        required: true
        allowed_values: ["chart.js", "ng2-charts", "marked"]
      - name: currentLoad
        logical_type: enum
        required: true
        allowed_values: [eager-initial]
      - name: targetLoad
        logical_type: enum
        required: true
        allowed_values: [lazy-on-demand]
      - name: realConsumers
        logical_type: list
        required: true
        constraints: "Rutas/componentes que realmente la usan (evolution, stats para charts; chat para marked)."
    relationships:
      - "DeferredLibrary N--1 LazyLoadBoundary."

  - name: BundleBudget
    description: >
      El presupuesto de tamaño del chunk inicial declarado en angular.json
      (configuración de build de producción, type: initial).
    attributes:
      - name: budgetType
        logical_type: enum
        required: true
        allowed_values: [initial]
      - name: maximumError
        logical_type: size
        required: true
        constraints: "Debe restaurarse a 1MB tras recortar las cargas eager (FR4.1)."
      - name: maximumWarning
        logical_type: size
        required: true
        constraints: "Debe fijarse por debajo de 1MB, objetivo ~900kB (FR4.2)."
    entity_level_constraints:
      - "El build de producción debe pasar con estos budgets (FR4.3, NFR1)."
      - "El budget solo se restaura DESPUÉS de recortar las cargas eager (FR4.4)."

  - name: PreloadingPolicy
    description: >
      La política que decide cuándo se precargan los chunks lazy tras el
      arranque. Objeto de diseño que reemplaza PreloadAllModules.
    attributes:
      - name: mode
        logical_type: enum
        required: true
        allowed_values: [delayed-idle]
        constraints: "Precarga tras un periodo de inactividad (FR3.1)."
      - name: idleDelay
        logical_type: duration
        required: false
        constraints: "Periodo de inactividad antes de precargar; valor concreto a decidir en implementación con medición (open question de requirements)."
    entity_level_constraints:
      - "No debe añadir dependencias con coste recurrente (FR3.2, NFR3)."
```

## Resumen del modelo de entidades

El refactor gira sobre cinco objetos de configuración de carga, no sobre datos de negocio:

- **AppBootstrapConfig** es la raíz: hoy carga gráficos y precarga todo de forma eager; el refactor lo cambia a registro lazy de gráficos y precarga con retardo.
- **LazyLoadBoundary** modela cada punto de diferido (chat, rutas de gráficos), y **DeferredLibrary** las tres librerías pesadas que se mueven fuera del inicial (chart.js, ng2-charts, marked) sin sustituirlas.
- **PreloadingPolicy** reemplaza `PreloadAllModules` por precarga con retardo tras inactividad.
- **BundleBudget** es el presupuesto de `angular.json` que se restaura a `maximumError: 1MB` (+ `maximumWarning` ~900 kB) una vez recortadas las cargas eager.

Detalle de reglas en `rules.md`; flujos y transiciones en `functional-spec.md`.
