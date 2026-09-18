## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-09-18T10:30:17Z
**Iteration:** 1

Revisión advisory del catálogo de componentes de `domain-design` para un intent
acotado (corrección del reparto del premio de ranking ante empates, FR1). El
objetivo de esta pasada es informar la decisión del gate humano, no abrir un
ciclo de corrección. He verificado buena-formación del catálogo, coherencia con
el intent y calidad de los ADR contra los artefactos aportados (`components.md`,
`decisions.md`, `requirements.md`, `team-practices.md`) y el RE
(`architecture.md`, `component-inventory.md`).

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | inception/domain-design/components.md > entidades TeamRoundPrize / TeamPrizeRow | Las dos entidades comparten identificador `(championship_id, team_id, matchday)` y cuatro de cinco atributos, pero difieren en el nombre del atributo posicional: `TeamRoundPrize.display_position` vs `TeamPrizeRow.position`. El mapeo resultado→fila (ADR-002, "trivial: mismos campos") no es literalmente campo-a-campo por esa asimetría; un desarrollador tendría que inferir que `display_position` → `position`. | Documentar explícitamente el mapeo `display_position` → `position` (o unificar el nombre), para que el cableado orquestador→persistencia no dependa de inferencia. | New |
| R-02 | Minor | inception/domain-design/components.md > PrizeCalculator.behaviour (regla FR1) y decisions.md > ADR-001 | El comportamiento describe el reparto como suma de posiciones contiguas dividida entre N con `round()` por parte, pero no explicita qué entradas por posición recibe la calculadora (¿los importes `money_per_ranking * ratio` ya materializados por posición, o los parámetros crudos `money_per_ranking`/`ranking_mode`/`total_pct` para calcularlos ella misma?). FR1.2 y los supuestos de `requirements.md` asumen que la fórmula por posición ya es correcta y no se toca; el contrato de entrada de la función pura no lo fija. | Precisar en el `behaviour` (o en un contrato de firma) si `PrizeCalculator` recibe los importes por posición ya calculados o los computa desde la config, para que la frontera pura quede implementable sin preguntar al arquitecto. | New |
| R-03 | Minor | inception/domain-design/components.md > PrizeCalculator.behaviour (FR1.4) | El diseño hereda de FR1.4/OQ1 el redondeo `round()` por parte, que puede hacer que la suma de los N premios repartidos no cuadre con la suma de las N posiciones contiguas (resto no distribuido) — p. ej. suma 3.000.001 / 2. Es una incertidumbre de negocio ya registrada (OQ1), no un defecto del catálogo, pero afecta a la implementabilidad determinista de la función pura y a la caracterización. | Ninguna acción bloqueante en domain-design; dejar constancia de que la función pura debe hacer observable/registrable el resto para que la caracterización capte qué hace Futmondo si el caso se materializa (según OQ1). | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (ninguna herramienta de validación declarada para esta etapa) | N/A | Verificación manual: nombres únicos; `depends_on`/`dependents` simétricos (Orchestrator→Calculator y Calculator.dependents=Orchestrator); grafo acíclico (una sola arista dirigida); cada entidad con un único dueño e identificador; `external_dependencies` (Futmondo API, Neon PostgreSQL) declaradas como dependencias externas, no como componentes. Todo PASS. |

### Resumen

El catálogo está bien formado y es coherente con el intent: `PrizeCalculator`
puro (sin I/O ni SQL) que posee `TeamRoundPrize`, `PrizeSyncOrchestrator` como
`sync_prizes` reducido a ingesta→cálculo→persistencia que posee `TeamPrizeRow`,
sin engordar el god-file y con la mitad de lectura (routers → `SELECT`/suma sobre
`team_prizes`) intacta, tal como describe el RE. Los dos ADR incluyen Context,
Decision, Consequences y Alternatives Rejected. No hay hallazgos Critical ni
Major; los tres hallazgos Minor son precisiones de contrato/mapeo y un recordatorio
sobre el resto del redondeo (OQ1) que el humano puede sopesar en el gate. Veredicto
`READY`.
