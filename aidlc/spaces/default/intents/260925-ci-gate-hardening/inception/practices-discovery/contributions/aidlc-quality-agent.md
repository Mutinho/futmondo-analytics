**Collaborator:** aidlc-quality-agent

## Contribution

Revisión independiente desde la perspectiva de calidad (testing posture, tooling
de cobertura, quality gates de CI, patrones test/código y HUECOS para la
entrevista con el humano) del Intent 4 — `260925-ci-gate-hardening` (scope infra,
brownfield, RE-RUN sobre baseline afirmada). Evidencia inspeccionada de primera
mano: `ci.yml`, `fly-deploy.yml`, `backend/ruff.toml`, `backend/pytest.ini`,
`angular-app/angular.json` (target `test`), `angular-app/package.json`.

### Testing Posture — refuerzo y matices

1. **Medición-antes-de-piso como paso de calidad obligatorio (FR11).** El piso
   `cov-fail-under` NO se puede fijar a ciegas: hay que ejecutar `pytest
   --cov=app` en verde una vez y **fijar el piso al porcentaje medido real**
   (piso = suelo observado, nunca aspiracional). Esto es el equivalente
   backend del "characterization-first" ya afirmado: se congela la señal antes
   de bloquear con ella. El anti-patrón a prohibir es subir el piso escribiendo
   tests-espejo que inflan cobertura sin aserciones significativas
   (`assert True` / specs que ejercitan líneas sin verificar efecto).

2. **`--cov-fail-under` es config, no un paso extra.** El enforcement backend
   debe vivir DENTRO de la misma invocación `pytest` (via `addopts` en
   `pytest.ini`, `--cov-fail-under=<N>`), igual que el frontend lo tiene dentro
   de `ng test`/`angular.json`. Fuente única de umbral por lado (pytest.ini para
   backend, angular.json para frontend), sin `continue-on-error` ni pasos
   paralelos que puedan desincronizarse.

3. **Cobertura significativa, no cosmética.** El ratchet sólo-sube es correcto,
   pero un piso alto con aserciones débiles es peor que uno modesto con
   aserciones reales. La posture test-after del equipo se mantiene: specs con
   aserción de efecto (payload/estado/modo de fallo), fixtures fake in-memory de
   `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`, `clean_jwt_env`, `fake_db`),
   sin red/BD real/credenciales (gitleaks escanea los tests). Coste 0 €.

### Tooling de cobertura — hallazgos verificados

- **Backend**: `pytest.ini` declara cobertura como informativa, **sin
  `cov-fail-under`** → hueco FR11 confirmado. `ci.yml` corre `pytest --cov=app
  --cov-report=term-missing` (BLOQUEANTE por tests, no por cobertura).
- **Asimetría backend (FR17.3) confirmada verbatim**: el job `verify` de
  `fly-deploy.yml` corre `pytest -q` **SIN `--cov`**. Un rojo de cobertura NO
  puede bloquear el push directo a `main` hoy. La cura (mover la misma
  invocación con `--cov` + el mismo piso a `verify`) es correcta y NO reordena
  la cadena `needs:`.
- **Frontend**: `angular.json` ya define `coverageThresholds` (statements 15 /
  branches 15 / functions 13 / lines 14) y **ambos** workflows corren `ng test
  --watch=false` — es decir, el frontend YA tiene paridad de enforcement de
  cobertura entre PR-gate y push-gate. El intent frontend es puramente
  **subir el ratchet** de esos cuatro umbrales al valor medido, no crear
  paridad (ya existe). Conviene decir esto explícitamente para no confundirlo
  con la asimetría backend.

### HUECOS adicionales para la entrevista con el humano (no cubiertos en el borrador)

- **HUECO-Q-A (drift de versión gitleaks entre workflows).** `ci.yml` usa
  `gitleaks/gitleaks-action@v3` mientras `verify` de `fly-deploy.yml` usa
  `@v2`. Dos gates "de secretos" en versiones distintas es deuda de paridad de
  tooling (misma clase de asimetría que `--cov`). ¿Se alinean ambos a `@v3` (y
  se fija a tag/SHA exacto por la regla de pin OSS) dentro de este intent, o se
  registra como deuda diferida?

- **HUECO-Q-B (pin del proveedor de cobertura frontend).**
  `@vitest/coverage-v8` está pineado a `4.1.11` (correcto), pero `vitest` está
  en rango abierto `^4.0.8`. El plugin de cobertura suele exigir versión
  emparejada con el runner; un bump de `vitest` por `npm ci` podría romper la
  medición del gate bloqueante. ¿Se pinea también `vitest` a versión exacta
  (coherente con la regla afirmada de pin en checks bloqueantes) en este intent
  o queda como deuda?

- **HUECO-Q-C (granularidad del ratchet backend).** ¿El piso backend es
  **line-only** (`--cov-fail-under` es un único número de líneas) o se busca
  paridad conceptual con el frontend, que ratea 4 métricas (statements/
  branches/functions/lines)? pytest-cov nativo sólo hace fallar por un total;
  branch-coverage requiere `--cov-branch`. Decidir si el ratchet backend
  incluye branch-coverage o se queda en line-coverage total en este intent.

- **HUECO-Q-D (margen de holgura del piso vs flapping).** Ya planteado por el
  líder: ¿piso = valor medido exacto, o medido menos un pequeño margen para
  evitar rojos por variación no determinista? Recomendación de calidad:
  **piso = valor medido exacto**, y si aparece flapping, arreglar el test
  no-determinista (nunca bajar el piso — regla afirmada). El margen sólo se
  justificaría si se demuestra no-determinismo irreducible.

- **HUECO-Q-E (audits sin fix disponible en free tier).** Ya planteado por el
  líder para severidad; añado el ángulo de calidad: al promover `pip-audit`/
  `npm audit` a bloqueante, un finding sin fix upstream bloquearía el gate sin
  acción posible. ¿Política de allowlist versionada y auditada (con fecha de
  revisión) vs diferir la promoción de ese audit concreto? La allowlist NO debe
  convertirse en un silenciador permanente (equivalente a relajar un umbral).

- **HUECO-Q-F (interacción del ratchet con el orden de promoción FR12).** Si
  se saneia/silencia deuda de lint antes de bloquear `ruff check`, cualquier
  test nuevo que se añada para ese saneamiento cambia la cobertura medida. ¿El
  piso de cobertura backend se fija ANTES o DESPUÉS de la oleada de promoción de
  linters/audits, para que la medición base sea estable? Recomiendo fijar el
  piso al final del escalón, sobre la suite ya estabilizada.

### Quality gates — orden recomendado (coste 0 €)

Coincido con la secuenciación audits→lint→cobertura del líder por ruido/señal.
Matiz de calidad: la **paridad de cobertura backend en `verify` (FR17.3)** debe
aterrizar en el MISMO commit que introduce el piso en `ci.yml`, o inmediatamente
después, para que no exista una ventana en la que el piso viva sólo en el
PR-gate y el push directo lo eluda.

## Positions

- AGREE: Piso backend fijado al valor medido y ratchet sólo-sube — es el
  equivalente backend del characterization-first ya afirmado.
- AGREE: Cerrar la asimetría `--cov` llevando la misma invocación + piso al job
  `verify`; verificado verbatim que `verify` corre `pytest -q` sin `--cov`.
- AGREE: `angular.json` como fuente única de umbral frontend con enforcement
  dentro de `ng test`; verificado que ambos workflows ya corren `ng test`.
- AGREE: Promoción escalonada advisory→bloqueante (audits→lint) en commits
  aislados, sin `--fix`/`ruff format` masivo, respetando la regla brownfield.
- AGREE: No reordenar la cadena `needs:` de `fly-deploy.yml`; el endurecimiento
  refuerza el contenido de `verify`, no su topología.
- OBJECT: El borrador describe la cobertura frontend como "deuda de paridad a
  cerrar" junto a la backend; la evidencia muestra que el frontend YA tiene
  paridad de enforcement en ambos workflows — su tarea es SÓLO subir el ratchet,
  no crear paridad. Debe separarse conceptualmente de la asimetría backend para
  no inducir trabajo inexistente.
- OBJECT: El borrador no captura el drift de versión de gitleaks (`@v3` en
  `ci.yml` vs `@v2` en `verify`) ni el rango abierto de `vitest` (`^4.0.8`)
  frente al pin de su plugin de cobertura; ambos son riesgos directos al gate
  bloqueante bajo la regla afirmada de pin exacto y deben resolverse en la
  entrevista (cerrar en este intent o registrar como deuda explícita).
