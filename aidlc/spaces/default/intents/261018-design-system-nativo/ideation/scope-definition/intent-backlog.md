# Intent Backlog — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: ideación. Idioma: castellano; tokens técnicos verbatim en inglés.
> Backlog priorizado de proto-Units (capacidades), MoSCoW + secuenciación risk-first con orden de dependencias.
> No es un plan de construcción fino (eso es un intent/etapa posterior); acompaña al scope-document.

## Priorización (MoSCoW)

| ID | Proto-Unit (capacidad) | MoSCoW | Orden | Dependencias | Source |
|----|------------------------|--------|-------|--------------|--------|
| DS-01 | **Spike de fidelidad**: tokens de color claro/oscuro + 1 componente (botón) validado contra el tema de Angular, en claro/oscuro. | Must | 1 (risk-first) | — | [Q4] [Q1] |
| DS-02 | Tokens de color semánticos completos (claro/oscuro) reproduciendo el tema Angular Material 3 (verde/violeta, `money-positive`/`money-negative`, splash). | Must | 2 | DS-01 | [Q1] [Q2] [Q3] |
| DS-03 | Tipografía Roboto + escala `h1/h2/h3` + Dynamic Type. | Must | 2 | DS-01 | [Q2] [Q3] |
| DS-04 | Tokens de espaciado. | Must | 2 | DS-01 | [Q2] [Q3] |
| DS-05 | Componentes SwiftUI base: campo de texto, tarjeta, estados de carga/error (el botón sale de DS-01). | Must | 3 | DS-02, DS-03, DS-04 | [Q1] [Q2] [Q3] |
| DS-06 | Pantalla de catálogo/preview (claro/oscuro + varios tamaños Dynamic Type) como evidencia. | Must | 4 | DS-05 | [Q2] [Q3] |
| DS-07 | Revestir el login de F1 con el sistema, sin cambios de comportamiento. | Must | 5 | DS-02..DS-05 | [Q1] [Q2] [Q3] |
| DS-08 | Variantes extra de componentes (tamaños/estilos secundarios). | Could | tras MVP | DS-05 | [Q2] |

## Lectura del backlog

- **Must (MVP del sistema de diseño)**: DS-01..DS-07. El spike DS-01 va primero por risk-first; el resto sigue el orden de dependencias. [Q4] [Q3]
- **Could**: DS-08 (variantes extra), tras el MVP. [Q2]
- **Fuera (no es backlog de este intent)**: tab bar nativa (B-08), pantallas de F2, animaciones avanzadas, temas extra, dependencias de pago. [Q6]

## Assumptions & Open Questions

None.
