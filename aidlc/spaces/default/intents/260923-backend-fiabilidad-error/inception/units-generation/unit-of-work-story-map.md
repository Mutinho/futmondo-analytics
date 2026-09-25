# Unit-of-Work Story Map — Fiabilidad backend (FR3.2 + FR4)

No se produjeron historias de usuario (user-stories omitida: intent de fiabilidad
interna). Se mapea cada requisito funcional/no-funcional a su unidad
implementadora.

## Mapa FR/NFR → Unidad

| Requisito | Unidad | Directory | Nota |
|---|---|---|---|
| FR3.2.1 (taxonomía recuperable/fatal) | U1 | u1-error-layer | base de la clasificación |
| FR3.2.2 (primera oleada arranque/migraciones/db_connection) | U1 | u1-error-layer | |
| FR3.2.3 (E722 advisory) | U1 | u1-error-layer | commit de config aislado |
| FR4.1 (módulo IntegrationErrors) | U1 | u1-error-layer | jerarquía de excepciones |
| FR4.2 (FutmondoClient tipado) | U2 | u2-integrations | depende de U1 |
| FR4.3 (inventario de llamadores) | U2 | u2-integrations | entregable previo a migración |
| FR4.4 (detección de baneo en estado) | U2 | u2-integrations | reuso sync_step_status |
| FR4.5 (doc de contratos) | U2 | u2-integrations | documentación |
| NFR1 (logging estructurado) | U2 | u2-integrations | |
| NFR2 (no-corrupción team_prizes) | U2 | u2-integrations | reemplazo transaccional atómico |
| NFR3 (sin secretos en excepciones) | U1 | u1-error-layer | en las definiciones de IntegrationErrors |

## Orden dentro de cada unidad

- **U1**: (1) `IntegrationErrors` (definiciones) → (2) characterization de capturas → (3) endurecimiento recuperable/fatal → (4) specs de efecto → (5) `E722` advisory.
- **U2**: (1) inventario + characterization de `_make_request` → (2) `FutmondoClient`/`SofascoreClient` tipados → (3) detección+estado en la ruta de sync → (4) no-corrupción `team_prizes` → (5) doc de contratos → (6) specs de efecto.

## Cobertura

Todos los FR/NFR asignados a una unidad; ambas unidades tienen requisitos.

## Assumptions & Open Questions

None.
