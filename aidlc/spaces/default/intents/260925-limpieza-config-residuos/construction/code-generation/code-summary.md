# Code Summary — Limpieza de configuración y residuos (FR14 + FR15)

Intent `260925-limpieza-config-residuos` · scope `refactor` (Minimal) · brownfield ·
zero-Unit · test-after / characterization-first. Poda sin lógica nueva, coste 0 €.

## Cambios por bloque

### FR14.1 — Retirada dead-path SQLite/Turso + huérfanos
- `backend/app/services/db_connection.py`: reescrito al motor único PostgreSQL/Neon.
  Eliminados `_init_turso`, `_init_sqlite`, `_TursoCursorWrapper`, `_convert_params`
  y las ramas `turso`/`sqlite` de `get_connection`/`adapt_sql`/`adapt_params`/
  `get_last_insert_id`/`sync`. `DBConnection.__init__` resuelve `DATABASE_URL`
  directamente (en lockstep con config.py — R-03); `_init_postgresql` pasa a firma
  `(database_url)`. `sync()` queda como no-op para compatibilidad de API.
- `backend/app/core/config.py`: eliminada la cascada `DATABASE_URL → TURSO_* →
  sqlite` y las vars `TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`, `DATABASE_TYPE`,
  `POSTGRES_*`. `DATABASE_PATH` **conservada** y marcada como ruta de caché local
  (la consumen `photo_service.py` y el god-file `data_manager_v2.py`; su limpieza es
  deuda registrada — R-02).
- `backend/requirements.txt`: eliminado `libsql-experimental==0.0.55` (dead dep).
- Huérfanos borrados (sin refs vivas): `backend/nixpacks.toml`,
  `backend/entrypoint.sh`, `backend/scripts/migrate_to_turso.py`,
  `backend/scripts/migrate_data_to_turso.py`.

### FR14.2 — IDs hardcodeados
- `backend/app/core/config.py`: `CHAMPIONSHIP_ID`/`LEAGUE_ID` pierden su default
  literal legacy → `os.getenv(..., "")`. El flujo multi-usuario usa el
  championship_id del usuario logado por request; un valor sin configurar es vacío
  explícito, nunca el ID hardcodeado retirado.

### FR15.1 — Unificar montaje matchdays
- `backend/app/main.py`: eliminado el montaje duplicado no canónico
  `prefix="/v1/matchdays"`; se conserva solo `/api/v1/matchdays`. Verificado que
  ningún cliente (angular-app/proxy/.github) consumía el prefijo retirado.

### FR15.2 — Residuos + .gitignore
- `git rm` de 6 residuos trackeados: `30825.jpg:Zone.Identifier`, `42874.jpg`,
  `42874.jpg:Zone.Identifier`, `IMG_9904.PNG:Zone.Identifier`,
  `stitch_angular_material_card_redesign/` (3), `stitch_team_card_dashboard/` (3).
  Los dos directorios `stitch_*` son propiedad de `root` en el working tree, así que
  se desindexaron con `git rm --cached -r` (dejan de estar trackeados; los ficheros
  físicos root-owned quedan en disco y ahora los cubre el nuevo `.gitignore`).
- `.gitignore`: añadidas reglas `*:Zone.Identifier` y `stitch_*/`.
- `node_modules.old-*/` y `*.db`: ya no trackeados → no-op documentado (FR15.2.3).

## Tests (test-after, characterization-first)
- `backend/tests/test_db_engine_characterization.py` (modificado): congela el
  contrato del path PostgreSQL/Neon (`adapt_params`, `adapt_sql`, `get_cursor`,
  `get_last_insert_id`); retiradas las aserciones turso/sqlite-producción en
  lockstep con la poda (Step 3/3bis, R-01).
- `backend/tests/test_error_layer_hardening.py` (modificado): actualizado al motor
  único (db_type postgresql, nueva firma `_init_postgresql`); semántica
  recuperable/fatal (rollback+raise, degrade de pool) preservada.
- `backend/tests/test_config_hardcoded_ids.py` (nuevo): asevera ausencia de los IDs
  legacy (por valor y en el source) y fallback a vacío.
- `backend/tests/test_matchdays_mount.py` (nuevo): asevera 401 en la ruta canónica
  (montada, auth-gated) y 404 en el prefijo retirado.

## Verificación
- Suite backend completa: **208 passed, 3 xfailed** (baseline previa: 203 passed,
  3 xfailed). Sin regresiones.
- `ruff check` sobre ficheros tocados: solo hallazgos **preexistentes** (I001, F401,
  F841 heredados verbatim del código original); no se aplicó `--fix` ni `ruff format`
  para no inflar el diff ni invalidar el binding de la reviewer (regla afirmada).
  Los tests nuevos no generan hallazgos.
- Import smoke del app: OK, sin `ImportError`.

## Deuda registrada
- `DATABASE_PATH` en config.py (limpieza ligada al refactor de god-files).
- Comentario obsoleto `_TursoCursorWrapper` en `data_manager_v2.py:519` (god-file, no
  se toca por C2; el código es duck-typed y sigue correcto).
- Asimetría de la señal `--cov` entre `ci.yml` y el job `verify` de `fly-deploy.yml`
  (fuera de alcance por Testing Contract).

## Nota de commits
No se ejecutó `git commit` ni `git push` (el commit lo realiza el humano al cierre
del intent). Los cambios están en el working tree / índice de la rama
`chore/limpieza-config-residuos`.
