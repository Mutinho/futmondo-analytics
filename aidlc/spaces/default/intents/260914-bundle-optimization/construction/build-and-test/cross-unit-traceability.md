# Cross-Unit Traceability — Optimización del bundle inicial

> Stage 3.6 Build and Test · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · directiva zero-Unit.
> Trabajo zero-Unit (refactor saltó units-generation): una sola unidad implícita. Este documento traza cada requisito/regla a su verificación en Build and Test.

## Trazabilidad requisito/regla → verificación

| ID | Descripción | Verificación en Build and Test | Estado |
|----|-------------|-------------------------------|--------|
| FR1.1 / BR1.1 | Charts no eager, registro lazy por ruta | Build: `provideCharts` fuera de `app.config.ts`; charts en chunk lazy | ✓ |
| FR1.2 / BR1.2 | charts fuera del chunk initial | Inspección de chunks iniciales: sin marcadores chart.js/ng2-charts | ✓ |
| FR1.3 / BR1.3 | Gráficos siguen renderizando | Manual (test-results §5) | Pendiente manual |
| FR2.1 / BR2.1 | Chat cargado bajo demanda | Chunk lazy `assistant-chat-component` (62 kB) | ✓ |
| FR2.2 / BR2.2 | marked fuera del initial | Inspección de chunks iniciales: sin marcadores marked | ✓ |
| FR2.3 / BR2.3 | Chat sigue funcionando (lazy) | Manual (test-results §5) | Pendiente manual |
| FR3.1 / BR3.1 | Precarga con retardo tras inactividad | Spec estrategia (5 tests verde) | ✓ |
| FR3.2 / BR3.2 | Precarga sin dependencias de pago | Sin deps nuevas; solo APIs navegador + RxJS | ✓ |
| FR3.3 / BR3.3 | Navegación lazy sigue funcionando | Spec estrategia + build (rutas lazy segmentadas) | ✓ |
| FR4.1 / BR4.1 | Restaurar maximumError 1MB + warning 900kB | `angular.json` + build pasa con esos budgets | ✓ |
| FR4.3 / BR4.2 | Build de producción pasa | Build completa sin error | ✓ |
| FR4.4 / BR4.3 | Recortar antes de restaurar budget | Orden verificado (build pasa con 1MB tras recorte) | ✓ |
| NFR1 | Chunk initial < 1 MB | Initial total 819.05 kB | ✓ |
| NFR2 / BR5.1 | Suite verde + verificación manual | 11/11 tests verde; manual pendiente | ✓ / manual |
| NFR3 / BR5.2 | Coste 0 €, no sustituir librerías | Sin deps nuevas; chart.js en lazy (no eliminado) | ✓ |
| NFR4 | Menor pico de transferencia tras arranque | Precarga diferida implementada (idleDelay 2000ms) | ✓ |

## Resumen de cobertura

- **Verificado automáticamente en Build and Test**: NFR1, NFR2, NFR3, NFR4, FR1.1/1.2, FR2.1/2.2, FR3.*, FR4.*, y sus BR asociados.
- **Pendiente de verificación manual** (no automatizable, componentes con `skipTests`): FR1.3/BR1.3 (gráficos renderizan) y FR2.3/BR2.3 (chat renderiza Markdown). Documentado en `test-results.md` §5.
- Sin huecos: todos los IDs upstream tienen verificación asignada.
