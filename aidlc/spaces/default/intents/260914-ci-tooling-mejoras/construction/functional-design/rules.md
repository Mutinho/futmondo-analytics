# Business Rules — Mejoras de CI/Tooling

> Etapa Functional Design (Construction) · Intent `260914-ci-tooling-mejoras`.
> "Reglas de negocio" aquí = reglas técnicas verificables de cada mejora. Trazan a FR1-FR6 de `requirements.md`.

```yaml
rules:
  # --- Grupo 1: GitHub Actions (FR1) ---
  - id: BR1.1
    statement: Toda action referenciada por `uses:` en ci.yml y fly-deploy.yml debe usar runtime Node 24.
    category: constraint
    applies_to: GitHubWorkflow.action_refs
    trigger: build/actualización de workflows
    logic: >
      IF una action referenciada usa runtime Node 20 THEN actualizarla a su última major
      estable (fijada por tag de major, p. ej. @v5) que use Node 24.
    on_violation: los workflows emiten el aviso "Node 20 is being deprecated"; considerar la mejora no cumplida.
    source: FR1.1, FR1.3

  - id: BR1.2
    statement: No debe existir ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION en los workflows.
    category: constraint
    applies_to: GitHubWorkflow.unsafe_node_flag
    trigger: revisión de workflows
    logic: IF la variable está presente THEN eliminarla.
    on_violation: incumple NFR4; falla el diseño.
    source: FR1.2, NFR4

  - id: BR1.3
    statement: La actualización cubre específicamente actions/setup-node (v4 -> última major) en ambos workflows; checkout, setup-python y gitleaks ya cumplen.
    category: constraint
    applies_to: GitHubWorkflow.action_refs
    trigger: build de workflows
    logic: >
      IF action == actions/setup-node@v4 THEN subir a la última major estable con Node 24.
      Revisar además superfly/flyctl-actions/setup-flyctl@master y browser-actions/setup-chrome@v1;
      fijar a una major/tag estable si procede sin coste.
    on_violation: queda un runtime Node 20 sin actualizar.
    source: FR1.1

  # --- Grupo 2: punycode DEP0040 (FR2) ---
  - id: BR2.1
    statement: El aviso DEP0040 (punycode) debe eliminarse actualizando las dependencias transitivas que lo arrastran, o documentarse si no es posible sin coste.
    category: policy
    applies_to: FrontendPackageManifest.dependencies, FrontendPackageManifest.devDependencies
    trigger: trabajo de actualización de dependencias
    logic: >
      IF actualizar las dependencias que arrastran punycode elimina el aviso THEN hecho.
      ELSE IF la transitiva no tiene versión libre de punycode en tier gratuito THEN registrar
      la nota de vigilancia en el CodeKB dependencies.md (aidlc/spaces/default/codekb/futmondo-analytics/dependencies.md),
      con la cadena transitiva concreta y la versión objetivo que lo eliminaría.
    on_violation: aviso persistente sin nota de vigilancia en dependencies.md => incumple FR2.3.
    source: FR2.1, FR2.2, FR2.3

  # --- Grupo 3: animaciones Angular 22 (FR3) ---
  - id: BR3.1
    statement: No se migra ninguna animación porque no existe uso de la API antigua de @angular/animations (0 imports, 0 triggers verificados).
    category: constraint
    applies_to: AppProvidersConfig, FrontendPackageManifest.dependencies
    trigger: verificación de animaciones
    logic: IF grep de triggers/imports de @angular/animations == 0 THEN no hay migración; documentar "sin acción".
    on_violation: n/a (hallazgo verificado).
    source: FR3.1, FR3.3

  - id: BR3.2
    statement: provideAnimationsAsync() y la dependencia @angular/animations se conservan porque los requiere Angular Material.
    category: constraint
    applies_to: AppProvidersConfig.provideAnimationsAsync, FrontendPackageManifest.dependencies
    trigger: decisión de retirada del provider
    logic: >
      IF Angular Material está en uso (37 ficheros) y depende del sistema de animaciones THEN
      NO retirar provideAnimationsAsync() ni @angular/animations.
    on_violation: retirar el provider degradaría la UX de Material (ripples, overlays, menús).
    source: FR3.2, FR3.3

  - id: BR3.3
    statement: El diseño documenta el acoplamiento Angular Material <-> sistema de animaciones y deja una observación de vigilancia para versiones futuras.
    category: policy
    applies_to: AppProvidersConfig
    trigger: cierre de la mejora 3
    logic: >
      Documentar que la retención del provider se debe a Material; registrar observación para
      revisar si versiones más nuevas de Angular/Material cambian el acoplamiento o publican guía de migración.
    on_violation: falta de trazabilidad de la decisión.
    source: FR3.4 (decisión de diseño del intent)

  - id: BR3.4
    statement: Tras cerrar la mejora 3, la salida de build/test no debe contener avisos de deprecación de @angular/animations.
    category: validation
    applies_to: GitHubWorkflow, FrontendPackageManifest
    trigger: build/test del frontend
    logic: IF la salida de build/test contiene un aviso de deprecación de @angular/animations THEN la mejora no está cerrada.
    on_violation: aviso presente => revisar.
    source: FR3.4

  # --- Grupo 4: Karma -> Vitest (FR4) ---
  - id: BR4.1
    statement: El builder de test de angular.json debe usar runner vitest en lugar de karma.
    category: constraint
    applies_to: AngularBuildConfig.test.runner
    trigger: migración del runner de test
    logic: IF angular.json test.runner == karma THEN cambiar a vitest (@angular/build:unit-test).
    on_violation: sigue usando Karma.
    source: FR4.1

  - id: BR4.2
    statement: Deben retirarse karma.conf.js y las devDependencies de Karma.
    category: constraint
    applies_to: FrontendPackageManifest.devDependencies
    trigger: migración del runner de test
    logic: >
      IF migración a Vitest completada THEN eliminar angular-app/karma.conf.js y las devDependencies:
      karma, karma-chrome-launcher, karma-coverage, karma-jasmine, karma-jasmine-html-reporter.
      Evaluar jasmine-core y @types/jasmine (retirarlos si Vitest no los usa; conservarlos si algún test los importa).
    on_violation: quedan restos muertos de Karma.
    source: FR4.2

  - id: BR4.3
    statement: Antes de migrar debe registrarse la línea base (suite verde con Karma); tras migrar, la suite pasa al menos el mismo conjunto de tests en verde en local y CI.
    category: validation
    applies_to: AngularBuildConfig, FrontendPackageManifest
    trigger: migración del runner de test
    logic: >
      Registrar resultado de `ng test` con Karma (línea base). Tras migrar, IF algún test que
      pasaba antes falla después THEN regresión: no aceptar. La suite debe estar verde en local y CI.
    on_violation: regresión de tests => bloquea.
    source: FR4.3, FR4.5

  - id: BR4.4
    statement: Antes de pushear el cambio de devDependencies del frontend debe verificarse npm ci + ng test en local (o revisarse el lock).
    category: policy
    applies_to: FrontendPackageManifest
    trigger: antes de push
    logic: IF se cambian devDependencies del frontend THEN ejecutar npm ci + ng test en local (o revisar el lock) antes de pushear.
    on_violation: riesgo de romper el gate de CI (regla de proyecto).
    source: FR4.4 (project.md ## Corrections)

  # --- Grupo 5: Node local (FR5) ---
  - id: BR5.1
    statement: Debe existir un .nvmrc que fije la versión de Node del proyecto en >=22.22.3 (o la LTS de CI).
    category: constraint
    applies_to: NodeVersionPin
    trigger: alineación de entorno local
    logic: IF .nvmrc ausente o versión < 22.22.3 THEN crear/actualizar .nvmrc con la versión objetivo.
    on_violation: persiste el aviso EBADENGINE en local.
    source: FR5.1

  - id: BR5.2
    statement: El README debe documentar el uso de .nvmrc/nvm para el entorno de desarrollo.
    category: policy
    applies_to: NodeVersionPin
    trigger: cierre de la mejora 5
    logic: Añadir nota en README sobre `nvm use` y la versión fijada.
    on_violation: falta de documentación del entorno.
    source: FR5.2

  # --- Transversal (FR6) ---
  - id: BR6.1
    statement: Tras cada mejora, la suite de tests existente permanece en verde y el pipeline fly-deploy.yml sigue desplegando.
    category: validation
    applies_to: GitHubWorkflow, FrontendPackageManifest, AngularBuildConfig
    trigger: tras aplicar cada mejora
    logic: IF tras una mejora la suite falla o el despliegue se rompe THEN regresión: no aceptar.
    on_violation: regresión => bloquea el avance.
    source: FR6.2, NFR2

  - id: BR6.2
    statement: Las mejoras se aplican en orden de menor a mayor riesgo (actions -> Node local -> punycode -> animaciones -> Karma->Vitest).
    category: policy
    applies_to: todas
    trigger: planificación de la aplicación
    logic: Seguir la secuencia por riesgo; Karma->Vitest al final.
    on_violation: n/a (guía de secuenciación).
    source: FR6.1

  - id: BR6.3
    statement: Ninguna mejora introduce gasto recurrente; solo soluciones en tiers gratuitos.
    category: constraint
    applies_to: todas
    trigger: cualquier decisión de dependencia/herramienta
    logic: IF una solución introduce coste recurrente THEN descartarla y buscar alternativa gratuita.
    on_violation: incumple la regla de proyecto de coste 0€.
    source: NFR1 (project.md ## Corrections)
```

## Resumen de reglas

| ID | Mejora | Categoría | Verificación |
|----|--------|-----------|--------------|
| BR1.1–BR1.3 | Actions GitHub | constraint | Sin aviso Node 20; setup-node a última major; sin flag inseguro |
| BR2.1 | punycode | policy | Aviso DEP0040 eliminado o con nota de vigilancia |
| BR3.1–BR3.4 | Animaciones | constraint/validation | Sin migración; provider conservado por Material; acoplamiento documentado; sin aviso de deprecación |
| BR4.1–BR4.4 | Karma→Vitest | constraint/validation | runner vitest; sin restos de Karma; línea base + suite verde; verificación local pre-push |
| BR5.1–BR5.2 | Node local | constraint/policy | .nvmrc presente; README documentado |
| BR6.1–BR6.3 | Transversal | validation/policy | No regresión; secuencia por riesgo; coste 0€ |
