# NFR Design — Performance (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Diseño (cómo se cumplen PR1-PR2)

- **PR1 (60 fps)**: `BudgetView` renderiza las filas con `List` (o `ScrollView` + `LazyVStack`) → sólo se construyen las filas visibles. `BudgetRow` es una vista de valor ligera (texto + tokens, sin cómputo en el cuerpo; el formateo de dinero se calcula una vez por valor). El orden se aplica en el VM (`TeamBudgetSort`, O(n) sobre listas cortas), no en el cuerpo de la vista.
- **PR2 (<100 ms)**: en `load()`/`selectChampionship`, el VM fija `state = .loading` de forma **síncrona** (en el hilo principal, `@MainActor`) antes del `await` de red; SwiftUI re-renderiza el indicador de inmediato.

## Verificación

Observación en iPhone 13 Pro, con criterio comprobable aunque manual: (a) scroll de la lista de equipos sin frames perdidos perceptibles a simple vista (proxy de 60 fps; opcionalmente contrastable con el FPS debug gauge de Instruments, gratuito); (b) al tocar un campeonato distinto, el spinner aparece antes de ~100 ms (sin "congelación" previa). No medible numéricamente en WSL; se registra el resultado de la observación en Performance Validation de Operación.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/nfr-requirements/performance-requirements.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/functional-spec.md`

## Assumptions & Open Questions

None.
