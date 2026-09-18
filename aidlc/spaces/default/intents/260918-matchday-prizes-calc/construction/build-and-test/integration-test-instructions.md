# Integration Test Instructions — matchday-prizes-calc

El cálculo puro (`PrizeCalculator`) no tiene integración externa propia (sin I/O
ni SQL). La integración relevante es `sync_prizes` (orquestador) → persistencia
`team_prizes`, que se ejercita en la caracterización con el fake de persistencia
`fake_db` (`_FakeInMemoryDB`, SQLite en memoria que corre el UPSERT `ON CONFLICT`
y el `DELETE ... NOT IN` reales) — cubierto por `test_prizes_characterization.py`.

- No se añaden tests de integración con Neon real (coste 0 €; el fake ejercita el
  SQL parametrizado real).
- La ruta de lectura (routers → `SELECT`/suma sobre `team_prizes`) no se toca y su
  consumo ya está caracterizado en `test_finance_characterization.py`.
