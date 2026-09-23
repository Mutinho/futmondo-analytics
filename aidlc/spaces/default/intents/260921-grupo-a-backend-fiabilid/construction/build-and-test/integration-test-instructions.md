# Instrucciones de tests de integración — Fiabilidad de la sync

> Conversation language: Spanish. Test Strategy: **Standard** → se generan
> instrucciones de integración de fronteras clave. Unidad única
> `sync-reliability` (no hay interacción cross-unit real; las "fronteras" son
> las integraciones internas de esta unidad con el estado de tarea y el
> endpoint de mercado). Coste 0 € (`pytest` + `TestClient`, sin red/BD reales).

## Framework y setup

- `pytest` desde `backend/` (`pytest.ini` con `pythonpath = .`).
- `fastapi.testclient.TestClient` para las fronteras HTTP.
- Fakes: task manager en memoria (dict) y cliente Futmondo mockeado
  (`monkeypatch`/`vi.fn`-equivalente en Python: `unittest.mock`), sin red.
- `JWT_SECRET=test-secret-not-default-000`.

## Cómo correr

```bash
cd backend
python -m pytest tests -ra -p no:cacheprovider
```

Solo las fronteras tocadas por esta unidad:

```bash
cd backend
python -m pytest tests/test_market_bid_sanity_cap.py tests/test_sync_degraded_steps.py -ra
```

## Fronteras cubiertas (Standard)

- **Frontera estado-de-tarea ↔ helper de degradación** (`test_sync_degraded_steps.py`):
  un paso non-critical (`prizes`/`phantoms`) que lanza escribe `progress[step]`
  con `status="degraded"` + `reason` vía `record_degraded_step`, y la Tarea
  global puede terminar aunque el paso quede degradado (BR3/NFR1). Un paso que
  no lanza conserva `done` (BR2).
- **Frontera HTTP `POST /api/v1/market/bid`** (`test_market_bid_sanity_cap.py`):
  validación de entrada en la frontera antes de proxyar a Futmondo — `price>cap`
  → 422 sin invocar al cliente; `price<=0` → 422; `price` válido → 200 e invoca
  al cliente mockeado (FR6/NFR5, defensa en profundidad).
- **Frontera arranque/migraciones** (`test_token_store_migrations.py`): un error
  de migración NO-"ya existe" se propaga (no se traga), un duplicado idempotente
  se ignora con log (FR3.2/BR5).

## Cobertura esperada (Standard)

- Fronteras clave de la unidad cubiertas con aserciones reales (estado, payload,
  status code, propagación). Sin piso de cobertura bloqueante en backend (como
  hoy); el gate de CI exige `pytest` verde.

## Datos de prueba y entorno

- Sin fixtures de BD real: fake SQLite (`conftest.py`) y dobles en memoria.
- Sin llamadas de red: el cliente Futmondo se mockea en cada test de bid.

## Sources

- `construction/sync-reliability/code-generation/unit-test-instructions.md`,
  `code-summary.md`; `functional-design/rules.md` (BR1-BR5).

## Assumptions & Open Questions

None.
