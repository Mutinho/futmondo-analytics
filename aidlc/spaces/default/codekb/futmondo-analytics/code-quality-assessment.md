# Evaluación de Calidad del Código — Futmondo Analytics

> Reverse-engineering. Escaneo previo FULL preservado; rerun FOCUSED sobre
> `backend/app/services/` y `backend/tests/`. Cobertura de tests, linting, CI/CD,
> calidad de documentación y deuda técnica, según la evidencia del scan y el
> código.

## Cobertura de tests

- **Backend**: `backend/tests/` con 6 ficheros de **caracterización** (congelan el
  comportamiento actual, metodología `custom` characterization-first, ver
  `conftest.py`): `test_analytics_service.py` (con fakes de `DataManager`),
  `test_auth_characterization.py`, `test_db_admin_guard.py`, `test_jwt_startup.py`,
  `test_db_engine_characterization.py`, `test_finance_characterization.py`.
  `--cov=app` disponible pero **sin piso bloqueante** (`pytest.ini`).
- **Frontend**: **cobertura efectivamente ~0**. Solo existe
  `angular-app/src/app/core/interceptors/auth.interceptor.spec.ts` (1 test).
  `angular.json` fija `skipTests: true` en todos los schematics → los componentes
  y servicios nuevos nacen sin test. `karma-coverage` está configurado (report
  html + text-summary) pero sin umbral.
- **Asimetría**: `ci.yml` marca `ng test` como bloqueante, pero el gate pasa con
  cobertura casi nula porque apenas hay specs.

## Hallazgo del intent — 3 tests rojos en `test_analytics_service.py` (foco del rerun)

Objetivo del intent `260912-analytics-tests-fix`: dejar en verde
`test_championship_trends`, `test_clause_network` y `test_player_value_trend`
para desbloquear el gate de CI de `fly-deploy.yml`, sin romper el resto de la
suite. **Dos raíces distintas**:

1. **Caches de instancia ausentes bajo la fixture** (`AttributeError`). El
   fixture `analytics_service` monkeypatchea `AnalyticsService.__init__` con:
   ```
   def fake_init(self):
       self.dm = stub_dm
   ```
   que NO inicializa `self._team_cache` ni `self._player_cache` (presentes en el
   `__init__` real, analytics_service.py:16-17). Los métodos afectados:
   - `test_championship_trends` → `get_championship_trends` (l.124) →
     `_safe_team_info` (l.18): lee `_player_cache["__teams_loaded__"]` (l.23) y
     escribe en `_team_cache` (l.29) → `AttributeError`.
   - `test_clause_network` → `get_clause_network` (l.668) → `_resolve_team`
     (l.94) → `_build_team_lookup` (l.55): lee/escribe `_team_cache` (l.57, l.92)
     → `AttributeError`.
   - `test_player_value_trend` → `get_player_value_trend` (l.437) también toca
     `_player_cache` vía `_safe_player_info` (l.40).
2. **Divergencia de nombre de clave de salida** (`KeyError`). `get_player_value_trend`
   emite `last_transaction_price` (l.474) mientras el test hace
   `assert result["players"][0]["latest_price"] == 1000000`. La cadena
   `latest_price` NO aparece en toda `backend/app/`. El valor esperado (1000000)
   equivale al actual `last_transaction_price = transactions_prices[-1]`
   (l.462/474), alimentado por el stub `get_transactions_raw` con `price: 1000000`.

### Punto de arreglo sugerido (ver ADR-RE-001 en `architecture.md`)

- **Recomendado (Alternativa A — arreglar el test, menor blast radius)**:
  1. En el `fake_init` del fixture, inicializar también
     `self._team_cache = {}` y `self._player_cache = {}` (replicar el estado del
     `__init__` real sin instanciar `DataManagerV2`).
  2. Alinear la aserción de clave del test con la salida real del servicio:
     usar `last_transaction_price` en `test_player_value_trend` (o mapear el
     valor esperado a esa clave). NO renombrar en el servicio bajo scope
     `bugfix`.
- **Alternativa B (tocar el servicio)**: añadir/renombrar la clave `latest_price`
  y/o endurecer los helpers ante caches ausentes. **Riesgo**: altera el contrato
  de salida consumido por `/api/v1/analytics/*` (skimmed only) — verificar esos
  consumidores antes de renombrar. Rechazada por defecto para `bugfix`.
- **Restricción dura**: no romper `test_player_form`, `test_opportunity_streaks`
  ni `test_matchday_projections` ni el resto de la suite de caracterización;
  postura de test del scope `bugfix` = regresión dirigida + suite existente en
  verde.

## Linting y formato

- **Backend**: ruff (`ruff.toml`, `select=["E","F","I"]`, con `E501/E402/E722`
  ignorados; per-file-ignores para `tests/**` y `conftest.py`). Modo **ADVISORY**
  en CI. Formato con ruff format (`quote-style = "double"`).
- **Frontend**: ESLint (`eslint.config.js`), `ng lint` **ADVISORY** en CI. Formato
  con Prettier (`.prettierrc`).

## CI/CD

Cuatro workflows GitHub Actions:

| Workflow | Trigger | Gates |
|----------|---------|-------|
| `ci.yml` | PR → main | **BLOQUEANTE**: gitleaks, pytest, `ng test`. **ADVISORY**: ruff, ESLint, pip-audit, npm audit (decisión escalonada R-05). |
| `fly-deploy.yml` | push → main | job `verify` (pytest + ng test) → deploy backend → deploy frontend → smoke test `/health`. **Gate a desbloquear por este intent.** |
| `daily-sync.yml` | cron | job one-shot en Fly con polling de estado y verificación de exit code. |
| `sofascore-sync.yml` | cron | one-shot; trata exit code 2 (baneo IP Sofascore) explícitamente. |

Procesos documentados en `docs/PR-GATE.md` y `docs/ROLLBACK.md`.

## Calidad de la documentación

- `README.md` completo (arquitectura, stack, deploy, endpoints).
- `docs/` rico: `PROJECT_CONTEXT`, planes de migración, `DEPLOY`, `ROLLBACK`,
  `PR-GATE`.
- Comentarios en castellano con referencias a NFRs/FRs (endurecimiento previo ya
  aplicado). Docstrings presentes en `conftest.py` y en la clase `AnalyticsService`.

## Deuda técnica

- **Contrato de test acoplado a atributos privados de instancia** (foco del rerun):
  el `fake_init` de `test_analytics_service.py` sustituye `__init__` completo y
  asume que los métodos públicos no dependen de `_team_cache`/`_player_cache`;
  sí dependen → fragilidad estructural (analytics_service.py:16-17 vs fixture).
- **Divergencia de nombre de clave de salida**: `last_transaction_price`
  (servicio) vs `latest_price` (test); no hay fuente única de verdad para el
  shape del dict de salida de `AnalyticsService`.
- **`_safe_team_info` mezcla dos caches**: usa `_player_cache["__teams_loaded__"]`
  como flag de carga de EQUIPOS (l.23/32); naming confuso.
- **`try/except` amplio en `_build_team_lookup`** (l.66-68) enmascara que
  `StubDM` no implementa `get_all_users_with_points`; el fallo real emerge en el
  acceso a `_team_cache`, no en el método del dm.
- **God files**: `data_manager_v2.py` (166 KB / ~4.700 líneas),
  `data_sync_service.py` (84 KB), `assistant_service.py` (51 KB),
  `analytics_service.py` (34 KB). Superan con creces el objetivo de <300 líneas.
- **Manejo de errores demasiado amplio**: 159 `except Exception` y 6 `except:`
  desnudos en `backend/app`; varios `except Exception: pass` silenciosos
  (`token_store.init_auth_tables`, `_ensure_conversations_table` en `assistant.py`,
  `_auto_detect_championships` en `auth/routes.py`).
- **Estado no durable en memoria**: `TaskManager` y `SessionStore` son singletons
  in-memory; un reinicio Fly pierde tareas de sync y sesiones → 403 "sesión
  expirada". `SessionStore` guarda email+password en claro en memoria.
- **Config heredada / entornos mezclados**: `config.py` con 3 backends de BD
  (SQLite/Turso/PostgreSQL) y ramas muertas; `nixpacks.toml` (Railway) y
  `migrate_to_turso.py` residuales; `constants.py` con `CHAMPIONSHIP_ID`/`LEAGUE_ID`
  hardcodeados.
- **`docker-compose.yml` fija `SSL_VERIFY=0`** en backend (local) — confirmar que
  no se propaga a producción.
- **Bug potencial**: `token_store.is_refresh_token_valid` con ternario ambiguo
  (naive/aware datetimes).
- **Doble montaje de rutas**: `matchdays` bajo `/api/v1/matchdays` y `/v1/matchdays`.
- **Validación de entrada**: `market.py::place_bid` acepta `price` sin validar
  rango/positividad en backend (solo el frontend valida min/max).

## Postura de seguridad (positivo)

Endurecimiento presente y correcto: JWT fail-fast (`config.py::resolve_jwt_secret`),
endpoints destructivos tras `ENABLE_DB_ADMIN` (404 por defecto), refresh HttpOnly,
CORS con whitelist, gitleaks bloqueante en CI.

## Nota de ejecución del rerun

No se pudo EJECUTAR pytest en este entorno (`python`/`python3` presentes pero sin
módulo `pytest`; regla coste 0€, scope Minimal → no se instalaron dependencias
globales). El diagnóstico de los 3 fallos es estático y concluyente; la ejecución
de la suite se realizará en el entorno de build (stage `build-and-test`).
