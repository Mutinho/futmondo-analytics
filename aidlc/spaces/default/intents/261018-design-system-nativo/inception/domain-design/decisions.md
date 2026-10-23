# Architecture Decision Records — Domain Design (Sistema de diseño nativo iOS)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.

## ADR-001: Decomposición en cuatro componentes (tokens / componentes / catálogo / theming del login)

- **Context**: el sistema de diseño reúne una base de tokens, componentes de UI, una pantalla de verificación y el revestimiento del login de F1. Hay que decidir cómo partir estos bloques para maximizar reutilización, trazabilidad y bajo acoplamiento, a coste 0 € y capa de presentación pura.
- **Decision**: cuatro componentes — `DesignTokens` (base), `DesignComponents` (depende de tokens), `DesignCatalog` (depende de tokens + componentes) y `LoginTheming` (depende de tokens + componentes). Grafo acíclico.
- **Consequences**: (+) separación limpia por responsabilidad y ritmo de cambio; trazabilidad 1:1 con los FR; el catálogo y el revestimiento del login no contaminan la base. (−) un poco más de estructura (4 bloques) que una solución monolítica.
- **Alternatives Rejected**: `DesignSystem` único (tokens+componentes) + `DesignCatalog` (Q1-B) — mezcla base estable con comportamiento de UI y empeora la trazabilidad FR→componente.

## ADR-002: Capa de presentación sin entidades de dominio

- **Context**: ¿los tokens deben modelarse como entidades de dominio?
- **Decision**: no; el sistema es una capa de presentación. Los tokens son constantes/recursos (Color Assets + `DesignTokens` Swift), no entidades persistentes. `entities: []` en todos los componentes.
- **Consequences**: (+) el modelo refleja la realidad (no hay datos persistentes propios); Functional Design no tendrá que definir esquemas de entidad. (−) ninguna relevante.
- **Alternatives Rejected**: modelar tokens como entidades (Q2-B) — artificial para constantes de presentación; añadiría complejidad sin valor.

## Assumptions & Open Questions

None.
