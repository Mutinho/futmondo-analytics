# Integration Test Instructions — Favoritos nativa iOS

## Aplicabilidad
**NO APLICA.** Estrategia **minimal** (scope `refactor`): los tests unitarios de
la unidad los cubre Code Generation (XCTest sobre `FutmondoKit`). No se generan
instrucciones de integración nuevas.

## Contexto
Favoritos es frontend-only sobre backend existente e inmutable (`getMyFavorites`,
`unfollow`). La única obligación de integración del scope es que la suite
existente siga en verde (232 tests).
