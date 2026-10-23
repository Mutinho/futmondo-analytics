# Build vs Buy — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (market-research). Idioma: castellano; tokens técnicos verbatim en inglés.

## Decisión

**Build**, y de forma forzada por las restricciones durables: la pantalla se construye con **SwiftUI (SDK de Apple, coste 0 €)** sobre la librería de diseño nativa de F1. No hay opción "buy" compatible con el mandato de coste 0 €:

| Opción | Veredicto |
|--------|-----------|
| **Build** con SwiftUI + `FutmondoKit`/DesignSystem existente | **Elegida.** Coste 0 €, reutiliza tokens/componentes ya construidos, sin dependencias nuevas. |
| Comprar un kit de componentes UI de terceros | Descartada: coste recurrente y/o dependencia de pago (viola coste 0 €); además duplicaría la librería de diseño propia. |
| Librería OSS de componentes | Innecesaria: el SDK de Apple + la librería de F1 bastan; añadir una dependencia OSS sólo suma superficie de mantenimiento sin valor aquí. |

## Dependencias

Ninguna nueva. Se consumen endpoints existentes del backend (`/api/v1/analytics/balances`, `/api/v1/user/championships`) sin cambios.

## Sources

- [memory:M1] `project.md`/`team.md`: coste 0 €, sólo SDK de Apple, sin dependencias de pago; librería de diseño nativa de F1.
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/intent-capture/intent-statement.md`.

## Assumptions & Open Questions

None.
