# Escaneo del desarrollador — Reverse Engineering (eslabón 1, pipeline)

Intent: `260912-analytics-tests-fix` (Brownfield · scope `bugfix` · depth Minimal).
Objetivo: dejar en verde 3 tests preexistentes de `backend/tests/test_analytics_service.py` para desbloquear el gate de CI de `.github/workflows/fly-deploy.yml`. Este documento es el handoff durable que el arquitecto sintetizará; NO contiene los 9 artefactos del codekb.

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply**:
  - backend/app/services/analytics_service.py
  - backend/tests/test_analytics_service.py
  - backend/conftest.py
  - backend/pytest.ini
  - backend/ruff.toml
- **Skimmed only**:
  - backend/app/services/ (data_manager_v2.py, db_connection.py, y demás colaboradores — vistos a nivel de contrato/firma, no leídos en profundidad; quedan fuera del área del intent)
  - backend/tests/ (los otros ficheros `test_*_characterization.py` — a nivel de directorio, para entender que el resto de la suite debe permanecer en verde)
  - .github/workflows/fly-deploy.yml (referenciado por el objetivo del gate; no leído en detalle)

> La cobertura PROFUNDA queda contenida dentro de `backend/app/services/` y `backend/tests/`, conforme a la amplitud ENFOCADA del snapshot. No se ha ampliado fuera de esas rutas.

### Packages Found
- app.services — Python — servicios de dominio (analítica, sync, clientes externos, gestión de datos)
- app.services.analytics_service — Python — clase `AnalyticsService`, objeto bajo test
- tests — Python — suite de caracterización (red de seguridad), sin BD real (fakes por fixture)

### Build System
- **Type**: pytest (test runner del backend); npm en la raíz para el monorepo (frontend)
- **Config Files**: backend/pytest.ini, backend/conftest.py, backend/ruff.toml, backend/requirements.txt
- **Build Dependencies**: `pytest` es la dependencia de test; el runner se ejecuta DESDE `backend/` (`pythonpath = .`) para que `from app...` resuelva.

### APIs Discovered
- Consumidores de `AnalyticsService` — backend/app/api/v1 (endpoints `/api/v1/analytics/*`) — no relevantes para el arreglo de los tests (los tests instancian el servicio directamente con un `StubDM`). Skimmed only.

### Frameworks & Libraries
- pytest — (versión resuelta por requirements.txt) — framework de test + `monkeypatch`
- ruff — lint + formato (Black-style, `quote-style = "double"`), modo TOLERANTE/advisory en esta fase

### Test Coverage
- **Test Directories**: backend/tests/
- **Test Frameworks**: pytest (fixtures + `monkeypatch`)
- **Coverage Config**: presente pero informativa (pytest.ini: cobertura sin piso bloqueante todavía; `--cov=app` opcional)

### Contrato/estructura de `AnalyticsService` (foco del intent)

`__init__` real (analytics_service.py:12-17):
```
self.dm = DataManagerV2()
self._team_cache: Dict[str, Dict[str, Dict]] = {}
self._player_cache: Dict[str, Dict] = {}
```

- El atributo `_team_cache` SÍ existe en el `__init__` real. Lo mismo `_player_cache`. (El enunciado del intent "AnalyticsService no tiene atributo _team_cache" describe el SÍNTOMA en tiempo de test, no el estado del código fuente.)
- El fixture `analytics_service` de `test_analytics_service.py` hace:
  ```
  def fake_init(self):
      self.dm = stub_dm
  monkeypatch.setattr(AnalyticsService, "__init__", fake_init)
  ```
  Es decir, sustituye `__init__` por uno que SOLO asigna `self.dm` y NO inicializa `_team_cache` ni `_player_cache`.

Métodos afectados y por qué fallan bajo el fixture:

- `test_championship_trends` → `get_championship_trends` (l.124) → `_safe_team_info` (l.18): lee `self._player_cache.get("__teams_loaded__")` (l.23) y escribe en `self._team_cache` (l.29). Con el `fake_init`, ambos atributos faltan → `AttributeError`.
- `test_clause_network` → `get_clause_network` (l.668) → `_resolve_team` (l.94) → `_build_team_lookup` (l.55): lee/escribe `self._team_cache` (l.57, l.92). Con el `fake_init`, falta el atributo → `AttributeError`.
- `test_player_value_trend` → `get_player_value_trend` (l.437): dos causas.
  1. El servicio emite la clave `last_transaction_price` (l.474), NUNCA `latest_price`; el test hace `assert result["players"][0]["latest_price"] == 1000000`. La clave `latest_price` no aparece en toda `backend/app/` → `KeyError`.
  2. El `StubDM.get_clausulable_player_stats` no incluye `player_name`, por lo que el método llama a `_safe_player_info` (l.40), que lee `self._player_cache` → `AttributeError` (mismo origen que arriba) si no se supera antes el `KeyError`.

Contrato observado esperado por el test para `get_player_value_trend`: el stub de `get_transactions_raw` devuelve una transacción con `price: 1000000`; el test espera que ese valor aparezca como `latest_price` (equivale al actual `last_transaction_price = transactions_prices[-1]`, l.462/474).

### Code Quality Indicators
- **Linting**: ruff (backend/ruff.toml), `select = ["E","F","I"]`, `ignore = ["E501","E402","E722"]`, per-file-ignores para `tests/**` y `conftest.py`; fase advisory (no bloqueante).
- **CI/CD**: .github/workflows/fly-deploy.yml — el gate a desbloquear; ejecuta la suite de pytest (ruff en modo advisory/continue-on-error en esta fase).
- **Documentation**: docstrings en `conftest.py` y en la clase; buena trazabilidad de intención en comentarios.

### Technical Debt Signals
- **Contrato de test acoplado a atributos privados de instancia**: al monkeypatchear `__init__` completo, el fixture asume implícitamente que los métodos públicos no dependen de estado inicializado en `__init__` (`_team_cache`, `_player_cache`). El servicio SÍ depende de ellos → fragilidad estructural (analytics_service.py:16-17 vs test fixture).
- **Divergencia de nombre de clave de salida**: `last_transaction_price` (servicio) vs `latest_price` (test). Contrato de datos no unificado; ninguna fuente única de verdad para el shape del dict de salida.
- **`_safe_team_info` mezcla dos caches** (usa `_player_cache["__teams_loaded__"]` como flag de carga de EQUIPOS, l.23/32): naming confuso; deuda menor pero relevante para entender el fallo cruzado.
- **try/except amplio en `_build_team_lookup`** (l.66-68) enmascara que `StubDM` no implementa `get_all_users_with_points`; el fallo real emerge en el acceso a `_team_cache`, no en el método del dm.

## Handoff Summary
- **Intent-relevant finding**: Los 3 fallos tienen dos raíces, no una. (a) El fixture `fake_init` de `test_analytics_service.py` sustituye `__init__` y omite `self._team_cache` y `self._player_cache` (existentes en analytics_service.py:16-17), provocando `AttributeError` en `get_championship_trends` (vía `_safe_team_info`) y `get_clause_network` (vía `_resolve_team`/`_build_team_lookup`). (b) `get_player_value_trend` (analytics_service.py:437) emite la clave `last_transaction_price` (l.474), mientras el test exige `latest_price`; `latest_price` no existe en `backend/app/`. Además ese método también toca `_player_cache` vía `_safe_player_info`.
- **Risks / follow-up**:
  - El punto de arreglo es una DECISIÓN del arquitecto: (1) inicializar `_team_cache`/`_player_cache` en el `fake_init` del test y alinear la clave (`latest_price` vs `last_transaction_price`), o (2) tocar el servicio (p. ej. añadir/renombrar la clave `latest_price` y/o hacer los métodos robustos ante caches ausentes). La restricción dura: NO romper los otros 3 tests del fichero (`test_player_form`, `test_opportunity_streaks`, `test_matchday_projections`) ni el resto de la suite de caracterización.
  - Testing Posture del scope `bugfix`: regresión dirigida al bug + suite existente en verde. Cualquier cambio de nombre de clave en el servicio afectaría a los consumidores `/api/v1/analytics/*` (skimmed only) — verificar antes de renombrar en el servicio.
  - No se pudo EJECUTAR pytest en este entorno: `python`/`python3` presentes pero sin módulo `pytest` instalado; por la regla de coste 0€ y scope Minimal no se instalaron dependencias globales. El diagnóstico es estático y concluyente; la ejecución de la suite se hará en el entorno de build (stage `build-and-test`).
