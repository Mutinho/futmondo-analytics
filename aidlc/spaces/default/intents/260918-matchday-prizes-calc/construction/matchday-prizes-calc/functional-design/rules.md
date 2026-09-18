# Functional Design — Reglas de negocio (matchday-prizes-calc)

```yaml
rules:
  - id: BR1.1
    statement: "El premio por puntos se paga siempre para los puntos de la jornada."
    category: calculation
    applies_to: TeamRoundPrize.points_prize
    trigger: "Cálculo del premio de una ronda (cualquier estado de ronda)."
    logic: "points_prize = round(round_points * money_per_point) si money_per_point > 0, si no 0."
    violation_behaviour: "N/A (cálculo determinista)."
    source: FR3.1

  - id: BR1.2
    statement: "El premio de ranking, MVP y dream-team solo se otorgan cuando la ronda está completa y cerrada."
    category: constraint
    applies_to: [TeamRoundPrize.ranking_prize, TeamRoundPrize.mvp_prize, TeamRoundPrize.dream_team_prize]
    trigger: "Cálculo del premio de una ronda."
    logic: "IF NOT (is_closed AND round_fully_played AND NOT is_advanced_pseudo_round) THEN ranking_prize = mvp_prize = dream_team_prize = 0."
    violation_behaviour: "Se pagan 0 en esos términos; points_prize sigue su regla BR1.1."
    source: FR3.1

  - id: BR2.1
    statement: "Solo entran al reparto de ranking los equipos activos (puntos de jornada > 0), limitados por users_to_rank cuando aplica."
    category: constraint
    applies_to: ranking eligibility
    trigger: "Antes de calcular el premio de ranking."
    logic: "active = [equipos con round_points > 0]; premiables = primeros min(len(active), users_to_rank>0 ? users_to_rank : len(active)) por orden de puntos."
    violation_behaviour: "Equipos no premiables reciben ranking_prize = 0."
    source: FR2.1

  - id: BR2.2
    statement: "El premio de una posición sigue la fórmula proporcional por modo (flop/top)."
    category: calculation
    applies_to: prize-per-position
    trigger: "Cálculo del ranking_prize base por posición."
    logic: >
      total_pct = active_members*(active_members+1)/2;
      IF ranking_mode == 'flop' THEN ratio(pos) = pos / total_pct
      ELSE ratio(pos) = (active_members - pos + 1) / total_pct;
      prize(pos) = round(money_per_ranking * ratio(pos)).
    violation_behaviour: "N/A (cálculo determinista)."
    source: FR2.1

  - id: BR3.1
    statement: "Reparto equitativo del premio de ranking entre equipos empatados a puntos."
    category: calculation
    applies_to: TeamRoundPrize.ranking_prize
    trigger: "Tras ordenar los equipos premiables por puntos de jornada."
    logic: >
      Agrupar los equipos premiables por round_points. Para cada grupo de N
      equipos que ocupa las posiciones contiguas p..p+N-1:
      sum_positions = suma de prize(pos) (BR2.2) para pos en p..p+N-1;
      ranking_prize de cada miembro = round(sum_positions / N).
      Un grupo de N=1 recibe exactamente prize(p) (sin regresión, FR1.3).
    violation_behaviour: "N/A (cálculo determinista). El reparto no depende del orden arbitrario de la API entre empatados."
    source: FR1.1, FR1.2, FR1.3

  - id: BR3.2
    statement: "Redondeo de cada parte del reparto de empate."
    category: calculation
    applies_to: TeamRoundPrize.ranking_prize
    trigger: "Al repartir sum_positions entre N empatados."
    logic: "cada parte = round(sum_positions / N). No se cuadra el resto (decisión: OQ1)."
    violation_behaviour: "Posible descuadre de ±1 por redondeo cuando la división no es entera; aceptado como comportamiento (OQ1)."
    source: FR1.4
```

## Resumen de reglas

| ID | Categoría | Resumen | Fuente |
|---|---|---|---|
| BR1.1 | calculation | points_prize siempre | FR3.1 |
| BR1.2 | constraint | ranking/MVP/dream-team solo con ronda completa | FR3.1 |
| BR2.1 | constraint | elegibilidad de ranking (activos, users_to_rank) | FR2.1 |
| BR2.2 | calculation | premio por posición (flop/top) | FR2.1 |
| BR3.1 | calculation | reparto equitativo ante empates | FR1.1–FR1.3 |
| BR3.2 | calculation | redondeo por parte (±1 aceptado) | FR1.4 |

## Assumptions & Open Questions

OQ1 (de requisitos): el reparto exacto del resto cuando `sum_positions / N` no
es entero queda sin cuadrar (round() por parte, BR3.2); se revisará si el caso
se materializa.
