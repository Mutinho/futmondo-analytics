## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-20T19:04:39Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/traceability.json > elements / upstream_elements | Existen `stories.md` con US1–US7, pero la trazabilidad enumera sólo FR1–FR8, no las US. La cadena hasta las historias de usuario queda implícita (vía FR) y no verificable de forma directa en este artefacto. | Añadir la cobertura por `USx.y` (una entrada por historia US1–US7) mapeada a su componente/entidad, o documentar explícitamente por qué se traza por FR en lugar de por US. | New |
| R-02 | Major | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/components.md > (documento completo) | El catálogo se expresa sólo en prosa: faltan el bloque `yaml` de componentes con `depends_on`/`dependents`/`entities`/`external_dependencies`, el diagrama `mermaid`, y las tablas de Component Summary, Entity Ownership, External Dependencies y Rationale (con Alternatives Rejected). Sin la simetría explícita `depends_on`↔`dependents` y la propiedad de entidades tabulada, el grafo de dependencias y el "una entidad = un componente dueño" no son auditables mecánicamente, y Units Generation consume este catálogo como fuente de verdad. | Añadir el catálogo `yaml` como fuente de verdad (componentes, dependencias simétricas, entidades con dueño único, dependencias externas) y derivar de él el diagrama y las tablas de resumen/ownership/rationale. | New |
| R-03 | Minor | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/components.md > "C8 — `SofascoreDetail` + `SofascoreService`" | C8 agrupa bajo un único id un DTO (`SofascoreDetail`) y un actor de servicio (`SofascoreService`), mezclando dos building blocks con responsabilidades distintas (modelo vs. carga/aislamiento de fallo). El aislamiento FR8.2 está bien decidido (ADR-5), pero la propiedad de la entidad `SofascoreDetail` queda difuminada. | Separar el DTO (`SofascoreDetail`) y el servicio (`SofascoreService`) en entradas de componente distintas, dejando la entidad `SofascoreDetail` con un único componente dueño. | New |
| R-04 | Major | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/components.md > catálogo yaml, campos dependents de BidSheet, CancelBidConfirmation, SofascoreDetailSheet y MarketView | Estos componentes declaran a `MarketPlayerCard`/`MarketView` como `dependents`, pero el componente nombrado no lista el enlace recíproco en su `depends_on` (`MarketPlayerCard.depends_on` sólo tiene `MarketViewModel`; `MarketView.depends_on` sólo tiene `MarketViewModel` y `MarketUserInfo`). El catálogo se declara "fuente de verdad" pero la relación de apertura de sheets queda registrada en un solo lado. El diagrama `mermaid` sí dibuja esos enlaces (`MarketPlayerCard -.abre.-> BidSheet`, etc.), con lo que diagrama y bloque yaml discrepan. | Hacer simétricos los pares: o bien añadir el `depends_on` recíproco en `MarketPlayerCard` (hacia `BidSheet`, `CancelBidConfirmation`, `SofascoreDetailSheet`) y en `MarketView` (hacia `MarketPlayerCard`), o bien retirar esas entradas de `dependents` si la relación no es una dependencia de llamada, de modo que el bloque yaml y el diagrama coincidan. | New |
| R-05 | Minor | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/components.md > catálogo yaml, dependents de MarketPlayer | `MarketPlayer.dependents` incluye `MarketService` ("producido al decodificar /market/today"), pero `MarketService.depends_on` no lista `MarketPlayer` (decodifica vía `MarketTodayResponse`). Es otra asimetría del mismo tipo; la cadena real es `MarketService → MarketTodayResponse → MarketPlayer`. | Retirar `MarketService` de `MarketPlayer.dependents` (la producción llega transitivamente vía `MarketTodayResponse`), o justificarlo explícitamente como enlace deliberado. | New |
| R-06 | Minor | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/components.md > entity MarketUserInfo > identifier | La regla de la etapa pide que cada entidad tenga un `identifier`; `MarketUserInfo` lo deja como texto "(value object — sin identidad...)". La decisión de modelarlo como value object sin identidad es razonable y está explicada, pero deja el campo `identifier` sin un atributo concreto. | Mantener la decisión (aceptable para un value object) pero dejar constancia de que la ausencia de identificador es intencionada, p. ej. normalizándolo a un marcador explícito tipo `n/a (value object)` para que la regla de ownership quede inequívoca. | New |
| R-07 | Minor | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/components.md > external_dependencies de MarketService y SofascoreService | `NetworkClient (FutmondoKit, F1)` se lista como `external_dependency` con `kind: other`. No es infra ni un tercero, es un componente `FutmondoKit` reutilizado de F1; la nota lo aclara ("no es un componente nuevo de F3"), pero clasificarlo junto a las APIs de terceros puede inducir a verlo como dependencia externa de red. | Es aceptable como está dado que queda fuera del alcance de F3; opcionalmente, distinguir en la nota que es una dependencia a un componente interno existente (reutilización) frente a las dependencias de terceros reales (`Futmondo API`, `Sofascore`). | New |
| R-08 | Minor | aidlc/spaces/default/intents/261020-mercado-pujas/inception/domain-design/decisions.md > Consolidated Summary, línea "C5 `MarketService` (actor: loadToday/placeBid/cancelBid + detalle Sofascore)" | El resumen consolidado todavía atribuye la carga del detalle Sofascore a `MarketService`, lo que contradice la propia decisión ADR-5/ADR-6 y el catálogo `yaml`, donde el detalle lo cargan `SofascoreService` + `SofascoreDetail` como componentes separados y aislados del Mercado. Es texto residual de una versión anterior, no afecta a la fuente de verdad (`components.md`). | Corregir la frase del resumen para que describa `MarketService` sólo como loadToday/placeBid/cancelBid y mencione la carga del detalle bajo `SofascoreService`/`SofascoreDetail`, alineándola con ADR-5/ADR-6. | New |

> R-01 Not re-checked this round

> R-02 Not re-checked this round

> R-03 Not re-checked this round

> R-04 Not re-checked this round

> R-05 Not re-checked this round

> R-06 Not re-checked this round

> R-07 Not re-checked this round

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| Revisión manual de simetría depends_on/dependents | PASS | Cada arista `depends_on A→B` tiene su recíproca en `B.dependents`, y cada entrada de `dependents` tiene su `depends_on` correspondiente. R-04 verificado: `MarketPlayerCard` depende de `BidSheet`/`CancelBidConfirmation`/`SofascoreDetailSheet` y `MarketView` de `MarketPlayerCard`, con recíprocos presentes; el mermaid incluye `MarketView --> MarketPlayerCard`. R-05 verificado: `MarketService` ya no figura en `MarketPlayer.dependents` (la relación es transitiva vía `MarketTodayResponse`) y `MarketService` no declara `depends_on MarketPlayer`. |
| Comprobación de aciclicidad del grafo | PASS | El grafo es un DAG. El triángulo `MarketView → MarketPlayerCard → MarketViewModel` no cierra ciclo: `MarketViewModel` sólo depende de `MarketService`/`MarketSorter`/`MarketWriteOutcome` (nodos terminales) y no de `MarketView` ni de `MarketPlayerCard`. Las nuevas aristas hacia los sheets terminan en hojas (`BidAmountValidator`, `SofascoreService → SofascoreDetail`). No se introdujo ningún ciclo. |
| Comprobación de propiedad de entidades | PASS | Tres entidades (`MarketPlayer`, `MarketUserInfo`, `SofascoreDetail`), cada una con exactamente un componente dueño del mismo nombre e identificador. R-06 verificado: `MarketUserInfo` normaliza su identificador a `n/a (value object)` tanto en el `yaml` como en la tabla Entity Ownership, coherente con su naturaleza de value object. |
| Comprobación de clasificación de dependencias externas | PASS | R-07 verificado: `NetworkClient` figura como `kind: internal-component-reuse` en `MarketService` y `SofascoreService` (bloque `yaml`) y en la tabla External Dependencies, con nota aclaratoria que lo distingue de los terceros reales (`Futmondo API`, `Sofascore`, `third-party-api`). Coherente con el patrón de reutilización F1. |
| Cobertura de historias en traceability.json | PASS | US1–US7 presentes, todas `status: OK`, y cada `target` referencia componentes declarados en `components.md`. |

### Summary

La revisión del catálogo revisado confirma que R-04 a R-07 quedaron consistentes: simetría `depends_on`/`dependents` completa, grafo acíclico (incluidas las nuevas aristas `MarketView→MarketPlayerCard` y `MarketPlayerCard→sheets`), propiedad de entidades inequívoca con marcador `n/a` aceptable para el value object, y `NetworkClient` reclasificado como reutilización interna. El único punto para que el humano pondere es una frase residual en el resumen consolidado de `decisions.md` que aún atribuye el detalle Sofascore a `MarketService`; es cosmético y no contamina la fuente de verdad, por lo que el diseño es implementable tal cual (READY).
