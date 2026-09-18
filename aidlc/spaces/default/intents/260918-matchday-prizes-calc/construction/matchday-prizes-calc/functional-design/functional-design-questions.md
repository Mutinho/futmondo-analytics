# Functional Design — Preguntas y confirmación (matchday-prizes-calc)

No hubo preguntas abiertas: el algoritmo y las reglas están fijados por los
requisitos (FR1–FR3) y el diseño de dominio.

## Consolidated Summary Confirmation

Resumen del diseño funcional de la unidad:

- **Entidades**: `PrizeConfig`, `RoundTeamEntry`, `TeamRoundPrize`, `TieGroup` (grupo de empatados a puntos que ocupa posiciones contiguas).
- **Reglas de negocio**: BR1.1 (points_prize siempre), BR1.2 (gating ronda completa), BR2.1 (elegibilidad), BR2.2 (premio por posición flop/top), **BR3.1 (reparto equitativo ante empates: suma de las N posiciones contiguas del grupo / N)**, BR3.2 (redondeo round() por parte, ±1 aceptado — OQ1).
- **Workflow**: points_prize → gating → conjunto premiable → premio por posición → agrupar por empate → repartir equitativamente → MVP/dream-team. Ejemplo jornada 5 = 1.500.000/1.500.000.
- **Sin máquina de estados** (cálculo puro sin estado persistente).
- Trazabilidad FR1→BR3.1/BR3.2, FR2→BR2.1/BR2.2, FR3→BR1.1/BR1.2.

Does this all look correct before I finalize the functional design?

- Looks correct
- Request changes

[Answer]: Looks correct
