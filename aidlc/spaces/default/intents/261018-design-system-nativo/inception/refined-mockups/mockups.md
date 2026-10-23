# Refined Mockups — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Mockups de media-alta fidelidad (descripción estructurada + ASCII) por pantalla, usando los tokens de `design-system-mapping.md`. iPhone 13 Pro vertical.

## Pantalla 1 — Catálogo / Preview (US3.1)

Scroll vertical con barra superior de controles. Fondo `surface`; textos `onSurface`.

```
┌───────────────────────────────┐
│ Design System · Catálogo   h1  │
│ [☀︎/☾ tema]      [A− A A+ texto]│  ← toggles (segmented control)
├───────────────────────────────┤
│ COLORES                     h2 │
│ ▣primary ▣tertiary ▣surface    │  ← swatches con etiqueta y hex
│ ▣money+ (+12,5 M) ▣money− (−3,2)│
│ ▭ splash gradient              │
│ TIPOGRAFÍA                  h2 │
│ H1 / H2 / H3 / Body (Roboto)   │
│ ESPACIADO                   h2 │
│ ▏xs ▎sm ▍md ▌lg █xl            │
│ COMPONENTES                 h2 │
│ [ PrimaryButton ] (normal)     │
│ [ PrimaryButton ] (loading ◌)  │
│ [ PrimaryButton ] (disabled)   │
│ ┌ TextInputField ✉ ──────────┐ │
│ │ Email                        │ │
│ └──────────────────────────────┘ │
│ ┌ TextInputField (error) ⚠ ──┐ │
│ Card: ┌──────────────┐         │
│       │ contenido     │        │
│       └──────────────┘         │
│ LoadingState ◌   ErrorState ⚠  │
└───────────────────────────────┘
```

Estados: al pulsar el toggle de tema conmuta claro/oscuro (todos los Color Assets); el control de texto cambia el tamaño de Dynamic Type simulado. [FR5.2]

## Pantalla 2 — Login de F1 revestido (US4.1)

Igual layout que F1 (card centrada sobre splash gradient), ahora con componentes del sistema.

```
┌───────────────────────────────┐
│    (LinearGradient splash)     │
│      ┌────────────────────┐    │
│      │   [logo 64]         │    │
│      │ Futmondo Analytics h1    │
│      │ Inicia sesión…  body     │
│      │ [TextInputField ✉ Email] │
│      │ [TextInputField 🔒 Pass👁]│
│      │ [ErrorState ⚠ (si hay)]  │
│      │ [ PrimaryButton      ]   │  ← loading = spinner
│      └────────────────────┘    │
└───────────────────────────────┘
```

Comportamiento: idéntico a F1 (login → auto-login Keychain → logout; validación; error). Sólo cambia la capa visual. [FR6]

## Responsive

iPhone vertical; la card del login usa `maxWidth 400`, paddings de la escala de espaciado y respeta `safeAreaInsets`. Sin iPad/landscape. [Q5]

## Assumptions & Open Questions

None.
