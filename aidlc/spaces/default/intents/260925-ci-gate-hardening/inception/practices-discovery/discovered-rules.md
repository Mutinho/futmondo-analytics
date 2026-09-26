# Practices Discovery — Discovered Rules

**Collaborator:** aidlc-pipeline-deploy-agent

Sólo restricciones **duras declaradas por el humano** (baseline afirmada en
`memory/team.md` + `memory/project.md`, más las específicas de ESTE intent de
endurecimiento del gate CI/CD, con las decisiones de la entrevista Q1–Q6 ya
integradas). No se inventan reglas de estilo blandas.

## Mandated

- ALWAYS mantener el proyecto a **coste 0 €**: sólo tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free); descartar toda mejora o dependencia con gasto recurrente.
- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`; un rojo nunca llega a producción.
- ALWAYS introducir el piso de cobertura backend como un **único `--cov-fail-under` en `pytest.ini`** (line-coverage total, dentro del mismo `addopts` de `pytest`), fijándolo al **valor medido exacto SIN margen** y al FINAL del escalón FR12 sobre la suite ya estabilizada; subirlo **sólo por trinquete** (el ratchet sólo sube). Si aparece flapping, arreglar el test no-determinista, nunca bajar el piso (FR11, Q6).
- ALWAYS cerrar la asimetría de la señal de cobertura backend llevando la misma invocación con `--cov` y el mismo piso al job `verify` de `fly-deploy.yml` (paridad con `ci.yml`), aterrizando esa paridad en el **mismo commit** (o inmediatamente después) que introduce el piso en `ci.yml`, de modo que el push directo a `main` no pueda saltarse el piso (FR17.3, Q4).
- ALWAYS dar **paridad real de gate PR ↔ push** AÑADIENDO al job `verify` de `fly-deploy.yml` los pasos de audit (`pip-audit`/`npm audit`) y lint (`ruff check` backend) que se vuelvan bloqueantes — hoy `verify` no los tiene: es añadir pasos, no flipear un flag (FR17.3, Q4).
- ALWAYS promover linters/audits de advisory a bloqueante de forma **escalonada** (FR12): primero los audits de dependencias, luego el lint (`ruff check` backend), cada promoción en su propio commit `chore(ci)` aislado con el trinquete fijado explícitamente (Q1).
- ALWAYS bloquear **npm audit en `high`** (no critical-only); si `high` genera demasiado ruido heredado de golpe, promover primero en `critical`, sanear y endurecer a `high` en commit posterior — el trinquete de severidad SÓLO endurece (Q2).
- ALWAYS bloquear en **pip-audit todo finding CON fix disponible**, gobernando los findings SIN fix por allowlist versionada (Q2).
- ALWAYS ejecutar `pip-audit` sobre el **entorno instalado/resuelto tras `pip install` (sin `-r`)**, no sobre los rangos de `requirements.txt`, para un gate reproducible (Q5).
- ALWAYS registrar los findings sin fix en una **allowlist versionada y auditada**, commiteada, con ID del advisory/CVE, dependencia+versión, motivo, fecha y **fecha de caducidad/revisión**, vía `pip-audit --ignore-vuln <ID>` y el equivalente versionado en npm; una entrada caducada vuelve a bloquear (Q3).
- ALWAYS **unificar gitleaks a una única versión y fijarla en AMBOS gates** (`ci.yml` y el job `verify` de `fly-deploy.yml`), que hoy corren `@v3` vs `@v2` (Q5).
- ALWAYS fijar a **versión exacta EN EL PASO QUE LA INSTALA** cada dependencia de tooling del gate bloqueante; en este intent: `ruff` y `pip-audit` (hoy `pip install ruff` sin pin) y `vitest` (hoy rango abierto `^4.0.8` frente a `@vitest/coverage-v8 == 4.1.11`) (Q5).
- ALWAYS aislar cada endurecimiento (piso de cobertura, promoción advisory→bloqueante, unificación/pin de versión) en su propio commit `chore(ci)` con el trinquete fijado, para rollback quirúrgico.
- ALWAYS sanear la **deuda de lint pre-bloqueo** POR FICHERO de forma quirúrgica, o suprimirla con `per-file-ignores` / `# noqa` puntual con rationale, ANTES de promover `ruff check` a bloqueante (Q1, OBJECT desarrollador).
- ALWAYS que los tests usen dobles/fakes en memoria (patrón `conftest.py`), sin red, sin BD real y sin credenciales/tokens reales (gitleaks escanea también los tests); specs que aseveran el efecto, nunca `assert True` ni specs espejo que inflen cobertura.
- ALWAYS verificar `npm ci` + `ng test` en contenedor `node:22.22.3` antes de pushear cualquier cambio de devDependencies del frontend.
- ALWAYS mantener `angular.json` (`coverageThresholds`) como fuente única de umbral de cobertura frontend, con el enforcement dentro de `ng test` (sin pasos extra ni `continue-on-error`); en este intent el frontend **sólo sube el ratchet**, no crea paridad (ya la tiene en ambos workflows).
- ALWAYS usar identificadores/docstrings/comentarios en INGLÉS y texto de usuario / mensajes de commit (Conventional Commits con scope) en CASTELLANO.

## Forbidden

- NEVER bajar/relajar un umbral o piso de cobertura para pasar el gate; el ratchet (backend y frontend) sólo sube.
- NEVER dejar `continue-on-error` permanente en un check promovido a bloqueante ni silenciar un audit borrándolo o bajando su nivel global; los findings sin fix van a la allowlist versionada con caducidad, nunca a un silenciador permanente (Q3).
- NEVER auditar los rangos declarados de `requirements.txt` (`pip-audit -r …`) para el gate bloqueante; se audita el entorno instalado/resuelto para evitar findings intermitentes y no reproducibles (Q5).
- NEVER correr dos versiones distintas del escáner de secretos hacia `main`; gitleaks se unifica y se fija en ambos gates (Q5).
- NEVER instalar ESLint ni tocar las devDependencies del frontend en este intent: ESLint frontend queda como **deuda diferida**; el frontend sólo sube el ratchet de cobertura (Q1).
- NEVER correr `ruff format` / Prettier en masa sobre ficheros brownfield ya modificados (infla diffs, expone avisos preexistentes e invalida el pase de revisión en vuelo); formatear sólo los ficheros nuevos o de forma quirúrgica.
- NEVER usar `--fix` masivo de ruff (ni `ruff check --fix` de repo entero) al promover `ruff check` a bloqueante; la promoción es un cambio de configuración aislado, sin reformateo.
- NEVER acallar la deuda de lint ampliando ni reescribiendo los god-files (`data_sync_service.py` ~84 KB, `data_manager_v2.py` ~166 KB, `assistant_service.py` ~51 KB) ni los routers SQL-en-endpoint; la deuda se sanea por fichero de forma quirúrgica o se suprime con `per-file-ignores`/`# noqa` puntual con rationale (Q1, OBJECT desarrollador).
- NEVER ampliar los god-files existentes ni el patrón SQL-en-router; este intent es config-only de CI/CD y no es excusa para refactor de oportunidad.
- NEVER introducir dependencias de pago ni servicios que fuercen salir de los tiers gratuitos; cualquier librería nueva es OSS y fijada a versión exacta.
- NEVER promover un check a bloqueante de golpe sin sanear/silenciar quirúrgicamente antes la deuda heredada que reportaría (promoción escalonada, no big-bang).
- NEVER añadir margen de holgura al piso de cobertura backend para evitar rojos por flapping; el piso es el valor medido exacto y el flapping se resuelve arreglando el test no-determinista (Q6).
- NEVER incluir `--cov-branch` en el piso backend de este intent; el piso es line-coverage total (line-only) (Q6).
- NEVER hardcodear secretos/tokens reales en workflows ni en specs; los secretos van vía `secrets` de GitHub Actions / Fly.io y en CI el `JWT_SECRET` es efímero y no productivo.
- NEVER reordenar la cadena `needs:` de `fly-deploy.yml` (`verify` → `deploy-backend` → `deploy-frontend` → `smoke-test`) al endurecer el gate; el endurecimiento refuerza el contenido de `verify`, no su topología.
