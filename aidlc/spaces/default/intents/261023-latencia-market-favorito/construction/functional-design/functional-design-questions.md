# Functional Design — Preguntas de diseño

Intent: `261023-latencia-market-favorito`. Consume: `requirements.md` (FR1–FR5,
NFR1–NFR6) + codeKB.

Hallazgos del código (anclan el diseño; no se preguntan):
- `balances.py` (rápido) lee de tablas **sincronizadas** en Neon (`transactions`,
  `teams`, `team_prizes`, `team_standings`) + 1 llamada viva. Patrón a replicar.
- `favorites.py` (lento) hace `SELECT player_id FROM player_favorites` (barato) y
  luego **`client.get_championship_players`** (llamada viva pesada, baja TODO el
  catálogo) + `get_matchday_standings` (otra viva).
- Datos de jugadores ya sincronizados: **`player_championship_stats` JOIN
  `players`** (valor/stats/propiedad por campeonato), **`sofascore_cache`**
  (rating/goals/…), `team_standings` (team_value), `market_today` (catálogo de
  mercado), `player_favorites`. (market.py ya los lee para su `user_info`.)
- Restricciones durables: NO ampliar `data_sync_service.py`/`data_manager_v2.py`
  ni SQL-en-router; capa de lectura nueva estrecha y testeable; characterization-
  first; sin tocar el contrato de respuesta.

Responde cada `[Answer]:` con la letra. Recomendación ⭐.

---

## Q1. Dónde vive la capa de lectura nueva

- A. Un **módulo/servicio nuevo** `services/sync_read/` (p. ej.
  `favorites_read.py`, `market_read.py`) con funciones puras-ish que reciben la
  conexión y devuelven los datos ya mapeados al contrato; los routers
  `favorites.py`/`market.py` llaman a esa capa en vez de al cliente vivo. NO se
  toca `data_sync_service.py`/`data_manager_v2.py`; el SQL vive en la capa nueva
  (no en el router), testeable con fakes en memoria. ⭐
- B. Añadir funciones a `data_manager_v2.py` (god-file) — PROHIBIDO por memoria.
- X. Other (please specify)

[Answer]: A

---

## Q2. `favorites/my`: fuente de los datos de jugador

- A. Leer los favoritos desde **`player_championship_stats` JOIN `players`**
  (valor, puntos, media, titularidad, posiciones, propiedad=free-agent) +
  **`sofascore_cache`** (rating/url) para el campeonato, filtrando por los
  `player_id` de `player_favorites`, y **eliminar** la llamada viva
  `get_championship_players`. Orden preservado: `position_order` asc, luego
  `value` desc. ⭐
- B. Mantener la llamada viva (no optimiza).
- X. Other (please specify)

[Answer]: A

---

## Q3. Trigger del fallback en sync-miss (FR4 — precisar el finding del revisor)

¿Cuándo se considera que NO hay datos sincronizados suficientes y se cae a la
ruta viva?

- A. Si el `SELECT` sincronizado para ese campeonato devuelve **0 filas de
  jugadores** (catálogo vacío / campeonato nunca sincronizado), fallback a la
  ruta viva actual; si devuelve filas, se sirve desde sync (aunque alguna métrica
  puntual sea nula, que se mapea como hoy). Se registra el fallback (log). ⭐
- B. Fallback si falta CUALQUIER campo de CUALQUIER jugador (demasiado estricto;
  casi siempre caería a vivo).
- X. Other (please specify)

[Answer]: A

---

## Q4. `market/today`: estado de pujas del usuario y CONCURRENCIA (finding Major del revisor)

Hoy `market/today` hace 1 llamada viva siempre para las pujas del usuario. Se
quiere servirlas desde estado propio invalidado tras pujar/cancelar, SIN perder
coherencia bajo concurrencia.

- A. Modelar las pujas del usuario como **estado derivado leíble de Neon**
  (tabla/consulta ya existente de transacciones/pujas del usuario+campeonato),
  recomputado en cada request desde la BD (no un caché en proceso con TTL): como
  es una **lectura de la BD**, un `bid`/`cancelbid` que escribe esa misma BD deja
  la siguiente lectura coherente por construcción (sin version-skew de caché).
  Si no existe una tabla de pujas del usuario consultable, usar
  caché-en-proceso con **invalidación explícita** tras `bid`/`cancelbid` y
  **read-through** (recomputar si no hay entrada), documentando que una escritura
  concurrente de otro proceso podría servir pujas de hasta N s de antigüedad
  (aceptable: no afecta a `balance`, solo al listado de pujas, y se corrige en la
  siguiente operación/expiración). La elección exacta la fija el detalle del
  diseño según exista o no esa tabla. ⭐
- B. Mantener SIEMPRE la llamada viva para pujas (prioriza frescura sobre
  latencia en market).
- X. Other (please specify)

[Answer]: A

---

## Q5. Coherencia de `user_info` tras una operación (FR2.2)

- A. Tras un `bid`/`cancelbid` aceptado, `user_info` (balance,
  `active_bids_total`, `active_bids_count`, `available_for_bids`) se recomputa de
  la **misma fuente** que las pujas (BD), de modo que la respuesta inmediata
  posterior a la operación es coherente; se añade un test de caracterización que
  fija "tras operar, user_info refleja el cambio". ⭐
- X. Other (please specify)

[Answer]: A
