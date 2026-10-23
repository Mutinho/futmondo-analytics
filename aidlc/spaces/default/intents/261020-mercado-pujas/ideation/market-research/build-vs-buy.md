# Build vs Buy — F3 Mercado (app nativa iOS)

## Sources

- `aidlc/spaces/default/intents/261020-mercado-pujas/ideation/intent-capture/intent-statement.md`
  — alcance (lectura + escritura + detalle Sofascore), consumo de endpoints
  existentes, sin cambios de backend.
- `aidlc/spaces/default/memory/project.md` / `team.md` — mandato **coste 0 €**
  (sólo SDK de Apple; excepción acotada: Apple Developer Program ~99 €/año sólo
  para distribución, no activada aquí); **tema Angular como fuente de verdad**;
  identificadores en inglés / texto de usuario en castellano.
- Base reutilizable F1/F2 en `ios/`: `FutmondoKit` (NetworkClient HTTPS,
  AuthService, ActiveChampionshipStore, MoneyFormatter) y `FutmondoApp`
  (DesignSystem, `RootTabView`).

## Decisión

**Build** con el **SDK de Apple (SwiftUI)**, reutilizando la base de F1/F2. No se
compra ni se incorpora ninguna dependencia de terceros.

## Alternativas consideradas

| Opción | Coste recurrente | Encaje con mandatos | Veredicto |
|---|---|---|---|
| **Build con SwiftUI + SDK Apple** (reutiliza `FutmondoKit`/`DesignSystem`) | 0 € | Cumple coste 0 €, tema Angular como fuente, sin dependencias | **Elegida** |
| Librería de UI/tabla de terceros (SPM) | Variable / riesgo de pago o abandono | Rompe "no dependencias de pago" y añade superficie; innecesaria (cards nativas bastan) | Rechazada |
| Framework cross-platform (p. ej. envoltorio web) | 0–variable | Contradice la decisión ya tomada de **app nativa** y el tema nativo; peor fidelidad | Rechazada |
| Mantener sólo la PWA (no portar) | 0 € | No cumple el intent (el objetivo ES llevar Mercado a nativo) | Rechazada |

## Consecuencias

- Reutilización máxima: `NetworkClient` ya habla HTTPS con el backend; falta sólo
  el **modelo/servicio de Mercado** en `FutmondoKit` (datos + escritura) y la
  **UI** en `FutmondoApp` (cards, banner, orden, puja/cancelar, sheet Sofascore).
- Riesgo arrastrado (F1/F2): errores arm-only que sólo afloran en build de
  dispositivo con `xtool` (síntesis de `Equatable`, strict concurrency Swift 6,
  APIs UIKit/SwiftUI, colisiones de nombres). Se aplica rigor anti-hueco-WSL.

## Assumptions & Open Questions

None.
