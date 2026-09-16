**Collaborator:** aidlc-devsecops-agent

## Contribution

Revisión de seguridad independiente del borrador del lead (`team-practices.md`,
`discovered-rules.md`, `evidence.md`) para el intent brownfield
`260914-durabilidad-estado-y-cre`. Verifiqué la evidencia citada:
`.github/workflows/ci.yml`, `backend/ruff.toml`, `angular-app/eslint.config.js`
y `code-quality-assessment.md`. Valoración global: el draft es fiel a la
evidencia y no inventa reglas; su encuadre de coste 0 € y de gate escalonado es
correcto. Aporto matices y huecos de la superficie de seguridad que el borrador
no captura con precisión.

### Lint / format (acuerdo con matiz)

- Confirmo el modelo escalonado advisory→bloqueante: ruff (`select=[E,F,I]`,
  `ignore=[E501,E402,E722]`, `line-length=100`, `py312`, format comillas dobles)
  y ESLint flat config (`typescript-eslint`+`angular-eslint`, reglas base a
  `warn`) corren `continue-on-error` en `ci.yml`. Coincide con el draft.
- **Matiz importante de encuadre**: lint/format NO es SAST. El draft lista lint
  bajo "Code Style" (correcto), pero conviene que la sección `## Testing Posture`
  o una nota deje explícito que **hoy no hay SAST ni DAST reales** en el pipeline.
  ruff/ESLint son estilo/pyflakes, no análisis de seguridad. Es una brecha
  conocida y aceptable en coste 0 €, pero debe quedar registrada como deuda, no
  omitida.
- **Trinquete de seguridad**: al pasar ruff a bloqueante (fase posterior),
  proponer añadir por trinquete reglas de bandera de seguridad de coste 0 € —
  ruff ya soporta la familia `S` (flake8-bandit) — para cubrir `assert` en prod,
  `subprocess`/`eval` inseguros y `try/except/pass`. Se alinea con el hallazgo
  `except Exception: pass` del codekb (enmascara fallos; señal de robustez y de
  seguridad). No introduce coste.

### SAST / DAST (hueco a registrar)

- **Verificado**: no existe paso SAST ni DAST en ningún workflow. Coherente con
  el nivel de madurez y con coste 0 €. Recomiendo NO afirmar una regla que exija
  SAST/DAST ahora (sería aspiracional, no evidente), pero SÍ registrar en
  `evidence.md` que su ausencia es una deuda de seguridad consciente. Opción de
  coste 0 € para el futuro: `semgrep` OSS o `bandit` en modo advisory sobre el
  backend Python, reutilizando el patrón escalonado ya existente.

### Escaneo de secretos (acuerdo fuerte)

- Confirmo gitleaks **BLOQUEANTE** desde el inicio con `fetch-depth: 0` (escanea
  el historial del PR). Es el control de seguridad más fuerte del pipeline y el
  draft lo eleva bien a regla mandatoria/prohibición. AGREE total aquí.
- **Matiz**: `ci.yml` inyecta `JWT_SECRET: ci-ephemeral-secret-not-a-real-one`
  en claro en el YAML. Es aceptable (no productivo, efímero, exigido por el guard
  NFR1.1 para que la app importe), pero conviene fijar la práctica de forma
  explícita para que nadie sustituya ese literal por un secreto real: los
  secretos productivos SIEMPRE via `secrets`/Fly.io, nunca literal en workflow.
- **Cobertura pre-commit ausente**: gitleaks solo corre en CI (backstop). Un hook
  pre-commit de gitleaks (coste 0 €) atajaría el secreto antes del push. Opcional,
  a decidir en entrevista; no lo elevo a regla dura por no estar en evidencia.

### Escaneo de dependencias / cadena de suministro (matices)

- **Verificado**: `pip-audit` y `npm audit` son advisory (`continue-on-error`).
  `npm audit` usa `--audit-level=high`; `pip-audit` corre sin umbral explícito.
  El draft lo describe bien como advisory en fase de saneamiento.
- **Huecos de cadena de suministro no reflejados en el draft**:
  1. **Pinning de acciones**: los workflows usan tags mutables (`actions/checkout@v5`,
     `gitleaks/gitleaks-action@v3`, etc.). Buena práctica de supply-chain de coste
     0 € es fijar por SHA. Deuda menor, registrar; no bloqueante.
  2. **`permissions`**: `ci.yml` fija `contents: read` (correcto, least-privilege).
     Verificar que `fly-deploy.yml` y los crons también acoten `permissions` al
     mínimo — pendiente de confirmar en entrevista/lectura.
  3. **Sin SBOM**: no hay generación de SBOM (Syft/Trivy). Coste 0 € y opcional;
     registrar como deuda, no como regla ahora.
- Proponer que el trinquete de endurecimiento (cuando lint pase a bloqueante)
  incluya elevar `pip-audit`/`npm audit` a bloqueante en `high/critical` **con
  archivo de supresiones justificadas y caducadas**, respetando coste 0 €.

### Deuda de seguridad de credenciales en claro (FR5) — punto central

- **Verificado en codekb**: `UserSession` guarda `email`/`password` de Futmondo
  en **texto plano en memoria** (FR5). El draft lo captura correctamente en
  `discovered-rules.md` con la prohibición NEVER de almacenar credenciales en
  claro ni en memoria ni, al diseñar durabilidad, en la BD.
- **Refuerzo (defense in depth)**: al persistir sesión/estado para FR1, la regla
  debe ser más específica que "cifrar o no guardar". Preferencia de seguridad,
  por orden:
  1. **No persistir el `password`** en absoluto (preferido): reconstruir sesión
     Futmondo por re-login/refresh en vez de guardar la credencial.
  2. Si hay que persistir para no exigir re-login, **cifrar en reposo** con clave
     gestionada como secreto (Fly.io secrets / env), NUNCA en el repo, y rotar.
- **Hallazgos de seguridad adicionales del codekb que el draft NO menciona** y
  que recomiendo registrar (aunque algunos queden fuera del foco de remediación):
  - `ng build` de producción usa `NODE_TLS_REJECT_UNAUTHORIZED=0` — desactiva la
    verificación TLS en el build. Señal de seguridad real; registrar como deuda a
    corregir aunque esté fuera de scope del intent.
  - `except Exception: pass` en migraciones y auto-detección — enmascara fallos
    (riesgo de repudio/observabilidad y de errores silenciosos en el camino de
    datos). Relevante al tocar el esquema para durabilidad.
  - Migraciones ad-hoc sin versionado (`CREATE TABLE IF NOT EXISTS` + `ALTER` en
    `try/except: pass`): al introducir persistencia de sesión/estado cifrada, el
    cambio de esquema debe hacerse de forma controlada; el `try/except: pass`
    puede ocultar un fallo de migración de la columna cifrada.

### Modelo de amenaza mínimo para la durabilidad (STRIDE, resumen)

Al diseñar la persistencia de `SessionStore`/`TaskManager` en Neon:
- **Information Disclosure**: la credencial persistida es el activo crítico →
  cifrado en reposo o no-persistencia (ver arriba).
- **Tampering/Integrity**: tareas de sync persistidas deben ser idempotentes y
  validar estado al retomar tras reinicio (evitar reejecución dañina).
- **Repudiation/observabilidad**: no silenciar fallos de migración/persistencia
  con `except: pass`; loguear sin volcar credenciales/tokens (PII).

## Positions

AGREE: Escalonado lint/format advisory→bloqueante (ruff/ESLint) tal como está en `ci.yml`.
AGREE: gitleaks BLOQUEANTE + prohibición de hardcodear secretos/credenciales.
AGREE: Prohibición FR5 de credenciales en claro (memoria y BD) y coste 0 € (Neon, sin Redis de pago).
AGREE: Gate de verificación (pytest + ng test) bloqueante antes de merge/deploy y guard JWT no-default (NFR1.1).

OBJECT: El draft encuadra el estado de seguridad del pipeline sin dejar explícito que **no hay SAST ni DAST**; añadir esa deuda registrada en `evidence.md` para no dar impresión de cobertura de análisis de seguridad que no existe.
OBJECT: La regla FR5 en `discovered-rules.md` debería precisar el orden de preferencia (1º no persistir `password`; 2º cifrar en reposo con clave gestionada como secreto), no solo "cifrar o evitar".
OBJECT: Faltan en la evidencia hallazgos de seguridad reales del codekb: `NODE_TLS_REJECT_UNAUTHORIZED=0` en build prod, `except Exception: pass` que enmascara fallos, y ausencia de escaneo de dependencias bloqueante/SBOM/pinning de acciones por SHA. Registrarlos como deuda consciente (no necesariamente como reglas duras hoy).
OBJECT: El literal `JWT_SECRET` en claro en `ci.yml` (aunque efímero y válido) debería acompañarse de una regla explícita de que los secretos productivos van SIEMPRE via `secrets`/Fly.io, nunca literales en workflow.
