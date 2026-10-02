# Integration Test Instructions — `261001-sync-god-file-resto`

## Aplicabilidad

La estrategia de test activa es **Minimal** (scope `refactor`). Minimal no genera
suites de integración adicionales: la verificación de equivalencia se cubre con
los tests de caracterización por dominio (unit-level, con fakes en memoria) y la
suite backend existente, que ya ejercita los límites relevantes.

## Red de seguridad existente

El gate de CI bloqueante (gitleaks + `pytest` + `ng test`) y la suite completa
backend (259 pasados) actúan como red de integración de facto para este refactor
de equivalencia estricta. No se añaden suites nuevas en este intent.
