# Instrucciones de tests — U1 sync-reliability

> Conversation language: Spanish. Metodología: test-after. Coste 0 € (solo
> `pytest`, ya presente). Sin red ni BD reales: fakes/dobles del task manager y
> del cliente Futmondo.

## Cómo correr

Desde `backend/` (el runner se ejecuta ahí para que `from app...` resuelva; ver
`pytest.ini` con `pythonpath = .`):

```bash
cd backend
python -m pytest tests -ra
```

Solo los tests nuevos de esta unidad:

```bash
cd backend
python -m pytest tests/test_sync_step_status.py tests/test_sync_degraded_steps.py tests/test_market_bid_sanity_cap.py -ra
```

Con cobertura informativa (opcional, sin piso bloqueante):

```bash
cd backend
python -m pytest tests --cov=app
```

Si el Python del sistema es más nuevo que el de CI (3.12), usar un venv efímero
excluyendo `libsql-experimental` (no compila fuera de 3.12 y los tests usan el
fake SQLite), y fijar un `JWT_SECRET` de arranque efímero
(`export JWT_SECRET=test-secret-not-default-000`). Alternativa a coste 0: contenedor
`python:3.12`.

## Qué cubren

- `test_sync_step_status.py` (FR3.1.1 / BR1):
  - `record_degraded_step` escribe `progress[step]` con `status="degraded"` +
    `reason` (y los `extra`), vía un `ProgressSink` doble.
  - Emite un `logger.warning` estructurado (se captura con `caplog`).
- `test_sync_degraded_steps.py` (FR3.1.2 / BR1 / BR2):
  - Un paso `prizes`/`phantoms` que lanza queda `degraded` (no `done`) con `reason`.
  - Un paso que NO lanza conserva `done` (sin regresión). Se usa un fake del task
    manager (dict en memoria); sin red.
- `test_market_bid_sanity_cap.py` (FR6 / BR4):
  - `price > PRICE_SANITY_CAP` → 422 y el cliente Futmondo NO es invocado.
  - `price <= 0` sigue → 422 (no regresión).
  - Un `price` válido intermedio → 200 e invoca al cliente (mock, sin red).

## Sources

- `functional-design/functional-spec.md`, `functional-design/rules.md`.
- Patrón de test replicado de `tests/test_market_bid_validation.py` y del fake DB
  de `conftest.py`.

## Assumptions & Open Questions

None.
