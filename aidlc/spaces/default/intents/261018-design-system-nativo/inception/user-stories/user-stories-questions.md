# User Stories — Plan y preguntas

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Plan de historias (INVEST, Given/When/Then, MoSCoW) derivado de requirements.md. Rellena cada `[Answer]:`.

## Plan propuesto

- **Personas**: una única persona — el **propietario/mantenedor-usuario** (desarrolla la app y la usa en su iPhone 13 Pro).
- **Formato**: "Como [persona], quiero [objetivo], para [beneficio]" + criterios de aceptación Given/When/Then; IDs `US{grupo}.{seq}` y `AC{grupo}.{seq}.{n}`.
- **Breakdown**: por área funcional alineada con los FR (tokens, componentes, catálogo, revestir F1, accesibilidad).
- **Priorización**: MoSCoW; los Must cubren el MVP del sistema de diseño.

## Q1. Enfoque de personas

- A. Una sola persona (propietario/mantenedor-usuario), coherente con el stakeholder único del intent.
- B. Separar dos roles (usuario final vs. desarrollador) aunque sean la misma persona.
- X. Other (please specify)

[Answer]: A. Una sola persona (propietario/mantenedor-usuario).

## Q2. Granularidad / breakdown de las historias

- A. Por área funcional alineada con los FR: tokens (FR1–FR3), componentes (FR4), catálogo (FR5), revestir F1 (FR6), accesibilidad (NFR1). Historias pequeñas y testables.
- B. Una historia por cada componente/token (más granular).
- X. Other (please specify)

[Answer]: A. Por área funcional alineada con los FR.

## Q3. ¿La accesibilidad (Dynamic Type, contraste, VoiceOver) se expresa como…?

- A. Criterios de aceptación transversales dentro de las historias de componentes y catálogo (no una historia aparte).
- B. Una historia propia de accesibilidad.
- X. Other (please specify)

[Answer]: A. Criterios de aceptación transversales en las historias de componentes y catálogo.

## Consolidated Summary Confirmation

Resumen de User Stories:

- **Persona única (Q1=A)**: propietario/mantenedor-usuario.
- **Breakdown por área FR (Q2=A)** y **accesibilidad como AC transversal (Q3=A)**.
- **6 historias**: US1.1 tokens color, US1.2 tipografía+Dynamic Type, US1.3 espaciado, US2.1 componentes base (+AC de accesibilidad), US3.1 catálogo verificable, US4.1 login revestido sin regresión. Todas Must.
- **Trazabilidad**: FR1–FR6 y NFR1/NFR3 cubiertos por historias; NFR2 (coste) y NFR4 (dispositivo) marcados N/A transversales.

¿Does this all look correct?

[Answer]: Looks correct
