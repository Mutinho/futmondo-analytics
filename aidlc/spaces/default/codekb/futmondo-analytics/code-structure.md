# Code Structure — Futmondo Analytics

> Refresco enfocado en latencia. Organización registrada una vez; detalle de
> componentes en `component-inventory.md`.

## Organización de alto nivel

```
backend/app/
  api/v1/endpoints/   # routers FastAPI (SQL-en-router heredado)
  services/           # lógica + integraciones + sync
    sync/             # orquestadores DDD por tipo de dato
    data_manager/     # adapters DDD extraídos del god-file
  stores/             # repositorios durables (task, session)
  auth/, security/, core/, models/
angular-app/src/app/
  features/market/    # vista de Mercado (fuente de verdad F3)
  features/budget/    # Presupuesto
  core/               # servicios, interceptors, guards
```

## Clasificación de ficheros (ruta de latencia)

| Fichero | Categoría | Rol en la latencia |
|---|---|---|
| `api/v1/endpoints/market.py` | Controller/Handler | `/today` lee caché + 1 llamada en vivo (pujas) |
| `api/v1/endpoints/favorites.py` | Controller/Handler | `/my` hace 2-3 llamadas en vivo |
| `api/v1/endpoints/balances.py` | Controller/Handler | patrón rápido: 1 llamada en vivo + reads sincronizados |
| `api/v1/endpoints/roster.py` | Controller/Handler | usa standings+roster en vivo (fuera de los 3, mismo patrón) |
| `api/v1/endpoints/sync.py` | Controller/Handler | triggers de sync; `_check_phantoms` (standings+roster en vivo) |
| `api/v1/endpoints/_helpers.py` | Utility | `get_user_futmondo_client` (sesión durable), `get_championship_config` |
| `api/v1/endpoints/_sofascore_helpers.py` | Utility | `build_sofascore_map`, `calculate_starter_pct` (lee `sofascore_cache`) |
| `services/data_sync_service.py` | Service (god-file, NO ampliar) | pre-sincroniza Neon vía orquestadores `services/sync/*` |
| `services/data_manager_v2.py` | Service (god-file, NO ampliar) | acceso a datos; parte en `data_manager/` |
| `services/futmondo_client.py` | Adapter | `_make_request` (timeout 15 s, errores tipados) |
| `services/sofascore_client.py` | Adapter | ratings Sofascore |
| `services/db_connection.py` | Config/DAO | pool PostgreSQL/Neon, `adapt_params` |
| `stores/{task,session}_repository.py` | Repository | persistencia durable (ojeado) |

## Patrones de código observados

- **SQL-en-router** (deuda heredada): SQL crudo con `db.adapt_params("? → %s")`
  dentro de los endpoints. NO ampliar.
- **Caché por fecha**: `market_today` keyed por `championship_id` + `market_date`.
- **Batch de queries**: `/market/today` carga transacciones en una sola query
  (LIMIT 200) en vez de N queries por jugador.
- **Un `get_connection()` por request**: evita checkouts repetidos del pool.
- **Errores de integración tipados**: `_make_request` lanza
  `IntegrationTimeout/Request/UnparseableError`, nunca `None` silencioso.
