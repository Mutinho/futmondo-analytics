# Requirements — Enriquecimiento del sync de jugadores (261023-sync-jugador-completo)

## Contexto

`GET /api/v1/favorites/my` muestra los favoritos (agentes libres) con precio y
media correctos pero **sin puntos, tendencia (`change`), equipo/escudo ni medias
casa/fuera** para la mayoría. Causa raíz verificada: `sync_players_full` lee solo
un subconjunto de los campos que `/5/league/championshipplayers` ya devuelve por
jugador, y descarta `points`, `change`, `home/away_average`, `matches`, `status`.
Objetivo: enriquecer el sync para persistir esos campos y servir favoritos
íntegros desde datos sincronizados, sin llamadas vivas ni dependencia de
`market_today`.

## Functional Requirements

### FR1 — El sync persiste la info completa del jugador
- FR1.1 `PlayersFullSyncOrchestrator` extrae y persiste, por jugador:
  `points`, `change`, `home_average`, `away_average`, `matches`, `status`
  (además de lo que ya guarda). (Q1-A)
- FR1.2 `points` se toma del objeto vivo (total acumulado que ya da Futmondo); no
  se agrega desde `player_performance`. (Q1-A)
- FR1.3 `home_average`/`away_average` llegan como string y pueden ser `"NaN"`:
  se normalizan a número o `None` (patrón `clean_float`). (RE)
- FR1.4 Se persiste `real_team_id` (`teamId`) en `players` para poder resolver
  equipo/escudo en lectura. (Q2-A)

### FR2 — Esquema sincronizado ampliado
- FR2.1 Columnas nuevas en **`players`**: `change`, `points`, `home_average`,
  `away_average`, `matches`, `status` (+ `real_team_id` si no estuviera). (Q1-A)
- FR2.2 La migración es un `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` idempotente
  en el arranque/migración existente; no amplía los god-files. (Q1-A, C1)

### FR3 — Equipo y escudo resueltos por teamId
- FR3.1 `team` (nombre) y `team_logo` se resuelven desde `real_team_id` con el
  mapa estático `LALIGA_TEAMS`, cayendo a `players.real_team_name` si falta. (Q2-A)

### FR4 — favorites/my lee los campos del sync
- FR4.1 `favorites_read` lee `change`/`points`/`home_average`/`away_average`/
  `matches`/`status` de `players` (sync) para TODOS los favoritos, no solo los
  presentes en `market_today`. (Q3-A)
- FR4.2 Se mantiene el orden actual (`position_order` asc, `value` desc) y las
  claves/tipos exactos del contrato. (Q5-A)

### FR5 — market/today sin cambios
- FR5.1 `market/today` no se toca en este intent (ya funciona desde
  `market_today`). (Q3-A)

## Non-Functional Requirements

- NFR1 (Compatibilidad) El contrato de `favorites/my` **no cambia**
  (claves/tipos/orden); solo cambia el ORIGEN de los valores. Sin cambios en
  Angular ni iOS. (Q5-A)
- NFR2 (Characterization-first) Congelar con tests el comportamiento actual de
  `sync_players_full` (qué persiste) y de `favorites_read` ANTES de ampliarlos;
  tests con fakes in-memory (`conftest.py`), sin red/DB real/credenciales. (Q5-A)
- NFR3 (Coste) Coste 0 €: solo Neon/Fly.io free; sin dependencias nuevas. (C3)
- NFR4 (Gate verde) Pasar el gate de CI bloqueante; el piso de cobertura solo
  sube, nunca baja. (C3)
- NFR5 (Sin backfill especial) Los campos se completan en el primer sync tras el
  deploy; mientras, `favorites_read` degrada con los defaults actuales. No se
  fuerza backfill. (Q4-A)
- NFR6 (Migración segura) El `ALTER TABLE` es idempotente y no destructivo; no
  borra ni altera datos existentes. (Q1-A)

## Constraints

- C1 **NUNCA ampliar los god-files** (`data_sync_service.py`,
  `data_manager_v2.py`) ni el patrón SQL-en-router; el código nuevo va tras la
  capa estrecha testeable del sync y de `sync_read`.
- C2 Contrato de respuesta inmutable (Angular + iOS).
- C3 Coste 0 €; gate de CI bloqueante verde antes de fusionar.

## Assumptions

- A1 `/5/league/championshipplayers` seguirá devolviendo `points`/`change`/
  `average`/`teamId`/`status` por jugador (verificado con respuesta cruda
  2026-10-24).
- A2 El sync de jugadores corre con frecuencia suficiente para poblar los campos
  nuevos poco después del deploy.
- A3 `LALIGA_TEAMS` cubre los `teamId` de LaLiga del campeonato (ya se usa en la
  ruta viva actual de favoritos).

## Out of scope

- O1 Cambiar el contrato de respuesta de los endpoints.
- O2 Adaptar `market/today` a leer del sync enriquecido.
- O3 Backfill forzado / script de migración de datos (el sync periódico lo cubre).
- O4 Cambios de CI/CD o despliegue más allá de pasar el gate existente.
- O5 iOS / Angular: no se tocan (el contrato no cambia).
