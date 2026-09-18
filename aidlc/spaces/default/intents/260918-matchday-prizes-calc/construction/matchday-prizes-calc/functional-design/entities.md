# Functional Design — Entidades (matchday-prizes-calc)

Modelo de entidades del cálculo puro de premios. Tecnológicamente agnóstico; sin
código ni SQL. El cálculo puro (`PrizeCalculator`) opera sobre estas entidades
en memoria; la persistencia (`team_prizes`) es responsabilidad del orquestador.

```yaml
entities:
  - name: PrizeConfig
    description: Configuración de premios del campeonato para una ronda.
    attributes:
      - { name: money_per_ranking, type: integer, required: true, min: 0, description: "importe base del premio de ranking" }
      - { name: ranking_mode, type: enum, required: true, allowed_values: [flop, top], description: "modo de reparto por posición" }
      - { name: users_to_rank, type: integer, required: true, description: "nº de posiciones premiadas; -1 = todas" }
      - { name: money_per_point, type: integer, required: true, min: 0 }
      - { name: mvp_bonus, type: integer, required: true, min: 0 }
      - { name: dream_team_bonus, type: integer, required: true, min: 0 }

  - name: RoundTeamEntry
    description: Entrada de un equipo en el ranking de una ronda (entrada del cálculo).
    attributes:
      - { name: team_id, type: string, required: true, unique: true }
      - { name: round_points, type: integer, required: true, min: 0, description: "puntos de la jornada; criterio de empate (FR1.1)" }
      - { name: api_position, type: integer, required: false, description: "posición cruda que devuelve la API (orden de índice)" }
    constraints:
      - "team_id identifica unívocamente al equipo dentro de la ronda"

  - name: TeamRoundPrize
    description: Resultado del cálculo por equipo para una ronda (salida del cálculo puro).
    attributes:
      - { name: team_id, type: string, required: true }
      - { name: ranking_prize, type: integer, required: true, min: 0, description: "premio de posición tras aplicar la regla de empate (FR1)" }
      - { name: mvp_prize, type: integer, required: true, min: 0 }
      - { name: points_prize, type: integer, required: true, min: 0 }
      - { name: dream_team_prize, type: integer, required: true, min: 0 }
      - { name: display_position, type: integer, required: true, description: "posición asignada para mostrar/persistir" }
    relationships:
      - "cada TeamRoundPrize corresponde a un RoundTeamEntry (1:1 por team_id dentro de la ronda)"

  - name: TieGroup
    description: Grupo de equipos empatados a puntos que ocupan posiciones contiguas.
    attributes:
      - { name: round_points, type: integer, required: true, description: "puntos compartidos por el grupo" }
      - { name: positions, type: list, required: true, description: "posiciones contiguas p..p+N-1 que ocupa el grupo" }
      - { name: member_team_ids, type: list, required: true, description: "los N equipos empatados" }
    constraints:
      - "N = len(member_team_ids) = len(positions); las posiciones son contiguas"
    relationships:
      - "un TieGroup agrupa 1..N RoundTeamEntry con el mismo round_points"
```

## Resumen

El cálculo recibe `PrizeConfig` y una lista de `RoundTeamEntry`, agrupa los
premiables por `round_points` en `TieGroup` y produce un `TeamRoundPrize` por
equipo. `TieGroup` es la entidad que materializa la regla de empate (FR1): para
un grupo de N equipos, el premio de ranking de cada miembro es la suma de los
premios de las N posiciones del grupo dividida entre N.

## Assumptions & Open Questions

None.
