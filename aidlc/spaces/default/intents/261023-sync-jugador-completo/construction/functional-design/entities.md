# Entities — Enriquecimiento del sync de jugadores

Modelo del jugador sincronizado tras el enriquecimiento. Fuente de verdad: el
bloque `yaml`. No se crean tablas nuevas; se amplía `players`.

```yaml
entities:
  - name: SyncedPlayer
    description: >
      Fila de jugador en la tabla `players`, poblada por PlayersFullSyncOrchestrator
      desde /5/league/championshipplayers. Se AMPLÍA con los campos que hoy se
      descartan, para que favorites_read los sirva sin llamadas vivas.
    table: players
    existing_columns:
      - { name: player_id, source: player.id }
      - { name: name, source: player.name }
      - { name: role, source: player.role, maps_to: position }
      - { name: role2, source: player.role2, maps_to: position2 }
      - { name: real_team_id, source: player.teamId, notes: "clave para resolver equipo/logo (FR3)" }
      - { name: real_team_name, source: player.team, notes: "puede faltar en el catálogo" }
      - { name: slug, source: player.slug }
      - { name: photo_url, source: player.photo }
      - { name: value, source: player.value }
      - { name: last_updated }
    new_columns:
      - { name: points, source: player.points, type: INTEGER, default: 0, notes: "total acumulado que da Futmondo (FR1.2)" }
      - { name: change, source: player.change, type: INTEGER, default: 0 }
      - { name: home_average, source: player.average.homeAverage, type: REAL, nullable: true, notes: "string → float; 'NaN'/vacío/no-parseable → NULL (FR1.3)" }
      - { name: away_average, source: player.average.awayAverage, type: REAL, nullable: true, notes: "idem" }
      - { name: matches, source: player.average.matches, type: INTEGER, default: 0 }
      - { name: status, source: player.status, type: TEXT, default: "''", notes: "'', injured, injured2, doubt, redcard, ok" }

  - name: FavoriteRow
    description: >
      Read-model de un favorito servido por favorites/my, ahora completo desde
      el sync. Mismas claves/tipos/orden que el contrato actual (NFR1).
    source: players (JOIN player_championship_stats para free-agent) + sofascore_cache
    fields_now_from_sync: [value, change, points, average, home_average, away_average, matches, team, team_logo, status]
    unchanged: "claves, tipos y orden (position_order asc, value desc)"

  - name: TeamResolution
    description: Resolución de equipo/escudo en lectura (no es tabla).
    logic: >
      team = LALIGA_TEAMS[real_team_id].name si existe; si no, real_team_name; si
      no, ''. team_logo = LALIGA_TEAMS[real_team_id].logo si existe; si no, ''.
      (FR3; cubre el peor caso del finding advisory M-FR3.1.)
```

## Resumen

- Se **amplía `players`** con 6 columnas (`points`, `change`, `home_average`,
  `away_average`, `matches`, `status`); `real_team_id` ya existe y se usa para el
  equipo/escudo.
- `average` del objeto vivo es un dict: `average.average` → ya mapeado a
  `average_overall` (stats); `homeAverage`/`awayAverage` (string, puede `"NaN"`)
  y `matches` se añaden a `players`.
- `FavoriteRow` no cambia de forma: solo cambia el ORIGEN (ahora completo).
