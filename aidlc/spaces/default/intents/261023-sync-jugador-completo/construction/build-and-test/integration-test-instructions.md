# Integration Test Instructions

Estrategia **minimal**: la frontera clave (sync → `players` → `favorites_read`)
está cubierta a nivel de componente por los tests nuevos, en particular
`tests/test_favorites_read_enriched.py` (favorito poblado → valores reales;
columnas nulas → defaults; team por `LALIGA_TEAMS`) y
`tests/test_sync_players_enrichment.py` (los 6 campos llegan a `player_records` y
se persisten). No se requieren tests de integración adicionales (no hay nuevas
fronteras externas; el sync usa la llamada que ya hacía).

```bash
python -m pytest tests/test_favorites_read_enriched.py tests/test_sync_players_enrichment.py -q
```
