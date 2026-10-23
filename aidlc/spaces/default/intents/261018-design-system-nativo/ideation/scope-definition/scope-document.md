# Scope Document — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: ideación. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, Material 3, Apple HIG) verbatim en inglés.
> Define el boundary in/out y la secuenciación. Consume: intent-statement, feasibility-assessment, constraint-register.

## Scope de workflow

`feature` (workflow-selected). [scope]

## Dentro de alcance (IN)

| # | Capacidad | MoSCoW | Source |
|---|-----------|--------|--------|
| IN-1 | Tokens de color semánticos claro/oscuro derivados del tema del frontend Angular (`angular-app/src/styles.scss`: Material 3 paleta verde/violeta, `money-positive`/`money-negative`, gradiente de splash) reproducidos en SwiftUI. | Must | [Q1] [Q2] |
| IN-2 | Tipografía Roboto con escala (`h1/h2/h3`) y soporte Dynamic Type. | Must | [Q1] [Q2] |
| IN-3 | Tokens de espaciado. | Must | [Q1] [Q2] |
| IN-4 | Componentes SwiftUI base: botón, campo de texto, tarjeta, estados de carga/error. | Must | [Q1] [Q2] |
| IN-5 | Pantalla de catálogo/preview que demuestra tokens y componentes en claro/oscuro y varios tamaños de Dynamic Type. | Must | [Q2] |
| IN-6 | Revestir el login de F1 con el sistema, sin cambios de comportamiento. | Must | [Q1] [Q2] |
| IN-7 | Variantes extra de componentes (tamaños/estilos secundarios). | Could | [Q2] |

## Fuera de alcance (OUT)

| # | Exclusión | Source |
|---|-----------|--------|
| OUT-1 | Navegación / tab bar nativa (B-08) — corresponde a F2. | [Q6] |
| OUT-2 | Aplicación del sistema a las pantallas de datos de F2 (eso lo hace F2). | [Q6] |
| OUT-3 | Animaciones/transiciones avanzadas y microinteracciones. | [Q6] |
| OUT-4 | Temas adicionales más allá de claro/oscuro (alto contraste, temas de marca personalizables). | [Q6] |
| OUT-5 | Cualquier dependencia de pago o servicio recurrente. | [Q6] |

## Secuenciación

**Risk-first con orden de dependencias** (Q4=B): primero un **spike** de tokens + 1 componente validado en claro/oscuro contra el frontend Angular (retira el riesgo dominante de fidelidad de reproducción), y luego el resto respetando la cadena de dependencias tokens → componentes → catálogo → revestir F1 (Q3=A). Sin deadlines (Q5=A). [Q4] [Q3] [Q5]

## Dependencias

Los tokens son la base; los componentes dependen de los tokens; el catálogo depende de los componentes; revestir F1 depende de tokens + componentes. [Q3]

## Assumptions & Open Questions

None.
