# Frontend Components — N/A (intent backend)

Intent **puramente backend**: enriquece el sync de jugadores y adapta
`favorites_read`. **No hay componentes de frontend nuevos ni modificados** y el
contrato de `GET /api/v1/favorites/my` **no cambia** (mismas claves/tipos/orden).
Angular e iOS no requieren cambios.

Lo que sí mejora para el usuario, sin tocar frontend: los favoritos (agentes
libres) pasarán a mostrar puntos, tendencia (`change`), equipo + escudo y medias
casa/fuera reales en cuanto corra el primer sync tras el deploy, en vez de
quedar en `-`/vacío.

## Frontera backend (en lugar de componentes de UI)

| Módulo (capa estrecha) | Cambio |
|---|---|
| `backend/app/services/sync/players_full/orchestrator.py` | Extrae y añade a `player_records` los 6 campos nuevos (BR1.1/BR1.2) |
| `backend/app/services/data_manager/players/infrastructure/players_adapter.py` | Upsert incluye las columnas nuevas (BR2.1) |
| `backend/app/services/data_manager/schema_lifecycle/...` | `ALTER TABLE players ADD COLUMN IF NOT EXISTS ...` idempotente (BR2.1/BR2.2) |
| `backend/app/services/sync_read/favorites_read.py` | SELECT + mapeo de los campos desde `players`; team/logo por `LALIGA_TEAMS` (BR3.1/BR4.1/BR4.2/BR5.2) |

SQL en la capa de sync/`sync_read`, **nunca** en el router ni en los god-files.
