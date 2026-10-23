# Integration Test Instructions — Calculadora nativa iOS

## Aplicabilidad

**NO APLICA en este intent.** La estrategia de test activa es **minimal**
(scope `refactor`): los tests unitarios de la unidad ya los cubre Code
Generation (XCTest sobre `FutmondoKit`). No se generan instrucciones de
integración nuevas.

## Contexto

La Calculadora es una pantalla **frontend-only** sobre backend existente e
inmutable (sin contratos nuevos que integrar). La interacción cross-screen
(invalidación de caché de Presupuesto/Mercado tras una venta) se valida en
dispositivo. La suite existente (204 tests) se mantiene en verde como única
obligación de integración de este scope.
