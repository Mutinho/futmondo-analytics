# Instrucciones de Tests Unitarios — Oleada 1: extracción DDD de `analytics`

> Intent `260927-god-files-refactor`, scope `refactor`, test strategy **Minimal**, brownfield. Conversation language: Spanish.
>
> Estrategia Minimal + characterization-first (BR1.3): 1 test verificable por comportamiento observable de cada `get_*` que se mueve, congelado ANTES de mover. La suite existente debe seguir en verde (scope floor `refactor`). Sin `assert True` ni specs espejo.

## Framework y configuración

- **Framework:** `pytest` (ya instalado; sin dependencias nuevas — coste 0 €, BR5.1).
- **Ubicación:** `backend/tests/` (snake_case). Se **extiende el fichero existente** `backend/tests/test_analytics_service.py` — NO se crea un árbol de tests paralelo nuevo.
- **Config:** `backend/pytest.ini` — `testpaths = tests`, `pythonpath = .`, `addopts = -ra --cov-fail-under=27`. El piso de cobertura (27, line-only) es **bloqueante** y solo aplica cuando la medición está activa (`--cov=app`); **NUNCA se baja** para pasar (ratchet solo sube). Si aparece flapping, se arregla el test no-determinista.

## Cómo correr los tests de ESTA unidad (comando exacto, runnable)

Ejecutar SIEMPRE **desde `backend/`** (para que `from app...` resuelva, como hace el test existente):

```bash
# Comando unit-scoped exacto (esta unidad):
cd backend && python -m pytest tests/test_analytics_service.py -v
```

Con cobertura (como en CI), acotada a la app:

```bash
cd backend && python -m pytest tests/test_analytics_service.py --cov=app --cov-report=term-missing
```

> El comando está **acotado a esta unidad** por ruta de fichero exacta (`tests/test_analytics_service.py`), no un `pytest` de proyecto entero. Build and Test correrá el comando de cada unidad; un comando sin acotar reejecutaría toda la suite por unidad.

Verificación de regresión global (que la suite completa sigue verde — scope floor), como paso final:

```bash
cd backend && python -m pytest --cov=app
```

## Objetivo de cobertura

- **Estrategia Minimal:** 1 test por comportamiento observable de cada `get_*` movido; piso happy-path por componente (fachada, adaptador). ~5–8 tests nuevos (los 5 `get_*` sin cobertura + contrato del adaptador + delegación).
- **Piso de cobertura:** el `--cov-fail-under=27` de `pytest.ini` NO se toca; la extracción no debe reducir la cobertura de líneas de la suite estabilizada.

## Qué caracterizar (characterization-first — ANTES de mover)

Extender el `StubDM` autocontenido del fixture con los métodos de datos que falten y añadir 1 test por cada `get_*` sin cobertura directa, aseverando el **payload observable real**:

1. `get_championship_custom_classification` — asevera una clave/valor concreto de la clasificación resultante.
2. `get_championship_heatmap` — asevera la forma/valor de una celda del heatmap.
3. `get_user_consistency` — asevera la métrica de consistencia de un usuario.
4. `get_user_market_activity` — asevera una entrada de actividad de mercado (usa el helper interno de resolución).
5. `get_market_watchlist` — asevera un item de la watchlist (ejercita el 2º `SELECT` crudo, sobre `players`).

Estos tests corren en VERDE contra `analytics_service.py` ACTUAL (sin mover) para congelar el comportamiento, y se re-verifican tras la extracción (mismo payload — BR1.1).

## Test de contrato del adaptador (tras implementar la capa)

Con un doble in-memory de la fachada de BD siguiendo el patrón `db.get_connection()` de `test_team_prizes_atomic_replacement.py`:

- `DataManagerAnalyticsAdapter.fetch_all_teams()` devuelve exactamente la forma de fila que producía `SELECT team_id, user_id, team_name FROM teams` (BR1.2).
- `DataManagerAnalyticsAdapter.fetch_players_by_ids([...])` devuelve la forma de `SELECT player_id, name, real_team_id, value FROM players WHERE player_id IN (...)` (BR1.2).
- Los métodos delegados (`get_team_standings_history`, etc.) llaman al `DataManagerV2` subyacente y devuelven su resultado sin transformarlo.

## Mocking / stubbing

- **Sin red, sin BD real, sin credenciales/tokens reales** (gitleaks escanea los tests) — NFR3, FR3.3.
- Doble de datos: `StubDM` autocontenido (patrón existente) inyectado por el nuevo constructor `AnalyticsService(data=stub_port)` (BR2.6, testeable sin monkeypatch). No hay `conftest.py` en `backend/tests/`; no se depende de fixtures inexistentes.
- Doble de BD para el adaptador: objeto in-memory que honra `get_connection()`/`get_cursor()`/`adapt_params()` (mismo contrato que `_DbLike` en `team_prizes_writer.py`).

## Gestión de datos de test

- Datos de prueba inline en el `StubDM`/dobles (deterministas), como ya hace `test_analytics_service.py`. Sin fixtures de BD externas ni ficheros de datos.
