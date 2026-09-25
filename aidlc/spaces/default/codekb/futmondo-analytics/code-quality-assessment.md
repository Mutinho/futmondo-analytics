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
  Este intent no la cierra.

## Linting / formato

- **Backend**: `ruff` (`backend/ruff.toml`, `select=["E","F","I"]`,
  `ignore=["E501","E402"]`; `E722` ya re-habilitado como advisory), advisory
  en CI.
- **Frontend**: ESLint (`eslint.config.js`) advisory; Prettier (`.prettierrc`).

## CI/CD

- `ci.yml` (PR→main): **gitleaks + pytest + ng test BLOQUEANTES**;
  ruff/ESLint/pip-audit/npm-audit advisory.
- `fly-deploy.yml` (push→main): `verify` (gitleaks+pytest+ng test) →
  deploy-backend → deploy-frontend → smoke `/health`.
- Crons Fly.io one-shot: `daily-sync.yml`, `sofascore-sync.yml`.

## Documentación

`README.md` + `docs/` (DEPLOY, ROLLBACK, PR-GATE, PROJECT_CONTEXT, varios
BACKLOG y planes históricos). Docstrings de caracterización con trazas a FR/BR
en los tests. Calidad razonable; deuda: docs/planes históricos acumulados.

## Deuda técnica — foco del intent (FR14/FR15)

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

**Riesgos / characterization-first**:
- Caracterizar `db_connection.py` ANTES de tocarlo: verificar que ningún
  llamador dependa de `adapt_params`/`adapt_sql` con `?` (SQLite) bajo Neon;
  no alterar el contrato del cursor en PostgreSQL.
- **El fake de tests está separado de la rama SQLite de producción**:
  `test_db_engine_characterization.py` y `fake_db` usan `db_type="sqlite"`
  deliberadamente (fake in-memory, NO la rama de producción). Retirar SQLite
  del código de producción NO debe romper el doble de test — confirmar la
  separación antes de borrar.
- Confirmar que no queda import vivo tras eliminar `_init_turso` al retirar
  `libsql-experimental` (coherente con coste 0 € y learning afirmado).

### FR14 — IDs hardcodeados

`CHAMPIONSHIP_ID` y `LEAGUE_ID` tienen defaults hardcodeados en
**`config.py`** (NO en `constants.py`; el enunciado FR14 nombra el fichero
equivocado). Residuo de la etapa mono-usuario en una app hoy multi-usuario/
multi-campeonato. `constants.py` sí contiene `LALIGA_TEAMS` (fallback
legítimo, no residuo).

### FR15 — Doble montaje de `matchdays`

En `main.py`, el mismo router se incluye dos veces
(`prefix="/api/v1/matchdays"` y `prefix="/v1/matchdays"`, comentario "avoid
redirect loops"). **Riesgo**: el segundo prefijo `/v1/matchdays` puede tener
**clientes legacy** — verificar consumo en frontend/Sofascore antes de
retirarlo.

### FR15 — Artefactos basura versionados

- `*.jpg:Zone.Identifier` (marcadores NTFS Windows): `42874.jpg:Zone.Identifier`,
  `30825.jpg:Zone.Identifier`, `IMG_9904.PNG:Zone.Identifier`; imágenes
  sueltas (`42874.jpg` ≈580 KB). **NO cubiertos por `.gitignore`** → requieren
  `git rm` explícito.
- Directorios `stitch_team_card_dashboard/` y
  `stitch_angular_material_card_redesign/` (mockups, ≈370 KB) — **no en
  `.gitignore`**.
- `angular-app/node_modules.old-1789382239/` (`.gitignore` cubre
  `node_modules.old-*/` — verificar si está trackeado históricamente).
- `backend/futmondo_data.db` (`.gitignore` ignora `*.db` — verificar tracking
  histórico).

### Deuda fuera de alcance (registrada)

- God-files: `data_manager_v2.py` ~166 KB, `data_sync_service.py` ~84 KB,
  `assistant_service.py` ~51 KB; patrón SQL-en-router. Regla afirmada: NO
  ampliar.
- Dependencias backend con rango abierto (deuda de pinning).
- Comentarios "Railway"/"Turso" obsoletos dispersos en
  `config.py`/`db_connection.py`/`docker-compose.yml`.
