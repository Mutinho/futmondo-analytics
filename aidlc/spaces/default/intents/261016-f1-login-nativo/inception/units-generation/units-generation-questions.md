# Units Generation — Preguntas (F1: Login nativo end-to-end)

> Idioma: castellano; tokens técnicos verbatim en inglés.

## Q1 — ¿Las unidades de trabajo y su DAG son correctos?

- A. **Correctos** — proceder a contract design (recomendado).
- B. Correctos con un ajuste (especifícalo).
- C. Replantear (especifícalo).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar units-generation, confirma:

- **3 unidades (camino lineal)**: `backend-refresh-transport` (`service`, sin dependencias) →
  `ios-network-client` (`library`, depende de backend) → `ios-native-auth` (`ui`, depende del
  cliente de red).
- **Mapa**: backend → US-7 (FR-4, FR-9); cliente de red → US-8 (FR-7); auth nativa → US-1…US-6
  (FR-1,2,3,5,6,8).
- **Trazabilidad**: FR/NFR/US → unidades sin orphans (`traceability.json`).

¿Está todo correcto?

[Answer]: Looks correct
