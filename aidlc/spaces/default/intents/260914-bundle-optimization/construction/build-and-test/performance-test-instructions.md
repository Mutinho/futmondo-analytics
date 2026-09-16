# Performance Test Instructions — Optimización del bundle inicial

> Stage 3.6 Build and Test · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield.

## Objetivo de rendimiento (el corazón de este intent)

El refactor ES una optimización de rendimiento del arranque. Los criterios medibles son:

- **NFR1 — Tamaño del chunk inicial < 1 MB.** Medido por el budget `type: initial` de Angular con `maximumError: 1MB`. **Verificado: 819.05 kB (< 1 MB).** ✓
- **NFR4 — Menor pico de transferencia tras el arranque.** La `IdlePreloadingStrategy` precarga los chunks lazy tras inactividad (`idleDelay = 2000 ms`) en lugar de inmediatamente (`PreloadAllModules`), sacando la precarga de la ventana crítica de arranque.

## Cómo medir

- **Tamaño de bundle** (automatizable, ejecutado):
  ```bash
  npx ng build --configuration production
  ```
  Leer la línea `Initial total` del desglose de chunks. Debe ser < 1 MB y el build debe pasar con `maximumError: 1MB`.
- **Momento de precarga** (cualitativo, manual): abrir DevTools → Network con la app en producción; confirmar que los chunks lazy NO se descargan inmediatamente al estabilizar el arranque, sino tras un periodo de inactividad. El valor `idleDelay` es ajustable en `idle-preloading-strategy.ts` si la medición sugiere otro margen (open question de requirements).

## Resultado

- NFR1: **cumplido y verificado** (819 kB < 1 MB).
- NFR4: implementado; verificación del momento de descarga es manual/cualitativa (no bloqueante, sin cambio funcional).
