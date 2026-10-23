## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Verdict:** READY
**Date:** 2026-10-20T18:59:56Z
**Iteration:** 1

### Resumen de la revisión

Pase ADVISORY único sobre `components.md` revisado tras el rechazo previo. Las
tres acciones requeridas se abordaron: (R-02) el catálogo `yaml` existe como
fuente de verdad con diagrama `mermaid` y tablas Component Summary / Entity
Ownership / External Dependencies / Rationale derivadas; (R-01)
`traceability.json` enumera US1–US7, todas `OK` con target de componente, y
`stories.md` existe; (R-03) el antiguo C8 está partido en `SofascoreDetail` (DTO,
dueño único de la entidad por `player_name`) y `SofascoreService` (actor), con su
ADR-6. El grafo de dependencias es acíclico, cada entidad tiene exactamente un
componente dueño, los nombres de componente son únicos, no hay autodependencias,
y la infra/terceros van en `external_dependencies`. La cobertura US1–US7 y el
mapeo FR1–FR8 en `elements[]` son correctos.

El único punto de peso para el humano antes de aprobar es una **asimetría
`depends_on`/`dependents`** en el bloque que se declara fuente de verdad: las
relaciones de presentación "X abre Y" se registran sólo en el lado hijo
(`Y.dependents = [X]`) sin el `X.depends_on = [Y]` correspondiente. La dirección
forward (todo `depends_on` tiene su `dependents` recíproco) sí es consistente, y
el diseño es implementable sin ambigüedad, por eso el veredicto es READY; pero es
exactamente la propiedad de simetría que R-02 pedía cerrar, así que se reporta
para que se decida en el gate.

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

> R-01 Not re-checked this round

> R-02 Not re-checked this round

> R-03 Not re-checked this round

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| (sin herramientas de validación listadas en la definición de etapa) | — | Verificación manual del bloque yaml: nombres únicos OK; todo `component:`/`owned_by` declarado OK; sin autodependencia OK; grafo acíclico OK; entidades con dueño único OK; forward `depends_on`→`dependents` simétrico OK; reverse `dependents`→`depends_on` con las asimetrías reportadas arriba. |
