# Design System Mapping — F3 Mercado (app nativa iOS)

> Mapeo de cada elemento de Mercado a los componentes/tokens del `DesignSystem`
> de F1/F2 (reutilización máxima; nada nuevo de pago).

## Sources

- `.../inception/refined-mockups/mockups.md`.
- Base F1/F2: `ios/Sources/FutmondoApp/DesignSystem/` y `FutmondoKit/DesignSystem/`.

## Mapeo

| Elemento Mercado | Componente/token reutilizado | Nota |
|---|---|---|
| Fondo de pantalla | `AuthenticatedBackground` (`background.jpg` vía `Bundle.module`) | Igual que F2 |
| Card de jugador | `NeonGlassCard` (DSElevation/glass) | Misma superficie oscura/neón |
| Botón "PUJAR" | `PrimaryButton` | Acento neón |
| Botón cancelar / orden | `GlassIconButton` (blanco) | Igual que F2 |
| Campo de importe | `TextInputField` | Teclado numérico + prefijo € |
| Chips de posición | `Chips` (position) | Reutilizado |
| Colores de dinero | `DSColor.moneyPositive` / `moneyNegative` | Umbrales FR3/US2 |
| Tipografía | `DSFont` (h1/h2/label/value) | Escala de F1 |
| Espaciado | `DSSpacing` | Escala de F1 |
| Estados carga/error/vacío | LoadingState / ErrorState / EmptyState de F2 | Reutilizados |
| Formato de moneda | `MoneyFormatter` (FutmondoKit) | es-ES, 0 decimales |

## Elementos sin equivalente 1:1 (cubrir con HIG)

- **Sheet de puja / detalle Sofascore**: `.sheet` nativo (HIG) con contenido
  `NeonGlassCard`.
- **Confirmación de cancelación**: `.confirmationDialog`/`.alert` nativo (HIG).
- **Badges Sofascore / % titular**: componiendo `DSColor`/`DSFont` (no había badge
  en F2; se crea con tokens existentes, sin dependencia nueva).

## Assumptions & Open Questions

None.
