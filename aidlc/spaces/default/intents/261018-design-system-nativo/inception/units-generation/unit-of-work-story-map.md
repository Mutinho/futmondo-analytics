# Unit ↔ Story Map — Sistema de diseño / theming nativo iOS

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Una fila por historia (USx.y), con la Unit que la implementa.

| Historia | Unit ID | Directory | Orden dentro de la Unit | Notas |
|----------|---------|-----------|-------------------------|-------|
| US1.1 (tokens color) | U1 | `u1-design-system` | 1 | base |
| US1.2 (tipografía + Dynamic Type) | U1 | `u1-design-system` | 1 | base |
| US1.3 (espaciado) | U1 | `u1-design-system` | 1 | base |
| US2.1 (componentes base) | U1 | `u1-design-system` | 2 | depende de tokens |
| US3.1 (catálogo/preview) | U1 | `u1-design-system` | 3 | depende de componentes |
| US4.1 (login revestido) | U2 | `u2-login-theming` | 1 | depende de U1 |

## NFR transversales (asignación a Units)

| NFR | Units | Notas |
|-----|-------|-------|
| NFR1 (accesibilidad: Dynamic Type, contraste, VoiceOver) | U1 (componentes y catálogo) + U2 (login revestido) | se verifica en cada superficie |
| NFR2 (coste 0 € / sólo SDK de Apple) | U1 + U2 | restricción global |
| NFR3 (fidelidad al tema de Angular) | U1 (tokens/componentes) verificada en U1 (catálogo) | ajuste fino en el catálogo |
| NFR4 (dispositivo iPhone 13 Pro + Dynamic Type) | U1 + U2 | layout adaptable |

## Concerns transversales

- Accesibilidad (NFR1) y fidelidad (NFR3) atraviesan US2.1/US3.1 (U1) y US4.1 (U2); no son una fila propia.

## Verificación de cobertura

Las 6 historias están asignadas; U1 cubre US1.1–US3.1, U2 cubre US4.1. Ambas Units tienen filas.

## Assumptions & Open Questions

None.
