# Units of Work — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Agrupa los componentes de domain-design en Units construibles. Topología solo; el orden económico lo decide Delivery Planning.

## Units

| Unit ID | Directory | Descripción | Kind | Despliegue | Complejidad |
|---------|-----------|-------------|------|------------|-------------|
| U1 | `u1-design-system` | Librería del sistema de diseño: tokens (color/tipografía/espaciado) + componentes base (botón, campo, tarjeta, estados) + pantalla de catálogo/preview. | library | Embebido en la app iOS (SwiftPM) | M |
| U2 | `u2-login-theming` | Revestir el login de F1 con la librería del sistema, sin cambios de comportamiento. | ui | Embebido en la app iOS | S |

## Responsabilidades

- **U1 (`u1-design-system`)**: posee DesignTokens, DesignComponents y DesignCatalog. Entrega la librería reutilizable y su catálogo de verificación (claro/oscuro + Dynamic Type). Es la base que consume U2 y las futuras pantallas de F2.
- **U2 (`u2-login-theming`)**: posee LoginTheming. Aplica tokens y componentes de U1 al login existente de F1 preservando su comportamiento (login → auto-login → refresh → logout).

## Notas de implementación / restricciones

- Sólo SDK de Apple (SwiftUI); coste 0 €; sin dependencias de pago. [NFR2]
- U1 define Color Assets (claro/oscuro) y `DesignTokens` (tipografía/espaciado) según `design-system-mapping.md`.
- U2 no cambia la lógica del login de F1; verificación manual de no-regresión en el iPhone 13 Pro. [FR6.2]
- Sin cambios de backend ni de CI/CD.

## Assumptions & Open Questions

None.
