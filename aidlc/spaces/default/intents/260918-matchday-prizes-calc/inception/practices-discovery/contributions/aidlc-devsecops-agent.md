**Collaborator:** aidlc-devsecops-agent

## Contribution

Revisión de seguridad y DevSecOps del borrador del lead para el intent de
cálculo de premios (`260918-matchday-prizes-calc`). Spoke ciego: no he visto las
contribuciones de quality ni de developer. Evalúo lint/format, SAST/DAST,
escaneo de secretos y de dependencias, controles de supply-chain, y la
superficie de seguridad que el área de premios pudiera introducir. Fuentes
inspeccionadas: `.github/workflows/{ci.yml,fly-deploy.yml}`, `backend/ruff.toml`,
`backend/requirements.txt`, `angular-app/package.json`, `.env.example`, y los
tres borradores del lead (`team-practices.md`, `discovered-rules.md`,
`evidence.md`).

### 1. Escaneo de secretos (gitleaks) — estado real verificado

- **gitleaks BLOQUEANTE en ambos caminos, confirmado en el código.** El PR gate
  (`ci.yml`, `pull_request → main`) usa `gitleaks/gitleaks-action@v3` sin
  `continue-on-error` → bloquea el job `quality`. El push a `main`
  (`fly-deploy.yml`) usa `gitleaks/gitleaks-action@v2` en el job `verify`, del
  que dependen los deploys vía `needs:` → un secreto detiene el despliegue. **El
  hueco FR5 que el brief describía como abierto YA ESTÁ CERRADO en el repo**: el
  borrador del lead ya lo refleja correctamente ("hueco FR5 ya cerrado"), y el
  contexto del brief está desactualizado en este punto. Confirmo la corrección
  del lead.
- **Divergencia menor de versión de acción** (observación, no bloqueante):
  `ci.yml` fija `gitleaks-action@v3` y `fly-deploy.yml` `@v2`. Es defensa en
  profundidad efectiva en ambos, pero conviene **unificar a la misma major**
  para paridad real de reglas y facilitar el mantenimiento (Dependabot/renovate
  a coste 0 €). No es alcance de este intent de premios; nota para diseño de
  pipeline.

### 2. Superficie de seguridad del área de premios — no introduce secretos nuevos

Análisis STRIDE acotado del flujo `sync_prizes → team_prizes → routers`:

- **CONFIRMADO: el área de premios NO maneja secretos nuevos.** `sync_prizes`
  reutiliza la sesión/credenciales Futmondo del usuario ya existentes (patrón
  multi-usuario descrito en README y RE) y escribe en `team_prizes` (dato de
  negocio, no sensible). No añade variables de entorno, ni claves, ni
  credenciales al `.env.example` (verificado: `.env.example` solo lista
  `FUTMONDO_EMAIL/PASSWORD`, `DATABASE_URL`, `BASE_URL`, `CHAMPIONSHIP_ID`,
  host/puerto). **No hay nueva superficie de secretos.**
- **Information Disclosure (bajo)**: los premios son importes monetarios de
  fantasy compartidos entre usuarios del mismo campeonato; la autorización ya la
  gobierna el Bearer token en `/api/v1/*` (fuera del cambio). El cálculo batch no
  cambia el modelo de acceso. **No aparece PII nueva ni dato sensible nuevo.**
- **Tampering / Integrity (relevante para la corrección del cálculo)**: la
  fórmula produce importes que los usuarios ven como saldo. Un cálculo erróneo no
  es una vulnerabilidad clásica, pero el gating por ronda completa
  (`round_fully_played`) y la limpieza defensiva `DELETE ... NOT IN` **sí tocan
  integridad de datos**: un `DELETE` mal acotado podría borrar filas de premios
  legítimas. **Recomiendo que la caracterización obligatoria (incertidumbre 2 de
  la interview) incluya explícitamente el alcance del `DELETE ... NOT IN`** como
  rama de afirmación obligatoria — es la única con potencial de pérdida de datos.
- **DoS / coste (relevante al mandato 0 €)**: `sync_prizes` acopla la API
  Futmondo con `time.sleep()` real y corre en los crons `daily-sync`/
  `sofascore-sync` (máquinas Fly one-shot). El mandato de dobles/fakes en test
  (patrón `conftest.py`) es también un control DevSecOps: **evita llamadas de red
  reales y coste en CI**. AGREE con el lead en ese patrón.

### 3. Lint / format y SAST — postura escalonada correcta, con oportunidad de coste 0 €

- **Postura escalonada advisory→bloqueante confirmada** y bien capturada por el
  lead: `ruff check` es `continue-on-error` en `ci.yml`; `ruff.toml` documenta el
  arranque tolerante (`select=["E","F","I"]`, `ignore=["E501","E402","E722"]`).
  ESLint también advisory. No objeto: endurecer de golpe sobre base heredada sin
  formatear rompería el gate. Coherente con la regla brownfield de NO correr
  `ruff format` masivo.
- **SAST de coste 0 € recomendable por trinquete** (ya insinuado en
  `team.md`/`project.md` línea base): al endurecer ruff, **activar la familia `S`
  (flake8-bandit)** para banderas de seguridad gratuitas — `assert` en producción
  (relevante: el cálculo de premios no debe usar `assert` para validar importes),
  `subprocess`/`eval` inseguros, `try/except/pass`. `sync_prizes` vive en un
  god-file con `try/except` amplios heredados (`E722` silenciado); la familia `S`
  daría señal sin coste. **Fuera del alcance de este intent de premios**;
  candidato de trinquete para diseño de CI.
- **DAST**: no aplica a coste 0 € para este intent (área batch interna, sin nueva
  superficie HTTP expuesta). El smoke test `/health` cubre la verificación de
  release. No propongo introducir DAST (coste/complejidad sin beneficio aquí).

### 4. Escaneo de dependencias y supply-chain

- **pip-audit / npm audit advisory confirmado** (`continue-on-error` en ambos
  pasos de `ci.yml`). Aceptable en fase de saneamiento. Observación: el área de
  premios **no añade dependencias nuevas** (verificado: `requirements.txt` y
  `package.json` no necesitan paquetes nuevos para caracterizar/mejorar un
  cálculo aritmético con dobles). Se mantiene la superficie de supply-chain
  actual.
- **Supply-chain / pinning**: mezcla observada de anclado exacto
  (`libsql-experimental==0.0.55`, `PyJWT==2.9.0`, `google-genai`, `groq`) y
  rangos abiertos (`requests>=`, `fastapi>=`, `pytest>=`). No es alcance de
  premios, pero recomiendo (trinquete, coste 0 €) **considerar Dependabot nativo
  de GitHub** para PRs de actualización con alerta de CVE — gratis en repos
  GitHub. Nota para diseño de pipeline, no para esta etapa.
- **Nota de higiene**: `libsql-experimental==0.0.55` no compila fuera de 3.12 y
  no lo ejercitan los tests (usan fake SQLite) — ya documentado en `project.md`.
  Sin impacto de seguridad para premios.

### 5. Constraints de seguridad de línea base — se mantienen intactos

Los `Forbidden`/`Mandated` de seguridad afirmados siguen vigentes y aplican al
intent de premios sin cambios:
- NEVER password Futmondo en claro (memoria ni BD) — el área de premios no toca
  auth, así que no reintroduce el riesgo, pero la regla se mantiene.
- NEVER `JWT_SECRET` default en producción / ALWAYS `JWT_SECRET` no-default en
  arranque (NFR1.1, `test_jwt_startup.py`) — sin cambios.
- El `JWT_SECRET: ci-ephemeral-secret-not-a-real-one` en los workflows es un
  literal de arranque **no productivo** exigido por el guard NFR1.1 para que la
  app importe en CI; **no es un secreto real** y por diseño no debe dispararse
  como hallazgo. Correcto tal cual está.

### 6. Recomendación sobre incertidumbre 5 (paridad `verify` ↔ gate de MR)

Desde seguridad, la parte crítica de la paridad (**gitleaks**) YA está replicada
en `verify`; el hueco restante es solo `--cov` (señal de cobertura, no de
seguridad). Por tanto, **desde DevSecOps la paridad de seguridad está resuelta**
y la decisión de añadir `--cov` a `verify` es de calidad/pipeline, no de
seguridad. Recomiendo **diferir `--cov` en `verify` a diseño de pipeline** y no
cargar este intent de premios con ello (coste 0 €, sin riesgo de seguridad
pendiente).

## Positions

AGREE: gitleaks BLOQUEANTE en PR gate y en `verify` (push→`main`) — verificado en
el código; el hueco FR5 está cerrado y el borrador del lead lo refleja
correctamente.

AGREE: postura escalonada advisory→bloqueante para ruff/ESLint y auditorías de
dependencias (pip-audit/npm audit); endurecer de golpe sobre base heredada
rompería el gate.

AGREE: el área de premios NO introduce superficie de secretos nueva ni
dependencias nuevas; reutiliza credenciales Futmondo existentes y escribe datos
de negocio no sensibles (`team_prizes`).

AGREE: mandato de dobles/fakes (patrón `conftest.py`) para caracterizar
`sync_prizes` — además de test-hygiene es control DevSecOps (evita red real y
coste, mantiene 0 €).

AGREE: NEVER `ruff format` masivo brownfield; mantener estable el binding de la
fuente reclamada durante la revisión.

OBJECT: None

### Notas fuera del alcance de esta etapa (candidatas a diseño de pipeline, coste 0 €)
- Unificar la major de `gitleaks-action` (`v3` en PR, `v2` en push) para paridad de reglas.
- Al endurecer ruff, activar por trinquete la familia `S` (flake8-bandit): `assert` en prod, `eval`/`subprocess` inseguros, `try/except/pass` — señal de seguridad gratis, relevante a los `try/except` amplios de `sync_prizes`.
- Reforzar caracterización obligatoria del `DELETE ... NOT IN` de `sync_prizes` por su potencial de pérdida de datos (integridad).
- Considerar Dependabot nativo de GitHub para PRs de actualización con alerta de CVE (gratis).
