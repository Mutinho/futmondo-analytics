# Frontend Components — U1 `u1-design-system` (SwiftUI)

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés. Nivel de diseño (sin implementación).

## Jerarquía

```
CatalogView (pantalla de catálogo)
├── ThemeToggle (claro/oscuro)
├── TextSizeControl (Dynamic Type)
├── ColorsSection        → muestra ColorToken (+ ejemplo money +/-)
├── TypographySection    → muestra TypographyToken (h1/h2/h3/body)
├── SpacingSection       → muestra SpacingToken
└── ComponentsSection
    ├── PrimaryButton (normal / loading / disabled)
    ├── TextInputField (normal / error / secure)
    ├── Card
    ├── LoadingState
    └── ErrorState
```

## Props / estado por componente

| Componente | Props | Estado |
|-----------|-------|--------|
| PrimaryButton | title, action, isLoading, isEnabled | — (derivado de props) |
| TextInputField | label, text (binding), icon?, isSecure, errorMessage? | foco; visibilidad (si secure) |
| Card | content (view builder) | — |
| LoadingState | message? | — |
| ErrorState | message | — |
| CatalogView | — | colorScheme (toggle), dynamicTypeSize (control) |

## Flujos de interacción

- CatalogView gestiona el `colorScheme` y el `dynamicTypeSize` del preview y los propaga a las secciones (BR1.1, BR1.2).
- Los componentes consumen los tokens de U1 vía la API pública (contract-summary): colores por rol, tipografía por estilo, espaciado por paso.

## Validación de formularios

TextInputField expone `errorMessage`; la validación la aporta el consumidor (p. ej. el login de U2), no la librería. La librería sólo presenta el estado de error (BR2.2).

## Integración con API

Ninguna de red. Integración in-process con la app anfitriona vía la API pública de la librería (contract-summary §1).

## Assumptions & Open Questions

None.
