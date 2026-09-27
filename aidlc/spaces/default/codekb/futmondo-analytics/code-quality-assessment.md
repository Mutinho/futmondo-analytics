# Evaluación de Calidad del Código — Futmondo Analytics

## Cobertura de tests

- **Backend**: `backend/tests/` (≈28 ficheros pytest, characterization-first).
  Fixtures fake in-memory en `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`
  SQLite `:memory:`, `clean_jwt_env`, `fake_db`) — sin red, sin BD real, sin
  credenciales. Cobertura `--cov=app` **observability-only** (SIN
  `cov-fail-under`).
- **Frontend**: Vitest (`@angular/build:unit-test` + `@vitest/coverage-v8`
  4.1.11 pin), con umbrales por métrica en `angular.json` (statements 15 /
  branches 15 / functions 13 / lines 14, en trinquete).
- **Asimetría conocida (deuda diferida afirmada)**: `ci.yml` mide `--cov=app`
  mientras `fly-deploy.yml` (job `verify`) corre `pytest -q` **sin `--cov`**.

## Linting / formato

- **Backend**: `ruff` (`backend/ruff.toml`, `select=["E","F","I"]`,
  `ignore=["E501","E402"]`; `E722`/bare-except re-habilitado advisory).
  **Sin `# noqa` en los 4 god files** (0). Advisory en CI.
- **Frontend**: ESLint (`eslint.config.js`) advisory; Prettier (`.prettierrc`).

## CI/CD

- `ci.yml` (PR→main): **gitleaks + pytest + ng test BLOQUEANTES**;
  ruff/ESLint/pip-audit/npm-audit advisory.
- `fly-deploy.yml` (push→main): `verify` (gitleaks+pytest+ng test) →
  deploy-backend → deploy-frontend → smoke `/health`.
- Crons Fly.io one-shot: `daily-sync.yml`, `sofascore-sync.yml`.

## Documentación

`README.md` + `docs/` (DEPLOY, ROLLBACK, PR-GATE, PROJECT_CONTEXT, varios
BACKLOG y planes históricos). Docstrings de módulo/clase presentes en los god
files; lógica interna escasamente documentada. Docstrings de caracterización
con trazas a FR/BR en los tests.

## Deuda técnica — foco del intent (FR13: descomposición de god files)

Los cuatro god files comparten el anti-patrón **SQL-en-servicio**. Anatomía,
seams de extracción y superficie pública por fichero en `code-structure.md`;
aquí, la señal de calidad y los riesgos de intervención.

### Señales de deuda por god file

- **`data_manager_v2.py`** (3692 líneas, 62 `def`, **94 `cursor.execute`
  inline**): `except: pass` ~29, 5 `except:` bare, 18 `except Exception`.
  `_init_database` (~330 líneas) mezcla DDL de todas las tablas. SQL crudo
  embebido en cada save/get. **Núcleo del acoplamiento** (8 routers + sync +
  analytics vía `self.dm`) y de **mayor riesgo**: cobertura directa ~cero.
- **`data_sync_service.py`** (1955 líneas): 28 `except Exception`, ~34
  `except:`-tipo. Funciones enormes: `sync_prizes` (303),
  `sync_player_performance` (223), `sync_dream_teams_mvps` (161).
- **`assistant_service.py`** (1158 líneas, **42 `cursor.execute` inline**):
  SQL-en-servicio dentro de los `_ctx_*`; guardrails/factual/tracker sin test.
- **`analytics_service.py`** (828 líneas, solo **2 `cursor.execute`**): el más
  limpio; ya delega en `self.dm`.

### Estado global / config module-level (acoplamiento oculto)

`data_sync_service` toma `CHAMPIONSHIP_ID`/`LEAGUE_ID`/`FUTMONDO_EMAIL/PASSWORD`
de `app.core.config`; assistant toma `GEMINI_API_KEY`/`GROQ_API_KEY` y límites
module-level; `_resolve_real_team_name` importa `LALIGA_TEAM_NAMES` de
constants dentro del método. Considerar inyección al extraer, **sin cambiar el
comportamiento observable**.

### Caché mutable per-instance

`analytics_service._team_cache`/`_player_cache`; `data_manager_v2.cache_duration`.

### Cobertura de tests por god file (estado previo a la extracción)

| God file | Cobertura directa | Notas |
|----------|-------------------|-------|
| `analytics_service.py` | **Buena** (6/10 `get_*`) | Seam de inyección `self.dm` ya existe; fake `DataManagerV2` por lambdas en `test_analytics_service.py`. **Menor riesgo.** |
| `data_sync_service.py` | **Parcial de efecto** | Contrato de fallo (DEGRADED/fatal) y `sync_prizes`/reemplazo atómico congelados; resto de `sync_*` sin caracterización directa. |
| `data_manager_v2.py` | **~cero** (solo indirecta) | God file más expuesto y menos protegido. |
| `assistant_service.py` | **cero** | Guardrails/factual/context/tracker sin test. |

### Riesgos / restricciones de la intervención (reglas afirmadas)

- **Characterization-first obligatorio** (mandato afirmado del proyecto) antes
  de mover código en `data_manager_v2.py` y `assistant_service.py` (cobertura
  directa ~cero/cero). Reutilizables: fake `DataManagerV2` por lambdas
  (`test_analytics_service.py`) y fakes in-memory de `conftest.py`
  (`_FakeInMemoryDB`) para caracterizar métodos con SQL antes de extraer un
  repositorio; la caracterización de efecto de sync (DEGRADED/fatal, prizes
  atómico) congela el contrato de fallo antes de trocear el sync.
- **Preservar la superficie pública**: `DataManagerV2.*` (8 routers),
  `DataSyncService.sync_*`/`sync_all`, `get_assistant_service()`/`ask()`,
  `AnalyticsService.get_*`. Cualquier extracción mantiene fachada delgada que
  delega, o los routers rompen.
- **NO sanear los `except: pass` del DM** (~29) ni los de `photo_service.py`:
  **deuda registrada FUERA de alcance** por regla afirmada — se preserva
  comportamiento, no se limpia oportunistamente al extraer.
- **NO ampliar los god files ni el patrón SQL-en-router** (regla afirmada); el
  código nuevo va tras capa/función estrecha testeable.
- **NO `ruff format` masivo** sobre estos ficheros brownfield ya modificados
  (infla diffs, expone avisos preexistentes, invalida el pase de revisión en
  vuelo); formatear solo los ficheros nuevos o quirúrgicamente.
- **Patrón de extracción de referencia**: paquete `prizes/` +
  `replace_team_prizes` (capa estrecha testeable + writer transaccional
  atómico) — replicable por dominio.

## Deuda técnica previa (intent 260925 — preservada)

### FR14 — Ramas de BD muertas SQLite/Turso (producción solo Neon)

Dead-path operativo completo y aislado:
- `config.py`: resolución en cascada `DATABASE_URL` → `TURSO_DATABASE_URL` →
  fallback `sqlite`; expone `TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`,
  `POSTGRES_*` manuales. Comentarios "Railway" obsoletos.
- `db_connection.py`: `_init_turso()` (libsql embedded replica),
  `_TursoCursorWrapper`, `_init_sqlite()`, y ramas `turso`/`sqlite` en
  `get_connection`/`adapt_sql`/`adapt_params`/`get_last_insert_id`/`sync`.
- `requirements.txt`: `libsql-experimental==0.0.55` (no compila fuera de 3.12;
  no lo ejercitan los tests).
- `nixpacks.toml`: config Railway/Nixpacks huérfana (`python311` incoherente).
- `scripts/migrate_to_turso.py` (14 KB) y `migrate_data_to_turso.py` (5 KB):
  sin uso en el flujo Neon.
- `entrypoint.sh`: arranca `cron` + uvicorn duplicando el `CMD` del Dockerfile;
  no referenciado por Dockerfile ni `fly.toml` (candidato a residuo).

**Riesgos / characterization-first** (contexto preservado, no re-verificado
en este run — ver Scope of Analysis, degradado a shallow):
- Caracterizar `db_connection.py` ANTES de tocarlo; no alterar el contrato del
  cursor en PostgreSQL.
- El fake de tests está separado de la rama SQLite de producción
  (`test_db_engine_characterization.py` y `fake_db` usan `db_type="sqlite"`
  deliberadamente).

### FR14 — IDs hardcodeados

`CHAMPIONSHIP_ID` y `LEAGUE_ID` tienen defaults hardcodeados en **`config.py`**
(NO en `constants.py`). Residuo de la etapa mono-usuario. `constants.py` sí
contiene `LALIGA_TEAMS` (fallback legítimo, no residuo).

### FR15 — Doble montaje de `matchdays`

En `main.py`, el mismo router se incluye dos veces
(`prefix="/api/v1/matchdays"` y `prefix="/v1/matchdays"`). El segundo puede
tener clientes legacy — verificar consumo antes de retirarlo.

### FR15 — Artefactos basura versionados

- `*.jpg:Zone.Identifier`, imágenes sueltas (`42874.jpg`), `stitch_*/`
  (mockups), `angular-app/node_modules.old-*/`, `backend/futmondo_data.db`
  (verificar tracking histórico). Detalle preservado del run previo.

### Deuda fuera de alcance (registrada, transversal)

- Dependencias backend con rango abierto (deuda de pinning).
- Comentarios "Railway"/"Turso" obsoletos dispersos.
