# Rules — Optimización del bundle inicial (frontend Angular)

> Stage 3.1 Functional Design · Intent `260914-bundle-optimization` · scope refactor · Minimal.
> Fuente: `requirements.md` (FR1–FR4, NFR1–NFR4) y `entities.md`.
> Reglas que formalizan la composición del bundle y las invariantes de "sin cambio funcional".

## Sources

- `requirements.md` — FR1, FR2, FR3, FR4, NFR1, NFR2, NFR3, NFR4.
- `entities.md` — AppBootstrapConfig, LazyLoadBoundary, DeferredLibrary, BundleBudget, PreloadingPolicy.

```yaml
rules:
  - id: BR1.1
    statement: "El registro de Chart.js/ng2-charts no debe ejecutarse de forma eager en el arranque."
    category: constraint
    applies_to: AppBootstrapConfig.chartRegistration
    trigger: "Al componer los providers de arranque de la app."
    logic: "IF chartRegistration == eager-global THEN mover el registro a las rutas/componentes lazy consumidores (evolution, stats)."
    violation_behaviour: "chart.js/ng2-charts permanecen en el chunk inicial; NFR1 no se cumple."
    source: FR1.1

  - id: BR1.2
    statement: "chart.js y ng2-charts no deben formar parte del chunk inicial de producción."
    category: constraint
    applies_to: DeferredLibrary (chart.js, ng2-charts)
    trigger: "Build de producción."
    logic: "IF el desglose de chunks del build incluye chart.js o ng2-charts en 'initial' THEN es una violación."
    violation_behaviour: "El objetivo de tamaño (NFR1) no se alcanza."
    source: FR1.2

  - id: BR1.3
    statement: "Las vistas de gráficos deben seguir renderizando correctamente tras la carga lazy."
    category: validation
    applies_to: LazyLoadBoundary (feature-evolution, feature-stats)
    trigger: "El usuario navega a evolution o stats."
    logic: "IF se navega a una ruta de gráficos THEN Chart.js se carga bajo demanda y el gráfico se renderiza igual que antes."
    violation_behaviour: "Regresión funcional; NFR2 no se cumple."
    source: FR1.3, NFR2

  - id: BR2.1
    statement: "AssistantChatComponent debe cargarse bajo demanda al abrir el chat, no de forma estática desde el arranque."
    category: constraint
    applies_to: LazyLoadBoundary (assistant-chat)
    trigger: "El usuario abre el chat del asistente."
    logic: "IF el chat aún no se ha abierto THEN AssistantChatComponent (y marked) no están cargados; al abrirlo se cargan bajo demanda."
    violation_behaviour: "marked permanece en el chunk inicial (BR2.2 falla)."
    source: FR2.1

  - id: BR2.2
    statement: "marked no debe formar parte del chunk inicial de producción."
    category: constraint
    applies_to: DeferredLibrary (marked)
    trigger: "Build de producción."
    logic: "IF el desglose de chunks del build incluye marked en 'initial' THEN es una violación."
    violation_behaviour: "El objetivo de tamaño (NFR1) no se alcanza."
    source: FR2.2

  - id: BR2.3
    statement: "El chat del asistente debe abrirse y renderizar Markdown correctamente tras su carga bajo demanda."
    category: validation
    applies_to: LazyLoadBoundary (assistant-chat)
    trigger: "El usuario abre el chat y envía/recibe mensajes."
    logic: "IF el chat se abre THEN se carga su código y renderiza Markdown con el mismo saneo/lógica que hoy."
    violation_behaviour: "Regresión funcional; NFR2 no se cumple."
    source: FR2.3, NFR2

  - id: BR3.1
    statement: "La estrategia de precarga debe precargar los chunks lazy tras un periodo de inactividad, no inmediatamente."
    category: policy
    applies_to: PreloadingPolicy
    trigger: "Tras estabilizar la aplicación en el arranque."
    logic: "IF la app ha estabilizado THEN esperar inactividad antes de precargar los chunks lazy (en lugar de PreloadAllModules inmediato)."
    violation_behaviour: "Se mantiene el pico de transferencia inmediato posterior al arranque; NFR4 no se cumple."
    source: FR3.1, NFR4

  - id: BR3.2
    statement: "La estrategia de precarga no debe introducir dependencias con coste recurrente."
    category: constraint
    applies_to: PreloadingPolicy
    trigger: "Elección de mecanismo de precarga."
    logic: "IF se necesita una estrategia de precarga THEN implementarla con el stack actual (PreloadingStrategy propia o equivalente), sin dependencias nuevas de pago."
    violation_behaviour: "Se viola la restricción de coste 0 € (NFR3)."
    source: FR3.2, NFR3

  - id: BR3.3
    statement: "La navegación entre rutas lazy debe seguir funcionando tras el cambio de precarga."
    category: validation
    applies_to: AppBootstrapConfig.preloadingStrategy
    trigger: "El usuario navega entre rutas."
    logic: "IF cambia la estrategia de precarga THEN todas las rutas lazy siguen cargándose y funcionando."
    violation_behaviour: "Regresión de navegación; NFR2 no se cumple."
    source: FR3.3, NFR2

  - id: BR4.1
    statement: "El budget initial debe restaurarse a maximumError 1MB y maximumWarning por debajo de 1MB."
    category: constraint
    applies_to: BundleBudget
    trigger: "Configuración de build de producción en angular.json."
    logic: "IF las cargas eager ya se han recortado THEN fijar maximumError=1MB y maximumWarning~900kB."
    violation_behaviour: "El techo relajado (1.2MB) esconde el peso; el intent no se cumple."
    source: FR4.1, FR4.2, NFR1

  - id: BR4.2
    statement: "El build de producción debe completar sin error con los budgets restaurados."
    category: validation
    applies_to: BundleBudget
    trigger: "ng build (builder @angular/build:application)."
    logic: "IF se ejecuta el build de producción con maximumError=1MB THEN debe pasar (chunk initial < 1MB)."
    violation_behaviour: "Build roto; objetivo NFR1 no alcanzado."
    source: FR4.3, NFR1

  - id: BR4.3
    statement: "Las cargas eager deben recortarse ANTES de restaurar el budget."
    category: policy
    applies_to: [BundleBudget, DeferredLibrary]
    trigger: "Orden de trabajo del refactor."
    logic: "IF se restaura el budget a 1MB antes de recortar (BR1.*, BR2.*) THEN el build de producción falla (fail-closed). Por tanto recortar primero, restaurar después."
    violation_behaviour: "Build de producción roto durante el trabajo."
    source: FR4.4

  - id: BR5.1
    statement: "La suite de tests existente debe seguir verde y debe verificarse manualmente que gráficos y chat funcionan."
    category: validation
    applies_to: "Verificación de no regresión (todo el refactor)"
    trigger: "Tras aplicar los cambios."
    logic: "IF se completan los cambios THEN ng test/vitest debe pasar Y verificación manual de evolution, stats y chat OK."
    violation_behaviour: "Riesgo de regresión no detectada; NFR2 no cumplido."
    source: NFR2

  - id: BR5.2
    statement: "No deben sustituirse ni eliminarse las librerías pesadas; solo cambia cuándo se cargan."
    category: constraint
    applies_to: DeferredLibrary
    trigger: "Cualquier cambio sobre chart.js/ng2-charts/marked."
    logic: "IF se toca una librería pesada THEN solo se cambia su momento de carga (eager→lazy), nunca se sustituye ni se elimina."
    violation_behaviour: "Riesgo de cambio funcional / regresión visual; contradice el intent y coste 0 €."
    source: NFR3, "Out of scope (requirements.md)"
```

## Resumen de reglas

| ID | Categoría | Resumen | Fuente |
|----|-----------|---------|--------|
| BR1.1 | constraint | Registro de charts no eager | FR1.1 |
| BR1.2 | constraint | charts fuera del chunk inicial | FR1.2 |
| BR1.3 | validation | Gráficos siguen renderizando (lazy) | FR1.3, NFR2 |
| BR2.1 | constraint | Chat cargado bajo demanda | FR2.1 |
| BR2.2 | constraint | marked fuera del chunk inicial | FR2.2 |
| BR2.3 | validation | Chat sigue funcionando (lazy) | FR2.3, NFR2 |
| BR3.1 | policy | Precarga con retardo tras inactividad | FR3.1, NFR4 |
| BR3.2 | constraint | Precarga sin dependencias de pago | FR3.2, NFR3 |
| BR3.3 | validation | Navegación lazy sigue funcionando | FR3.3, NFR2 |
| BR4.1 | constraint | Restaurar maximumError 1MB + warning <1MB | FR4.1, FR4.2, NFR1 |
| BR4.2 | validation | Build de producción pasa | FR4.3, NFR1 |
| BR4.3 | policy | Recortar antes de restaurar budget | FR4.4 |
| BR5.1 | validation | Suite verde + verificación manual | NFR2 |
| BR5.2 | constraint | No sustituir/eliminar librerías pesadas | NFR3 |
