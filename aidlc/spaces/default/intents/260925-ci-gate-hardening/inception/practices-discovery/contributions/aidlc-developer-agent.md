**Collaborator:** aidlc-developer-agent

## Contribution

Revisión independiente del borrador del líder desde la perspectiva de desarrollo
(naming, límites de capas, manejo de errores, organización de ficheros y
convenciones de code-style) para el Intent 4 — `260925-ci-gate-hardening` (scope
infra, brownfield). Verifiqué la evidencia real en disco; no soy consciente de
las contribuciones de otros colaboradores.

### Evidencia verificada en disco

- **God-files confirmados** (tamaños reales): `app/services/data_sync_service.py`
  (~84,6 KB), `app/services/data_manager_v2.py` (~166,2 KB) y
  `app/services/assistant_service.py` (~51,7 KB). El borrador ya los lista en
  `NEVER ampliar los god-files`; los tres nombres son correctos. Confirmo la
  regla: cualquier saneo de deuda de lint que un endurecimiento fuerce (p. ej.
  `E722`/`F401` que salte al bloquear `ruff check`) debe hacerse **quirúrgico y
  sin reescribir** estos ficheros, nunca refactor de oportunidad dentro de ellos.
- **Patrón SQL-en-router confirmado**: `app/api/v1/endpoints/` contiene routers
  grandes (`market.py` ~24,7 KB, `sync.py` ~16,9 KB, `roster.py` ~14,1 KB,
  `analytics.py` ~13,4 KB, `balances.py`, `player_finances.py`, `transactions.py`).
  Este intent es config-only de CI/CD: NO debe tocar esa lógica ni migrarla; el
  endurecimiento del gate no es excusa para redistribuir SQL fuera del router.
- **`backend/ruff.toml`**: `target-version = "py312"`, `line-length = 100`,
  `select = ["E","F","I"]`, `ignore = ["E501","E402"]` (E722 ya fuera del ignore
  → advisory por trinquete), `[lint.per-file-ignores]` para `tests/**` (E402,
  F401) y `conftest.py` (E402), y un bloque `[format]` presente. El borrador lo
  describe con fidelidad.
- **`ci.yml`**: `ruff check`, ESLint, `pip-audit`, `npm audit` con
  `continue-on-error: true` (advisory); `gitleaks` + `pytest --cov=app` + `ng test`
  bloqueantes. El paso de ruff hace `pip install ruff` **sin pin** y ESLint corre
  `npx ng lint || echo ...`.
- **`fly-deploy.yml` job `verify`**: `pytest -q` **sin `--cov`** (asimetría
  backend real), `ng test` con cobertura, cadena `needs:` `verify → deploy-backend
  → deploy-frontend → smoke-test (/health)`.
- **`eslint.config.js`**: comentario explícito de que `angular-eslint`,
  `@typescript-eslint/*` y `eslint` **aún NO están instalados como
  devDependencies** ("se añaden al adoptar el gate bloqueante"). Reglas hoy en
  `warn`.
- **`angular.json` / `pytest.ini`**: coherentes con el borrador (umbral frontend
  dentro de `ng test`; cobertura backend informativa, sin piso).

### Puntos que refuerzo (perspectiva code-style)

1. **Promover `ruff check` a bloqueante sin gatillar `ruff format` ni `--fix`
   masivo**: la promoción es un cambio de **una sola línea** en `ci.yml` (quitar
   `continue-on-error: true` del paso de ruff), en su propio commit `chore(ci)`,
   dejando el bloque `[format]` de `ruff.toml` sin ejercitar. Ningún job del
   pipeline invoca `ruff format`, y la reviewer sólo corre `ruff check` — así el
   binding de la fuente reclamada se mantiene estable durante su pasada. La deuda
   que `ruff check` reporte hoy en advisory debe saneárse **quirúrgicamente por
   fichero** (o silenciarse vía `per-file-ignores`/`# noqa` puntual con
   rationale) ANTES de bloquear, nunca con un `--fix` de repo entero.
2. **Aislamiento por commit `chore(ci)`**: cada promoción advisory→bloqueante y
   cada piso de cobertura en su propio commit aislado, con el trinquete fijado
   explícitamente, para rollback quirúrgico. Scope de commit en castellano,
   identificadores/docstrings en inglés — coherente con la regla afirmada.
3. **Pin exacto en el paso que instala la herramienta del gate**: hoy `ci.yml`
   hace `pip install ruff` sin versión. Al volver `ruff check` bloqueante, el
   pin exacto de `ruff` (y de `pip-audit`) debe vivir **en el paso que lo
   instala** (o en un requirements de tooling), no sólo enunciarse: un `ruff`
   flotante puede introducir reglas nuevas que rompan el gate de forma no
   determinista. El borrador afirma el pin; lo hago accionable señalando el punto
   exacto.

## Positions

- OBJECT: El borrador afirma en Code Style que "Este intent no toca
  devDependencies del frontend" mientras que en la promoción escalonada de FR12
  incluye "ESLint frontend" como paso a bloqueante. `eslint.config.js` declara
  explícitamente que `angular-eslint`, `@typescript-eslint/*` y `eslint` **aún no
  están instalados**, y `ci.yml` corre `npx ng lint || echo ...` (tolerante a
  ausencia del binario). Volver ESLint **bloqueante** exige **añadir esas
  devDependencies** (pin exacto) — lo que SÍ toca `package.json`/lockfile del
  frontend y por tanto dispara la regla afirmada de verificar `npm ci` + `ng test`
  en `node:22.22.3` antes de pushear. Rationale: la contradicción es material;
  propongo (a) explicitar que la promoción de ESLint conlleva instalar+pinnar sus
  devDependencies bajo la regla de contenedor Node, o (b) excluir ESLint del
  alcance de ESTE intent y dejarlo como deuda diferida (promover sólo audits +
  `ruff check` backend), evitando ampliar la superficie del frontend en un intent
  infra de gate.

- OBJECT: La regla `NEVER usar --fix masivo de ruff` cubre bien la promoción de
  lint, pero el borrador no fija la política para la **deuda que `ruff check`
  reportará al bloquear** más allá de "saneada o silenciada quirúrgicamente".
  Rationale: sin una política escrita, el riesgo real es que alguien "arregle el
  gate" con `ruff check --fix` de repo o editando los god-files. Propongo añadir
  a Forbidden/Mandated una regla explícita: la deuda de lint pre-bloqueo se sanea
  **por fichero de forma quirúrgica** o se suprime con `per-file-ignores`/`# noqa`
  puntual con rationale, y **NUNCA** ampliando ni reescribiendo
  `data_sync_service.py`, `data_manager_v2.py`, `assistant_service.py` ni los
  routers SQL-en-endpoint para acallar avisos.

- AGREE: Resto del borrador (piso `cov-fail-under` al valor medido y sólo por
  trinquete; cierre de la asimetría de cobertura backend en `verify`; orden
  escalonado audits→lint→cobertura; `angular.json` como fuente única del umbral
  frontend; no reordenar la cadena `needs:`; pin exacto OSS; secretos vía
  `secrets` y `JWT_SECRET` efímero en CI; reviewer sólo `ruff check`;
  identificadores/docstrings en inglés y texto usuario/commits en castellano;
  coste 0 € / free tier). La evidencia en disco respalda cada punto.
