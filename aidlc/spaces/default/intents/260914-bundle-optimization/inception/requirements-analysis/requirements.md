# Requirements — Optimización del bundle inicial (frontend Angular)

> Intent: `260914-bundle-optimization` · Scope: `refactor` · Profundidad: Minimal · Test Strategy: Minimal
> Refactor del frontend `angular-app/` para reducir el bundle inicial por debajo de 1 MB **sin cambio funcional** y a **coste 0 €**.

## Sources

- `[desc]` Initial description: "Optimizar el bundle inicial del frontend Angular para bajar de 1 MB (lazy-loading, revision de dependencias pesadas como chart.js/ng2-charts y marked, carga de Material) y restaurar el presupuesto maximumError de angular.json a 1 MB. Sin cambio funcional, coste 0 euros." (`project-description.json`)
- `[scope]` Workflow-selected scope: `refactor` (profundidad Minimal, Test Strategy Minimal).
- `[Q1]`–`[Q4]` Respuestas de clarificación en `requirements-analysis-questions.md` (modo guiado): Q1=B, Q2=C, Q3=B, Q4=A.
- Contexto brownfield del Reverse Engineering:
  - `business-overview.md` — dominio, funcionalidad clave (gráficos en evolution/stats, chat del asistente) y restricción de coste 0 €.
  - `architecture.md` — composición del bundle inicial: cadenas eager de `provideCharts`, `marked` vía el asistente, y `PreloadAllModules`; ADR (borrador) de diferir librerías pesadas y el orden recortar→restaurar-budget.
  - `code-structure.md` — ubicación de los ficheros implicados (`app.config.ts`, `app.ts`, `shared/components/assistant-*`, `features/evolution`, `features/stats`) y configuración de build (`angular.json`).
- Regla de proyecto (memory): coste 0 € — solo soluciones en tiers gratuitos, sin dependencias con gasto recurrente.

## Análisis de intención

El usuario quiere que el **chunk inicial** (`type: initial`, medido por el budget de `angular.json`) del frontend Angular quede por debajo de 1 MB, para poder **restaurar el `maximumError` a `1MB`** (hoy relajado a `1.2MB`). El objetivo es de **rendimiento/salud del build**, no de negocio: la app debe comportarse exactamente igual (mismos gráficos, mismo chat, misma navegación funcional). La causa raíz, según `architecture.md`, son tres cargas **eager** cuyos consumidores reales son **lazy**. El trabajo es de reestructuración de imports/configuración, sin añadir ni cambiar funcionalidad y sin coste recurrente.

## Requisitos funcionales

> "Funcional" aquí abarca el comportamiento observable del build y de la app; este refactor no añade features de usuario.

### FR1 — Sacar Chart.js/ng2-charts del bundle inicial
- **FR1.1**: El registro de Chart.js (`provideCharts(withDefaultRegisterables())`, hoy en `app.config.ts`) debe dejar de evaluarse de forma eager en el arranque y pasar a registrarse a nivel de las rutas/componentes lazy que consumen gráficos (`features/evolution`, `features/stats`). Origen: `[desc]`, `architecture.md`, `code-structure.md`.
- **FR1.2**: Tras el cambio, `chart.js` y `ng2-charts` NO deben formar parte del chunk `initial` del build de producción (verificable en el desglose de chunks del build). Origen: `[desc]`, `[Q1]`.
- **FR1.3**: Las vistas de gráficos (`features/evolution`, `features/stats`) deben seguir renderizando correctamente sus gráficos tras la carga lazy. Origen: `[Q4]`, `business-overview.md`.

### FR2 — Diferir el chat del asistente y `marked`
- **FR2.1**: `AssistantChatComponent` debe cargarse **bajo demanda** al abrir el chat (no de forma estática desde la cadena eager `App → AssistantFabComponent`). Origen: `[Q3]`, `architecture.md`.
- **FR2.2**: Como consecuencia de FR2.1, `marked@18` NO debe formar parte del chunk `initial` del build de producción. Origen: `[Q3]`, `[Q1]`.
- **FR2.3**: El chat del asistente debe seguir abriéndose y renderizando Markdown correctamente tras su carga bajo demanda (mismo saneo/lógica que hoy). Origen: `[Q4]`, `business-overview.md`.

### FR3 — Estrategia de precarga con retardo
- **FR3.1**: Sustituir `withPreloading(PreloadAllModules)` en `app.config.ts` por una estrategia de precarga **con retardo** que precargue los chunks lazy tras un periodo de inactividad tras el arranque, en lugar de inmediatamente. Origen: `[Q2]`.
- **FR3.2**: La estrategia debe implementarse sin añadir dependencias con coste recurrente (una `PreloadingStrategy` propia o un mecanismo equivalente disponible en el stack actual). Origen: `[Q2]`, regla de proyecto (coste 0 €).
- **FR3.3**: La navegación entre rutas lazy debe seguir funcionando; el cambio de precarga no debe romper ninguna ruta ni su carga bajo demanda. Origen: `[Q4]`.

### FR4 — Restaurar el budget del bundle inicial
- **FR4.1**: En `angular.json`, tras completar FR1–FR3, restaurar el budget `type: initial` a `maximumError: 1MB`. Origen: `[desc]`, `[Q1]`.
- **FR4.2**: Fijar el `maximumWarning` del budget `type: initial` por debajo de 1 MB (objetivo ~900 kB) como margen de alerta. Origen: `[Q1]`.
- **FR4.3**: El build de producción (`ng build`/builder `@angular/build:application`) debe completar sin error con esos budgets. Origen: `[Q1]`, `[Q4]`.
- **FR4.4**: El orden de trabajo debe ser recortar las cargas eager (FR1–FR3) **antes** de restaurar el budget (FR4.1), ya que restaurarlo primero haría fallar el build de producción. Origen: `architecture.md` (ADR borrador).

## Requisitos no funcionales

- **NFR1 — Tamaño del bundle inicial**: el chunk `initial` del build de producción debe quedar por debajo de **1 MB** (1 048 576 bytes según el budget de Angular), y el build debe pasar con `maximumError: 1MB`. Criterio de aceptación medible y verificable en el output del build. Origen: `[desc]`, `[Q1]`.
- **NFR2 — Sin cambio funcional (no regresión)**: la suite de tests existente del frontend (`ng test` / vitest vía `@angular/build:unit-test`) debe seguir **verde** tras los cambios, y debe verificarse **manualmente** que los gráficos (`features/evolution`, `features/stats`) y el chat del asistente siguen funcionando. Origen: `[Q4]`, `business-overview.md`.
- **NFR3 — Coste 0 €**: la solución debe basarse exclusivamente en cambios de configuración e imports del stack actual; NO debe introducir dependencias nuevas ni servicios con gasto recurrente. Origen: `[desc]`, regla de proyecto (memory).
- **NFR4 — Transferencia de red tras el arranque**: con FR3, la precarga de chunks lazy no debe dispararse de forma inmediata al estabilizar la app, sino tras inactividad, reduciendo el pico de transferencia posterior al arranque respecto al comportamiento actual (`PreloadAllModules`). Objetivo cualitativo, verificable observando el orden/momento de descarga de chunks. Origen: `[Q2]`.

## Restricciones

- **C1**: Tecnología fijada — Angular 22 (standalone + signals), builder `@angular/build:application`, Angular Material 22.1.6; no se cambia el stack. Origen: `technology-stack.md`, `code-structure.md`.
- **C2**: Sin dependencias nuevas ni sustitución de librerías pesadas (Chart.js/ng2-charts/marked se conservan; solo cambia CUÁNDO se cargan). Origen: `[Q3]`, `architecture.md` (alternativa (b) rechazada), NFR3.
- **C3**: Coste 0 € en tiers gratuitos (Neon/Fly.io/GitHub Actions). Origen: regla de proyecto.
- **C4**: Verificar `npm ci` y `ng test`/build del frontend en local (o en contenedor `node:<versión de .nvmrc>` si el Node local no alcanza el mínimo del Angular CLI 22) antes de pushear, para no romper el gate de CI. Origen: reglas de proyecto (memory).

## Assumptions & Open Questions

### Assumptions
- `[assumption]` La carga de Angular Material en el shell raíz (`app.ts`: sidenav, toolbar, etc.) es legítimamente eager (es el chrome de la app) y NO se difiere; el margen ahí es menor (tree-shaking/uso puntual) y queda fuera del objetivo principal. Origen: `architecture.md`. A confirmar en diseño si se decide actuar sobre Material.
- `[assumption]` La carga lazy de `AssistantChatComponent` y del registro de charts es suficiente, junto con la restauración del budget, para dejar el inicial por debajo de 1 MB. Si tras FR1–FR3 el inicial siguiera ≥ 1 MB, haría falta un recorte adicional (a evaluar en construcción con medición).

### Open Questions
- None.

## Out of scope

- Cambios funcionales de la aplicación (nuevas features, cambios de UX o de comportamiento de negocio).
- Sustituir Chart.js, ng2-charts o marked por alternativas más ligeras (rechazado por "sin cambio funcional" y coste 0 €).
- Diferir o reestructurar la carga de Angular Material del shell raíz (salvo tree-shaking sin impacto funcional; no es el objetivo).
- Optimizaciones del backend, CI/CD, despliegue o infraestructura.
- Revisar `NODE_TLS_REJECT_UNAUTHORIZED=0` del build de producción (señal de seguridad anotada en `architecture.md`, fuera de este intent).
