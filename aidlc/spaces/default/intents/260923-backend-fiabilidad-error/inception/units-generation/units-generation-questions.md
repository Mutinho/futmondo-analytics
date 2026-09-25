# Units Generation — Preguntas de decomposición

Intent: **Fiabilidad backend — manejo de errores (FR3.2) + contratos de integración (FR4)**

## Sources

- [desc] Initial description: "Intent 1 del plan de mejoras: FR3.2 (manejo de errores, recuperable/fatal) + FR4 (contratos e integraciones Sofascore/Futmondo, deteccion reflejada en estado sin corromper datos). Scope feature, brownfield. Secuenciacion dependencia-primero: capa de errores -> clientes -> estado. NO ampliar god-files; codigo nuevo tras capa/funcion estrecha testeable. Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/team.md#Way of Working`: "Sigue la secuenciación de dependencia del scope-document: capa de errores (FR3.2) → clientes (FR4) → estado degradado."

---

## Q1. Estrategia de límite de unidad

Los 6 componentes (IntegrationErrors nuevo + clientes/sync/db/status modificados) son todos backend Python cohesivo, en un único despliegue (`futmondo-api` en Fly.io). ¿Cómo agrupamos en unidades de trabajo?

- A. **Por eje de dependencia (2 unidades)**: U1 = capa de errores (IntegrationErrors + endurecimiento de capturas de arranque/migraciones/`db_connection.py`, FR3.2); U2 = integraciones (clientes tipados + detección/estado + inventario de llamadores + no-corrupción, FR4), que depende de U1. Refleja el orden dependencia-primero afirmado [memory:M1].
- B. **Una sola unidad**: todo el intent es una intervención acotada y cohesiva; una unidad con orden interno de historias.
- C. **Fino (por componente)**: una unidad por componente tocado.
- X. Other (please specify)

[Answer]: A. Por eje de dependencia (2 unidades): U1 = capa de errores (IntegrationErrors + endurecimiento de capturas de arranque/migraciones/db_connection.py, FR3.2); U2 = integraciones (clientes tipados + detección/estado + inventario de llamadores + no-corrupción, FR4), depende de U1.

## Q2. Granularidad

- A. **Gruesa**: pocas unidades grandes (coherente con A o B de Q1); menos overhead de coordinación para un mantenedor único.
- B. **Fina**: más unidades pequeñas.
- X. Other (please specify)

[Answer]: A. Gruesa: pocas unidades grandes (2 unidades); menos overhead de coordinación para un mantenedor único.

## Q3. Modelo de despliegue

- A. **Monolítico (sin cambios)**: todo despliega como parte de `futmondo-api` en Fly.io; este intent no cambia la topología de despliegue. Las unidades son de organización del trabajo, no de despliegue independiente.
- B. Otra cosa (indícalo en Other).
- X. Other (please specify)

[Answer]: A. Monolítico (sin cambios): todo despliega como parte de futmondo-api en Fly.io; las unidades son de organización del trabajo, no de despliegue independiente.

## Consolidated Summary Confirmation

Resumen de la decomposición (antes de fijar los artefactos):

- **Estrategia (Q1=A)**: 2 unidades por eje de dependencia. **Granularidad (Q2=A)**: gruesa. **Despliegue (Q3=A)**: monolítico, sin cambios de topología.
- **U1 `u1-error-layer`** (`kind: library`, M, `depends_on: []`): capa de errores — `IntegrationErrors` + endurecimiento de capturas de arranque/migraciones/`db_connection.py` (FR3.2, FR4.1).
- **U2 `u2-integrations`** (`kind: service`, M/L, `depends_on: [u1-error-layer]`): clientes tipados (Futmondo/Sofascore), detección en estado, inventario de llamadores, no-corrupción `team_prizes` (FR4.2-4.5, FR4.4, NFR1/NFR2/NFR3).
- **DAG**: `u1-error-layer` → `u2-integrations` (acíclico).
- **Artefactos**: unit-of-work.md, unit-of-work-dependency.md (con bloque YAML de aristas), unit-of-work-story-map.md, traceability.json.

[Answer]: Looks correct
