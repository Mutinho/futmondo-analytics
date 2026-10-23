# Mob Composition — F3 Mercado (app nativa iOS)

> Cómo colabora el flujo AI-DLC en las etapas que lo requieren. Dado el tamaño de
> la feature y el patrón ya probado en F1/F2, la entrega es **conductor + sub-agente
> por etapa**, no un mob multi-persona simultáneo.

## Sources

- `.../ideation/team-formation/team-assessment.md` y `skill-matrix.md`.

## Modelo de colaboración

- **Inline (mayoría de etapas)**: el conductor adopta la persona de dominio y
  produce los artefactos; el propietario decide en el gate.
- **Delegación puntual**:
  - **Code Generation**: sub-agente **developer** por unidad.
  - **Reviews**: sub-agente **product-lead** (artefactos de producto) y
    **architecture-reviewer** (diseño), según cada etapa.
- **Construcción prevista en 2 unidades** (igual patrón que F2):
  - **U1 — datos de Mercado en `FutmondoKit`**: modelo `MarketPlayer`/`user_info`,
    servicio de lectura y escritura (pujar/cancelar), formato/validación; con
    XCTest.
  - **U2 — UI de Mercado en `FutmondoApp`**: banner, cards, orden, diálogos de
    puja/cancelación, sheet Sofascore, y la 2ª pestaña del `TabView`.
  (La partición definitiva la fija Units Generation en Inception.)

## Cadencia / checkpoints

- "Autónomo hasta checkpoint" por unidad; un "ok" por summary. Validación en
  dispositivo por el propietario al cierre de la UI.

## Assumptions & Open Questions

None.
