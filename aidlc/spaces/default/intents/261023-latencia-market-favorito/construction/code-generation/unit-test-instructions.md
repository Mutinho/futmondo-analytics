# Unit Test Instructions — Optimización de latencia (read-from-sync)

## Framework y configuración

- Backend `pytest` + `pytest-cov` (ya configurado en `backend/pytest.ini`,
  `pythonpath = .`). Fakes in-memory del `backend/conftest.py` (`fake_db`,
  `_FakeInMemoryDB` sobre SQLite `:memory:`, autouse que evita conexión real).
- **Sin red, sin BD real, sin credenciales/tokens reales** (gitleaks escanea los
  tests). Patrón: sembrar tablas en el `fake_db` y ejercitar el SQL parametrizado
  real de la capa nueva.

## Comando (unit-scoped — solo los ficheros de esta unidad)

Desde `backend/`:

```bash
python -m pytest tests/test_favorites_read_characterization.py tests/test_favorites_read.py tests/test_market_read.py tests/test_sync_read_endpoints.py -q
```

(Ejecutar los ficheros nuevos que existan; en Build and Test corre la suite
completa. NO usar un `pytest` sin filtrar aquí.)

## Objetivos de cobertura

- Scope **refactor**: no se introduce piso nuevo; el piso heredado
  `--cov-fail-under=27` **no se baja**. La capa nueva se cubre con sus tests
  (happy-path + ramas de fallback/defaults). La suite existente permanece verde.

## Mocking / stubbing

- Usar `fake_db` del `conftest.py` para la persistencia (SQLite in-memory).
- Para los endpoints, doblar el cliente Futmondo (sin red) como hacen
  `test_sync_players_full_characterization.py` / `test_analytics_service.py`.
- Nunca copiar datos ni credenciales reales.

## Datos de prueba

- Sembrar `players`, `player_championship_stats`, `player_favorites`,
  `sofascore_cache`, `player_performance`, `market_today` con filas mínimas
  deterministas por test (una por aserción de efecto).

## Orden (test-after, characterization-first)

1. Primero los tests de caracterización (Step 3) que congelan el shape ACTUAL y
   pasan contra el código sin tocar.
2. Después, por capa: implementar `sync_read` → escribir y correr sus tests;
   modificar los routers → escribir y correr sus tests.
