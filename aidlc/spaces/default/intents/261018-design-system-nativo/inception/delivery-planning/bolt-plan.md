# Bolt Plan — Sistema de diseño / theming nativo iOS

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Un **Bolt** es una pasada de construcción sobre una porción del trabajo que termina en algo que corre. Orden en serie según el DAG de Units.

## Bolt 1 — Librería del sistema de diseño (U1 `u1-design-system`)

- **Units**: U1.
- **Walking skeleton**: no aplica (línea base OFF; sistema en producción).
- **Definition of Done**: tokens (Color Assets claro/oscuro + `DesignTokens` tipografía/espaciado), componentes base (PrimaryButton, TextInputField, Card, LoadingState, ErrorState) y pantalla de catálogo/preview implementados; el catálogo compila y permite alternar claro/oscuro y tamaño de Dynamic Type; accesibilidad (contraste, VoiceOver, táctil) verificada en el catálogo.
- **Confidence hypothesis**: el catálogo demuestra que la reproducción del tema de Angular en SwiftUI es fiel y que claro/oscuro + Dynamic Type funcionan transversalmente — retira el riesgo dominante antes de tocar F1.
- **Demo esperada**: abrir el catálogo en el iPhone 13 Pro, alternar tema y tamaño de texto, comparar con el tema de Angular.

## Bolt 2 — Revestir el login de F1 (U2 `u2-login-theming`)

- **Units**: U2 (depende de U1).
- **Definition of Done**: el login de F1 usa los componentes y tokens de U1; su comportamiento (login → auto-login → refresh → logout, validación, errores) no cambia; verificación manual de no-regresión en el iPhone 13 Pro.
- **Confidence hypothesis**: el sistema de diseño se aplica a una pantalla real (el login) sin regresión, validando que sirve de base para F2.
- **Demo esperada**: login revestido en el iPhone 13 Pro, visualmente coherente con el sistema y funcionalmente idéntico a F1.

## Assumptions & Open Questions

None.
