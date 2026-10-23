# Contract Summary — Sistema de diseño / theming nativo iOS

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Un único boundary inter-unit: U2 `u2-login-theming` consume la API pública de la librería U1 `u1-design-system`. No hay API externa ni contrato de red.

## Contracts table

| # | Provider Unit | Consumer | Mechanism | Owner |
|---|---------------|----------|-----------|-------|
| 1 | `u1-design-system` (U1) | `u2-login-theming` (U2) | API pública de librería Swift (SwiftPM), in-process | U1 |

## Contrato 1 — Superficie pública Swift de `u1-design-system`

Contrato de tipos/API Swift (no OpenAPI/AsyncAPI; es consumo in-process). Esquema de la superficie pública que U1 garantiza a U2 y a futuros consumidores (F2):

```yaml
# shared-schema (Swift public API surface) — u1-design-system
module: DesignSystem        # nombre del paquete/módulo SwiftPM de U1 que agrupa DesignTokens, DesignComponents y DesignCatalog como targets/áreas internas; NO funde los componentes de domain-design (ver ADR-001). El nombre final del módulo se confirma en code-generation.
public_api:
  colors:                      # Color Assets expuestos (resuelven claro/oscuro automáticamente)
    type: SwiftUI.Color (via asset catalog + accessor)
    tokens: [primary, onPrimary, tertiary, surface, onSurface, onSurfaceVariant,
             moneyPositive, moneyNegative, errorContainer]
    splashGradient: LinearGradient   # 135° #1B5E20→#2E7D32→#43A047
  typography:
    type: DesignTokens.Typography
    styles: [h1, h2, h3, body]       # Roboto con fallback a sistema; Dynamic Type
  spacing:
    type: DesignTokens.Spacing
    steps: [xs, sm, md, lg, xl]      # 4/8/16/24/32 pt
  components:
    - name: PrimaryButton
      inputs: [title: String, action: () -> Void, isLoading: Bool, isEnabled: Bool]
    - name: TextInputField
      inputs: [label: String, text: Binding<String>, icon: Image?, isSecure: Bool, errorMessage: String?]
    - name: Card
      inputs: [content: () -> View]
    - name: LoadingState
      inputs: [message: String?]
    - name: ErrorState
      inputs: [message: String]
  accessibility_guarantee: >
    Todos los componentes exponen label/rol VoiceOver, soportan Dynamic Type y cumplen
    el contraste objetivo (≥4.5:1 / ≥3:1) en claro y oscuro. [NFR1]
```

## Contract ownership rules

- **Owner**: U1 es dueña de la superficie pública. U2 (y F2) son consumidores.
- **Cambios rompientes**: al ser mismo repo y único mantenedor, un cambio rompiente en la API de U1 se corrige en el mismo cambio en los consumidores; el compilador Swift garantiza que no queden referencias rotas. Sin versionado SemVer formal. [Q2]
- **Cambios aditivos**: nuevos tokens o componentes no rompen a los consumidores existentes (añaden superficie, no la quitan).

## Open questions

| Contract | Question | Blocks |
|----------|----------|--------|
| 1 | Nombres finales de símbolos públicos (p. ej. `Color.dsPrimary` vs. `DesignSystem.Color.primary`) | se fija en functional-design / code-generation de U1 |

## Assumptions & Open Questions

- [assumption] El nombre de módulo `DesignSystem` y la forma exacta de los accessors se concretan en la construcción de U1; aquí se fija la superficie (qué expone), no la sintaxis final. [Q1]
