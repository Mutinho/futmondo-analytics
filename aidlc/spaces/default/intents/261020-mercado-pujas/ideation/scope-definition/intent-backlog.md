# Intent Backlog — F3 Mercado (app nativa iOS)

> Priorización MoSCoW del alcance confirmado. Fuente de verdad del
> comportamiento: la vista Angular de Mercado.

## Sources

- `.../ideation/scope-definition/scope-document.md` — alcance dentro/fuera.
- `.../ideation/intent-capture/intent-statement.md` — decisiones Q1–Q4 = A.
- `.../ideation/feasibility/constraint-register.md` — restricciones.

## Must have (M)

- **M1** — Segunda pestaña "Mercado" en el `RootTabView` (junto a Presupuesto).
- **M2** — Carga de Mercado del campeonato activo (`GET /market/today`) con
  estados carga/error/vacío.
- **M3** — Banner de usuario (Presupuesto, En pujas, Balance, Puja máxima,
  Disponible).
- **M4** — Lista de **cards** de jugador con los campos 1:1 de la card Angular.
- **M5** — Selector de **orden descendente** por campo (mismos campos que F2).
- **M6** — **Pujar** por un jugador: diálogo con importe validado (mín precio de
  mercado, máx disponible, default puja sugerida), `POST /market/bid`, señal de
  resultado y refresco.
- **M7** — **Cancelar** puja activa: confirmación, `POST /market/cancelbid`,
  señal de resultado y refresco.

## Should have (S)

- **S1** — **Detalle Sofascore** como sheet nativa con carga asíncrona (rating +
  stats, loading/error). (Confirmado en alcance Q3=A; S por ser el elemento de
  menor acoplamiento que podría diferirse sin romper el núcleo del Mercado.)
- **S2** — Marca visual de **favorito** en la card (`is_favorite`).

## Could have (C)

- **C1** — Afinados de microinteracción (hápticos, animaciones) coherentes con
  F2, si el tiempo lo permite.

## Won't have (this intent) (W)

- **W1** — Vista de **tabla** (sólo cards).
- **W2** — **Calculadora / Finanzas** (= F4).
- **W3** — Pestañas/secciones adicionales más allá de Presupuesto + Mercado.
- **W4** — Cambios de backend / contrato de API.
- **W5** — Distribución (Apple Developer Program) y migración a asset catalog.

## Assumptions & Open Questions

None.
