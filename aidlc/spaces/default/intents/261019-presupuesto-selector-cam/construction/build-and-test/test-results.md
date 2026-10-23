# Test Results — F2 (Build and Test)

> Fase: construcción (build-and-test). Idioma: castellano; tokens técnicos verbatim en inglés.

## Resultado ejecutable (WSL)

- `cd ios && swift build` → **Build complete** (0 errores); el target SwiftUI `FutmondoApp` compila para arm64 en dispositivo (validado con `xtool dev run`).
- `cd ios && swift test` → **105 tests, 0 fallos** (F1 + U1 + U2: incluye DTOs/formato/orden/fallback/persistencia, `SortKeyPresentation`, `TransactionDatePresenter`, `fetchTeamDetail` y el test de contraste de la card oscura). Suite verde, sin regresión.
- Ruido `libxml2` de WSL ignorado (no afecta a build/tests).

## Pendiente de validación en dispositivo (iPhone 13 Pro, manual)

- Render 60 fps, feedback <100 ms (NFR4); VoiceOver + Dynamic Type (NFR5); fidelidad con el tema Angular (NFR3); flujo end-to-end (login→Presupuesto→cambio de campeonato→orden→estados→logout). Se registra en Performance Validation de Operación.

## Veredicto

- Capa ejecutable (lógica + build): **verde**.
- Capa de UI/experiencia: **pendiente de validación manual en dispositivo** (regla durable WSL).

## Assumptions & Open Questions

None.
