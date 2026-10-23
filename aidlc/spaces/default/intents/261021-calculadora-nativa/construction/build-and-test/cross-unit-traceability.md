# Cross-Unit Final Coverage Gate — Calculadora nativa iOS

## Veredicto: PASS

Todos los `FR` y `NFR` de `requirements.md` están cubiertos (status `OK`) a
través de la cadena de trazabilidad functional-design (FR→BR) +
code-generation (BR→fichero), y los ficheros destino existen. No hay etapa
`user-stories` en este plan a medida, así que no hay `AC` de tres segmentos que
enumerar.

Unidad única (sin Units); se leen la trazabilidad de functional-design
(`construction/functional-design/traceability.json`) y la de code-generation
(`construction/code-generation/traceability.json`).

## Cobertura de requisitos funcionales (FR)

| ID | Cubierto por (BR) | Fichero(s) implementador(es) | Estado |
|---|---|---|---|
| FR1 (carga/frescura) | BR11.1 | CalculatorViewModel.swift | OK |
| FR2 (cabecera resumen) | BR3.1, BR6.1, BR6.2, BR2.1 | CalculatorHeader.swift, CalculatorMath.swift | OK |
| FR3 (toggle en venta) | BR5.1, BR4.1 | CalculatorPreferences.swift, CalculatorViewModel.swift | OK |
| FR4 (proyección fecha) | BR1.1, BR1.2 | CalculatorMath.swift, CalculatorView.swift | OK |
| FR5 (listado cards) | BR5.2, BR7.1 | CalculatorView.swift, CalculatorPlayerCard.swift, CalculatorSorter.swift | OK |
| FR6 (selección múltiple) | BR2.1 | CalculatorViewModel.swift, CalculatorMath.swift | OK |
| FR7 (invariantes dinero) | BR1.1, BR2.1, BR2.2, BR3.1, BR3.2, BR4.1, BR4.2 | CalculatorMath.swift (+ CalculatorMathTests.swift) | OK |
| FR8 (poner a la venta) | BR8.1, BR8.2 | CalculatorView.swift, CalculatorViewModel.swift, SellOutcome.swift, RosterService.swift | OK |
| FR9 (cancelar venta) | BR9.1 | OnSaleSection.swift, CalculatorViewModel.swift, RosterService.swift | OK |
| FR10 (coherencia cruzada) | BR10.1 | SplashView.swift, CalculatorViewModel.swift | OK |
| FR11 (navegación/pestaña) | — (UI/nav) | RootTabView.swift | OK |

## Cobertura de requisitos no funcionales (NFR)

| ID | Evidencia | Estado |
|---|---|---|
| NFR1 (coste 0 €) | `Package.swift` `dependencies: []`; solo SDK de Apple | OK |
| NFR2 (idioma) | identificadores/comentarios en inglés, UI en castellano (todo el código nuevo) | OK |
| NFR3 (arquitectura/testabilidad) | lógica en FutmondoKit con XCTest (204 verde); vistas en FutmondoApp `#if canImport(SwiftUI)` | OK |
| NFR4 (look&feel) | CalculatorPlayerCard reutiliza estética de Mercado; design system existente | OK |
| NFR5 (rendimiento 120 Hz) | caché DataFreshness, carga paralela, píldora con un solo Bool (sin estado por frame) | OK |
| NFR6 (accesibilidad) | labels accesibles, selección no solo-color, Reduce Motion (animaciones y haptics) | OK |
| NFR7 (seguridad) | sin credenciales; UserDefaults no sensible; NetworkClient autenticado reutilizado | OK |

## Elementos sin cubrir

Ninguno.
