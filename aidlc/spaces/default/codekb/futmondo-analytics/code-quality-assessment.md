# Code Quality Assessment

## Cobertura de tests

- **Backend**: piso **BLOQUEANTE** `--cov-fail-under=27` (line-only, SIN
  `--cov-branch`) en `backend/pytest.ini` (`addopts = -ra --cov-fail-under=27`;
  cobertura real medida 27.52%, piso=27 por trinquete). Requiere `--cov=app` en la
  invocación — paridad `ci.yml` ↔ job `verify` de `fly-deploy.yml`. Sube solo por
  trinquete; nunca se relaja para pasar el gate.
- **Fakes in-memory (patrón de characterization)**: `backend/conftest.py`
  (raíz del runner, no en `tests/`) define `_FakeInMemoryDB` + `_FakeCursor`
  (SQLite `:memory:`, convierte `?`→`%s` espejo del `adapt_params` real), fixture
  `fake_db`, `clean_jwt_env`. Sin red, sin BD real, sin credenciales reales.
- **Suite**: `backend/tests/` (≈40+ `test_*.py`, muchos `*_characterization.py`).
  Tests que ya referencian `DataManagerV2` directamente (base de partida para la
  characterization del objetivo): `test_analytics_service.py`,
  `test_db_admin_guard.py`, `test_finance_characterization.py`.
- **Frontend**: umbrales por métrica en `angular.json` (`coverageThresholds`:
  statements 15 / branches 15 / functions 13 / lines 14), enforcement dentro de
  `ng test` (builder `@angular/build:unit-test` + Vitest). Prosa preservada.

## Linting

- **`ruff`** backend (`backend/ruff.toml`: `py312`, `line-length = 100`,
  `select = ["E","F","I"]`, `ignore = ["E501","E402"]`), modo **ADVISORY** escalonado.
  La deuda del god-file está **REGISTRADA en `per-file-ignores`**:
  `"app/services/data_manager_v2.py" = ["E722","F841","F401","I001"]` (E722/bare-except
  como deuda afirmada; saneo diferido a este refactor dedicado, NUNCA tocando/ampliando
  el fichero antes). Al descomponer, esa deuda se sanea en los ficheros **NUEVOS**;
  el original se vacía por extracción, no por reescritura in-place.
- Regla afirmada: **NUNCA** `ruff format` masivo sobre ficheros brownfield;
  formatear solo ficheros nuevos o de forma quirúrgica. La reviewer sólo corre
  `ruff check`.

## CI/CD

- **`.github/workflows/ci.yml`** (PR gate): gitleaks (bloqueante), `ruff check`
  (`ruff==0.16.9`, advisory), `pytest` con `--cov=app` (bloqueante, piso 27),
  `pip-audit==2.10.1` + allowlist-expiry (bloqueante), `npm audit --audit-level=high`
  (bloqueante). **`fly-deploy.yml`** replica el gate en el job `verify` antes de
  desplegar a Fly.io (`cdg`). Crons `daily-sync.yml`, `sofascore-sync.yml`.

## Calidad de documentación

- `README.md` extenso (es); `docs/` presente. Docstrings de módulo/clase ricos y en
  inglés en los contextos DDD (`analytics`/`assistant`/`sync`/`prizes` documentan
  BR/FR y el "único módulo con SQL"). El god-file tiene docstring de módulo +
  docstrings por método razonables.

## Deuda técnica (foco del scan: `data_manager_v2.py`)

- **God-file (señal principal)**: `data_manager_v2.py`, 3692 líneas / ~162–166 KB,
  una sola clase `DataManagerV2` con 57 métodos y 14 clusters de responsabilidad
  mezclados. SQL embebido masivo: 148 sentencias (34 `INSERT` / 75 `SELECT` / 14
  `UPDATE` / 15 `CREATE TABLE` / 24 `ON CONFLICT`). Es el **último god-file original
  sin descomponer**; `ruff` lo tiene en `per-file-ignores`. **NEVER ampliar/reescribir**.
- **Punto de corrupción — reemplazo de conjunto por DELETE**: `delete_orphan_players`
  (L549–595) ejecuta `DELETE FROM players ... WHERE player_id NOT IN (...) AND NOT
  EXISTS (...)` (rama Postgres `<> ALL(%s)`, rama SQLite `NOT IN (placeholders)`).
  Tiene guardia (`if not live_player_ids: return 0`) pero el borrado y los upserts
  previos NO comparten una transacción explícita a nivel del método: patrón de
  reemplazo de conjunto a elevar al **patrón atómico de referencia**
  (`prizes/team_prizes_writer.py`: upsert + DELETE stale en UNA transacción,
  rollback todo-o-nada). El `team_prizes_writer` documenta el anti-patrón histórico
  a NO replicar (DELETE separado cuyo fallo se tragaba con `except: logger.warning`
  dejando estado MIXTO).
- **Broad/bare excepts**: 18 `except Exception` + 5 `except:` desnudos en el
  god-file (L57, L68, L672, L1388, L1628, …). Deuda afirmada (E722 en
  per-file-ignores). A caracterizar y preservar comportamiento observable antes de
  extraer; no silenciar fallos nuevos.
- **`return None` como posible señal de fallo**: 16 `return None` en el god-file.
  Varios legítimos (`get_*_by_id` con tipo `Optional[...]`), pero debe distinguirse
  el `None` "no encontrado" (contrato legítimo) del `None` "fallo tragado" (deuda),
  conforme a la regla afirmada NEVER usar `return None` silencioso como señal de fallo.
- **SQL-en-router (deuda existente, NO ampliar)**: 17 de 23 routers con
  `cursor.execute` inline; entre los consumidores del objetivo
  `clausulable_players.py` (L75–79, L170–179), `player_finances.py` (L38),
  `user_stats.py`, `sync.py` mezclan SQL inline con el facade. A preservar/observar,
  no a tocar en esta etapa.
- **Acoplamiento amplio del objetivo**: `DataManagerV2` lo consumen 8 routers + los
  10 adapters de `sync/*` + adapters de `analytics`/`assistant` +
  `data_sync_service` + `data_initializer_v2` + `futmondo_service`. El refactor debe
  **preservar la superficie pública exacta** (constructor `skip_init=True`, nombres
  y firmas de los 57 métodos); romperla rompe las 4 oleadas DDD ya entregadas.
- **Divergencia de ramas SQL por engine**: métodos con `if self.db.db_type in
  ["postgresql","postgres"]: ... else: (SQLite)`. Producción es PostgreSQL/Neon
  exclusivamente; la rama SQLite sobrevive para el fake de tests. Characterization
  debe cubrir la rama productiva sin romper la ejecución contra `_FakeInMemoryDB`.
