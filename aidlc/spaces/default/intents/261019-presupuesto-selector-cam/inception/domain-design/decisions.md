# Domain Design — Decisions (ADRs) (F2)

> Fase: inception (domain-design). Idioma: castellano; tokens técnicos verbatim en inglés.
> Formato ADR: Context / Decision / Consequences / Alternatives Rejected.

## ADR-1 — Separación lógica pura (`FutmondoKit`) vs vistas (`FutmondoApp`)

- **Context**: la cobertura de UI SwiftUI no es fiable en WSL (regla durable); la lógica debe ser testeable con `swift test`.
- **Decision**: toda la lógica (DTOs, `MoneyFormatter`, `TeamBudgetSort`, servicios, `ActiveChampionshipStore`) va en `FutmondoKit`; las vistas y el `BudgetViewModel` orquestador van en `FutmondoApp` bajo `#if canImport(SwiftUI)`.
- **Consequences**: `FutmondoKitTests` cubre la lógica en CI/WSL; las vistas se validan en dispositivo. Mantiene el patrón de F1.
- **Alternatives Rejected**: (a) todo en el target de app → no testeable en WSL; (b) lógica en la vista (massive view) → no testeable, acoplada.

## ADR-2 — Estado del campeonato activo con `UserDefaults`

- **Context**: la web persiste el campeonato activo en `localStorage` (`futmondo_active_championship`); hay que replicar el patrón en nativo.
- **Decision**: `ActiveChampionshipStore` persiste el `championship_id` activo en `UserDefaults`; es la fuente del `championship_id` que consume `BudgetService`.
- **Consequences**: al reabrir, se restaura el último campeonato (FR3.2); primer arranque toma `championships[0]` (FR3.3). No almacena credenciales (los tokens siguen en Keychain/memoria, NFR2).
- **Alternatives Rejected**: (a) sólo en memoria → no persiste entre sesiones; (b) Keychain → innecesario (no es secreto).

## ADR-3 — `ViewModel` orquestador vs lógica en la vista

- **Context**: `BudgetView` combina carga, estados, orden y cambio de campeonato.
- **Decision**: un `BudgetViewModel` (`@Observable`) orquesta servicios + store + sort y expone un estado explícito (loading/loaded/error/empty); la vista sólo renderiza.
- **Consequences**: la orquestación es fina y la vista delgada; parte del VM podría testearse si no toca SwiftUI (se mantiene la lógica pura en `FutmondoKit`).
- **Alternatives Rejected**: lógica dispersa en la vista → difícil de razonar y de validar.

## ADR-4 — DTO completo (9 campos) aunque la lista muestre 4

- **Context**: refined-mockups muestra 4 métricas en la fila; el detalle (5 restantes) es follow-up.
- **Decision**: `TeamBudget` modela los **9** campos del endpoint; `BudgetRow` usa sólo 4.
- **Consequences**: cuando llegue el detalle de equipo no hay que rehacer el modelo ni volver al endpoint. FR1.2 se cumple por disponibilidad.
- **Alternatives Rejected**: modelar sólo 4 → habría que ampliar el DTO y re-decodificar en el futuro.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/domain-design/components.md`
- [memory] reglas durables (verificación WSL, seguridad, coste 0 €)

## Assumptions & Open Questions

None.
