# NFR Requirements — Tech Stack Decisions (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## TS1 — Cero dependencias nuevas (NFR1)
- U1 usa sólo Foundation + el `FutmondoKit` existente (`NetworkClient`, auth). `Package.swift` mantiene `dependencies: []`. Sin librerías OSS ni de pago.

## TS2 — Target y testabilidad (NFR6)
- Todo U1 vive en el target library `FutmondoKit` (sin SwiftUI), compilable y testeable con `swift test` en Linux/WSL. El testTarget `FutmondoKitTests` sigue dependiendo sólo de `FutmondoKit`.
- Formateo de dinero y resolución de activo implementados con **aritmética y lógica puras** (sin `NumberFormatter`/locale) para tests deterministas en WSL.
- **Desviación deliberada de FR1.3** (anotada para que el gate no la lea como contradicción): la redacción original de FR1.3 decía "separador de la locale" y "half-up"; en construcción se fija **separador `,` constante** (independiente de locale) y **redondeo half-away-from-zero** por aritmética entera. Es una decisión de determinismo de tests en WSL que **preserva** el resultado visible esperado (`12,4M`, `-1,2M`); no relaja ningún requisito.

## TS3 — Concurrencia
- Tipos de dominio `Sendable`; servicios `async`/`throws`. Reutiliza el modelo `actor`/`async` de `AuthService` de F1 sin cambiarlo.

## Sources

- `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md`
- `aidlc/spaces/default/memory/project.md` (coste 0 €, verificación WSL)

## Assumptions & Open Questions

None.
