# Performance Test Instructions — Sistema de diseño nativo iOS

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

Los NFR de performance de este intent son de **render de UI** (NFR4.1 60 fps objetivo, NFR4.2 feedback de loading <100 ms), no de red/throughput. No son medibles con `swift test` en WSL (no hay runtime de UI); se validan por observación en el iPhone 13 Pro.

## Verificación

- **Build**: `cd ios && swift build` (confirma que no se introduce código que rompa el render).
- **En dispositivo (manual)**: abrir el catálogo y el login revestido; comprobar scroll fluido (≈60 fps) y que el estado `loading` del botón aparece de inmediato al pulsar. Herramienta: observación / Instruments (coste 0 €).

## Owning stage

El objetivo cuantitativo formal queda como verificación manual en dispositivo; no hay stage de performance-validation gestionada de pago en este stack.

## Assumptions & Open Questions

None.
