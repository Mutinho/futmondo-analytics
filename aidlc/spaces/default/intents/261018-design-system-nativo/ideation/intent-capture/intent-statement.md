# Intent Statement — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: ideación. Idioma: castellano; tokens técnicos (SwiftUI, Dynamic Type, iOS Keychain, Angular, HIG) verbatim en inglés.
> Documento de encuadre: establece el problema, beneficiario, éxito, disparador y señal de alcance. No contiene detalle de implementación.

## Problem Statement

La app nativa iOS (Swift/SwiftUI) sólo tiene hoy el login (F1) construido, sin una capa de diseño común. Construir las pantallas de datos (F2) y posteriores sin una base compartida de estilo provocaría retrabajo (repasar todas las pantallas después), incoherencia visual entre pantallas y una construcción más lenta, además de reinventar en cada pantalla el soporte de claro/oscuro y accesibilidad. [desc] [Q1] Este intent resuelve ese problema entregando una **capa de diseño reutilizable** (tokens de color claro/oscuro, tipografía con Dynamic Type, espaciado y componentes SwiftUI base: botones, campos, tarjetas, estados de carga/error), **sólo con SDK de Apple** y a coste 0 €. [desc] [Q1] [memory:M1]

## Target Customer

En este proyecto personal el beneficiario es una misma persona en dos papeles: **usuario final** de la app en el iPhone 13 Pro, que gana una experiencia visual consistente y cómoda; y **desarrollador/mantenedor**, que reduce el coste de mantener estilos dispersos pantalla a pantalla. [Q2] [Q5]

## Success Metrics

- Las pantallas de F2 pueden construirse **usando sólo los componentes y tokens del sistema**, sin que ninguna pantalla defina estilos propios ad-hoc. [Q3]
- El login de F1 queda **revestido con el sistema sin cambios de comportamiento** (sólo capa visual), verificable en el iPhone 13 Pro. [Q3]
- **Claro/oscuro y Dynamic Type** funcionan en todos los componentes base, demostrable con una pantalla de catálogo/preview. [Q3]
- **Coste 0 €**: sólo SDK de Apple, sin ninguna dependencia de pago ni servicio recurrente. [Q3] [memory:M1] [memory:M2]

## Initiative Trigger

Es una decisión ya tomada al cerrar F1 (2026-10-18): el momento óptimo para esta capa es **antes de F2**, porque la alimenta y de paso reviste el login de F1 con coste marginal; hacerla tras F2/F3 ya construidas obligaría a retrabajo. [Q4] [desc]

## Initial Scope Signal

- **Scope seleccionado en el workflow**: `feature` (workflow-selected). [scope]
- **Boundary de producto confirmado por el usuario (Q8)** — esta primera versión deja FUERA: componentes complejos específicos de pantalla, incluida la navegación/tab bar nativa (B-08), que corresponde a F2; la aplicación del sistema a las pantallas de F2 (eso lo hace F2; este intent sólo entrega la capa y reviste F1); animaciones/transiciones avanzadas y microinteracciones; y temas adicionales más allá de claro/oscuro (alto contraste, temas de marca personalizables). [Q8]

## Assumptions & Open Questions

- [assumption] La referencia de diseño es el **tema del frontend Angular existente** (`angular-app/src/styles.scss`: Material 3 con paleta verde/violeta, Roboto, modo claro/oscuro y tokens semánticos propios), que el sistema de diseño nativo debe **reproducir en SwiftUI** al 100%. Google Stitch, considerado inicialmente como referencia, queda **descartado** (decisión del propietario, 2026-10-18). El mapeo exacto de Material 3 a SwiftUI se concretará en las etapas de mockups. [Q9]
