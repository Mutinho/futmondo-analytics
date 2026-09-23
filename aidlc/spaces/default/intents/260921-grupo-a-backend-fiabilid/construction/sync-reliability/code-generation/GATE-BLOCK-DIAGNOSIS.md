# Diagnóstico — Gate de code-generation bloqueado por bytecode en el snapshot de fuente

> Unidad: `sync-reliability` (intent `260921-grupo-a-backend-fiabilid`).
> Fecha: 2026-09-23. Estado: etapa **aparcada** en el gate; código y tests
> COMPLETOS y revisados READY (166 pytest en verde). El bloqueo es de
> infraestructura, no del trabajo de la unidad.

## Síntoma

Al abrir el gate de aprobación de `code-generation`, el completion-guard (RFC #662)
rechaza con:

```
Refusing to complete "code-generation": 77 application-source path(s) changed
during this stage run that no reviewed unit's source manifest claims
(backend/__pycache__/conftest.cpython-314-pytest-9.1.1.pyc, … and 76 more).
```

Los 77 paths son TODOS ficheros `.pyc` de `__pycache__/` (bytecode Python),
gitignored (`.gitignore:7` → `__pycache__/`). No son código fuente de la unidad.

## Causa raíz

El snapshot de fuente de la etapa (`<record>/.aidlc-source-review/code-generation/`)
se generó con un **walk de sistema de ficheros que NO excluye los ficheros
ignorados por git**. Evidencia:

- `baseline-0bb0939cc771.tsv` (inicio de etapa, sesión previa) contiene **76**
  entradas `.pyc` y **9** entradas `.claude/…` — ambas rutas están fuera del
  control de versiones (`.claude/` y `__pycache__/`), luego el listing NO es
  git-aware (`git ls-files` no las ve: `git ls-files backend | grep -c pyc → 0`).
- El bytecode `.pyc` preexistía en el árbol al arrancar la etapa (dejado por una
  ejecución de `pytest` de una sesión anterior, `cpython-314`).
- El guard compara ese baseline contra el estado del árbol. Como los `.pyc`
  fueron regenerados (hashes distintos) o borrados, aparecen como "cambios de
  fuente no reclamados".

El punto exacto del código: en `.kiro/tools/aidlc-lib.ts`,
`SOURCE_FINGERPRINT_HARD_EXCLUDED_NAMES` (≈ línea 14118) lista
`.cache, .git, .gradle, .mypy_cache, .next, .nuxt, .pytest_cache, .ruff_cache,
.tox, .venv, node_modules, venv` — pero **NO incluye `__pycache__`**, y no hay
exclusión por extensión `*.pyc`. El walk de source-listing incluye por tanto
todo el bytecode que haya en el árbol.

(Comportamiento análogo al bug ya parcheado localmente y documentado en
`docs/AIDLC-LOCAL-FIX.md`: el motor cae a un camino que no respeta las
exclusiones esperadas.)

## Por qué no hay salida limpia dentro del flujo

- **Borrar los `.pyc`**: un borrado sigue siendo un "cambio" frente al baseline.
- **Recapturar el snapshot / re-fingerprint / re-revisar**: el guard compara
  contra el baseline FIJO de arranque; recapturar no lo sustituye.
- **Reclamar los `.pyc` en `source-manifest.json`**: inviable — el manifest
  valida `version:1` y rutas de FUENTE REAL existentes que el reviewer
  inspecciona; los `.pyc` no existen en disco ni son inspeccionables.
- **Revertir al estado exacto del baseline**: imposible — el `.tsv` guarda
  `path\tmode\tsha256`, no los blobs; y el bytecode se regenera con hashes
  distintos según la versión de Python.

## Fix propuesto (pendiente de aprobación humana; NO aplicado)

Añadir `__pycache__` a `SOURCE_FINGERPRINT_HARD_EXCLUDED_NAMES` en
`.kiro/tools/aidlc-lib.ts` (y, si el listing hashea por fichero, excluir también
la extensión `*.pyc`). Con esa exclusión, el bytecode queda fuera del universo
de fuente en AMBOS lados (baseline recomputado y estado actual), y el gate abre
limpio sin tocar el manifest ni el código de la unidad.

Alcance del parche: mínimo y local (una entrada en una lista), reversible,
alineado con la política del parche local ya presente. Requiere regenerar el
baseline de la etapa tras el cambio (o que el guard recompute con la nueva
exclusión).

Verificación tras el fix:
1. `docker run --rm -v "$PWD":/repo -w /repo/backend -e JWT_SECRET=... -e PYTHONDONTWRITEBYTECODE=1 python:3.12 pytest tests -ra` → 166 passed.
2. `aidlc engine orchestrate report --stage code-generation --result awaiting-approval` → sin rechazo por fuente no reclamada.

## Mitigación preventiva recomendada (independiente del fix)

- Exportar `PYTHONDONTWRITEBYTECODE=1` en los runners de test, o correr pytest
  con `-p no:cacheprovider` y limpiar `__pycache__`/`*.pyc` tras cada ejecución,
  para que el árbol de trabajo no acumule bytecode que contamine snapshots.

## Estado del trabajo de la unidad (sano)

- Código: `backend/app/services/sync_step_status.py` (nuevo), cableado `degraded`
  en `sync.py`, `PRICE_SANITY_CAP`+422 en `market.py`, `except` estrechado en
  `token_store.py`, log de contexto en `db_connection.py`.
- Tests: `test_sync_step_status.py`, `test_sync_degraded_steps.py`,
  `test_market_bid_sanity_cap.py`, `test_token_store_migrations.py` (166 en verde).
- Revisión adversarial: READY (R-01 Critical resuelto y con test de regresión;
  R-02 riesgo aceptado; R-03 positivo).
- `source-manifest.json`: version 1, 9 fuentes reales (restaurado a su forma
  correcta; sin bytecode).
