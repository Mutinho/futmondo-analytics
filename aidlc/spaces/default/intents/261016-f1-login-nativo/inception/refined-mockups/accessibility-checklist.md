# Accessibility Checklist — F1: Login nativo (iOS)

> Fase: inception (refined-mockups). Idioma: castellano; tokens técnicos verbatim en inglés.

| # | Criterio | Cómo se cumple | Estado |
|---|----------|----------------|--------|
| A1 | Labels accesibles en campos | `TextField`/`SecureField` con label visible y `accessibilityLabel` | Plan |
| A2 | Toggle de contraseña etiquetado | `accessibilityLabel("Mostrar/Ocultar contraseña")` | Plan |
| A3 | Orden de foco lógico | `@FocusState` Email → Contraseña → botón | Plan |
| A4 | Dynamic Type | tipografías con `Font` escalable; sin tamaños fijos que trunquen | Plan |
| A5 | VoiceOver | elementos agrupados y anunciados; error anunciado al aparecer | Plan |
| A6 | Reduce Motion | animaciones/shake/`symbolEffect` degradan a instantáneo con `accessibilityReduceMotion` | Plan |
| A7 | Contraste | texto/controles sobre el punto **más claro** del `LinearGradient` cumplen **WCAG AA** (≥ 4.5:1 texto normal, ≥ 3:1 texto grande/iconos); se verifica el peor caso del degradado | Plan |
| A8 | Estados de error no solo por color | el error se comunica con icono + texto, no solo color rojo | Plan |
| A9 | Objetivos táctiles | botones ≥ 44×44 pt | Plan |

> "Plan" = criterio de diseño a verificar en la validación manual del cliente nativo (NFR-3); el
> arnés de test de accesibilidad automatizado queda como deuda registrada junto al arnés XCTest.

## Sources

- [consumes] mockups.md, interaction-spec.md, requirements.md (FR-8), accessibility-wcag
  (knowledge del design agent).

## Assumptions & Open Questions

None.
