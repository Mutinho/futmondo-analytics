# Market Trends — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (market-research). Idioma: castellano; tokens técnicos verbatim en inglés.

## Aplicabilidad

**NO-APLICA/ligero.** Al ser una feature de paridad para uso propio, no hay tendencias de mercado que dirijan el diseño. La única "tendencia" relevante es técnica y ya está decidida en memoria: patrones nativos iOS idiomáticos (SwiftUI + Apple HIG) sobre el tema Material 3 de la web.

## Señales técnicas relevantes (no de mercado)

- Patrón iOS para selección contextual siempre accesible: menú en la navigation bar (`Menu` en toolbar) es el idiom actual de Apple HIG para cambiar de contexto sin ocupar espacio fijo. Alinea con la decisión Q1-A.
- Listas de datos en iPhone: `List`/`LazyVStack` con filas ricas es el patrón nativo preferido frente a tablas con scroll horizontal (alinea con Q3-A).

## Sources

- Apple HIG (referencia de patrones nativos; sin coste).
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/intent-capture/intent-statement.md`.

## Assumptions & Open Questions

None.
