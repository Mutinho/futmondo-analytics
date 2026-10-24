# Business Rules — Enriquecimiento del sync de jugadores

Fuente de verdad: bloque `yaml`. `BRx.y` son claves de trazabilidad.

```yaml
rules:
  # Grupo 1 — Extracción en el sync
  - id: BR1.1
    statement: "PlayersFullSyncOrchestrator extrae points, change, homeAverage, awayAverage, matches y status del objeto vivo y los añade a player_records para el upsert en players."
    category: calculation
    applies_to: PlayersFullSyncOrchestrator
    trigger: "Durante el bucle de ingestión de cada jugador."
    logic: "player_records[i] += {points: player.points, change: player.change, home_average: norm(player.average.homeAverage), away_average: norm(player.average.awayAverage), matches: player.average.matches, status: player.status}."
    violation: "Seguir descartando esos campos."
    source: FR1.1, FR1.2
  - id: BR1.2
    statement: "La normalización norm() de home/away average convierte el string a float; 'NaN', vacío, None o no-parseable → None (reutiliza clean_float). points/change/matches ausentes → 0; status ausente → ''."
    category: policy
    applies_to: PlayersFullSyncOrchestrator
    trigger: "Al mapear cada campo numérico/estado."
    logic: "norm(x)=clean_float(x, None) con guardas para '', None y no-numérico (addresses advisory M-FR1.3)."
    violation: "Persistir 'NaN' como texto o romper por un string no numérico."
    source: FR1.3

  # Grupo 2 — Esquema
  - id: BR2.1
    statement: "La tabla players gana las columnas points INTEGER DEFAULT 0, change INTEGER DEFAULT 0, home_average REAL, away_average REAL, matches INTEGER DEFAULT 0, status TEXT DEFAULT ''. El upsert (single y batch) las incluye."
    category: constraint
    applies_to: players_adapter
    trigger: "Migración de esquema + upsert."
    logic: "ALTER TABLE players ADD COLUMN IF NOT EXISTS ... (idempotente, no destructivo); INSERT/ON CONFLICT actualiza las nuevas columnas."
    violation: "Migración no idempotente o que altere/borre datos; ampliar un god-file para esto."
    source: FR2.1, FR2.2, NFR6
  - id: BR2.2
    statement: "La migración vive donde ya se definen/alteran las tablas (schema_lifecycle / arranque), NO en un god-file nuevo ni en el router."
    category: constraint
    applies_to: schema_lifecycle
    trigger: "Arranque / _ensure_schema_updates."
    logic: "Se añade el ALTER idempotente al punto de evolución de esquema existente."
    violation: "SQL-en-router o god-file."
    source: C1

  # Grupo 3 — Equipo/escudo en lectura
  - id: BR3.1
    statement: "favorites_read resuelve team y team_logo desde real_team_id con LALIGA_TEAMS; fallback a real_team_name para team; peor caso (sin entrada en LALIGA_TEAMS Y sin real_team_name) → team='' y team_logo=''."
    category: calculation
    applies_to: favorites_read
    trigger: "Al componer cada FavoriteRow."
    logic: "team = LALIGA_TEAMS.get(real_team_id,{}).get('name') or real_team_name or ''; team_logo = LALIGA_TEAMS.get(real_team_id,{}).get('logo') or ''. (addresses advisory M-FR3.1)"
    violation: "Dejar team/team_logo indefinidos o romper si teamId no está en el mapa."
    source: FR3.1

  # Grupo 4 — Lectura de favoritos desde sync
  - id: BR4.1
    statement: "favorites_read lee points, change, home_average, away_average, matches y status de players (sync) para TODOS los favoritos, no solo los presentes en market_today. market_today pasa a ser, como mucho, un complemento opcional."
    category: calculation
    applies_to: favorites_read
    trigger: "GET /api/v1/favorites/my."
    logic: "SELECT ... p.points, p.change, p.home_average, p.away_average, p.matches, p.status FROM players ... ; mapear al contrato."
    violation: "Volver a depender de market_today para esos campos."
    source: FR4.1
  - id: BR4.2
    statement: "El orden (position_order asc, value desc) y las 20 claves/tipos del contrato de favorites/my no cambian; solo cambia el ORIGEN de algunos valores. Contrato completo: player_id, name, slug, position, position2, team, team_logo, value, change, points, average, home_average, away_average, matches, rating, sofascore_rating, sofascore_url, starter_pct, status, position_order."
    category: policy
    applies_to: favorites_read
    trigger: "Al serializar."
    logic: >
      Cambian de ORIGEN (ahora desde players sync): change, points, home_average,
      away_average, matches, status, team, team_logo. SIGUEN IGUAL que hoy:
      player_id, name, slug, position(role), position2(role2), value,
      average(average_overall de stats), rating(=0 plano), sofascore_rating,
      sofascore_url, starter_pct, position_order (todos de sus fuentes actuales:
      players/stats/sofascore_cache). `status` pasa a leerse de players.status
      (hoy hardcodeado a ''), lo cual DEPENDE del assumption A1 (el objeto vivo
      trae status por jugador — verificado 2026-10-24).
    violation: "Cambiar forma/orden/tipo de cualquier clave; omitir starter_pct o los sofascore_*."
    source: FR4.2, NFR1

  # Grupo 5 — Characterization-first y seguridad
  - id: BR5.1
    statement: "Antes de ampliar, se congela con tests el comportamiento ACTUAL de: (a) qué campos persiste PlayersFullSyncOrchestrator en player_records/stats; (b) la forma del contrato de favorites/my (las 20 claves); (c) la selección de favoritos (fav True AND no userteamId); (d) el no-leak de credenciales en logs/errores; (e) el ORIGEN actual de points (SUM(player_performance.points), que para agentes libres da 0) y de status (hoy hardcodeado a ''), para que el cambio a players.points / players.status quede documentado como intencional y no como regresión silenciosa."
    category: policy
    applies_to: tests
    trigger: "Code Generation (test-after, characterization-first)."
    logic: "Tests con fakes in-memory (conftest.py); enumeran esas ramas/campos, incl. el cambio de origen de points y status (addresses advisory M-NFR2, y los findings del review de diseño sobre points/status)."
    violation: "Cambiar la fuente sin congelar antes; assert True."
    source: NFR2
  - id: BR5.2
    statement: "Hasta el primer sync tras el deploy, un favorito cuyas columnas nuevas estén vacías ve los defaults: points=0, change=0, home_average=None, away_average=None, matches=0, status='' (idénticos a los defaults que el contrato ya produce). El sync periódico las completa; no hay backfill forzado."
    category: policy
    applies_to: favorites_read
    trigger: "Favorito con columnas nuevas aún nulas."
    logic: "COALESCE/guardas a los defaults listados (addresses advisory M-NFR5)."
    violation: "Exponer null crudo donde el contrato espera 0/''; forzar backfill."
    source: NFR5
  - id: BR5.3
    statement: "No se introducen credenciales en logs/mensajes de error nuevos; se preserva el patrón actual (str(e), sin token/password)."
    category: policy
    applies_to: PlayersFullSyncOrchestrator
    trigger: "Ruta de error del sync."
    logic: "Mantener el logging actual sin material de credencial."
    violation: "Loguear token/password."
    source: C1, seguridad afirmada
```

## Resumen de reglas

| Grupo | Tema | Reglas |
|---|---|---|
| BR1 | Extracción + normalización en el sync | BR1.1, BR1.2 |
| BR2 | Esquema ampliado idempotente (sin god-files) | BR2.1, BR2.2 |
| BR3 | Equipo/escudo por teamId (peor caso definido) | BR3.1 |
| BR4 | favorites_read desde sync + contrato intacto | BR4.1, BR4.2 |
| BR5 | characterization-first + defaults + sin credenciales | BR5.1, BR5.2, BR5.3 |
