# Practices Discovery — Entrevista (Intent 4, gate CI/CD hardening)

Re-run sobre prácticas ya afirmadas. Solo se pregunta lo que el borrador del
líder y las revisiones ciegas (calidad, desarrollo, seguridad) no pudieron
establecer. La evidencia sugiere respuestas; la intención del equipo es
decisión humana.

Áreas cubiertas por la baseline afirmada y NO re-preguntadas: trunk-based +
squash-merge, walking skeleton OFF, coste 0 €, gate bloqueante gitleaks+pytest+ng
test, no ampliar god-files, no reformateo brownfield masivo, pin OSS exacto,
idioma código inglés / usuario+commits castellano.

---

## Q1 — Alcance de ESLint frontend en la promoción a bloqueante (FR12)

El plan promueve linters/audits de advisory a bloqueante. Pero el frontend hoy
NO tiene ESLint instalado: `eslint.config.js` declara que `angular-eslint`,
`@typescript-eslint/*` y `eslint` aún no son devDependencies, y CI corre
`npx ng lint || echo ...` (tolerante a que falte). Volver ESLint bloqueante
obligaría a instalar+pinnar esas devDependencies (toca `package.json`/lockfile y
dispara la regla de verificar `npm ci` + `ng test` en `node:22.22.3`).

- A. Excluir ESLint de este intent (deuda diferida): promover a bloqueante solo
  los audits + `ruff check` backend. No se toca el frontend salvo subir el
  ratchet de cobertura. (Recomendación de desarrollo: menor superficie.)
- B. Incluir ESLint: instalar+pinnar sus devDependencies y promoverlo a
  bloqueante, con verificación `npm ci` + `ng test` en `node:22.22.3`.
- X. Other (please specify)

[Answer]: A. Excluir ESLint de este intent (deuda diferida); a bloqueante solo audits + `ruff check` backend; el frontend solo sube ratchet de cobertura.

## Q2 — Severidad que bloquea en los audits de dependencias (FR12)

Al promover `pip-audit` (backend) y `npm audit` (frontend) a bloqueante, ¿qué
corte de severidad bloquea el gate?

- A. npm audit bloquea en `high` (no critical-only); pip-audit bloquea todo
  finding CON fix disponible, y los findings SIN fix se gobiernan por allowlist
  (ver Q3). Si `high` genera demasiado ruido heredado de golpe, promover primero
  en `critical`, sanear, y endurecer a `high` en commit posterior (el trinquete
  de severidad solo endurece). (Recomendación de seguridad.)
- B. Bloquear solo en `critical` en ambos audits (más permisivo).
- X. Other (please specify)

[Answer]: A. npm audit bloquea en `high`; pip-audit bloquea todo finding con fix, y los sin-fix se gobiernan por allowlist (Q3); si `high` genera ruido de golpe, promover primero en `critical` y endurecer a `high` (el trinquete de severidad solo endurece).

## Q3 — Findings de audit sin fix disponible en el free tier (FR12)

Un finding sin fix upstream bloquearía el gate sin acción posible. ¿Política?

- A. Allowlist versionada y auditada, commiteada en el repo (ID CVE/advisory,
  dependencia+versión, motivo, fecha y fecha de caducidad/revisión), vía
  `pip-audit --ignore-vuln <ID>` y equivalente npm. Nada de `continue-on-error`
  permanente ni silenciar borrando el audit; una entrada caducada vuelve a
  bloquear. (Recomendación de calidad+seguridad.)
- B. Diferir la promoción de ese audit concreto hasta que haya fix.
- X. Other (please specify)

[Answer]: A. Allowlist versionada y auditada, commiteada en el repo (ID CVE/advisory, dependencia+versión, motivo, fecha y caducidad), vía `pip-audit --ignore-vuln <ID>` y equivalente npm; nada de `continue-on-error` permanente; una entrada caducada vuelve a bloquear.

## Q4 — Paridad real de audits/lint en el gate de push (`verify` de fly-deploy.yml) (FR17.3)

El job `verify` (push directo a `main`) hoy NO tiene pasos de audit ni de lint:
solo gitleaks + `pytest -q` (sin `--cov`) + `ng test`. "Replicar la promoción en
ambos gates" no es flipear un flag: exige AÑADIR esos pasos a `verify` (mismo
hueco de defensa en profundidad que FR17.3 cierra para la cobertura).

- A. Sí, en alcance: `verify` recibe la señal de cobertura backend con piso
  (paridad con ci.yml) Y los pasos de audit/lint que se vuelvan bloqueantes, para
  que el push directo no eluda el gate. La paridad de cobertura backend aterriza
  en el mismo commit (o inmediatamente después) que introduce el piso en ci.yml.
  (Recomendación de calidad+seguridad.)
- B. Solo cerrar la asimetría de cobertura backend en `verify` (FR17.3 estricto);
  los audits/lint bloqueantes quedan solo en el gate de PR, y su paridad en
  `verify` se registra como deuda diferida.
- X. Other (please specify)

[Answer]: A. Sí, en alcance: `verify` recibe la señal de cobertura backend con piso (paridad con ci.yml) Y los pasos de audit/lint que se vuelvan bloqueantes; la paridad de cobertura backend aterriza en el mismo commit (o inmediatamente después) que introduce el piso en ci.yml.

## Q5 — Deuda de tooling del pipeline: drift de versiones y pin de acciones

Las revisiones detectaron: (a) gitleaks corre `@v3` en ci.yml y `@v2` en
`verify` (dos versiones del mismo escáner hacia `main`); (b) acciones de
terceros por tag mutable (`setup-flyctl@master`); (c) `vitest` en rango abierto
`^4.0.8` frente al pin de su plugin `@vitest/coverage-v8==4.1.11`; (d)
`ci.yml` hace `pip install ruff` sin pin; (e) `pip-audit -r requirements.txt`
audita rangos, no el set instalado.

- A. Cerrar en este intent lo que es riesgo directo al gate bloqueante: unificar
  gitleaks a una versión y fijarla, pinnar `ruff`/`pip-audit` en el paso que los
  instala, pinnar `vitest`, y auditar el entorno instalado (no `-r`). Pin de
  acciones por SHA se decide en ci-pipeline. (Recomendación de las tres voces.)
- B. Cerrar solo el subconjunto mínimo (pin de `ruff`/`pip-audit`, unificar
  gitleaks) y registrar el resto (SHA de acciones, `vitest`) como deuda diferida.
- X. Other (please specify)

[Answer]: A. Cerrar en este intent lo que es riesgo directo al gate bloqueante: unificar gitleaks a una versión y fijarla, pinnar `ruff`/`pip-audit` en el paso que los instala, pinnar `vitest`, y auditar el entorno instalado (no `-r`); el pin de acciones por SHA se decide en ci-pipeline.

## Q6 — Granularidad y holgura del piso de cobertura backend (FR11)

El piso `cov-fail-under` se fija al valor medido y solo sube por trinquete
(regla afirmada). Dos matices a decidir:

- A. Line-coverage total (un único `--cov-fail-under` en `pytest.ini`),
  piso = valor medido exacto (sin margen); si aparece flapping, se arregla el
  test no-determinista, nunca se baja el piso. El piso se fija al FINAL del
  escalón FR12, sobre la suite ya estabilizada. (Recomendación de calidad.)
- B. Incluir branch-coverage (`--cov-branch`) además de line, con paridad
  conceptual con el frontend (varias métricas).
- C. Piso = valor medido MENOS un pequeño margen de holgura anti-flapping.
- X. Other (please specify)

[Answer]: A. Line-coverage total (un único `--cov-fail-under` en `pytest.ini`), piso = valor medido exacto (sin margen); si aparece flapping, se arregla el test no-determinista, nunca se baja el piso; el piso se fija al FINAL del escalón FR12, sobre la suite ya estabilizada.

## Consolidated Summary Confirmation

Resumen de lo que se afirmará y promoverá a `memory/team.md` + `project.md`:

- **Way of Working / Walking Skeleton / Deployment**: baseline afirmada intacta;
  walking skeleton OFF; on-merge a Fly.io sin staging; cadena `needs:` de
  `fly-deploy.yml` NO se reordena; cada endurecimiento en commit `chore(ci)`
  aislado para rollback quirúrgico.
- **Testing Posture**: test-after; medición-antes-de-piso; piso backend
  `cov-fail-under` (line-only, valor medido exacto, sin margen) fijado al FINAL
  del escalón FR12 y solo por trinquete; cierre de la asimetría `--cov` llevando
  la misma invocación + piso a `verify`; ratchet frontend solo sube umbrales de
  `angular.json` (ya hay paridad de enforcement); coste 0 €.
- **Code Style / FR12**: promoción escalonada advisory→bloqueante = audits
  primero (pip-audit/npm audit), luego `ruff check` backend; **ESLint frontend
  EXCLUIDO de este intent (deuda diferida)**; nunca `ruff format`/`--fix` masivo;
  deuda de lint saneada quirúrgica o `per-file-ignores`/`# noqa`, NUNCA ampliando
  god-files ni routers SQL; pin OSS exacto (ruff, pip-audit, vitest) en el paso
  que instala.
- **Audits**: npm audit bloquea en `high`, pip-audit bloquea findings con fix;
  findings sin fix → allowlist versionada con caducidad; auditar el entorno
  instalado (no `-r`); unificar y fijar versión de gitleaks en ambos gates.
- **Paridad de gate (FR17.3)**: `verify` recibe cobertura backend con piso Y los
  pasos de audit/lint bloqueantes, para que el push directo a `main` no eluda el
  gate.

¿Todo correcto antes de generar/integrar los artefactos?

[Answer]: Looks correct
