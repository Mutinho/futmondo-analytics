# Sync de jugadores — qué se persiste y qué falta (261023-sync-jugador-completo)

Ingeniería inversa enfocada del flujo de datos de `sync_players_full`, base del
intent de enriquecimiento. Verificado en código y en producción (token fresco).

## Flujo actual (verificado)

`DataSyncService.sync_players_full` → `PlayersFullSyncOrchestrator.sync()`
(`backend/app/services/sync/players_full/orchestrator.py`) lee el objeto vivo de
Futmondo de `client.get_championship_players(championship_id)` (endpoint
`/5/league/championshipplayers`, devuelve `{players: [...]}`) y persiste:

- En **`players`** (vía `save_players_batch`): `name, role, role2, teamId, team,
  slug, photo, value`. (El INSERT batch incluye `value`; el single-insert NO.)
- En **`player_championship_stats`** (vía `save_player_championship_stats`):
  `owner_team_id, owner_team_name, owner_user_id, clause_price, suggested_clause,
  clause_date, average_last_five, average_overall`.

**NO extrae ni persiste del objeto vivo:** `points` (puntos totales), `change`
(tendencia de valor), `home_average`/`away_average`/`matches` (medias
detalladas), ni el logo del equipo (`team_logo`).

## Dónde viven hoy esos campos que faltan

- `points`: solo en `player_performance` (por jornada×equipo), que **no tiene
  filas para agentes libres** → SUM=0 para favoritos libres.
- `change`, `home_average`, `away_average`, `matches`, `team_logo`: solo en
  `market_today` (mercado del día, ~25-30 jugadores) → ausentes para la mayoría
  de agentes libres.

## Evidencia de producción (token fresco, 2026-10-23)

- `GET /market/today` (jugador del mercado) SÍ trae todos los campos por jugador:
  `change, points, home_average, away_average, matches, team_logo, team`, etc.
- `GET /favorites/my` (champ 592416…): de 33 favoritos, **32 sin
  points/team/team_logo/change**; `value` y `average` sí (desde `players` /
  `player_championship_stats`).

## Incógnita CERRADA en diseño (verificada con respuesta cruda, 2026-10-24)

`/5/league/championshipplayers` **SÍ devuelve todos los campos por jugador, para
TODOS los jugadores del catálogo** (no solo los del mercado). Forma real de cada
jugador (ejemplo Carvajal, agente libre que salía vacío en favoritos):

```json
{ "id", "name", "slug", "role", "role2", "photo", "points": 5, "value": 3465740,
  "status": "", "rating": 2, "change": 139994, "teamId": "504e581e...",
  "average": { "average": 5, "homeAverage": "5.00", "awayAverage": "NaN",
               "averageLastFive": "5.00", "matches": 1, "fitness": [...], "total": "5.0" },
  "userteamId"?, "userteam"? }
```

**Conclusión:** la fuente es suficiente y es la llamada que el sync YA hace. El
problema es SOLO un mapeo incompleto en `sync_players_full`: lee
`name/role/role2/teamId/team/slug/photo/value` y, de `average`, sólo
`averageLastFive`/`average`. **Descarta `points`, `change`, `homeAverage`,
`awayAverage`, `matches`, `status`, `rating`.** El diseño del enriquecimiento NO
necesita otra fuente ni otra llamada:
1. Ampliar el esquema sincronizado (columnas nuevas en `players` o en
   `player_championship_stats`: `change`, `points`, `home_average`,
   `away_average`, `matches`, `status`; `teamId`→logo se deriva con `LALIGA_TEAMS`).
2. Extraer esos campos en `PlayersFullSyncOrchestrator` (characterization-first
   sobre su comportamiento actual antes de ampliarlo).
3. `favorites_read` (y market) leen esos campos del sync → favoritos completos
   sin llamadas vivas ni dependencia de `market_today`.

Notas de datos reales a tener en cuenta en el mapeo:
- `homeAverage`/`awayAverage` vienen como STRING y pueden ser `"NaN"` → limpiar a
  `None` (ya existe `clean_float`).
- `average.matches` es el nº de partidos; `average.average` es la media overall.
- `teamId` siempre presente; `team` (nombre) NO siempre viene en el objeto del
  catálogo → el logo/nombre se resuelve por `teamId` con `LALIGA_TEAMS`.
- `status` puede ser `""`, `"injured"`, `"injured2"`, `"doubt"`, `"redcard"`, `"ok"`.

## Restricciones heredadas (afirmadas)

- Coste 0; characterization-first sobre `sync_players_full` antes de cambiarlo.
- No ampliar a mano los god-files salvo lo imprescindible del propio sync; capa
  estrecha testeable; contrato de respuesta de los endpoints intacto.
- Cambio de esquema (nuevas columnas en `players`/stats o tabla de stats más
  rica) + re-sincronización para poblarlas.
