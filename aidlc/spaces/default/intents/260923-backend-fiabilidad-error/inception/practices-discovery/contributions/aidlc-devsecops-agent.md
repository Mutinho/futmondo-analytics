**Collaborator:** aidlc-devsecops-agent

## Contribution

Revisión de dominio DevSecOps del borrador del lead (lint/format, secret-scanning,
dependency-scanning, supply-chain y toque de manejo de secretos) para el intent de
fiabilidad backend (FR3.2 + FR4). El borrador está bien alineado con la baseline afirmada
y con la evidencia del codekb; las observaciones siguientes son huecos que la **entrevista
humana** debe cerrar, no reescrituras.

### 1. Enforcement de `E722` — la decisión de trinquete necesita bit explícito del humano

La evidencia confirma el hallazgo del lead: `backend/ruff.toml` tiene
`ignore = ["E501","E402","E722"]` y `ruff check` corre **advisory** (`continue-on-error`) en
ambos caminos de CI. El lead lo trata como condicional ("cualquier objetivo de FR3.2 que
quiera enforcement… deberá re-habilitar `E722`"). Eso deja la decisión abierta. Como la
evidencia también dice que los `except: pass` reales viven **fuera** del alcance FR3.2
declarado (`data_manager_v2.py` L57-58/L68-69/L672-673 y `photo_service.py` L475-476 están
todos en el "fuera de alcance"; la primera oleada FR3.2 es `main.py` + `scripts/migrate_*`
+ `db_connection.py`, y las migraciones **loguean**, no son bare-except), re-habilitar
`E722` **hoy** haría fallar advisory sobre 4 sitios que este intent NO va a tocar. La
entrevista debe resolver un binario claro:

- **(a)** re-habilitar `E722` ahora pero mantenerlo **advisory** (visibilidad sin bloquear),
  aceptando que señalará deuda fuera de alcance; o
- **(b)** diferir `E722` a un intent futuro que aborde `data_manager_v2.py`/`photo_service.py`,
  dejando que FR3.2 se apoye sólo en la reviewer + tests por ahora.

Recomendación de dominio: **(a) advisory** es el shift-left correcto (hace visible la deuda
sin romper el gate ni forzar reflow), pero es intent del equipo, no juicio del agente.
Sugiero que el lead añada esta bifurcación como pregunta explícita en Step 4.

### 2. Aislar el cambio de regla del reflow — el borrador lo dice, falta el "cómo"

El borrador arrastra correctamente la regla afirmada de NO `ruff format` masivo y nota que
"el enforcement exige re-habilitar `E722` aislando el reflow". Un matiz operable que falta:
editar `ignore` en `ruff.toml` es un cambio de **una línea de config**, no un `format`, así
que **no arrastra reflow por sí mismo** — el riesgo de reflow sólo aparece si alguien corre
`ruff format` o `ruff check --fix` a la vez. Sugiero que el lead lo haga explícito en Code
Style: el cambio de `ruff.toml` va en **su propio commit aislado** (`chore(ci)`), sin
`--fix` ni `format`, para que el binding de la fuente reclamada de la reviewer (que sólo
corre `ruff check`) se mantenga estable. Esto es coherente con la nota de `ruff.toml`
("tras un formateo inicial en un commit aislado").

### 3. Secret-scanning: cobertura de los tests nuevos y de los docstrings de caracterización

El borrador dice bien que gitleaks es bloqueante en ambos caminos y que los tests usan
fakes/dobles sin credenciales. Refuerzo de dominio para el interview: los tests de
caracterización de FR4 van a **mockear el login de Futmondo** (`futmondo_client.login()`
hoy devuelve `bool`) y el flujo de credenciales por usuario resuelto en `_helpers`. Riesgo
concreto: es fácil que un doble de login lleve un password/token de aspecto realista como
literal de fixture y dispare gitleaks (que **escanea también `tests/`**). La práctica a
afirmar: **fixtures con valores obviamente falsos y no-entrópicos** (p. ej. `"fake-token"`,
`"test-secret"`), nunca cadenas de alta entropía que parezcan reales; alinear con el
`clean_jwt_env` ya existente en `conftest.py`. Además, `test_jwt_startup.py`/NFR1.1 ya fija
el arranque `JWT_SECRET` no-default — al endurecer el arranque de `main.py` (primera oleada
FR3.2) hay que **no regresionar** ese guard: la reclasificación de errores de boot no debe
degradar un `JWT_SECRET` default a "recuperable".

### 4. ¿El hardening de errores toca manejo de secretos/credenciales? — sí, en un punto

Respondiendo directamente a mi foco de dominio: el cambio de contrato de
`futmondo_client._make_request` (de `None`/`bool` a excepción tipada propagada, FR4) **sí
roza el manejo de credenciales**, porque el fallo de `login()` es hoy un `bool` y pasará a
propagarse. Guardarraíl a afirmar: la nueva excepción tipada y su mensaje/log **NUNCA deben
incluir el password ni el token Futmondo del usuario** en el texto de la excepción, en
`repr`, ni en `logger.error(..., exc_info=True)`. Esto conecta con la regla afirmada "NEVER
almacenar la contraseña Futmondo en claro (ni en memoria ni en base de datos)" y con la
guía de seguridad (no loguear secretos/PII/tokens). Sugiero que Code Style incorpore:
**las excepciones de integración llevan modo de fallo + contexto no sensible (status, endpoint,
si aplica), nunca material de credencial**. Es un hueco que ni team-practices ni
discovered-rules cubren hoy.

### 5. Dependency-scanning y supply-chain — consistente, con una nota de precisión

El borrador afirma coste 0 € / sin deps de pago / stdlib suficiente / cualquier lib OSS a
versión exacta. Coherente con la evidencia (`pip-audit` advisory en `ci.yml`; el intent no
prevé deps nuevas). Nota de precisión para evidence.md: el patrón recuperable/fatal se
replica de `SofascoreIPBanError` que ya vive sobre `curl_cffi`, y el cliente Futmondo usa
`requests` — **ambas ya son dependencias existentes**, así que FR4 NO introduce ninguna
dependencia de red nueva ni amplía la superficie de supply-chain. Bien. La regla "NEVER
introducir dependencias de pago; cualquier librería nueva sería OSS y fijada a versión
exacta" es correcta y suficiente; si el equipo quisiera un scanner SAST de Python
(bandit/semgrep) para respaldar la detección de bare-except/broad-except sería OSS y coste
0 €, pero eso es **ampliación de pipeline fuera del alcance declarado** — lo dejo como deuda
observable, no como propuesta a colar en este intent.

### 6. Simetría de gate no-cobertura entre `ci.yml` y `verify` (fuera de alcance, confirmado)

El borrador difiere correctamente la asimetría `--cov=app` (ci.yml) vs `pytest -q` sin
`--cov` (`verify`) como deuda. Desde seguridad confirmo lo importante: **gitleaks es
bloqueante en AMBOS caminos** (`@v3` en PR, `@v2` en `verify`, sin `continue-on-error`), así
que la asimetría es sólo de señal de cobertura, no de secret-scanning; ningún hueco de
seguridad se abre por diferirla. Sugerencia menor: registrar en evidence.md que **el
`gitleaks@v2` de `verify` está desalineado en major con el `@v3` de PR** — no es un fallo de
este intent, pero conviene anotarlo como deuda de pin para un futuro trabajo de pipeline
(no bloquea nada aquí).

## Positions

- AGREE: La secuenciación FR3.2 → FR4 → estado degradado y la excepción tipada propagada (no `return None`) son la postura de seguridad correcta y trazan a `SofascoreIPBanError`.
- AGREE: gitleaks bloqueante en ambos caminos y tests con fakes/dobles sin credenciales es la baseline correcta y ya vigente.
- AGREE: coste 0 €, sin deps de pago, sin deps nuevas de red (FR4 reusa `requests`/`curl_cffi` existentes) — supply-chain sin cambios.
- OBJECT: El borrador deja "re-habilitar `E722`" como condicional; la entrevista debe fijar un binario explícito (advisory-ahora vs diferir), porque los `except: pass` reales están fuera del alcance FR3.2 y re-habilitar hoy señala deuda que este intent no toca.
- OBJECT: Falta una regla explícita de que la nueva excepción tipada de `futmondo_client` NUNCA incluya password/token en su mensaje, `repr` o `exc_info`; el hardening de FR4 roza el manejo de credenciales y ni team-practices ni discovered-rules lo cubren.
