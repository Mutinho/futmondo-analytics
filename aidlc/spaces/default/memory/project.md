# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance; contradictions with broader policy
> are rejected. Populated by practices-discovery and the self-learning loop.
>
> Use sparingly: most teams don't need a project layer. Reach for it
> only when this specific project needs stable, durable guidance beyond the
> team practice (for example, package-specific release checks or an additional
> regression suite for a legacy component).

## Way of Working

<!-- Project-specific specialisation. Example: -->
<!-- This monorepo requires package-scoped branch names and a package owner -->
<!-- review in addition to the team's normal merge policy. -->

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

<!-- Project-specific specialisation. -->

## Change Control

<!-- Project-specific. Mode: strict or relaxed. Strict here holds for every intent and cannot be changed from chat. -->

## Deployment

<!-- Project-specific specialisation. -->

## Code Style

<!-- Project-specific specialisation. -->

- NUNCA correr `ruff format` masivo sobre archivos brownfield ya modificados: infla diffs con reflow ajeno, expone avisos preexistentes y (al cambiar bytes) invalida el pase de revisión en vuelo. Formatear SOLO los archivos nuevos de la unidad, o de forma quirúrgica; la reviewer solo corre `ruff check` (no `format`), así que el binding de la fuente reclamada se mantiene estable durante su pasada si los archivos nuevos ya están formateados. (learned 2026-09-16) <!-- cid:260914-durabilidad-estado-y-cre:code-generation:d7c0abb41ccada61c3f057facae6ffcf14f199480e188a8fca2562657840933c -->

## Tech Stack

<!-- Technology choices locked for this project. -->

## Decided

<!-- Decisions made in earlier stages that should not be re-asked. -->
<!-- Format: DECIDED: [decision] (Stage [slug], [date]) -->

## Scope Overrides

<!-- Custom scope rules for this project. -->

## Forbidden

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: NEVER [behavior] (affirmed [date]) -->
<!-- Example: NEVER throw exceptions across service layer boundaries (affirmed 2026-05-17) -->

- NEVER almacenar la contraseña Futmondo en claro: ni en memoria (deuda actual de (affirmed 2026-09-15)

`UserSession`, FR5) ni en la base de datos al diseñar la durabilidad. (El orden de (affirmed 2026-09-15)

preferencia entre re-autenticación y cifrado en reposo se decide en diseño, no aquí.) (affirmed 2026-09-15)

- NEVER usar un `JWT_SECRET` por defecto en producción; el arranque del servicio web (affirmed 2026-09-15)

exige un secreto no-default (NFR1.1; endurecido en `test_jwt_startup.py`). (affirmed 2026-09-15)

- NEVER almacenar la contraseña Futmondo en claro: ni en memoria ni en base de datos. (affirmed 2026-09-18)

- NEVER usar un `JWT_SECRET` por defecto en producción. (affirmed 2026-09-18)

- NEVER ampliar los god-files existentes (`data_sync_service.py` ~84 KB, (affirmed 2026-09-18)

`data_manager_v2.py` ~166 KB) ni el patrón SQL-en-router al tocar el cálculo de premios; (affirmed 2026-09-18)

el código nuevo va tras una capa/función estrecha testeable. (affirmed 2026-09-18)

- NEVER correr `ruff format` masivo sobre archivos brownfield ya modificados (infla diffs, (affirmed 2026-09-18)

expone avisos preexistentes e invalida el pase de revisión en vuelo); formatear solo los (affirmed 2026-09-18)

archivos nuevos o de forma quirúrgica. (affirmed 2026-09-18)

- NEVER bajar/relajar un umbral de cobertura para pasar el gate; el ratcheting solo sube. (Q7-A) (affirmed 2026-09-18)

- NEVER hardcodear secretos/tokens reales en specs; los tests de auth usan fakes/dobles (gitleaks escanea `*.spec.ts`). (Q7-C) (affirmed 2026-09-18)

- NEVER reintroducir `skipTests: true` en los schematics donde se retire. (Q7-E) (affirmed 2026-09-18)

- NEVER almacenar la contraseña Futmondo en claro (ni en memoria ni en base de datos). (affirmed 2026-09-18)

- NEVER ampliar los god-files existentes (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router. (affirmed 2026-09-18)

- NEVER correr `ruff format` masivo sobre archivos brownfield ya modificados; formatear solo los archivos nuevos o de forma quirúrgica. (affirmed 2026-09-18)

- NEVER ampliar los god-files existentes (`data_sync_service.py` ~84 KB / 1915 líneas, `data_manager_v2.py` ~166 KB) ni el patrón SQL-en-router al tocar el manejo de errores o los contratos de integración; el código nuevo va tras una capa/función estrecha testeable. (affirmed 2026-09-24)

- NEVER traer al alcance de este intent los `except: pass` de `data_manager_v2.py` (Intent 3, god-file) ni de `photo_service.py` (Q6): quedan como **deuda registrada**; la primera oleada FR3.2 se mantiene en arranque/migraciones/`db_connection.py`/clientes + los puntos de corrupción de `data_sync_service.py`. (affirmed 2026-09-24)

- NEVER incluir el password ni el token Futmondo del usuario en el mensaje, el `repr` ni el `exc_info` de una excepción de integración (Q5); las excepciones llevan modo de fallo + contexto no sensible (status, endpoint), nunca material de credencial. (Extiende las reglas afirmadas de no-credenciales-en-claro.) (affirmed 2026-09-24)

- NEVER usar `return None` silencioso como señal de fallo en el cliente de integración; el modo de fallo se expone como excepción tipada propagada (FR4). (affirmed 2026-09-24)

- NEVER tragar un fallo que pueda **corromper datos** tras un commit previo (p. ej. el `DELETE FROM team_prizes ... NOT IN (...)` cuyo `try/except → logger.warning` deja la caché en estado mixto sin señal al consumidor); usar reemplazo transaccional atómico como el patrón de referencia ya caracterizado. (affirmed 2026-09-24)

- NEVER correr `ruff format` masivo sobre archivos brownfield ya modificados (infla diffs, expone avisos preexistentes e invalida el pase de revisión en vuelo); formatear sólo los archivos nuevos o de forma quirúrgica. (affirmed 2026-09-24)

- NEVER bajar/relajar un umbral o piso de cobertura para pasar el gate; el ratcheting sólo sube. (affirmed 2026-09-24)

- NEVER almacenar la contraseña Futmondo en claro (ni en memoria ni en base de datos). (affirmed 2026-09-24)

- NEVER usar un `JWT_SECRET` por defecto en producción. (affirmed 2026-09-24)

- NEVER introducir dependencias de pago; cualquier librería nueva sería OSS y fijada a versión exacta (no se prevé ninguna, stdlib suficiente). (affirmed 2026-09-24)

- NEVER bajar/relajar un umbral o piso de cobertura para pasar el gate; el ratchet (backend y frontend) sólo sube. (affirmed 2026-09-25)

- NEVER dejar `continue-on-error` permanente en un check promovido a bloqueante ni silenciar un audit borrándolo o bajando su nivel global; los findings sin fix van a la allowlist versionada con caducidad, nunca a un silenciador permanente (Q3). (affirmed 2026-09-25)

- NEVER auditar los rangos declarados de `requirements.txt` (`pip-audit -r …`) para el gate bloqueante; se audita el entorno instalado/resuelto para evitar findings intermitentes y no reproducibles (Q5). (affirmed 2026-09-25)

- NEVER correr dos versiones distintas del escáner de secretos hacia `main`; gitleaks se unifica y se fija en ambos gates (Q5). (affirmed 2026-09-25)

- NEVER instalar ESLint ni tocar las devDependencies del frontend en este intent: ESLint frontend queda como **deuda diferida**; el frontend sólo sube el ratchet de cobertura (Q1). (affirmed 2026-09-25)

- NEVER correr `ruff format` / Prettier en masa sobre ficheros brownfield ya modificados (infla diffs, expone avisos preexistentes e invalida el pase de revisión en vuelo); formatear sólo los ficheros nuevos o de forma quirúrgica. (affirmed 2026-09-25)

- NEVER usar `--fix` masivo de ruff (ni `ruff check --fix` de repo entero) al promover `ruff check` a bloqueante; la promoción es un cambio de configuración aislado, sin reformateo. (affirmed 2026-09-25)

- NEVER acallar la deuda de lint ampliando ni reescribiendo los god-files (`data_sync_service.py` ~84 KB, `data_manager_v2.py` ~166 KB, `assistant_service.py` ~51 KB) ni los routers SQL-en-endpoint; la deuda se sanea por fichero de forma quirúrgica o se suprime con `per-file-ignores`/`# noqa` puntual con rationale (Q1, OBJECT desarrollador). (affirmed 2026-09-25)

- NEVER ampliar los god-files existentes ni el patrón SQL-en-router; este intent es config-only de CI/CD y no es excusa para refactor de oportunidad. (affirmed 2026-09-25)

- NEVER introducir dependencias de pago ni servicios que fuercen salir de los tiers gratuitos; cualquier librería nueva es OSS y fijada a versión exacta. (affirmed 2026-09-25)

- NEVER promover un check a bloqueante de golpe sin sanear/silenciar quirúrgicamente antes la deuda heredada que reportaría (promoción escalonada, no big-bang). (affirmed 2026-09-25)

- NEVER añadir margen de holgura al piso de cobertura backend para evitar rojos por flapping; el piso es el valor medido exacto y el flapping se resuelve arreglando el test no-determinista (Q6). (affirmed 2026-09-25)

- NEVER incluir `--cov-branch` en el piso backend de este intent; el piso es line-coverage total (line-only) (Q6). (affirmed 2026-09-25)

- NEVER hardcodear secretos/tokens reales en workflows ni en specs; los secretos van vía `secrets` de GitHub Actions / Fly.io y en CI el `JWT_SECRET` es efímero y no productivo. (affirmed 2026-09-25)

- NEVER reordenar la cadena `needs:` de `fly-deploy.yml` (`verify` → `deploy-backend` → `deploy-frontend` → `smoke-test`) al endurecer el gate; el endurecimiento refuerza el contenido de `verify`, no su topología. (affirmed 2026-09-25)

- NEVER hardcodear secretos/tokens reales en el repo (código, specs, workflows ni (affirmed 2026-10-06)

documentos de análisis): los secretos van vía `secrets` de GitHub Actions / (affirmed 2026-10-06)

Fly.io y en CI el `JWT_SECRET` es efímero y no productivo (gitleaks escanea (affirmed 2026-10-06)

todo el árbol). (affirmed 2026-10-06)

- NEVER introducir dependencias de pago ni servicios que fuercen salir de los (affirmed 2026-10-06)

tiers gratuitos (salvo la excepción acotada de publicación de distribución (affirmed 2026-10-06)

nativa anotada arriba); cualquier librería que se proponga en la ruta de (affirmed 2026-10-06)

implementación sería OSS y fijada a versión exacta. (affirmed 2026-10-06)

- NEVER almacenar la contraseña Futmondo en claro (ni en memoria ni en base de (affirmed 2026-10-06)

datos); cualquier modelo de sesión que proponga el análisis nativo debe (affirmed 2026-10-06)

preservar esta garantía. Al perder la cookie `HttpOnly` del navegador, el (affirmed 2026-10-06)

refresh token debe ir a **almacenamiento seguro nativo** (iOS Keychain / (affirmed 2026-10-06)

Android Keystore vía `@nativescript/secure-storage`), **NUNCA** a (affirmed 2026-10-06)

`ApplicationSettings` ni `localStorage` en claro (regla durable de seguridad, (affirmed 2026-10-06)

central al riesgo de portabilidad del modelo de sesión). (affirmed 2026-10-06)

- NEVER almacenar la contraseña Futmondo en claro (ni en memoria ni en base de (affirmed 2026-10-18)

datos); cualquier modelo de sesión del cliente nativo debe preservar esta (affirmed 2026-10-18)

garantía (el refresh token va a **almacenamiento seguro nativo** — iOS Keychain (affirmed 2026-10-18)

—, NUNCA a `localStorage` ni almacenamiento en claro). (affirmed 2026-10-18)

- NEVER usar un `JWT_SECRET` por defecto en producción; el arranque del servicio (affirmed 2026-10-18)

web exige un secreto no-default (NFR1.1). (affirmed 2026-10-18)

- NEVER bajar/relajar un umbral o piso de cobertura para pasar el gate; el (affirmed 2026-10-18)

ratcheting sólo sube, y el flapping se arregla en el test no-determinista. (affirmed 2026-10-18)

- NEVER correr `ruff format` masivo ni `--fix` de repo entero (ni Prettier (affirmed 2026-10-18)

masivo) sobre ficheros brownfield ya modificados (infla diffs, expone avisos (affirmed 2026-10-18)

preexistentes e invalida el pase de revisión en vuelo); formatear sólo los (affirmed 2026-10-18)

ficheros nuevos o de forma quirúrgica. (affirmed 2026-10-18)

- NEVER ampliar los god-files existentes (`data_sync_service.py`, (affirmed 2026-10-18)

`data_manager_v2.py`, `assistant_service.py`, `photo_service.py`) ni el patrón (affirmed 2026-10-18)

SQL-en-router; este intent de diseño no es excusa para refactor de oportunidad. (affirmed 2026-10-18)

- NEVER introducir dependencias de pago ni tooling de diseño de pago; cualquier (affirmed 2026-10-18)

librería nueva sería OSS y fijada a versión exacta (no se prevé ninguna para la (affirmed 2026-10-18)

capa de diseño, que se cubre con el SDK de Apple). (affirmed 2026-10-18)

## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

- ALWAYS mantener el proyecto a coste 0 €: descartar toda mejora o dependencia con (affirmed 2026-09-15)

gasto recurrente; solo soluciones sostenibles en tiers gratuitos (Neon free, (affirmed 2026-09-15)

Fly.io free allowance, GitHub Actions free). (ya afirmada en `project.md`) (affirmed 2026-09-15)

- ALWAYS pasar el gate de CI bloqueante (gitleaks + `pytest` + `ng test`) antes de (affirmed 2026-09-15)

fusionar a `main`; un rojo nunca llega a producción. (affirmed 2026-09-15)

- ALWAYS caracterizar (congelar con tests) el comportamiento de `SessionStore` y (affirmed 2026-09-15)

`TaskManager` antes de refactorizarlos hacia durabilidad (characterization-first; (affirmed 2026-09-15)

hoy no tienen cobertura directa). (affirmed 2026-09-15)

- ALWAYS mantener el proyecto a **coste 0 €**: descartar toda mejora o dependencia con (affirmed 2026-09-18)

gasto recurrente; solo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free (affirmed 2026-09-18)

allowance, GitHub Actions free). (affirmed 2026-09-18)

- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `pytest` + `ng test`) antes de (affirmed 2026-09-18)

fusionar a `main`; un rojo nunca llega a producción. (affirmed 2026-09-18)

- ALWAYS **caracterizar (congelar con tests) el comportamiento de `sync_prizes` en TODAS (affirmed 2026-09-18)

sus ramas antes de refactorizarlo** hacia la mejora del cálculo de premios (affirmed 2026-09-18)

(characterization-first, Q2=A): `points_prize`, gating `round_fully_played`, ranking (affirmed 2026-09-18)

flop/top, MVP, dream-team, jornada adelantada/negativa y el borrado defensivo (affirmed 2026-09-18)

`DELETE ... NOT IN`. Hoy la producción del premio tiene cobertura directa cero. Extiende a (affirmed 2026-09-18)

este intent el mandato ya afirmado de characterization-first para `SessionStore`/`TaskManager`. (affirmed 2026-09-18)

- ALWAYS exigir un `JWT_SECRET` **no-default** en el arranque del servicio web (NFR1.1; (affirmed 2026-09-18)

endurecido en `test_jwt_startup.py`). (affirmed 2026-09-18)

Afirmadas en la entrevista de ESTE intent (Q7): (affirmed 2026-09-18)

- ALWAYS verificar `npm ci` + `ng test` en contenedor `node:22.22.3` antes de pushear cambios de devDependencies del frontend. (Q7-B) (affirmed 2026-09-18)

- ALWAYS fijar versión exacta (pin) del proveedor de cobertura `@vitest/coverage-v8` (OSS, coste 0 €); nada de rangos abiertos en un gate bloqueante. (Q7-D) (affirmed 2026-09-18)

Arrastradas (ya afirmadas, siguen vigentes): (affirmed 2026-09-18)

- ALWAYS mantener el proyecto a coste 0 €: descartar toda mejora o dependencia con gasto recurrente; solo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free). (affirmed 2026-09-18)

- ALWAYS pasar el gate de CI bloqueante (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`; un rojo nunca llega a producción. (affirmed 2026-09-18)

- ALWAYS exigir un `JWT_SECRET` no-default en el arranque del servicio web (NFR1.1; endurecido en `test_jwt_startup.py`). (affirmed 2026-09-18)

- ALWAYS mantener el proyecto a **coste 0 €**: descartar toda mejora o dependencia con gasto recurrente; sólo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free). (affirmed 2026-09-24)

- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`; un rojo nunca llega a producción. (affirmed 2026-09-24)

- ALWAYS **caracterizar (congelar con tests) el comportamiento brownfield antes de endurecerlo** (characterization-first): extiende el mandato ya afirmado para `sync_prizes`/`SessionStore`/`TaskManager` a cada broad-except / `except: pass` de la primera oleada FR3.2 que se reclasifique y al contrato de `futmondo_client._make_request` ANTES de cambiar su señal de fallo. (affirmed 2026-09-24)

- ALWAYS **caracterizar los llamadores de `futmondo_client._make_request` y entregar un inventario verificable de llamadores** ANTES del cambio de contrato de integración (Q4); la migración cubre el núcleo (`_make_request` + los llamadores donde un `None` no detectado corrompe datos) y el resto queda como deuda registrada. (affirmed 2026-09-24)

- ALWAYS **aseverar el EFECTO en los specs de modo de fallo** (Q1): recuperable → paso marcado `DEGRADED` vía `sync_step_status.py` y la operación NO falla; fatal → excepción tipada propagada Y sin datos a medias escritos. NUNCA un `pytest.raises` sin aserción de estado (nada de specs espejo que capturan sin aseverar el efecto). (affirmed 2026-09-24)

- ALWAYS exigir un `JWT_SECRET` **no-default** en el arranque del servicio web (NFR1.1; endurecido en `test_jwt_startup.py`). (affirmed 2026-09-24)

- ALWAYS señalar el fallo de integración externa como **excepción tipada por modo de fallo, propagada** (extendiendo `SofascoreIPBanError`), con `except <Typed>: raise` antes del `except Exception` genérico. (affirmed 2026-09-24)

- ALWAYS distinguir en el manejo de errores lo **recuperable** (degrada y continúa; marca `StepStatus.DEGRADED` vía `sync_step_status.py`, sin corromper datos) de lo **fatal** (aborta limpio, sin dejar datos a medias). (affirmed 2026-09-24)

- ALWAYS que los tests usen dobles/fakes en memoria (patrón `conftest.py`), sin red, sin DB real y sin credenciales/tokens reales (gitleaks escanea los tests). (affirmed 2026-09-24)

- ALWAYS mantener el proyecto a **coste 0 €**: sólo tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free); descartar toda mejora o dependencia con gasto recurrente. (affirmed 2026-09-25)

- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`; un rojo nunca llega a producción. (affirmed 2026-09-25)

- ALWAYS introducir el piso de cobertura backend como un **único `--cov-fail-under` en `pytest.ini`** (line-coverage total, dentro del mismo `addopts` de `pytest`), fijándolo al **valor medido exacto SIN margen** y al FINAL del escalón FR12 sobre la suite ya estabilizada; subirlo **sólo por trinquete** (el ratchet sólo sube). Si aparece flapping, arreglar el test no-determinista, nunca bajar el piso (FR11, Q6). (affirmed 2026-09-25)

- ALWAYS cerrar la asimetría de la señal de cobertura backend llevando la misma invocación con `--cov` y el mismo piso al job `verify` de `fly-deploy.yml` (paridad con `ci.yml`), aterrizando esa paridad en el **mismo commit** (o inmediatamente después) que introduce el piso en `ci.yml`, de modo que el push directo a `main` no pueda saltarse el piso (FR17.3, Q4). (affirmed 2026-09-25)

- ALWAYS dar **paridad real de gate PR ↔ push** AÑADIENDO al job `verify` de `fly-deploy.yml` los pasos de audit (`pip-audit`/`npm audit`) y lint (`ruff check` backend) que se vuelvan bloqueantes — hoy `verify` no los tiene: es añadir pasos, no flipear un flag (FR17.3, Q4). (affirmed 2026-09-25)

- ALWAYS promover linters/audits de advisory a bloqueante de forma **escalonada** (FR12): primero los audits de dependencias, luego el lint (`ruff check` backend), cada promoción en su propio commit `chore(ci)` aislado con el trinquete fijado explícitamente (Q1). (affirmed 2026-09-25)

- ALWAYS bloquear **npm audit en `high`** (no critical-only); si `high` genera demasiado ruido heredado de golpe, promover primero en `critical`, sanear y endurecer a `high` en commit posterior — el trinquete de severidad SÓLO endurece (Q2). (affirmed 2026-09-25)

- ALWAYS bloquear en **pip-audit todo finding CON fix disponible**, gobernando los findings SIN fix por allowlist versionada (Q2). (affirmed 2026-09-25)

- ALWAYS ejecutar `pip-audit` sobre el **entorno instalado/resuelto tras `pip install` (sin `-r`)**, no sobre los rangos de `requirements.txt`, para un gate reproducible (Q5). (affirmed 2026-09-25)

- ALWAYS registrar los findings sin fix en una **allowlist versionada y auditada**, commiteada, con ID del advisory/CVE, dependencia+versión, motivo, fecha y **fecha de caducidad/revisión**, vía `pip-audit --ignore-vuln <ID>` y el equivalente versionado en npm; una entrada caducada vuelve a bloquear (Q3). (affirmed 2026-09-25)

- ALWAYS **unificar gitleaks a una única versión y fijarla en AMBOS gates** (`ci.yml` y el job `verify` de `fly-deploy.yml`), que hoy corren `@v3` vs `@v2` (Q5). (affirmed 2026-09-25)

- ALWAYS fijar a **versión exacta EN EL PASO QUE LA INSTALA** cada dependencia de tooling del gate bloqueante; en este intent: `ruff` y `pip-audit` (hoy `pip install ruff` sin pin) y `vitest` (hoy rango abierto `^4.0.8` frente a `@vitest/coverage-v8 == 4.1.11`) (Q5). (affirmed 2026-09-25)

- ALWAYS aislar cada endurecimiento (piso de cobertura, promoción advisory→bloqueante, unificación/pin de versión) en su propio commit `chore(ci)` con el trinquete fijado, para rollback quirúrgico. (affirmed 2026-09-25)

- ALWAYS sanear la **deuda de lint pre-bloqueo** POR FICHERO de forma quirúrgica, o suprimirla con `per-file-ignores` / `# noqa` puntual con rationale, ANTES de promover `ruff check` a bloqueante (Q1, OBJECT desarrollador). (affirmed 2026-09-25)

- ALWAYS que los tests usen dobles/fakes en memoria (patrón `conftest.py`), sin red, sin BD real y sin credenciales/tokens reales (gitleaks escanea también los tests); specs que aseveran el efecto, nunca `assert True` ni specs espejo que inflen cobertura. (affirmed 2026-09-25)

- ALWAYS verificar `npm ci` + `ng test` en contenedor `node:22.22.3` antes de pushear cualquier cambio de devDependencies del frontend. (affirmed 2026-09-25)

- ALWAYS mantener `angular.json` (`coverageThresholds`) como fuente única de umbral de cobertura frontend, con el enforcement dentro de `ng test` (sin pasos extra ni `continue-on-error`); en este intent el frontend **sólo sube el ratchet**, no crea paridad (ya la tiene en ambos workflows). (affirmed 2026-09-25)

- ALWAYS usar identificadores/docstrings/comentarios en INGLÉS y texto de usuario / mensajes de commit (Conventional Commits con scope) en CASTELLANO. (affirmed 2026-09-25)

- ALWAYS mantener el proyecto a **coste 0 €**: sólo soluciones sostenibles en (affirmed 2026-10-06)

tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free); (affirmed 2026-10-06)

descartar toda mejora o dependencia con gasto recurrente. **Excepción aceptada y (affirmed 2026-10-06)

acotada**: el **coste de publicación de distribución nativa** (Apple Developer (affirmed 2026-10-06)

Program ~99 €/año; Google Play Developer) es una excepción conocida y bounded a (affirmed 2026-10-06)

este mandato, exclusivamente para habilitar la distribución de una app nativa; el (affirmed 2026-10-06)

análisis de viabilidad lo documenta como coste recurrente de distribución. Para (affirmed 2026-10-06)

todo lo demás, el mandato de coste 0 € sigue durable y sin relajar. (affirmed 2026-10-06)

- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `ruff check` + `pytest` + (affirmed 2026-10-06)

`pip-audit` + `ng test` + `npm audit`) antes de fusionar a `main`, también para (affirmed 2026-10-06)

cambios puramente documentales; un rojo nunca llega a producción. (affirmed 2026-10-06)

- ALWAYS mantener el **escaneo de dependencias (`pip-audit` / `npm audit`) y de (affirmed 2026-10-06)

secretos (`gitleaks`) como control de cadena de suministro durable y (affirmed 2026-10-06)

BLOQUEANTE en AMBOS gates** (`ci.yml` job `quality` y `fly-deploy.yml` job (affirmed 2026-10-06)

`verify`), de modo que un secreto o una dependencia vulnerable nunca llegue a (affirmed 2026-10-06)

producción. (Control permanente; separado de la mecánica intent-específica de (affirmed 2026-10-06)

promoción escalonada, allowlist versionada con caducidad o pin de versiones (affirmed 2026-10-06)

concretas de tooling, que NO es una regla de equipo durable.) (affirmed 2026-10-06)

- ALWAYS usar **identificadores, docstrings y comentarios en INGLÉS** y **texto (affirmed 2026-10-06)

de cara al usuario / mensajes de commit en CASTELLANO** (Conventional Commits (affirmed 2026-10-06)

con scope); en los documentos de análisis, prosa en castellano y tokens (affirmed 2026-10-06)

técnicos (frameworks, rutas, claves YAML) verbatim en inglés. (affirmed 2026-10-06)

- ALWAYS mantener el proyecto a **coste 0 €**: sólo soluciones sostenibles en (affirmed 2026-10-18)

tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free); (affirmed 2026-10-18)

descartar toda mejora o dependencia con gasto recurrente. El sistema de diseño (affirmed 2026-10-18)

nativo iOS se sostiene con el **SDK de Apple** (coste 0 €), sin tooling de (affirmed 2026-10-18)

diseño de pago. **Excepción aceptada y acotada**: el coste de publicación de (affirmed 2026-10-18)

distribución nativa (Apple Developer Program ~99 €/año) es la única excepción (affirmed 2026-10-18)

conocida y bounded, sólo para habilitar la distribución de la app nativa. (affirmed 2026-10-18)

- ALWAYS pasar el **gate de CI bloqueante** (gitleaks + `ruff check` + `pytest` + (affirmed 2026-10-18)

`pip-audit` + `ng test` + `npm audit`) antes de fusionar a `main`, también para (affirmed 2026-10-18)

cambios de diseño/documentales; un rojo nunca llega a producción. (affirmed 2026-10-18)

- ALWAYS reproducir en **SwiftUI** (sólo SDK de Apple, coste 0 €) el tema del (affirmed 2026-10-18)

frontend Angular existente como **fuente de verdad** del diseño nativo iOS (affirmed 2026-10-18)

(`angular-app/src/styles.scss`: Material 3 paleta primaria verde, terciaria (affirmed 2026-10-18)

violeta, tipografía `Roboto`, modo claro/oscuro vía Material + `body.dark-theme`, (affirmed 2026-10-18)

tokens semánticos `money-positive`/`money-negative`, escala `h1`/`h2`/`h3`, (affirmed 2026-10-18)

gradiente de splash verde). **Google Stitch queda descartado** como referencia (affirmed 2026-10-18)

(decisión del propietario, 2026-10-18). Donde Material 3 no tenga equivalente (affirmed 2026-10-18)

1:1 en SwiftUI, cubrir con **Apple HIG** sin introducir dependencias de pago. (affirmed 2026-10-18)

- ALWAYS usar **identificadores, docstrings y comentarios en INGLÉS** y **texto (affirmed 2026-10-18)

de cara al usuario / mensajes de commit en CASTELLANO** (Conventional Commits (affirmed 2026-10-18)

con scope); en la prosa de los artefactos de diseño, castellano con tokens (affirmed 2026-10-18)

técnicos verbatim en inglés. (affirmed 2026-10-18)

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->
- ALWAYS mantener el proyecto a coste 0€: descartar toda mejora o dependencia con gasto recurrente; solo proponer soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free) (learned 2026-09-11) <!-- cid:260911-analisis-mejoras:intent-capture:a64ea58ac71fc6e7985eddb4c78948ff11827c7ed40537a25c6fac73a6bb3c81 -->
- ALWAYS verificar npm ci y ng test en local (o revisar el lock) antes de pushear tras cambiar devDependencies del frontend, para no romper el gate de CI (learned 2026-09-14) <!-- cid:260912-analytics-tests-fix:deployment-execution:0ea68257a2ff0bccf48656b5ace52be1efaf362d3166078342c2a0491ce27727 -->
- ALWAYS verificar el build/tests del frontend en un contenedor `node:<versión de .nvmrc>` (con volumen anónimo para `node_modules`) cuando el Node local no alcance el mínimo que exige el Angular CLI; coste 0€ (learned 2026-09-14) <!-- cid:260914-ci-tooling-mejoras:deployment-execution:4a9616552729869fa85366642edb5f7079643479f82a6cf5c5d3baeb8674792c -->
- Para reproducir la suite de pytest en local a coste 0 cuando el Python del sistema es más nuevo que el de CI, crear un venv efímero excluyendo `libsql-experimental` (no compila fuera de 3.12 y no lo ejercitan los tests, que usan el fake SQLite) y fijar un `JWT_SECRET` de arranque efímero. (learned 2026-09-16) <!-- cid:260914-durabilidad-estado-y-cre:build-and-test:f52ef2ddf207ebcfd3e714b2c51187edc37270edcd4e578e7a7026806759a479 -->
- En etapas de Operation cuyo conocimiento asume AWS/CloudWatch, adaptar al stack real (Fly.io + Neon) y al mandato de coste 0 €: generar artefactos con las herramientas gratuitas disponibles (`fly logs`, healthcheck, logging estructurado) y marcar explícitamente como NO-APLICA/diferido lo que exige servicios de pago (SLO formales con burn-rate, tracing distribuido, anomaly detection ML), documentando la alternativa gratuita en vez de inventar infraestructura inexistente. (learned 2026-09-16) <!-- cid:260914-durabilidad-estado-y-cre:observability-setup:f9a04574d004210fe9d1df0e23a826a072857aa96e41777667e6c0e7237d8e61 -->
- ALWAYS reproducir en SwiftUI (con solo SDK de Apple, coste 0 €) el tema del frontend Angular existente como fuente de verdad del diseno de la app nativa iOS: `angular-app/src/styles.scss` (Material 3 paleta primaria verde `mat.$green-palette` / terciaria violeta, tipografia Roboto, modo claro/oscuro via `body.dark-theme`, y tokens semanticos propios `money-positive`/`money-negative`, escala `h1`/`h2`/`h3`, gradiente de splash verde). Google Stitch queda descartado como referencia (decision del propietario, 2026-10-18). Donde Material 3 no tenga equivalente 1:1 en SwiftUI, cubrir con Apple HIG sin introducir dependencias de pago. (learned 2026-10-18) <!-- cid:261018-design-system-nativo:feasibility:a5f2ab6a02bfdec630b8eb2f08dad9c2002a381b6639b58b7cbef59348726e9f -->
- Al construir la app nativa iOS desde Linux/WSL con el toolchain de Swift, `actool` (asset catalog compiler) NO está disponible, así que los Color Sets del sistema de diseño se definen EN CÓDIGO (hex claro/oscuro con fuente única en un token Swift, p. ej. `DSColorToken`), no en `Assets.xcassets`; la migración a asset catalog se difiere a cuando se construya en dispositivo con `xtool`. Mantener `Package.swift` sin `resources` del asset catalog en ese caso. (learned 2026-10-19) <!-- cid:261018-design-system-nativo:code-generation:34bf8e5b58745fabbba280244fef2f6385fb7f10c430f597f103e702cef8e596 -->
- La cobertura de línea vía llvm-cov NO es medible de forma fiable con el toolchain de Swift en Linux/WSL; para código iOS, el piso de cobertura no se verifica numéricamente en WSL. La lógica pura testeable se coloca en el target library (`FutmondoKit`) y se cubre con XCTest ejecutable (`swift test`); las vistas SwiftUI van en el target de app guardadas con `#if canImport(SwiftUI)` y se validan en dispositivo (arnés de UI nativo diferido), quedando fuera del cómputo de cobertura. (learned 2026-10-19) <!-- cid:261018-design-system-nativo:code-generation:6748388652678b62542b349c903ab36e5bae4948e5dc8ee56ad35cafd52eef3d -->
- En SwiftUI, el crossfade skeleton→contenido NO se consigue con `.transition(.opacity)` en las ramas de un `switch` (SwiftUI reemplaza el subárbol y el contenido aparece de golpe); usar un `ZStack` con AMBAS capas montadas y opacidad cruzada por un flag `isLoading` (componente reutilizable `CrossfadeLoader`), animado con `.animation(value: isLoading)` y gated por Reduce Motion. (learned 2026-10-23) <!-- cid:261022-favoritos-nativa:build-and-test:23d3065b018b6601ae7457f8d3ff166e3f39f11cd7fb276b04bb02e5dc3ff038 -->
- Skeleton de carga nativo iOS a coste 0 y con efecto moderno: relleno con gradiente de marca en movimiento (`AuroraFill`, verde→violeta del design system, drift en bucle) + entrada escalonada + crossfade al contenido, como componentes reutilizables (`SkeletonCard`/`SkeletonRow`/`SkeletonHeader`/`SkeletonScreen`/`SkeletonListScreen` en `FutmondoApp/Shared/`), respetando Reduce Motion. Preferir esto al spinner + 'Cargando…'. Las pantallas con lista de FILAS (p. ej. Presupuesto) necesitan su propio `SkeletonRow` fiel a la fila real, no el grid de tiles. (learned 2026-10-23) <!-- cid:261022-favoritos-nativa:build-and-test:12549635ef118737b5ab4532525bbde5289d1642a7d255ffee3bc970a643743a -->
