# Code Quality Assessment — Futmondo Analytics

> Merge CURRENT. Evaluación previa (latencia) **preservada**; se añade la del
> flujo player-sync y las restricciones durables aplicables al enriquecimiento.

## Calidad del flujo player-sync (hallazgo del intent)

- **Buena separación DDD**: `sync_players_full` y los adapters `data_manager/*`
  siguen puerto (Protocol, sin SQL) + adapter (único SQL) + servicio fino, con
  IDs de business-rule en los docstrings. El SQL vive concentrado y testeable.
- **Gap de datos, no de código**: el límite para Favoritos/Mercado es que
  `sync_players_full` **no persiste** `points/change/home_average/away_average/
  matches/team_logo`. Esos campos quedan dispersos en `player_performance`
  (points, por jornada, vacío para agentes libres) y `market_today` (el resto,
  ~30 jugadores/día). `read_favorites` ya los lee de donde existen, pero el sync
  no los escribe para todos.
- **Punto de corrupción conocido**: `delete_orphan_players`
  (`DELETE ... NOT IN` / `<> ALL(%s)`) sin reemplazo transaccional atómico
  (deferido, OQ2); vigilar si el cambio de esquema toca `players`.
- **`except Exception` no-fatales** en el orquestador (huérfanos, stats,
  favoritos): degradan y continúan (registran `warning`); correcto para
  robustez, pero enmascaran fallos parciales de persistencia.

## Rendimiento (hallazgo del store previo — preservado)

- La latencia percibida es **proporcional al número de llamadas HTTP en vivo a
  Futmondo por request**, no a Neon:
  - `/analytics/balances` ~0.4 s: 1 llamada en vivo + reads sincronizados.
  - `/market/today` ~1.6 s: 1 llamada en vivo obligatoria (pujas del usuario).
  - `/favorites/my`: fast-path desde el sync; fallback vivo (2-3 llamadas) solo
    en sync-miss.
- Buenas prácticas presentes: un único `get_connection()` por request, batch de
  transacciones (LIMIT 200), pool con reintento de conexiones muertas.

## Deuda técnica (constraints durables — NO ampliar)

- **God-files**: `data_sync_service.py` (~15 KB) y `data_manager_v2.py`
  (~33 KB). El enriquecimiento NO debe ampliarlos: los campos nuevos van tras los
  adapters DDD (`players_adapter`/`schema_lifecycle_adapter`) y una capa narrow
  testeable.
- **SQL-en-router**: SQL crudo en `market.py`/`favorites.py`/`balances.py`. NO
  ampliar; el SQL nuevo va en `sync_read`/adapters.
- **`except Exception: pass` defensivos** (market/orquestador): silencian
  fallos; fuera del alcance salvo que corrompan datos.

## Manejo de errores

- Integración tipada y propagada (`integration_errors`), nunca `None`
  silencioso; `_make_request` distingue timeout/request/unparseable y no filtra
  credenciales.
- `db_connection.get_connection` hace `rollback()+raise` ante fallo.
- Favoritos devuelve `401` actionable cuando la sesión no es recuperable.

## Testing

- Backend: suite `pytest` characterization-first con fakes in-memory
  (`conftest.py`), sin red/DB real. Gate de CI bloqueante.
- **Mandato durable**: congelar con tests `sync_players_full` en todas sus ramas
  antes de enriquecerlo (hoy la producción del sync de jugadores tiene cobertura
  directa escasa). Mantener la suite en verde y no bajar el piso de cobertura.

## Seguridad

- Nunca contraseña Futmondo en claro; refresh token en cookie `HttpOnly`;
  `JWT_SECRET` no-default al arranque.
- Un enriquecimiento del sync no debe exponer datos privados entre usuarios: los
  campos a persistir son del catálogo compartido (no pujas), compatible con el
  modelo actual.

## Riesgos de la mejora

- **INCÓGNITA CRÍTICA**: ¿trae `/5/league/championshipplayers` los campos que
  faltan por jugador? Si no, hace falta otra fuente (`/1/player/summary`,
  `/1/player/fullprofile` o Sofascore) → coste HTTP por jugador y cambio de
  diseño. Verificar con llamada cruda antes de diseñar.
- **Cambio de esquema + re-sync**: poblar columnas nuevas exige migración DDL
  (vía `schema_lifecycle`) y un re-sync completo; planificar en Functional
  Design.
- Mantener el **contrato de respuesta** de Favoritos/Mercado byte-for-byte: el
  enriquecimiento cambia la FUENTE de los campos, no las claves/tipos.
