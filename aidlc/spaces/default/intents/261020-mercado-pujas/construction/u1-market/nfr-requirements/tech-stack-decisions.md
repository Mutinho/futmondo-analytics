# Tech Stack Decisions — u1-market

> Unit `u1-market` (kind `ui`). No introduce tecnología nueva: todo SDK de Apple,
> reutilizando la capa `FutmondoKit`/`FutmondoApp` de F1/F2. IDs derivados de NFR1
> (coste 0 €).

## Sources

- `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md` (stack `ios/`).
- `.../inception/requirements-analysis/requirements.md` (NFR1, NFR5).
- `nfr-requirements-questions.md` (Q3).

## Decisiones

| Área | Selección | Rationale | ID |
|---|---|---|---|
| UI | SwiftUI (SDK Apple) | Target nativo iOS; vistas bajo `#if canImport(SwiftUI)`, validadas en dispositivo; reutiliza componentes del DesignSystem de F1/F2. | NFR1.1 |
| Tema/diseño | DesignSystem de F1/F2 (tokens Material 3 → SwiftUI) | Reproduce el tema Angular como fuente de verdad; donde no hay 1:1, Apple HIG. | NFR2.1 |
| Lógica/datos | `FutmondoKit` (library, Swift 6 strict concurrency) | Lógica testeable con XCTest en WSL (modelos, `MarketService`/`SofascoreService` actors, `MarketSorter`, `BidAmountValidator`, `MarketWriteOutcome`). | NFR5.1 |
| Networking | Foundation `URLSession` vía `NetworkClient` (F1, reutilizado) | Sin libs externas; `Bearer` inyectado; rechazo de no-https. | NFR1.3 |
| Estado observable | Observation (`@Observable`) / `ObservableObject` | `MarketViewModel` como en el patrón de F2. | NFR1.4 |
| Almacén seguro | Keychain Services (reutilizado de F1) | El refresh token ya vive en Keychain; `u1-market` no añade almacenamiento. | NFR3.3 |
| Tests | XCTest (`swift test --package-path ios`) | Comando de verificación del intent; cubre la lógica de `FutmondoKit`. | NFR5.2 |
| Dependencias | **Ninguna nueva** (`Package.swift` sigue con `dependencies: []`) | Mandato coste 0 €; sólo SDK de Apple. | NFR1.2 |

## Reutilización (no es tecnología nueva)

- `NetworkClient` / `URLSessionNetworkClient`, `AuthService` / sesión (F1).
- `DesignSystem`: tokens (`DSColorToken`, `money-positive`/`money-negative`),
  `Card`, `PrimaryButton`, `TextInputField`, estados loading/error (F1/F2).
- `RootTabView` (F1/F2), extendido con la 2ª pestaña.

## Restricciones del toolchain (ya afirmadas)

- `actool` no disponible en WSL → tokens de color en código, no en
  `Assets.xcassets`.
- `llvm-cov` no fiable en WSL → la lógica testeable va a `FutmondoKit` (XCTest);
  las vistas SwiftUI se validan en dispositivo, fuera del cómputo de cobertura.

## Idioma (NFR4)

| ID | Requisito | Verificación |
|---|---|---|
| NFR4.1 | Identificadores, docstrings y comentarios en **inglés**; texto de cara al usuario (strings visibles de la pantalla de Mercado) y mensajes de commit en **castellano**. | Revisión de código / `ruff`/Prettier donde aplique; strings de UI en castellano. |

## Assumptions & Open Questions

None.
