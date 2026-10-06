# Cross-Unit Traceability — calculadora-mejora

Gate de cobertura final de la etapa (Build and Test, Step 10). Enumera los
`FR`/`NFR` de `requirements.md` y verifica su cobertura en el `traceability.json`
de code-generation (unidad `calculator-toggle`). No hay `user-stories` en este
scope (refactor), así que no se enumeran ACs.

## Verdicto: PASS

Todos los requisitos funcionales con lógica dedicada están cubiertos con estado
`OK` y fichero existente; los requisitos de preservación/restricción se cubren
por diseño (sin fichero de implementación nuevo).

## Cobertura por ID

| ID | Estado | Owning | Target / justificación |
|----|--------|--------|------------------------|
| FR1.1 | OK | code-generation | `calculator.component.html` (toggle) |
| FR1.2 | OK | code-generation | `calculator.component.ts` (ON suma onSaleTotal) |
| FR1.3 | OK | code-generation | `calculator.component.ts` (OFF excluye onSaleTotal) |
| FR1.4 | OK | code-generation | `calculator.component.ts` (computed reactivo) |
| FR2.1 | OK | code-generation | `calculator.component.ts` (activeBidsTotal siempre resta) |
| FR3.1 | OK | code-generation | `calculator.component.ts` (persistencia localStorage) |
| FR3.2 | OK | code-generation | `calculator.component.ts` (restauración) |
| FR3.3 | OK | code-generation | `calculator.component.ts` (default ON) |
| FR3.4 | OK | code-generation | `calculator.component.ts` (fallback ON) |
| FR4.1 | N/A | — | Preservación: vender sin cambios (no requiere código nuevo) |
| FR4.2 | N/A | — | Preservación: fuentes de datos sin cambios |
| FR5.1 | OK | code-generation | `calculator.component.ts` (lista excluye onSale con ON) |
| FR5.2 | OK | code-generation | `calculator.component.html` (oculta bloque; incluye en lista con OFF) |
| FR5.3 | OK | code-generation | `calculator.component.ts` (deseleccionados) |
| FR5.4 | OK | code-generation | `calculator.component.ts` (reconstrucción; OFF→ON) |
| FR5.5 | OK | code-generation | `calculator.component.ts` (invariante anti-doble-conteo) |
| NFR1 | N/A | — | Coste 0 €: verificado por diseño (sin dependencias nuevas) |
| NFR2 | OK | code-generation | `calculator.component.html` (toggle Material accesible) |
| NFR3 | Met | build-and-test | Gate CI (`ng test`) en verde |
| NFR4 | OK | code-generation | `calculator.component.spec.ts` (13 specs) |
| NFR5 | N/A | — | Mantenibilidad: no hubo backend; frontend-only |

## Elementos sin cobertura

- Ninguno (los `N/A` son requisitos de preservación/restricción sin
  implementación dedicada, justificados arriba).

## Sources

- `requirements.md` (FR1–FR5, NFR1–NFR5).
- `code-generation/traceability.json`.

## Assumptions & Open Questions

None.
