# Logical Components — U1 `u1-design-system`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.
> Estructura lógica de la librería SwiftUI (módulo SwiftPM `DesignSystem` dentro de `ios/`).

## Estructura propuesta (SwiftPM target)

```
DesignSystem (target/módulo)
├── Tokens/
│   ├── DSColor        (accessors a los Color Assets por rol: primary, tertiary, surface, …, money+/-)
│   ├── DSTypography   (estilos h1/h2/h3/body con Dynamic Type; Roboto + fallback)
│   ├── DSSpacing      (xs/sm/md/lg/xl)
│   └── DSSplashGradient
├── Components/
│   ├── PrimaryButton
│   ├── TextInputField  (usa SecureField cuando isSecure; el toggle de visibilidad es estado interno de la vista, NO parte de la superficie pública del contrato)
│   ├── Card
│   ├── LoadingState
│   └── ErrorState
└── Catalog/
    └── CatalogView     (+ ThemeToggle, TextSizeControl, secciones)
Resources/
└── Assets.xcassets     (Color Sets con Any/Dark Appearance)
```

## Resolución de NFR por diseño

| NFR | Cómo se cumple |
|-----|----------------|
| NFR2.1 (coste 0 €) | Sólo SDK de Apple; sin dependencias en `Package.swift`. |
| NFR2.3 (secure field) | `SecureField` + toggle local; sin copia del valor. |
| NFR3 (fidelidad tema) | Color Assets derivados del tema de Angular; verificable en CatalogView. |
| NFR1 (accesibilidad) | Dynamic Type en DSTypography; `accessibilityLabel`/rol en componentes; contraste de los Color Sets. |

## Assumptions & Open Questions

None.
