# Code Quality Assessment — futmondo-analytics

## Test Coverage

- **Backend**: `backend/tests/` (~55 archivos, mayoría `*_characterization.py`:
  prizes, `sync_*`, `data_manager_*` por responsabilidad, auth, finance, durable
  session/task, integration errors, jwt startup). Fakes in-memory en `conftest.py`
  (`_FakeInMemoryDB`/`_FakeCursor` sobre SQLite `:memory:`, `clean_jwt_env`,
  `fake_db`) — sin red, sin BD real, sin credenciales/tokens reales.
  - **Piso bloqueante** `--cov-fail-under=27` en `pytest.ini` (line-only, sin
    `--cov-branch`; cobertura real medida ~27.52 %). Ratchet: sólo sube.
- **Frontend**: specs junto al código (`*.spec.ts` en `core/services`, `core/guards`,
  `core/interceptors`, `features/market`). `calculator` **no tiene spec**.
  - Umbrales por métrica en `angular.json > test.coverageThresholds`: statements 19 /
    branches 19 / functions 17 / lines 18 (ratchet manual, sólo sube).

## Linting

- **ruff** backend (`backend/ruff.toml`, `py312`, `line-length=100`,
  `select=["E","F","I"]`, `ignore=["E501","E402"]`, `per-file-ignores` para
  god-files/adaptadores/tests).
- **ESLint** frontend: config presente (`eslint.config.js`) pero **advisory** y sus
  devDependencies **no instaladas** (deuda diferida). `npx ng lint` tolerante a la
  ausencia. Prettier configurado (`.prettierrc`).
- **gitleaks** (escaneo de secretos), **pip-audit**, **npm audit** — ver CI/CD.

## CI/CD

- **`.github/workflows/ci.yml`** — gate en `pull_request → main`. Estado ACTUAL del
  código (ya endurecido por un intent previo): `ruff check`, `pip-audit` y
  `npm audit --audit-level=high` son **BLOQUEANTES** (pins `ruff==0.16.9`,
  `pip-audit==2.10.1`); `pytest --cov=app --cov-fail-under` y `ng test` bloqueantes;
  `gitleaks-action@v3` bloqueante. **Sólo ESLint frontend sigue advisory**
  (`continue-on-error`).
  - Nota de divergencia regla↔código: varias afirmaciones de `team.md`/`project.md`
    describen audits/lint como "advisory" y `requirements.txt` con rangos abiertos;
    ese estado **ya fue endurecido/pinneado**. Este CodeKB refleja el **código
    actual**, no el histórico de reglas.
- **`.github/workflows/fly-deploy.yml`** — push a `main` → deploy Fly.io; job
  `verify` replica el gate antes de desplegar.
- **Crons**: `daily-sync.yml`, `sofascore-sync.yml` (máquinas Fly one-shot).

## Documentation Quality

- README raíz detallado + `docs/` extenso (DEPLOY, ROLLBACK, PR-GATE,
  PROJECT_CONTEXT, planes de migración/backlog). Docstrings de módulo ricos en los
  componentes DDD nuevos.

## Technical Debt

- **God-files** (regla afirmada: NUNCA ampliar/reescribir) — `data_manager_v2.py`
  (~33 KB hoy, antes ~166 KB; delega a submódulos DDD), `data_sync_service.py`
  (~15 KB tras extracciones), `assistant_service.py` (~2 KB, fachada fina). La
  descomposición DDD está **en curso y avanzada**; los `per-file-ignores` de
  `ruff.toml` registran `E722`/`F841`/`F401`/`I001` como **deuda registrada** movida
  verbatim a los adaptadores (no saneada, para preservar comportamiento
  byte-a-byte).
- **SQL-en-router / SQL inline** — persiste en `player_finances.py`
  (`_get_finance_config` ejecuta `SELECT` directo) y en `main.py` (ruta de fotos con
  `SELECT` inline). Código nuevo debe ir tras una capa/función estrecha testeable.
- **`bare-except` / broad-except** — deuda registrada en `data_manager_v2.py`,
  `photo_service.py` y adaptadores; `E722` re-habilitado como advisory por trinquete
  pero silenciado por fichero en los god-files.
- **DB SQLite local commiteada** — `backend/futmondo_data.db` (65 KB) en el árbol;
  en prod sólo Neon PostgreSQL.
- **`node_modules.old-*`** — directorio obsoleto en `angular-app/` (ruido de
  workspace, no afecta build).

## Constraints (reglas afirmadas, reflejadas como invariantes)

- **Seguridad (positivo observado)**: `config.py` fail-fast si falta/por defecto
  `JWT_SECRET`; credenciales Futmondo nunca en claro (cifrado `FUTMONDO_CRED_KEY`);
  sin secretos hardcodeados en el código de aplicación. Mantener: NEVER password
  Futmondo en claro, NEVER `JWT_SECRET` por defecto en prod.
- **Characterization-first**: `calculator.component.ts` y sus `computed()` de
  proyección **no tienen spec**; congelar comportamiento antes de refactorizar.
- **Trazabilidad del dinero**: respetar `team_prizes` como única fuente de verdad y
  el reemplazo atómico (`replace_team_prizes`) para no reintroducir estado mixto.
- **Ratchet de cobertura sólo sube** (backend 27, frontend 19/19/17/18); código
  nuevo con specs que aseveren el efecto.
- **Coste 0 €**: todo en tiers gratuitos.

## Sources

- `developer-scan.md`: Code Quality Indicators, Technical Debt Signals, Handoff
  Summary (incl. correcciones de contexto regla↔código).
- Reglas afirmadas en `team.md` / `project.md` (reflejadas como invariantes, no como
  hallazgos nuevos).
