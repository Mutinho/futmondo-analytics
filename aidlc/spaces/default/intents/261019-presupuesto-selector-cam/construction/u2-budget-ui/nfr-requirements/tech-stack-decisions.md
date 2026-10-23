# NFR Requirements — Tech Stack Decisions (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## TS1 — Cero dependencias nuevas (NFR1)
- U2 usa sólo SwiftUI (SDK de Apple) + el DesignSystem de F1 + los protocolos de U1. `Package.swift` sin cambios de dependencias.

## TS2 — Target y guardas (NFR6)
- Todo el código de U2 vive en el target de app `FutmondoApp` bajo `#if canImport(SwiftUI)` (no compila/corre en el testTarget de WSL). `BudgetViewModel` es `@MainActor @Observable`.
- No se añaden tests XCTest de vistas (cobertura de UI no fiable en WSL); la lógica testeable ya está en U1. Verificación de U2 = `swift build` + validación en dispositivo.

## TS3 — Liquid Glass automático
- El material Liquid Glass de iOS 26 lo aporta `TabView` nativo al compilar con el SDK reciente; sin librerías ni código de efecto propio (coste 0 €).

## Sources

- `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md`
- `aidlc/spaces/default/memory/project.md` (coste 0 €, verificación WSL/dispositivo)

## Assumptions & Open Questions

None.
