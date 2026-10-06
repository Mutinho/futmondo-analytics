# Integration Test Instructions — calculadora-mejora

## Estado

**NO-APLICA** en este intent. Estrategia de test = **Minimal**, scope =
**refactor**: no se genera suite de integración nueva. El cambio es
frontend-only y se verifica con tests de componente (unit) de
`calculator.component.spec.ts`, que ya ejercitan la composición de la lista, el
cálculo condicional y la persistencia con los servicios HTTP stubeados.

## Cobertura equivalente

- La interacción con las fuentes de datos (`getMyRoster()`, `market/today`,
  `getOnSale()`) no cambia; su contrato ya está cubierto por la suite existente
  y los stubs del spec del componente.

## Sources

- `code-generation/unit-test-instructions.md`.
- `aidlc-state.md` → `Test Strategy: Minimal`.

## Assumptions & Open Questions

None.
