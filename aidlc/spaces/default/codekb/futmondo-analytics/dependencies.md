# Dependencies — Futmondo Analytics

> Refresco enfocado en latencia. Foco en el grafo de dependencias de la ruta de
> petición de los 3 endpoints.

## Dependencias externas (backend, relevantes)

- `fastapi`, `uvicorn` — framework web / ASGI.
- `requests` — `FutmondoClient` (llamadas en vivo a Futmondo, timeout 15 s).
- `curl_cffi` — `SofascoreClient` (ratings).
- `psycopg2` — pool de conexiones a Neon PostgreSQL.
- `PyJWT`, `python-dotenv` — auth / config.

(Fijadas a versión exacta en `backend/requirements.txt`; no se introducen
dependencias de pago. `requirements.txt` no abierto línea a línea este run.)

## Grafo interno — ruta de latencia

```
market.py        → _helpers.get_user_futmondo_client → session_service → FutmondoClient
                 → _sofascore_helpers (sofascore_cache) → db_connection
                 → assistant_service._save_market_to_db (fallback caché)
favorites.py     → _helpers.get_user_futmondo_client → FutmondoClient
                 → _sofascore_helpers.build_sofascore_map → db_connection
balances.py      → _helpers.{get_user_futmondo_client,get_championship_config}
                 → FutmondoClient.get_matchday_standings → db_connection
data_sync_service → data_manager_v2 (god-file) + services/sync/* (DDD) → db_connection
                  → FutmondoClient
FutmondoClient   → requests, integration_errors
db_connection    → psycopg2 (pool), core.config.DATABASE_URL
```

## Dependencias cruzadas / acoplamientos a vigilar

- `market.py` depende de `assistant_service` (import lazy) para persistir el
  catálogo en `market_today`.
- `favorites.py` NO depende de ninguna tabla pre-sincronizada de catálogo (de
  ahí su coste): acoplado directamente a `FutmondoClient.get_championship_players`.
- Los endpoints acoplan SQL crudo a `db_connection` (SQL-en-router, deuda).
- Un lector read-from-sync nuevo debe depender de una capa/función estrecha
  testeable, sin ampliar `data_sync_service` ni `data_manager_v2`.

## Referencias circulares

Ninguna crítica observada en la ruta de latencia; los imports de
`assistant_service` y de los orquestadores `services/sync/*` son lazy
(dentro de función) para no alterar el grafo de import de los facades.
