# Design System Mapping — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (refined-mockups). Idioma: castellano; tokens técnicos verbatim en inglés.
> Mapea cada elemento de F2 a los tokens/componentes de la librería de diseño de F1 (`FutmondoKit`/`FutmondoApp` DesignSystem). F2 consume, no rediseña.

| Elemento F2 | Token / componente F1 | Origen (tema Angular) |
|-------------|-----------------------|-----------------------|
| Nombre de equipo (`team_name`) | `DSFont` escala h3 | `h3` de `styles.scss` |
| `balance`, `performance` ≥0 | `DSColor.moneyPositive` | `money-positive` |
| `balance`, `performance` <0 | `DSColor.moneyNegative` | `money-negative` |
| Etiquetas secundarias (puja máx, premios) | `DSFont` body + color secundario | tipografía Material 3 body |
| Superficie de fila/card | `Card` component (DesignSystem) | superficie Material 3 |
| Fondo / primaria (navigation bar, acentos) | `DSColor` primary verde (light/dark) | `mat.$green-palette` |
| Indicador de carga | `LoadingState` component | spinner Material |
| Estado de error | `ErrorState` component + botón | patrón de error |
| Espaciado entre elementos | `DSSpacing` escala | densidad Material |
| Modo claro/oscuro | tokens light/dark de `DSColorValue` | Material + `body.dark-theme` |

Donde Material 3 no tenga equivalente 1:1 (p. ej. el material de la tab bar), se usa el comportamiento nativo del SDK (Liquid Glass) por Apple HIG, sin tokens de pago.

## Componentes nuevos de F2 (sobre la librería)

- `BudgetRow` (o card) que compone los tokens anteriores — nuevo en `FutmondoApp`, reutilizando `Card`/`DSFont`/`DSColor`.
- `ChampionshipMenu` (contenido del `Menu` de la navigation bar) — nuevo, usando tipografía/colores del DesignSystem.
- Si falta algún token puntual, se añade al DesignSystem en el mismo estilo (no se crea un sistema paralelo).

## Sources

- `ios/Sources/FutmondoApp/DesignSystem/*`, `ios/Sources/FutmondoKit/DesignSystem/*`
- `angular-app/src/styles.scss` (fuente de verdad)

## Assumptions & Open Questions

None.
