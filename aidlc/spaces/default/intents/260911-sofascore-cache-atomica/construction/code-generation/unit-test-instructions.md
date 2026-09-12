# Instrucciones de Test Unitario — Reemplazo transaccional de la caché de Sofascore

> Intent: `260911-sofascore-cache-atomica` · Scope: `bugfix` · Estrategia de
> test: Minimal · Metodología: `test-after` (Testing Contract del plan).

## Framework y configuración

- Framework: **pytest** (ya presente; `backend/pytest.ini`, `backend/conftest.py`).
- El runner se ejecuta DESDE `backend/` para que `from app...` resuelva
  (`pythonpath = .` en `pytest.ini`; patrón de `test_analytics_service.py` y
  `conftest.py`).
- **Sin BD real y sin credenciales reales**: se inyectan fakes de la conexión
  `db` (patrón `test_analytics_service.py`) y fakes del cliente Sofascore/futmondo.

## Cómo ejecutar los tests DE ESTE trabajo (comando unit-scoped)

Ejecutar exactamente (desde `backend/`):

```bash
python -m pytest tests/test_sofascore_sync_characterization.py -ra
```

Este comando es el runnable exigido antes del primer ciclo de test (en
`test-after`, el runner se verifica antes de escribir el primer test). NO se usa
un `pytest tests` global: eso reejecutaría toda la suite.

## Alcance y volumen (estrategia Minimal + suelo de scope bugfix)

Un test verificable por requisito al nivel más estrecho, más un happy-path por
componente, más la regresión dirigida del bug. Tests planificados en
`test_sofascore_sync_characterization.py`:

1. `should_apply_replacement`: repoblado OK ≥ umbral → `True`, razón `"ok"` (FR2.4).
2. `should_apply_replacement`: baneo → `False`, razón `"ip_ban"` (FR2.2).
3. `should_apply_replacement`: parcial < 50% → `False`, razón `"below_threshold"` (FR2.4).
4. Cliente Sofascore: respuesta 403 → lanza `SofascoreIPBanError` (FR2.1).
5. Cliente Sofascore: respuesta 404 → devuelve `None` (no baneo) (FR2.1).
6. Endpoint (regresión): repoblado exitoso → DELETE+INSERT en la MISMA conexión,
   caché reemplazada (FR1.1, FR1.2).
7. Endpoint (regresión): baneo a mitad → NO se ejecuta DELETE, caché intacta,
   `applied=False`, `reason="ip_ban"` (FR1.3, FR2.2, NFR1).
8. Endpoint (regresión): parcial < 50% → NO DELETE, caché intacta,
   `reason="below_threshold"` (FR1.3, FR2.4).

Total aproximado: 8 tests (dentro del rango Minimal 5-15).

## Objetivos de cobertura

Cobertura como métrica informativa (sin piso bloqueante en este scope, per
`pytest.ini`). Obligación real: la suite existente (6 ficheros de
caracterización) permanece en verde (NFR4) y el bug queda cubierto por la
regresión dirigida.

## Guía de mocking / stubbing

- Fake de `db`: objeto con `get_connection()` (context manager que registra si se
  llamó `DELETE`/INSERT), `get_cursor(conn)`, y `db_type = "sqlite"` para forzar
  la rama `executemany` (evita `psycopg2`). Se verifica el ORDEN: DELETE e INSERT
  ocurren en la misma conexión, o ninguno ocurre.
- Fake del cliente Sofascore: `search_player` / `get_player_full_info`
  parametrizables por jugador; uno de ellos lanza `SofascoreIPBanError` para el
  caso de baneo.
- Fake del cliente Futmondo (`get_user_futmondo_client`): devuelve standings y
  mercado mínimos con jugadores `computer=True`.
- Monkeypatch de `get_db`, `get_sofascore_client` y `get_user_futmondo_client` en
  el módulo del endpoint.

## Gestión de datos de prueba

Datos sintéticos en el propio test (nombres de jugador ficticios). Nunca se
copian datos ni tokens reales de Futmondo/Sofascore.
