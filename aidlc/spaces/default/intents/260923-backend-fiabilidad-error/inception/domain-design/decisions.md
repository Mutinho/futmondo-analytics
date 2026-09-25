# Architecture Decision Records — Domain Design (Fiabilidad backend)

## ADR-001: Módulo dedicado `IntegrationErrors` como bloque de definiciones puro

- **Context**: FR4.1 exige que las excepciones de integración vivan en un módulo
  estrecho con raíz común `IntegrationError`. Hoy `SofascoreIPBanError` vive
  dentro del cliente Sofascore; extenderla a Futmondo acoplaría dos clientes con
  runtimes distintos (`curl_cffi` vs `requests`). [memory:M1]
- **Decision**: crear un componente `IntegrationErrors` que contiene SOLO la
  jerarquía (raíz `IntegrationError` + subtipos por modo de fallo: baneo,
  timeout, respuesta no parseable), sin lógica de decisión ni dependencias. (Q1=A)
- **Consequences**: (+) alta cohesión, sin dependencias (módulo hoja),
  trivially testeable, reusable por ambos clientes y por la ruta de sync;
  el tipo codifica recuperable/fatal. (−) requiere migrar `SofascoreIPBanError`
  a heredar de la nueva raíz (cambio pequeño, caracterizado primero).
- **Alternatives Rejected**: (B) módulo con jerarquía + helper de clasificación —
  rechazado por mezclar "qué fallos existen" con "qué hacer ante cada uno", dos
  concerns con ritmos de cambio distintos y acoplaría el módulo de tipos a la
  ruta de sync.

## ADR-002: La clasificación recuperable→acción vive en el punto de captura de la ruta de sync

- **Context**: la taxonomía recuperable/fatal (FR3.2.1) debe traducirse en acción
  (degradar vs abortar). Existe `sync_step_status.record_degraded_step` (FR3.1)
  y la regla de no ampliar los god-files. [memory:M2]
- **Decision**: la traducción fallo→acción vive en el punto de captura de la ruta
  de sync (componente `SyncService` existente): recuperable → `record_degraded_step`
  + continuar; fatal → dejar propagar sin escribir datos a medias. Sin componente
  nuevo para esto; solo se endurecen capturas existentes. (Q2=A)
- **Consequences**: (+) la decisión vive donde está el contexto (paso, `task_id`,
  `ProgressSink`); reusa infraestructura existente; no amplía estructuralmente el
  god-file. (−) la lógica queda distribuida en los puntos de captura (mitigado
  porque el tipo de excepción ya lleva la clasificación, así que el punto de
  captura solo enruta).
- **Alternatives Rejected**: (B) helper de decisión nuevo — innecesario porque el
  tipo de excepción ya codifica recuperable/fatal; añadiría indirección sin ganancia.

## ADR-003: El inventario de llamadores de `_make_request` es un artefacto de diseño, no un componente

- **Context**: FR4.3 exige un inventario verificable de llamadores antes del
  cambio de contrato de `futmondo_client`.
- **Decision**: el inventario es un artefacto de análisis/documento (tabla que
  mapea llamadores y marca los que corrompen datos), no un bloque de código. (Q3=A)
- **Consequences**: (+) guía la migración sin inflar el catálogo de componentes.
  (−) debe mantenerse actualizado si el god-file cambia (se produce en construcción).
- **Alternatives Rejected**: modelarlo como componente — no tiene lógica ni
  lifecycle propios; sería un abuso del catálogo.

## Assumptions & Open Questions

None.
