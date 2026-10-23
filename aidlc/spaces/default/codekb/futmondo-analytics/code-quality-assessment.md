# Code Quality Assessment — Futmondo Analytics

> Refresco enfocado en latencia. Evaluación centrada en la ruta de los 3
> endpoints y en las restricciones durables de memoria.

## Rendimiento (hallazgo núcleo del intent)

- La latencia percibida es **proporcional al número de llamadas HTTP en vivo a
  Futmondo por request**, no a Neon:
  - `/analytics/balances` ~0.4 s: 1 llamada en vivo + reads sincronizados.
  - `/market/today` ~1.6 s: 1 llamada en vivo obligatoria (pujas del usuario)
    pese a cachear el catálogo en `market_today`; +1 condicional sin caché.
  - `/favorites/my` ~3.4 s: 2-3 llamadas en vivo encadenadas; la peor,
    `get_championship_players` (`/5/league/championshipplayers`), descarga la
    lista completa de jugadores solo para filtrar favoritos.
- Buenas prácticas ya presentes: un único `get_connection()` por request, batch
  de transacciones (LIMIT 200) en `/market/today`, persistencia de
  `futmondo_team_id` para evitar una llamada extra, pool con reintento de
  conexiones muertas.

## Deuda técnica (constraints durables — NO ampliar)

- **God-files**: `data_sync_service.py` (~15 KB) y `data_manager_v2.py` (~33 KB).
  La mejora de latencia NO debe ampliarlos; un lector read-from-sync va tras una
  capa/función estrecha testeable.
- **SQL-en-router**: SQL crudo dentro de `market.py`/`favorites.py`/`balances.py`.
  NO ampliar el patrón.
- **`except Exception: pass` defensivos** en `market.py` (lectura de caché,
  favoritos, pujas en vivo): silencian fallos; registrados como deuda, fuera del
  alcance salvo que corrompan datos.

## Manejo de errores

- Integración tipada y propagada (`integration_errors`), nunca `None`
  silencioso; `_make_request` distingue timeout/request/unparseable. Excepciones
  sin material de credencial.
- `db_connection.get_connection` hace `rollback()+raise` ante fallo (no deja
  datos a medias).
- Favoritos devuelve `401` actionable cuando la sesión no es recuperable.

## Testing

- Backend: suite `pytest` characterization-first con fakes in-memory
  (`conftest.py`), sin red/DB real. Gate de CI bloqueante.
- Cualquier mejora de latencia debe mantener la suite en verde y NO bajar el
  piso de cobertura (`--cov-fail-under`, ratchet solo sube).

## Seguridad

- Nunca contraseña Futmondo en claro; refresh token en cookie `HttpOnly`.
- `JWT_SECRET` no-default obligatorio al arranque.
- Un read-from-sync o caché de pujas no debe exponer pujas de un usuario a otro
  (hoy las pujas van siempre en vivo justo por esta privacidad).

## Riesgos de la mejora

- Un read-from-sync del catálogo de jugadores en `/favorites/my` depende de la
  frescura del sync en background.
- Una caché de pujas del usuario necesitaría invalidación tras
  `bid`/`cancelbid`.
