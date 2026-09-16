# Requirements Analysis — Preguntas de clarificación

> Intent: `260914-bundle-optimization` (scope refactor, profundidad Minimal).
> Optimizar el bundle inicial del frontend Angular por debajo de 1 MB, sin cambio funcional, coste 0 €.
> El escaneo de Reverse Engineering ya identificó los ejes técnicos (charts/marked eager, PreloadAllModules, budget). Estas preguntas cierran las pocas decisiones abiertas.

---

## Q1 — Objetivo de tamaño del bundle inicial

El intent pide "bajar de 1 MB" y restaurar `maximumError` a `1MB` en `angular.json`. ¿Cuál es el criterio de éxito medible que quieres para el chunk inicial (`type: initial`) en build de producción?

- A. El build de producción debe pasar con `maximumError: 1MB` (el bundle inicial queda por debajo de 1 MB). Es el criterio duro.
- B. Además de A, fijar también `maximumWarning` por debajo de 1 MB (p. ej. 900 kB) para tener margen de alerta.
- C. Objetivo más agresivo: bajar el inicial claramente por debajo de 1 MB (p. ej. < 900 kB) y ajustar los budgets a ese valor.
- D. Solo reducir lo posible sin comprometerme a un umbral concreto; mantener el budget actual (1.2MB) si no se llega.
- X. Other (please specify)

[Answer]: B

---

## Q2 — Estrategia de precarga (`PreloadAllModules`)

Hoy `app.config.ts` usa `withPreloading(PreloadAllModules)`, que precarga todos los chunks lazy tras el arranque. Esto NO afecta al budget `initial` (que es lo que pide el intent), pero sí a la transferencia total de red. ¿Qué hago con la precarga?

- A. Dejar `PreloadAllModules` como está — el objetivo es solo el budget `initial`; no tocar la percepción de navegación instantánea.
- B. Cambiar a precarga selectiva/bajo demanda (sin `PreloadAllModules`) para reducir también la transferencia total tras el arranque.
- C. Cambiar a una estrategia con retardo (precargar tras un tiempo de inactividad) como término medio.
- D. Decidir en implementación con medición; dejar el requisito como "a evaluar".
- X. Other (please specify)

[Answer]: C

---

## Q3 — Diferir `marked` y el chat del asistente

`marked@18` entra en el bundle inicial vía la cadena eager `App → AssistantFabComponent → AssistantChatComponent → import 'marked'`. El chat solo se muestra tras `@if (chatOpen())`. ¿Hasta dónde diferir?

- A. Diferir solo `marked` (import dinámico) manteniendo el resto de la cadena del asistente como está.
- B. Diferir el `AssistantChatComponent` completo (carga bajo demanda al abrir el chat), lo que arrastra `marked` con él.
- C. Lo que consiga sacar `marked` del inicial con menor riesgo funcional; que lo decida la implementación.
- X. Other (please specify)

[Answer]: B

---

## Q4 — Alcance de "sin cambio funcional" y verificación

El intent exige "sin cambio funcional". ¿Cómo definimos el criterio de que no hubo regresión, dado que la suite de tests del frontend es mínima?

- A. La suite de tests existente (`ng test` / vitest) debe seguir verde; verificación manual de que gráficos (evolution, stats) y chat del asistente siguen funcionando.
- B. Solo que la suite existente siga verde (sin verificación manual adicional).
- C. Añadir alguna comprobación extra mínima además de A (p. ej. smoke test manual de las rutas afectadas documentado).
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones capturadas:

- Objetivo de tamaño (Q1): el build de producción debe pasar con `maximumError: 1MB` en `angular.json` (bundle inicial < 1 MB), y además `maximumWarning` por debajo de 1 MB (~900 kB) como margen de alerta.
- Precarga (Q2): sustituir `PreloadAllModules` por una estrategia de precarga con retardo (precargar los chunks lazy tras un periodo de inactividad), como objetivo adicional de rendimiento/transferencia; coste 0 €, sin dependencias nuevas.
- Diferir el asistente (Q3): cargar `AssistantChatComponent` bajo demanda al abrir el chat, sacando `marked@18` del bundle inicial junto con el código del chat.
- Charts (del escaneo, no cuestionado): mover el registro de Chart.js/ng2-charts (`provideCharts`) al nivel de las rutas/componentes lazy que los usan (`features/evolution`, `features/stats`), sacándolos del inicial.
- Sin cambio funcional (Q4): la suite de tests existente (`ng test`/vitest) debe seguir verde, más verificación manual de que gráficos (evolution, stats) y chat del asistente siguen funcionando.
- Restricciones transversales: sin cambio funcional; coste 0 € (solo cambios de configuración/imports, ninguna dependencia nueva); orden de trabajo recortar cargas eager ANTES de restaurar el budget a 1MB (si no, el build de producción falla).

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
