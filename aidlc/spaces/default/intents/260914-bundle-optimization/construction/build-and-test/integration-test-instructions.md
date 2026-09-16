# Integration Test Instructions — Optimización del bundle inicial

> Stage 3.6 Build and Test · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield.

## Alcance

Este refactor NO introduce nuevas integraciones ni cambia contratos entre módulos: solo reestructura CUÁNDO se cargan tres librerías del frontend (chart.js, ng2-charts, marked) y la estrategia de precarga de rutas. No hay nuevas fronteras de integración que probar automáticamente.

La única "integración" observable es la carga diferida:
- El bloque `@defer` del chat resuelve `AssistantChatComponent` (+ `marked`) bajo demanda.
- El registro lazy de charts a nivel de componente en `evolution`/`stats`.
- La `IdlePreloadingStrategy` integrándose con `provideRouter(withPreloading(...))`.

## Verificación aplicada

- El **build de producción** (ver `build-instructions.md`) es la verificación de integración de facto: si el `@defer`, el registro lazy de charts o la estrategia de preloading estuvieran mal cableados, el build fallaría (como ocurrió con NG8001, ya corregido) o los chunks no se segmentarían. El build pasa y el desglose de chunks confirma la segmentación correcta.
- La navegación entre rutas lazy (integración router ↔ preloading) se cubre en la verificación manual (`test-results.md` §5) y por el spec de la estrategia (rutas sin `loadChildren`/`loadComponent` y `data.preload===false` no se precargan).

No se añaden tests de integración nuevos (scope refactor Minimal no añade floor; NFR3 coste 0 €).
