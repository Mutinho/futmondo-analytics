# Constraint Register — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: ideación. Idioma: castellano; tokens técnicos verbatim en inglés.
> Restricciones técnicas, económicas, organizativas y regulatorias que acotan el intent. Cada fila lleva su fuente.

## Técnicas

| ID | Restricción | Source |
|----|-------------|--------|
| C-T1 | Sólo SDK de Apple (SwiftUI); ninguna librería de UI de terceros ni dependencia de pago. | [Q4] [memory:M1] |
| C-T2 | Capa autocontenida que encaja con la estructura SwiftPM/`xtool.yml` y las convenciones del código iOS de F1 (sin integraciones externas). | [Q1] |
| C-T3 | Construcción/firma/instalación por la cadena `xtool` desde WSL con firma gratuita (ya validada en F1). | [Q3] |
| C-T4 | El soporte de claro/oscuro y Dynamic Type debe ser transversal a todos los componentes base (sin reglas ad-hoc por pantalla). | [Q7] |
| C-T5 | Revestir el login de F1 sin cambiar su comportamiento (sólo capa visual). | [Q7] |

## Económicas

| ID | Restricción | Source |
|----|-------------|--------|
| C-E1 | Coste 0 € recurrente; la excepción acotada de publicación nativa (Apple Developer Program) NO se activa en este intent. | [Q4] [memory:M1] [memory:M2] |

## Organizativas

| ID | Restricción | Source |
|----|-------------|--------|
| C-O1 | Un único decisor/mantenedor; sin plazo, sin change freeze ni prioridades en conflicto. | [Q5] [Q4] |

## Regulatorias

| ID | Restricción | Source |
|----|-------------|--------|
| C-R1 | Sin requisitos regulatorios (PCI/HIPAA/SOC2/residencia); la capa no maneja datos personales ni de pago. Se preserva la regla durable de no almacenar credenciales en claro (no afectada por este intent). | [Q2] |

## Assumptions & Open Questions

None.
