# Accessibility Checklist — Sistema de diseño nativo iOS

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Objetivo: WCAG AA donde aplique a móvil nativo (Q4=A). Verificable con Accessibility Inspector de Xcode. [NFR1]

| # | Criterio | Aplica a | Verificación |
|---|----------|----------|--------------|
| A1 | Contraste texto normal ≥ 4.5:1 en claro y oscuro | todos los tokens de texto sobre superficie | Accessibility Inspector / contrast checker |
| A2 | Contraste texto grande y elementos de UI ≥ 3:1 | botones, bordes de campo | Accessibility Inspector |
| A3 | Dynamic Type: el texto escala sin recortes ni solapamientos | tipografía y todos los componentes | preview con tamaños hasta `.accessibility3` |
| A4 | VoiceOver: label y rol correctos | PrimaryButton, TextInputField, estados | VoiceOver en iPhone 13 Pro |
| A5 | Estado anunciable (loading/error) | PrimaryButton, ErrorState | VoiceOver |
| A6 | Áreas táctiles ≥ 44×44 pt | botones, toggle de visibilidad, controles del catálogo | inspección de layout |
| A7 | No depender solo del color para transmitir estado | error (icono + texto, no solo rojo) | revisión visual |

## Assumptions & Open Questions

None.
