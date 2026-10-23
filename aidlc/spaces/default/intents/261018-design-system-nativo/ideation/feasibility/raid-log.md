# RAID Log — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: ideación. Idioma: castellano; tokens técnicos verbatim en inglés.
> Risks, Assumptions, Issues, Dependencies. Cada fila lleva su fuente.

## Risks

| ID | Riesgo | Impacto | Mitigación | Source |
|----|--------|---------|------------|--------|
| R-01 | **Fidelidad de reproducción** (dominante): mapear el tema de Angular Material 3 (paleta verde/violeta, Roboto, tokens semánticos) a SwiftUI cuando no hay equivalencia 1:1. | Medio: componentes/tokens que no reflejen el tema de Angular. | Donde no haya equivalente directo, usar Apple HIG a coste 0 €; definir primero los tokens semánticos y validar en una pantalla de catálogo/preview contra el frontend Angular. | [Q7] [Q8] |
| R-02 | **Transversalidad claro/oscuro + Dynamic Type**: que algún componente no responda correctamente sin reglas ad-hoc por pantalla. | Medio: incoherencia visual o fallo de accesibilidad. | Definir tokens semánticos y probar todos los componentes en ambos modos y varios tamaños de Dynamic Type en el catálogo/preview. | [Q7] |
| R-03 | **Revestir F1 con regresión**: aplicar la capa al login ya construido podría alterar su comportamiento. | Medio: regresión funcional en el login validado de F1. | Aplicar sólo capa visual; verificar en el iPhone 13 Pro que login → auto-login → logout siguen igual. | [Q7] |
| R-04 | **Curva de aprendizaje SwiftUI**: experiencia aún limitada. | Bajo (sin plazo): más tiempo de iteración. | Sin plazo; apoyarse en patrones estándar de Apple HIG y en el código de F1. | [Q3] [Q4] |

## Assumptions

| ID | Supuesto | Source |
|----|----------|--------|
| A-01 | La referencia de diseño es el tema del frontend Angular existente (`angular-app/src/styles.scss`: Material 3 paleta verde/violeta, Roboto, claro/oscuro, tokens semánticos propios), reproducido en SwiftUI. Google Stitch queda descartado (decisión del propietario, 2026-10-18). El mapeo exacto Material 3 → SwiftUI se concreta en mockups. | [Q8] [Q7] |
| A-02 | La cadena `xtool`/WSL con firma gratuita sigue operativa como en F1 (no se re-valida en este intent). | [Q3] |

## Issues

| ID | Issue | Source |
|----|-------|--------|
| — | None. | — |

## Dependencies

| ID | Dependencia | Source |
|----|-------------|--------|
| D-01 | Tema del frontend Angular existente (`angular-app/src/styles.scss`) como fuente de verdad del diseño a reproducir (colores, tipografía, claro/oscuro, tokens semánticos). | [Q8] |
| D-02 | Proyecto iOS de F1 (login) como base a revestir y estructura SwiftPM/`xtool.yml` sobre la que encaja la capa. | [Q1] |

## Assumptions & Open Questions

None.
