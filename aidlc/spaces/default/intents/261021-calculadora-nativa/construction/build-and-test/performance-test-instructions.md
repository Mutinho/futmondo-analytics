# Performance Test Instructions — Calculadora nativa iOS

## Aplicabilidad

**NO APLICA en este intent.** Estrategia **minimal**; no hay NFR de rendimiento
cuantificado que exija load testing ni benchmarks locales.

## Contexto

El rendimiento (scroll fluido a 120 Hz, carga en paralelo, caché en memoria) se
cubre con los patrones nativos ya documentados en
`native-ios-ui-patterns.md` (ProMotion, `onScrollGeometryChange` con un solo
`Bool`, sin escrituras de estado por frame) y se valida cualitativamente en
dispositivo, no con una etapa formal de validación de rendimiento.
