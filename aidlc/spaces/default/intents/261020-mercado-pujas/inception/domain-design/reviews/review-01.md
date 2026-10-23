## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Verdict:** READY
**Date:** 2026-10-20T18:23:56Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/traceability.json > elements / upstream_elements | Existen `stories.md` con US1–US7, pero la trazabilidad enumera sólo FR1–FR8, no las US. La cadena hasta las historias de usuario queda implícita (vía FR) y no verificable de forma directa en este artefacto. | Añadir la cobertura por `USx.y` (una entrada por historia US1–US7) mapeada a su componente/entidad, o documentar explícitamente por qué se traza por FR en lugar de por US. | New |
| R-02 | Major | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/components.md > (documento completo) | El catálogo se expresa sólo en prosa: faltan el bloque `yaml` de componentes con `depends_on`/`dependents`/`entities`/`external_dependencies`, el diagrama `mermaid`, y las tablas de Component Summary, Entity Ownership, External Dependencies y Rationale (con Alternatives Rejected). Sin la simetría explícita `depends_on`↔`dependents` y la propiedad de entidades tabulada, el grafo de dependencias y el "una entidad = un componente dueño" no son auditables mecánicamente, y Units Generation consume este catálogo como fuente de verdad. | Añadir el catálogo `yaml` como fuente de verdad (componentes, dependencias simétricas, entidades con dueño único, dependencias externas) y derivar de él el diagrama y las tablas de resumen/ownership/rationale. | New |
| R-03 | Minor | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/components.md > "C8 — `SofascoreDetail` + `SofascoreService`" | C8 agrupa bajo un único id un DTO (`SofascoreDetail`) y un actor de servicio (`SofascoreService`), mezclando dos building blocks con responsabilidades distintas (modelo vs. carga/aislamiento de fallo). El aislamiento FR8.2 está bien decidido (ADR-5), pero la propiedad de la entidad `SofascoreDetail` queda difuminada. | Separar el DTO (`SofascoreDetail`) y el servicio (`SofascoreService`) en entradas de componente distintas, dejando la entidad `SofascoreDetail` con un único componente dueño. | New |

### Summary

El diseño es implementable y coherente con los contratos aguas arriba: la partición `FutmondoKit` (lógica testeable) vs `FutmondoApp` (SwiftUI, `#if canImport(SwiftUI)`), el resultado tipado `MarketWriteOutcome` (ADR-2), el tope de puja = `available_for_bids` (Q1=A, ADR-3), el `SofascoreService` dedicado para el aislamiento de fallo (FR8.2, ADR-5) y el mandato coste 0 € (ADR-4) están todos respetados, sin ampliar god-files. Las dos observaciones Major son de completitud y auditabilidad del artefacto (trazabilidad por US y catálogo `yaml` + tablas derivadas), no fallos arquitectónicos; conviene que el humano las sopese antes de aprobar, ya que Units Generation consume este catálogo.
