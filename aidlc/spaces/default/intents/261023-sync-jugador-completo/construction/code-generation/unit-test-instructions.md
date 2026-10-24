# Unit Test Instructions — Enriquecimiento del sync de jugadores

## Framework y configuración

- Backend `pytest` + `pytest-cov` (`backend/pytest.ini`, `pythonpath = .`). Fakes
  in-memory del `backend/conftest.py` (`fake_db`, `_FakeInMemoryDB` sobre SQLite
  `:memory:`, autouse que evita conexión real). Sin red, sin BD real, sin
  credenciales (gitleaks escanea los tests).

## Comando (unit-scoped — solo los ficheros de esta unidad)

Desde `backend/`:

```bash
python -m pytest tests/test_sync_players_enrichment.py tests/test_players_adapter_enrichment.py tests/test_favorites_read_enriched.py tests/test_schema_players_columns.py -q
```

(Ejecutar los ficheros nuevos que existan; en Build and Test corre la suite
completa. NO usar un `pytest` sin filtrar aquí.)

## Objetivos de cobertura

- Scope **refactor**: no se introduce piso nuevo; el piso heredado
  `--cov-fail-under=27` **no se baja**. Las capas nuevas/modificadas se cubren
  con sus tests (happy-path + ramas de normalización/defaults). Suite existente
  en verde.

## Mocking / stubbing

- `fake_db` del `conftest.py` para persistencia (SQLite in-memory).
- Doblar el cliente Futmondo (sin red) con la forma cruda verificada del objeto
  jugador (incluyendo `points`, `change`, `average.homeAverage`="NaN", etc.),
  como hacen `test_sync_players_full_characterization.py` /
  `test_analytics_service.py`.
- Nunca copiar datos/credenciales reales.

## Datos de prueba

- Sembrar `players` (con y sin las columnas nuevas pobladas),
  `player_championship_stats`, `player_favorites`, `sofascore_cache`,
  `player_performance`; filas mínimas deterministas por aserción.

## Orden (test-after, characterization-first)

1. Primero Step 1 (caracterización) — congela el comportamiento ACTUAL (incl.
   origen de `points`=SUM(player_performance) y `status`='') y pasa contra el
   código sin tocar.
2. Después, por capa: migración → upsert → orquestador → `favorites_read`,
   implementando y luego escribiendo/corriendo los tests de cada una.
