# Design System Mapping — Angular Material 3 → SwiftUI

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Mapeo del tema del frontend Angular (`angular-app/src/styles.scss`) a tokens nativos SwiftUI. Valores representativos (Q1=A); el ajuste fino se valida en el catálogo (FR5.2) contra Angular. Materialización: Color Assets (claro/oscuro) + `DesignTokens` (Q2=A).

## 1. Tokens de color (Color Assets, Any/Dark Appearance) — [FR1]

| Token SwiftUI (Color Asset) | Rol Material 3 / origen | Claro | Oscuro | Fuente |
|-----------------------------|-------------------------|-------|--------|--------|
| `primary` | `mat.$green-palette` (primary) | `#2E7D32` | `#66BB6A` | styles.scss (verde) |
| `onPrimary` | on-primary | `#FFFFFF` | `#0A1F0C` | HIG/contraste |
| `tertiary` | `mat.$violet-palette` (tertiary) | `#7E57C2` | `#B39DDB` | paleta violeta Material |
| `surface` | surface / `--mat-sys-surface-container-lowest` | `#FFFFFF` | `#121212` | styles.scss body |
| `onSurface` | on-surface | `#1C1B1F` | `#E6E1E5` | Material 3 |
| `onSurfaceVariant` | on-surface-variant (headers de tabla) | `#49454F` | `#CAC4D0` | styles.scss tabla |
| `moneyPositive` | token semántico propio | `#2E7D32` | `#66BB6A` | styles.scss `.money-positive` |
| `moneyNegative` | token semántico propio | `#D32F2F` | `#EF5350` | styles.scss `.money-negative` |
| `errorContainer` | fondo de error | `#FFEBEE` | `#3A1416` | styles.scss `.error-message` |

**Splash gradient** (recurso, no Color Asset único): `LinearGradient` 135° `#1B5E20 → #2E7D32 → #43A047`. [FR1.3]

> Nota: los hex de `primary`/`tertiary`/`surface`/`onSurface` son los tonos representativos de Material 3; se validan de un vistazo en el catálogo contra el render de Angular y se afinan si hace falta (sin coste). [Q1]

## 2. Tipografía (`DesignTokens.Typography`) — [FR2]

| Estilo | Tamaño/peso (claro de `styles.scss`) | SwiftUI | Dynamic Type |
|--------|--------------------------------------|---------|--------------|
| `h1` | 28 pt / 700 | `Font` Roboto (o `.system`) weight `.bold`, relativo a `.largeTitle` | sí |
| `h2` | 20 pt / 600 | relativo a `.title2` weight `.semibold` | sí |
| `h3` | 16 pt / 600 | relativo a `.headline` | sí |
| `body` | 14 pt / 400 | relativo a `.body`/`.callout` | sí |

Roboto se usa si está empaquetada; si no, fuente del sistema con la misma escala (FR2.3). Todos los estilos usan `@ScaledMetric`/`Font.relativeTo` para Dynamic Type. [FR2.2]

## 3. Espaciado (`DesignTokens.Spacing`) — [FR3]

`xs=4`, `sm=8`, `md=16`, `lg=24`, `xl=32` (pt).

## 4. Componentes → origen Angular — [FR4]

| Componente SwiftUI | Referencia Angular | Notas |
|--------------------|--------------------|-------|
| `PrimaryButton` | `mat-flat-button color="primary"` (login) | estados normal/disabled/loading (spinner) |
| `TextInputField` | `mat-form-field appearance="outline"` + `matPrefix` icon | label, icono opcional, estado de error |
| `Card` | `mat-card` | superficie con `surface`, corner radius 16 |
| `LoadingState` / `ErrorState` | `mat-spinner` / `.error-message` | reutilizables |

## 5. Donde Material 3 no tiene equivalente 1:1

Densidad de Material, ciertos `--mat-sys-*` computados y `::ng-deep` no portan; se cubren con **Apple HIG** (p. ej. alturas de control, `cornerRadius`, áreas táctiles ≥44 pt). [NFR3]

## Assumptions & Open Questions

- [assumption] Los hex de primary/tertiary/surface/onSurface son representativos de Material 3 y se afinan en el catálogo contra Angular; no se extraen en runtime. [Q1]
