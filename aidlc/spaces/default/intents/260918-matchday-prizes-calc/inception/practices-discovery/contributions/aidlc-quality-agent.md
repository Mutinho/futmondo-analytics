**Collaborator:** aidlc-quality-agent

## Contribution

Revisión ciega de calidad sobre el borrador del lead para el intent
`260918-matchday-prizes-calc` (cálculo/mejora de premios). Inspeccioné de forma
independiente: `code-quality-assessment.md`, `code-structure.md`,
`backend/pytest.ini`, `backend/conftest.py`, el árbol real `backend/tests/`,
`.github/workflows/ci.yml` y el par de tests de caracterización de finanzas
(`test_finance_characterization.py`) y de sync (`test_sofascore_sync_characterization.py`).

### Testing posture (evaluación)

- **Metodología `test-after` + characterization-first**: correcta y consistente
  con la línea base afirmada (`team.md`/`project.md`) y con el patrón real del
  repo. El repo YA vive esta postura: casi todos los tests presentes son
  caracterización (`test_auth_characterization`, `test_finance_characterization`,
  `test_sofascore_sync_characterization`, `test_durable_*_characterization`,
  `test_db_engine_characterization`). Extender el objetivo a `sync_prizes` es la
  aplicación natural del mandato, no una postura nueva.
- **GAP CRÍTICO confirmado**: `data_sync_service.sync_prizes()` (~1577-1885)
  **produce** `team_prizes` y hoy tiene **cobertura directa cero**. El
  **consumo** sí está caracterizado (`test_finance_characterization.py` congela la
  fórmula agregada de `get_player_finances`, incluida la lectura de `team_prizes`
  como fuente de verdad, budget 200M por defecto y el 500 en error). La red de
  seguridad protege el lado que lee, no el lado que escribe la cifra monetaria —
  exactamente el lado que este intent va a tocar. La postura del draft
  (caracterizar producción antes de refactorizar) es obligada, no opcional.

### Tooling de cobertura (evaluación)

- **Sin piso bloqueante** confirmado en `pytest.ini`: cobertura es métrica
  informativa (`--cov=app` opt-in), sin `cov-fail-under`. El draft acierta al
  mantener 80% como referencia global no-bloqueante y **exigir en su lugar tests
  de los caminos nuevos y de error de la producción del premio** como puerta de
  "hecho". Piso porcentual global adicional sería ruido brownfield; la puerta
  correcta es "existe caracterización de `sync_prizes` antes del cambio + tests
  del nuevo contrato después", como propone el draft.
- **Asimetría `--cov` observada**: `ci.yml` (PR→`main`) corre
  `pytest -q --cov=app --cov-report=term-missing`; `fly-deploy.yml` `verify`
  (push→`main`) corre `pytest -q` **sin `--cov`**. La cobertura sólo se mide en
  el gate de PR. Para un intent que introduce lógica monetaria nueva es una
  señal que conviene no perder en el camino push-directo.

### Quality gates de CI (evaluación)

- **Bloqueantes** correctos y confirmados en `ci.yml`: gitleaks, `pytest`,
  `ng test`. **Advisory** (`continue-on-error`): ruff, ESLint, pip-audit,
  npm audit. El draft lo refleja bien. Nada que endurecer en esta etapa; el
  escalonado advisory→bloqueante de lint es decisión de saneamiento previa
  afirmada.

### Patrones de test/código reutilizables (a coste 0 €)

El patrón de dobles YA existe y es directamente reutilizable para caracterizar
`sync_prizes` sin red, sin `time.sleep()` real y sin coste:

- **`test_finance_characterization.py` — patrón más cercano**: monta una app
  FastAPI mínima y hace `monkeypatch.setattr(pf, "DataManagerV2", ...)` +
  `get_db` falso. Para `sync_prizes` (que vive en `services/`, no en un router),
  el análogo es **monkeypatch del cliente Futmondo y del acceso a datos** dentro
  de `data_sync_service`, con **respuestas de ronda deterministas** (sin red) y
  un doble de persistencia que capture los UPSERT a `team_prizes`.
- **`conftest.py` — `_FakeInMemoryDB` + fixture `fake_db`**: SQLite `:memory:`
  que honra el contrato `db_connection` (`get_connection`/`get_cursor`/
  `adapt_params`, `db_type="sqlite"`), ejercita el SQL parametrizado real
  (incluidos el `UPSERT ON CONFLICT` y el `DELETE ... WHERE matchday NOT IN`)
  sin tocar Neon. Es el doble idóneo para verificar la **limpieza defensiva** y
  el upsert de `team_prizes` de forma determinista. Cada test crea/limpia su
  propio almacén (fixture per-test), sin estado mutable compartido.
- **`test_sofascore_sync_characterization.py` — precedente de aislamiento de
  función pura**: extrae la decisión de negocio a una función pura
  (`should_apply_replacement`) y la testea sin I/O. Es el modelo a seguir para
  el punto 1 de la interview: **extraer la fórmula de premios a una función
  estrecha y pura** hace la caracterización trivial y barata, frente a intentar
  caracterizar los ~300 líneas embebidas con SQL+`sleep`+API intercalados.

### GAPS que la interview debe resolver (refuerzo/matices sobre el draft)

Estoy de acuerdo con las 6 incertidumbres del `evidence.md`. Aporto, desde
calidad, prioridad y precisión sobre las que más afectan a la testabilidad:

- **(Incertidumbre 1 — alcance del refactor) — RECOMENDACIÓN de calidad**:
  extraer la fórmula a una **función pura testeable** (patrón
  `should_apply_replacement`) es lo que hace la caracterización determinista y a
  coste 0 €. Caracterizar `sync_prizes` *in situ* obliga a stubear API+`sleep`+
  SQL a la vez y produce tests frágiles. Recomiendo que la interview incline
  hacia extracción estrecha, no corrección *in situ*.
- **(Incertidumbre 2 — granularidad de caracterización) — la interview DEBE
  cerrar el conjunto mínimo obligatorio**, porque define la puerta de "hecho".
  Propuesta de calidad como piso: (a) `points_prize` (siempre), (b) gating por
  `round_fully_played` (ranking/mvp/dream-team sólo con ronda cerrada), (c)
  ranking flop/top, (d) pseudo-jornada negativa (matchday sintético), (e) el
  `DELETE ... WHERE matchday NOT IN` (idempotencia/limpieza). Sin (b) y (e)
  caracterizados, cualquier cambio de fórmula es regresión silenciosa.
- **(Incertidumbre 3 — bugs a congelar vs corregir) — decisión de negocio que
  bloquea el diseño de tests**: si el intent cambia importes existentes a
  propósito, los tests de fase 1 que congelan ese comportamiento deben marcarse
  como "a retirar/actualizar de forma trazable" desde el inicio (como se hizo con
  `test_auth_characterization` para FR9). La interview debe decir explícitamente
  qué comportamiento actual es bug y qué es contrato a preservar.
- **(Incertidumbre 4 — cobertura)**: desde calidad, **no** activar un piso
  porcentual global (ruido brownfield). Sí exigir cobertura de los caminos
  nuevos/de error de las piezas de premios como criterio de merge.
- **(Incertidumbre 5 — paridad `verify`↔gate-de-MR)**: gap real (medición de
  cobertura sólo en PR). Diferir a diseño de pipeline es aceptable, pero debe
  quedar registrado como deuda, no cerrarse por omisión.
- **(Incertidumbre 6 — doble semántica de "puntos" e identidad frágil en
  `player_finances`)**: es un **riesgo de corrección de la cifra** (doble conteo
  u omisión del término de puntos, y doble conteo por resolución de identidad por
  nombre). Aunque el diseño decida dejarlo fuera de alcance, calidad pide **al
  menos un test que fije el comportamiento actual del término de puntos** para
  detectar si la mejora del cálculo lo altera sin querer.

## Positions

AGREE: `test-after` + characterization-first, con caracterización obligatoria de
la PRODUCCIÓN del premio (`sync_prizes`) antes del refactor. Confirmado como GAP
crítico: producción con cobertura cero, consumo ya caracterizado.

AGREE: mantener 80% líneas como referencia global no-bloqueante y sustituir el
piso porcentual por la puerta "caracterización antes + tests del nuevo contrato
después", exigiendo cobertura de caminos nuevos y de error de las piezas de
premios.

AGREE: dobles/fakes a coste 0 € reutilizando el patrón existente (`conftest.py`
`_FakeInMemoryDB`/`fake_db`, monkeypatch de `DataManagerV2`/cliente Futmondo como
en `test_finance_characterization.py`), sin red ni `time.sleep()` real.

AGREE: no ampliar god-files ni SQL-en-router; extraer la fórmula tras una capa/
función estrecha testeable.

OBJECT: el draft de `team-practices.md` afirma que `verify` (push→`main`) corre
"`pytest -q` **sin `--cov`** pero **sí con gitleaks** (hueco FR5 ya cerrado)" y lo
presenta como matiz cerrado. La evidencia sostiene que gitleaks está en `verify`,
pero el hueco de **paridad de cobertura** (`--cov` sólo en el gate de PR, no en
`verify`) sigue ABIERTO. Recomiendo redactar este punto como deuda de pipeline
pendiente (incertidumbre 5), no como hueco resuelto, para no cerrar por omisión
una decisión que es de la interview/diseño de pipeline.
