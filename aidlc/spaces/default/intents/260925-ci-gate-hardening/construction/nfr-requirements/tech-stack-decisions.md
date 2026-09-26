# Tech Stack Decisions — Intent 4 (gate CI/CD hardening)

Este intent no introduce tecnología nueva de aplicación; las decisiones son
sobre el **tooling del gate de CI/CD**, todo OSS y fijado a versión exacta, a
coste 0 €. Se mantiene el stack de producción sin cambios (FastAPI/Python 3.12,
Angular 22, Neon, Fly.io, GitHub Actions).

## Decisiones de tooling del gate

| Herramienta | Decisión | Rationale | Alternativa rechazada |
|-------------|----------|-----------|-----------------------|
| `ruff` | Fijar a versión exacta en el paso que lo instala; promover `ruff check` a bloqueante (último paso del escalón). | Hoy `pip install ruff` sin pin: un ruff flotante puede introducir reglas nuevas que rompan el gate de forma no determinista. | Dejar sin pin (no reproducible); usar flake8/pylint (más lento, no es el linter del proyecto). |
| `pip-audit` | Fijar a versión exacta; ejecutar sobre el entorno instalado (sin `-r`); bloquear findings con fix. | Auditar el venv resuelto refleja lo que se despliega y evita findings intermitentes. OSS, coste 0 €. | `safety` (requiere cuenta/API para la base completa); auditar rangos con `-r` (no reproducible). |
| `npm audit` | Bloquear en `high` (built-in de npm). | Sin dependencia nueva; `high` cubre clases explotables que critical-only dejaría pasar. Coste 0 €. | `snyk`/`socket` (freemium con límites; riesgo de salir del free tier). |
| `vitest` | Fijar a versión exacta, emparejada con `@vitest/coverage-v8 == 4.1.11`. | Un bump por `npm ci` del runner podría desalinear el plugin de cobertura y romper la medición del gate bloqueante. | Rango abierto `^4.0.8` (no reproducible). |
| `gitleaks` (action) | Unificar a una única versión y fijarla en ambos gates. | Hoy `@v3` en `ci.yml` vs `@v2` en `verify`: dos versiones del mismo escáner hacia `main` es divergencia de comportamiento. | Mantener dos versiones (divergente); TruffleHog (cambio de herramienta innecesario). |
| `pytest` + `pytest-cov` | Piso `--cov-fail-under` en `pytest.ini` (line-only). | Ya son la suite del proyecto; el piso vive en config, no en un paso extra. | Herramienta de cobertura externa (innecesaria). |

## Decisiones de configuración

- **Piso de cobertura backend**: único `--cov-fail-under` en `pytest.ini`,
  line-coverage total (sin `--cov-branch`), valor medido exacto, solo trinquete.
- **Allowlist de vulnerabilidades**: fichero versionado en el repo (`pip-audit
  --ignore-vuln <ID>` + equivalente npm), con caducidad; no `continue-on-error`.
- **Sin dependencias de pago**: toda herramienta es OSS y cabe en el free tier.

## Fuera de alcance

- ESLint frontend (deuda diferida; no se tocan devDependencies del frontend).
- Pin de acciones de terceros por SHA (se decide en ci-pipeline).
- SAST/DAST dedicado (deuda documentada).

## Sources

- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/requirements-analysis/requirements.md` (FR11–FR16).
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/practices-discovery/team-practices.md` (Code Style, Q1/Q2/Q5).
- `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md`.

## Assumptions & Open Questions

- None.
