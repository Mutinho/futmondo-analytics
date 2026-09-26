# Security Design — Intent 4 (gate CI/CD hardening)

> Etapa de diseño: arquitectura de seguridad del gate (patrones y decisiones),
> no implementación. Las ediciones concretas de workflows/config son de
> code-generation / ci-pipeline. Los snippets son ilustrativos (≤15 líneas).

Este es el eje central del intent: el endurecimiento del gate es **seguridad de
supply-chain y de la cadena de release** a coste 0 €. Perspectivas superpuestas:
DevSecOps (supply-chain, escaneo), Compliance (trazabilidad/auditoría del gate),
Quality (que la señal sea real, no cosmética).

## Activo protegido y modelo de amenaza (acotado al gate)

El activo es `main` y, por extensión, el release a producción. Vectores que este
diseño cierra o endurece:

1. **Dependencia vulnerable con fix disponible que llega a producción** —
   `pip-audit`/`npm audit` hoy advisory (`continue-on-error`).
2. **Gate no reproducible / evadible** — `pip-audit -r` audita rangos; tooling
   flotante (`pip install ruff` sin pin, `vitest ^4.0.8`); gitleaks en dos
   versiones (`@v3` vs `@v2`).
3. **Secreto filtrado en repo o tests** — cubierto por gitleaks bloqueante (ya
   operativo); este intent lo unifica y fija.
4. **Push directo a `main` que elude el gate** — `verify` hoy no corre audits ni
   lint.

## Principio rector: defensa en profundidad con paridad de rutas

Toda ruta hacia `main` — PR (`ci.yml`, job `quality`) y push directo
(`fly-deploy.yml`, job `verify`) — debe aplicar el **mismo** conjunto de
controles de seguridad bloqueantes. La paridad no es "flipear un flag": exige
**añadir** a `verify` los pasos de audit y lint que hoy no tiene (NFR-SEC.6,
FR14.2). El endurecimiento refuerza el CONTENIDO de `verify`; **no** reordena la
cadena `needs:` (`verify → deploy-backend → deploy-frontend → smoke-test`).

## Controles de seguridad (diseño)

### C1 — Audit de dependencias backend: `pip-audit` (NFR-SEC.1)

- **Política**: bloquea ante **todo finding CON fix disponible**. No se intenta
  corte por severidad numérica (la señal CVSS es inconsistente en las fuentes de
  pip-audit).
- **Superficie auditada**: el **entorno instalado/resuelto tras `pip install`
  (sin `-r`)**, no los rangos de `requirements.txt`. Así el gate refleja lo que
  se despliega y evita findings intermitentes por lo que resuelva pip ese día
  (reproducibilidad, NFR5.1).
- **Findings sin fix**: gobernados por allowlist versionada (ver C4), nunca
  silenciando el gate.
- **Pin**: `pip-audit` fijado a versión exacta en el paso que lo instala (C5).

### C2 — Audit de dependencias frontend: `npm audit` (NFR-SEC.2)

- **Política**: bloquea en severidad **`high`** (`--audit-level=high`), no
  critical-only: `high` incluye clases explotables (prototype pollution, ReDoS,
  RCE en transitivas) que critical-only dejaría pasar.
- **Trinquete de severidad SÓLO endurece**: si `high` genera demasiado ruido
  heredado de golpe, se promueve primero en `critical`, se sanea, y se endurece
  a `high` en commit posterior (critical→high). Nunca se relaja.
- **Restricción de alcance**: **no** se instalan ni tocan devDependencies del
  frontend (ESLint frontend es deuda diferida); `npm audit` es built-in y no
  requiere dependencia nueva.

### C3 — Escáner de secretos: `gitleaks` unificado y fijado (NFR-SEC.4)

- **Problema**: hoy `ci.yml` usa `gitleaks-action@v3` y `verify` usa `@v2` — dos
  versiones del mismo escáner hacia `main` = divergencia de comportamiento.
- **Diseño**: **unificar a una única versión y fijarla** en AMBOS gates. Los
  secretos se escanean también en los tests (los tests usan fakes/dobles, nunca
  credenciales reales).
- **Fuera de alcance**: el pin por SHA de acciones de terceros mutables
  (`setup-flyctl@master`, etc.) se decide en ci-pipeline (FR13.4), no aquí.

### C4 — Allowlist versionada de excepciones (NFR-SEC.3, decisión Q1/Q2)

Gobierna los findings **sin fix upstream** sin silenciar el gate.

- **Ubicación (Q1=A)**: **fichero nativo por herramienta en su ecosistema**:
  - Backend: fichero de ignore-vulns versionado consumido por
    `pip-audit --ignore-vuln <ID>` (p. ej. bajo `backend/`).
  - Frontend: el mecanismo de supresión nativo de npm versionado.
  - Cada entrada lleva, en el propio fichero: **ID del advisory/CVE,
    dependencia+versión, motivo (sin fix upstream), fecha y fecha de
    caducidad/revisión**.
- **Enforcement de caducidad (Q2=A)**: un **paso determinista en el gate**
  compara la fecha de caducidad de cada entrada con la fecha actual y **falla el
  job** si alguna está caducada — antes o junto al audit. Una entrada caducada
  **vuelve a bloquear** automáticamente. Cero dependencias de pago.
- **Prohibiciones**: NUNCA `continue-on-error` permanente en un check promovido,
  NUNCA borrar/silenciar el audit ni bajar su nivel global. Un finding sin fix
  va a la allowlist con caducidad, nunca a un silenciador permanente.

Snippet ilustrativo del enforcement de caducidad (pseudocódigo, ≤15 líneas):

```bash
# Falla si alguna entrada de la allowlist superó su fecha de caducidad.
today=$(date -u +%F)
while read -r cve dep expiry _; do
  [ "$cve" = "#" ] && continue          # comentarios
  if [ "$expiry" \< "$today" ]; then
    echo "::error::allowlist entry $cve ($dep) expired on $expiry"
    exit 1
  fi
done < "$ALLOWLIST_FILE"
```

### C5 — Tooling del gate a versión exacta (NFR-SEC.5)

Un tooling flotante puede introducir reglas nuevas que rompan el gate de forma
no determinista, o desalinear un plugin de cobertura. Se fija a **versión exacta
EN EL PASO QUE LA INSTALA**:

| Herramienta | Estado hoy | Diseño |
|-------------|-----------|--------|
| `ruff` | `pip install ruff` sin pin | pin exacto en el paso de instalación |
| `pip-audit` | sin pin | pin exacto en el paso de instalación |
| `vitest` | rango abierto `^4.0.8` | pin exacto emparejado con `@vitest/coverage-v8 == 4.1.11` |
| `gitleaks` (action) | `@v3` / `@v2` divergentes | versión única fijada en ambos gates |

Nada de rangos abiertos en un check bloqueante (patrón ya seguido con
`@vitest/coverage-v8 == 4.1.11` y `PyJWT == 2.9.0`).

### C6 — Higiene de secretos en workflows y specs (NFR4.1)

- Secretos siempre vía `secrets` de GitHub Actions / Fly.io.
- En CI el `JWT_SECRET` es **efímero y no productivo**
  (`ci-ephemeral-secret-not-a-real-one`).
- **NUNCA** hardcodear secretos/tokens reales en workflows ni en specs; los
  tests usan fakes/dobles (gitleaks escanea también los tests).
- **NUNCA** usar un `JWT_SECRET` por defecto en producción (NFR1.1 de inception;
  arranque endurecido en `test_jwt_startup.py`).

## Promoción escalonada (no big-bang) — orden de endurecimiento

La promoción advisory→bloqueante es **escalonada** (FR12), cada una en su propio
commit `chore(ci)` aislado con el trinquete fijado, con la deuda heredada
saneada/silenciada quirúrgicamente ANTES de bloquear:

1. Audits de dependencias (mayor señal de seguridad): `pip-audit`, luego
   `npm audit`.
2. Lint bloqueante (`ruff check`) — **último** paso del escalón.

Nunca se promueve un check de golpe sin sanear antes la deuda que reportaría. La
deuda de lint se sanea **por fichero de forma quirúrgica** o con
`per-file-ignores`/`# noqa` puntual con rationale; **NUNCA** ampliando o
reescribiendo los god-files (`data_sync_service.py`, `data_manager_v2.py`,
`assistant_service.py`) ni los routers SQL-en-endpoint, y **NUNCA** con
`ruff check --fix` de repo entero ni `ruff format` masivo.

## Compliance / auditoría

- El proyecto no está bajo marco regulatorio formal (fantasy football, datos no
  sensibles regulados); no aplican cláusulas específicas de GDPR/HIPAA/PCI más
  allá de la higiene de no filtrar credenciales.
- El requisito de auditoría relevante es interno: la **allowlist versionada con
  caducidad** (C4) da trazabilidad auditable de qué vulnerabilidad se aceptó,
  por qué y hasta cuándo — auditable en git sin coste.

## Fuera de alcance (deuda de seguridad documentada)

- **SAST/DAST dedicado** (CodeQL/Semgrep/ZAP): CodeQL añadiría minutos de Actions
  y ruido sobre god-files heredados; DAST exige un entorno corriendo.
  `ruff`/`pip-audit`/`npm audit`/gitleaks cubren el mínimo viable a coste 0 €.
- **Pin de acciones de terceros por SHA**: se decide en ci-pipeline (FR13.4).

## Trazabilidad

- NFR-SEC.1 → C1; NFR-SEC.2 → C2; NFR-SEC.3 → C4; NFR-SEC.4 → C3;
  NFR-SEC.5 → C5; NFR-SEC.6 → principio de paridad + C1/C2; NFR4.1 → C6.

## Sources

- `../nfr-requirements/security-requirements.md` (NFR-SEC.1–6, NFR4.1).
- `../nfr-requirements/tech-stack-decisions.md` (pins, allowlist, superficies).
- `aidlc/spaces/default/memory/team.md` §Code Style / §Deployment (Q1/Q2/Q3/Q5).
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (coste 0 €, secretos).

## Assumptions & Open Questions

- None.
