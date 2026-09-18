# Unit Test Instructions — matchday-prizes-calc

## Framework y configuración

- Backend: `pytest` + `pytest-cov`, ejecutado **desde `backend/`**
  (`backend/pytest.ini`: `testpaths = tests`, `pythonpath = .`).
- Fakes compartidos en `backend/conftest.py`: `fake_db` / `_FakeInMemoryDB`
  (SQLite en memoria que respeta el contrato `db_connection` y ejercita el SQL
  parametrizado real, incluido `DELETE ... NOT IN`), `clean_jwt_env`.

## Comando de ejecución (unit-scoped)

Ejecutar SOLO los tests de esta unidad (no la suite completa), desde `backend/`:

```bash
cd backend && python -m pytest tests/test_prizes_characterization.py tests/test_prizes_calculator.py -q
```

## Cobertura objetivo

- Estrategia standard: 5-8 tests por componente. Exigir tests de los caminos
  nuevos y de error del cálculo de premios; el 80% de líneas es referencia
  global no bloqueante (sin `cov-fail-under` en el repo).

## Mocking / stubbing

- **API Futmondo**: fake determinista de las respuestas de ronda (ranking,
  matches, dream team, lineups). Sin red, sin `time.sleep` real
  (monkeypatch de `time.sleep` a no-op si se ejercita el orquestador).
- **Persistencia**: `fake_db` en memoria; cada test crea y limpia su propio
  almacén de `team_prizes`; nunca se comparte estado mutable.
- Patrón de referencia: `test_finance_characterization.py` (doble de
  `DataManagerV2` + `get_db` falso) y `test_analytics_service.py`.

## Gestión de datos de test

- Datos de ronda deterministas construidos en el test (no fixtures externas ni
  datos reales). El ejemplo de la jornada 5 (posiciones 3ª=1.285.714,
  4ª=1.714.286; empate → 1.500.000/1.500.000) se codifica como caso explícito.
