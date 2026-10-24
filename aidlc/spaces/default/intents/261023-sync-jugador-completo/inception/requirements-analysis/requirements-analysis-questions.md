# Requirements Analysis — Preguntas

Intent `261023-sync-jugador-completo`. Enriquecer `sync_players_full` para
persistir la info completa de cada jugador y servir favoritos (y mercado)
íntegros desde el sync. La ingeniería inversa ya verificó que
`/5/league/championshipplayers` trae todos los campos; estas preguntas fijan
alcance y decisiones de producto. Cada ⭐ es la recomendación.

---

## Q1. Dónde persistir los campos nuevos (esquema)

`change`, `points`, `home_average`, `away_average`, `matches`, `status` no se
guardan hoy. ¿Dónde los añadimos?

- A. ⭐ Columnas nuevas en **`players`** (`change`, `points`, `home_average`,
  `away_average`, `matches`, `status`), que es per-jugador y ya la lee
  `favorites_read`. Un solo `ALTER TABLE` idempotente en el arranque/migración,
  sin tocar los god-files. `points` del objeto vivo es el total acumulado del
  jugador (ya viene calculado por Futmondo), así que se guarda directo (no hace
  falta agregarlo de `player_performance`).
- B. Columnas nuevas en `player_championship_stats` (per-campeonato). Más
  correcto si estos valores variaran por campeonato, pero el objeto de
  `championshipplayers` los da por jugador global → añade complejidad sin
  beneficio.
- X. Other (please specify)

[Answer]: A

---

## Q2. Equipo y escudo (team / team_logo)

El objeto trae `teamId` (siempre) pero no siempre `team` (nombre); el logo no
viene.

- A. ⭐ Derivar `team` (nombre) y `team_logo` desde `teamId` con el mapa estático
  `LALIGA_TEAMS` (ya existe en el repo) como fuente principal, cayendo a
  `players.real_team_name` si falta. Persistir `real_team_id` (teamId) en
  `players` para poder resolverlo en lectura. Coste 0, sin llamadas extra.
- X. Other (please specify)

[Answer]: A

---

## Q3. Alcance de los consumidores (¿solo favoritos, o también mercado?)

- A. ⭐ **Favoritos/my** es el objetivo principal (es donde se ve el bug). El
  enriquecimiento del sync beneficia también a cualquier lector futuro, pero en
  este intent solo **adaptamos `favorites_read`** para leer los campos nuevos;
  `market/today` ya funciona (sus datos salen de `market_today`) y no se toca.
- B. Adaptar también `market/today` para leer del sync enriquecido en vez de
  `market_today`. Amplía alcance sin resolver un bug visible hoy.
- X. Other (please specify)

[Answer]: A

---

## Q4. Re-sincronización / backfill de datos existentes

Las columnas nuevas estarán vacías hasta el próximo sync.

- A. ⭐ **No hace falta backfill especial**: el sync de jugadores ya corre
  periódicamente (y bajo demanda); en la primera ejecución tras el deploy
  poblará los campos nuevos para todos los jugadores. Mientras tanto,
  `favorites_read` degrada con los defaults actuales (como hoy). Se documenta
  que los campos se completan tras el primer sync.
- B. Forzar un sync inmediato / script de backfill como parte del release.
  (Innecesario; el sync periódico lo cubre.)
- X. Other (please specify)

[Answer]: A

---

## Q5. Contrato de respuesta y compatibilidad

- A. ⭐ El contrato de `favorites/my` **no cambia** (mismas claves/tipos/orden);
  solo cambia el ORIGEN de los valores (ahora completos desde sync). Sin cambios
  en Angular ni iOS. Characterization-first: congelar el comportamiento del sync
  y del endpoint antes de tocarlos; suite en verde; piso de cobertura no baja.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de lo acordado (Todas A):

- **Q1** Columnas nuevas en `players` (`change`, `points`, `home_average`,
  `away_average`, `matches`, `status`); `points` directo del objeto vivo.
- **Q2** `team`/`team_logo` resueltos por `teamId` con `LALIGA_TEAMS` (+ `real_team_id` persistido).
- **Q3** Alcance: solo `favorites/my` / `favorites_read`; `market/today` no se toca.
- **Q4** Sin backfill forzado; el sync periódico puebla los campos tras el deploy.
- **Q5** Contrato inmutable; characterization-first; suite verde; piso de cobertura no baja.

[Answer]: Looks correct
