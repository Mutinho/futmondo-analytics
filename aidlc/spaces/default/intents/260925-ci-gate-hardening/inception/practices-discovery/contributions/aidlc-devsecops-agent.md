**Collaborator:** aidlc-devsecops-agent

## Contribution

Perspectiva de seguridad de pipeline (lint/format, SAST/DAST, escaneo de
secretos y de dependencias, supply-chain) sobre el endurecimiento del gate
CI/CD del Intent 4 (`260925-ci-gate-hardening`, scope infra, brownfield). Todo
a coste 0 € con herramientas OSS y GitHub Actions free; versiones exactas para
cualquier dependencia OSS nueva; los tests usan fakes/dobles, nunca secretos
reales (gitleaks escanea también los tests).

### 1. Orden de promoción (FR12): audits ANTES que lint — de acuerdo, con matiz de señal

El orden **audits de dependencias primero, lint después** es correcto desde
seguridad: un CVE explotable en una dependencia es una amenaza real de
supply-chain (mayor señal de seguridad), mientras que `ruff check`/ESLint son
higiene de código (menor riesgo de seguridad, mayor ruido heredado). Confirmo
contra la evidencia real (`.github/workflows/ci.yml`, job `quality`) que hoy
corren en advisory (`continue-on-error: true`) exactamente:

- `pip-audit -r requirements.txt` (backend, advisory)
- `npm audit --audit-level=high` (frontend, advisory)
- `ruff check .` (backend, advisory)
- `npx ng lint` (frontend, advisory, con `|| echo`)

y que gitleaks + pytest (`--cov=app`) + ng test ya son BLOQUEANTES. El punto de
partida de FR12 está confirmado verbatim.

### 2. Severidad que debe bloquear: HIGH (no critical), escalonado

Recomendación de seguridad para el umbral exacto:

- **npm audit**: mantener `--audit-level=high` como umbral bloqueante. `high`
  incluye clases explotables habituales (prototype pollution, ReDoS, RCE en
  transitivas) que `critical`-only dejaría pasar. Bloquear en `high` es la
  postura correcta; `critical`-only es demasiado permisivo para un gate de
  producción.
- **pip-audit**: `pip-audit` no filtra por severidad de forma nativa fiable en
  todas las fuentes (OSV/PyPI advisories no siempre traen CVSS normalizado). La
  postura pragmática y coste-0 es: **cualquier finding con fix disponible
  bloquea**; los findings **sin fix** se gobiernan por allowlist (ver §3). No
  intentar un corte por severidad numérica en pip-audit porque la señal es
  inconsistente y generaría falsos verdes.
- **Escalonar la severidad también dentro de cada audit**: si al medir la base
  heredada `high` produce demasiado ruido bloqueante de golpe, promover primero
  a bloqueante en `critical`, sanear, y bajar el corte a `high` en un commit
  posterior. El trinquete de severidad **sólo endurece** (critical→high), nunca
  se relaja.

### 3. Findings sin fix en free tier: ALLOWLIST VERSIONADA (no diferir en silencio)

Recomiendo **allowlist versionada en el repo** frente a "diferir":

- Un finding sin fix disponible upstream **no debe silenciarse borrando el
  audit ni bajando el nivel global**; se registra explícitamente en una
  **allowlist versionada** commiteada, con: ID del advisory/CVE, dependencia +
  versión, motivo (sin fix upstream), fecha, y **fecha de caducidad/revisión**.
- Mecanismo coste 0 €: `pip-audit --ignore-vuln <ID>` (flag nativo) y, para
  npm, un fichero de excepciones versionado (o `npm audit` + filtro explícito
  documentado). Nada de `continue-on-error` permanente: eso convierte el gate
  en decorativo.
- La allowlist es **auditable y caduca**: cada entrada se revisa en el
  siguiente toque del gate; una entrada caducada vuelve a bloquear. Esto
  preserva "un rojo nunca llega a producción" sin pagar por un servicio de
  gestión de vulnerabilidades.
- "Diferir" sin registro es lo que hay que evitar: pierde trazabilidad y
  reintroduce el riesgo silenciosamente.

### 4. Gate gitleaks: operativo, pero con dos huecos de supply-chain a cerrar

gitleaks ya es bloqueante en AMBOS gates (PR y push→main), lo cual es correcto
y defensa en profundidad. Dos observaciones de seguridad sobre la evidencia
real:

- **Deriva de versión de la acción**: `ci.yml` usa `gitleaks/gitleaks-action@v3`
  y `fly-deploy.yml` (job `verify`) usa `gitleaks/gitleaks-action@v2`. Un gate
  de seguridad bloqueante no debería correr dos versiones distintas del mismo
  escáner en dos rutas hacia `main` (riesgo de reglas/comportamiento
  divergente). **Unificar a la misma versión** en ambos workflows como parte de
  este intent (cambio de config aislado, coste 0 €).
- **Pin de acciones de terceros por tag mutable**: las acciones OSS de terceros
  (`gitleaks-action@v2/@v3`, `superfly/flyctl-actions/setup-flyctl@master`)
  están fijadas a tags mutables. Para un gate bloqueante de seguridad, la
  práctica de supply-chain es **fijar por SHA de commit** (o al menos tag
  inmutable), coherente con la regla ya afirmada de "versión exacta en checks
  bloqueantes". `@master` en `setup-flyctl` es especialmente frágil. Lo dejo
  como recomendación fuerte; el alcance exacto (todas las acciones vs sólo las
  de los jobs bloqueantes) se decide en ci-pipeline.

### 5. `pip-audit -r requirements.txt` audita RANGOS declarados, no el set instalado

`backend/requirements.txt` tiene varias dependencias con **rango abierto**
(`requests>=2.31.0`, `fastapi>=0.104.0`, `psycopg2-binary>=2.9.9`, `curl_cffi>=0.16.0`,
`pytest>=8.0.0`, etc.) y sólo unas pocas pinneadas (`PyJWT==2.9.0`,
`google-genai==1.14.0`, `groq==0.25.0`). Para un **audit bloqueante estable**:

- Auditar `-r requirements.txt` (rangos) hace que el resultado del gate dependa
  de qué resuelve pip ese día → findings intermitentes y gate no reproducible.
- Recomendación coste 0 €: auditar el **entorno instalado y resuelto** tras el
  `pip install` (ejecutar `pip-audit` sin `-r`, sobre el venv ya instalado), de
  modo que el audit refleje exactamente lo que se despliega. Complementa la
  regla ya afirmada de pin exacto: la deuda de pinning de rangos abiertos es una
  debilidad de supply-chain que este gate expondrá — sanearla (pinning) es
  parte natural del endurecimiento.

### 6. Hueco en el job `verify` de `fly-deploy.yml` (defensa en profundidad incompleta)

La sección Deployment del líder dice que "las promociones advisory→bloqueante
de FR12 se replican en ambos gates (PR y push)". Contra la evidencia real esto
requiere trabajo adicional que conviene hacer explícito: el job `verify` de
`fly-deploy.yml` **hoy NO tiene NINGÚN paso de audit ni de lint** — sólo
gitleaks + `pytest -q` (sin `--cov`) + `ng test`. Por tanto "replicar la
promoción" en `verify` no es flipear un `continue-on-error` (no existe): es
**añadir** los pasos `pip-audit`/`npm audit`/`ruff check` a `verify` antes de
poder bloquearlos ahí. Sin eso, un push directo a `main` se salta los audits y
el lint por completo — exactamente el mismo tipo de hueco que FR17.3 cierra
para la cobertura. Recomiendo tratarlo como parte del endurecimiento (paridad
real de gate PR ↔ push), no asumirlo cubierto.

### 7. SAST/DAST: fuera de alcance a coste 0 €, documentar como deuda

Para completar la perspectiva DevSecOps: no recomiendo introducir SAST
dedicado (CodeQL/Semgrep) ni DAST (ZAP) en este intent — CodeQL es gratis en
repos públicos pero añade minutos de Actions y ruido de findings sobre los
god-files heredados, y DAST exige un entorno corriendo. `ruff`/ESLint +
`pip-audit`/`npm audit` + gitleaks cubren el mínimo viable de seguridad de
pipeline a coste 0 €. Dejar SAST/DAST como **deuda documentada**, no como
alcance de este gate.

## Positions

- AGREE: Orden de promoción FR12 = audits de dependencias PRIMERO, lint DESPUÉS. Correcto desde seguridad (CVE explotable > higiene de estilo) y confirmado contra el estado advisory real de `ci.yml`.
- AGREE: Promoción escalonada por commit aislado `chore(ci)`, saneando/silenciando la deuda heredada antes de bloquear; nada de big-bang. Reduce el riesgo de romper el gate y facilita rollback quirúrgico.
- AGREE: Pin a versión exacta de toda dependencia OSS relevante a un check bloqueante; sin rangos abiertos en el gate. Práctica de supply-chain correcta (ya seguida con `@vitest/coverage-v8 == 4.1.11`, `PyJWT == 2.9.0`).
- AGREE: gitleaks bloqueante en ambos gates y JWT_SECRET efímero/no productivo en CI; tests con fakes/dobles, nunca secretos reales (gitleaks escanea tests). Coherente con las reglas afirmadas de no-credenciales.
- AGREE: No reordenar la cadena `needs:` de `fly-deploy.yml`; el endurecimiento refuerza el contenido de `verify`, no su topología.
- OBJECT: La afirmación "las promociones FR12 se replican en ambos gates" trata como trivial un trabajo real: el job `verify` de `fly-deploy.yml` NO tiene hoy pasos de audit ni lint (sólo gitleaks + pytest sin `--cov` + ng test). Replicar en `verify` exige AÑADIR esos pasos, no flipear `continue-on-error`. Rationale: sin esto, el push directo a `main` se salta audits/lint — hueco de defensa en profundidad análogo al de cobertura que FR17.3 cierra. Debe declararse explícitamente como parte del alcance.
- OBJECT: Umbral de severidad de audits dejado como open question sin recomendación de seguridad. Rationale: recomiendo BLOQUEAR EN `high` (no critical-only) para npm audit — `critical`-only deja pasar clases explotables (ReDoS/prototype-pollution/RCE en transitivas); para pip-audit, bloquear todo finding con fix disponible y gobernar los sin-fix por allowlist. Postura de seguridad concreta, no diferible al azar.
- OBJECT: Findings sin fix en free tier — la política debe ser ALLOWLIST VERSIONADA con caducidad (p. ej. `pip-audit --ignore-vuln <ID>` + fichero de excepciones commiteado con CVE/versión/motivo/fecha de revisión), NO "diferir" en silencio ni `continue-on-error` permanente. Rationale: diferir sin registro pierde trazabilidad y reintroduce el riesgo de supply-chain silenciosamente; la allowlist mantiene el gate real, auditable y coste 0 €.
- OBJECT: `pip-audit -r requirements.txt` audita los RANGOS declarados, no el set resuelto/instalado, y `requirements.txt` tiene múltiples rangos abiertos (`requests>=`, `fastapi>=`, `psycopg2-binary>=`, `curl_cffi>=`, `pytest>=`). Rationale: en un gate BLOQUEANTE esto produce findings intermitentes y no reproducibles; auditar el entorno ya instalado (sin `-r`) tras `pip install` refleja lo que realmente se despliega. Sanear la deuda de pinning de rangos abiertos es parte natural del endurecimiento.
- OBJECT: Deriva de versión del escáner de secretos — `ci.yml` usa `gitleaks-action@v3` y `verify` usa `@v2`, y ambas rutas a `main` fijan acciones de terceros por tag mutable (`@v2/@v3`, `setup-flyctl@master`). Rationale: un gate de seguridad bloqueante debe correr la MISMA versión del escáner en ambas rutas y fijar acciones de terceros por SHA/tag inmutable (coherente con la regla afirmada de "versión exacta en checks bloqueantes"); `@master` es especialmente frágil frente a supply-chain.
