# Instrucciones de Test — Arreglo de AnalyticsService

## Framework y configuración
- Runner: `pytest` (existente). Config: `backend/pytest.ini` (`pythonpath = .`,
  `--cov=app` disponible pero sin piso bloqueante).
- No se crea runner ni configuración nueva (brownfield, scope bugfix Minimal).

## Cómo ejecutar los tests de esta unidad (comando exacto, scoped)
Desde el directorio `backend/`:

```bash
python -m pytest tests/test_analytics_service.py -q
```

(Requiere `pytest` instalado en el entorno; el entorno de análisis no lo tenía,
la ejecución real se valida en el stage Build and Test / entorno de CI.)

## Alcance de los tests
- Los 6 tests de `test_analytics_service.py` deben pasar tras el arreglo:
  - `test_championship_trends`, `test_clause_network`, `test_player_value_trend`
    (los 3 arreglados por este intent)
  - `test_player_form`, `test_opportunity_streaks`, `test_matchday_projections`
    (deben seguir en verde)
- Cobertura: sin objetivo de piso adicional (Minimal). El criterio es exit code 0.

## Regresión dirigida (scope floor bugfix)
Los 3 tests arreglados son la regresión que congela el comportamiento correcto:
- presencia de `_team_cache`/`_player_cache` bajo el fixture
- clave de salida `last_transaction_price` en `get_player_value_trend`

## Mocking / stubbing
- Se usa la `StubDM` existente del fixture (monkeypatch de `AnalyticsService.__init__`).
- No se introducen mocks nuevos.

## Datos de test
- Los datos provienen de los lambdas de `StubDM` (ya presentes). El valor
  esperado `1000000` en `test_player_value_trend` proviene de
  `get_transactions_raw` (`price: 1000000`).
