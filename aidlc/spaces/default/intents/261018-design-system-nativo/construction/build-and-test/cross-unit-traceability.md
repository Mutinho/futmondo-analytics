# Cross-Unit Traceability — Sistema de diseño nativo iOS

> Fase: construcción (gate de cobertura cross-unit). Idioma: castellano; tokens técnicos verbatim en inglés.

## Veredicto: PASS

Todos los FR/NFR de requirements.md y todas las historias/AC están cubiertos por al menos una Unit con status OK (o N/A justificado para los verificables sólo en dispositivo), y sus ficheros objetivo existen.

## Cobertura por requisito

| ID | Cubierto por | Unit | Target (fichero) | Estado |
|----|--------------|------|------------------|--------|
| FR1 (+FR1.3) | tokens de color | U1 | DSColorValue.swift / DSColor.swift | OK |
| FR2 | tipografía | U1 | DSTypographyScale.swift / DSFont.swift | OK |
| FR3 | espaciado | U1 | DSSpacing.swift | OK |
| FR4 (+FR4.1/FR4.2) | componentes | U1 | Components/*.swift | OK |
| FR5 | catálogo | U1 | Catalog/CatalogView.swift | OK |
| FR6.1 | login revestido | U2 | LoginView.swift | OK |
| FR6.2 | no-regresión login | U2 | LoginView.swift (+ suite F1 verde) | N/A (verificación en dispositivo) |
| NFR1 | accesibilidad | U1 | ContrastRatio.swift + componentes | OK (contraste) / dispositivo (VoiceOver/Dynamic Type) |
| NFR2 (.4/.5/.6) | seguridad/preservación | U1/U2 | security-design + LoginView.swift | OK |
| NFR3 | fidelidad tema Angular | U1 | tokens/componentes | OK (código) / dispositivo (comparación visual) |
| NFR4 (.1/.2) | render | U2 | LoginView.swift / performance-design | OK (loading) / dispositivo (60 fps) |

## Historias (US)

US1.1–US1.3 → U1 (tokens); US2.1 → U1 (componentes); US3.1 → U1 (catálogo); US4.1 → U2 (login revestido). Todas cubiertas.

## Elementos sin cubrir

Ninguno. Los marcados N/A/dispositivo son verificables sólo en el iPhone 13 Pro por naturaleza (UI nativa), con su owning explícito; no son gaps de implementación.

## Assumptions & Open Questions

None.
