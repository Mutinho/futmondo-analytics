# CI Config — Intent 4 (gate CI/CD hardening)

> Etapa terminal de Construction (scope infra, config-only). Configuración
> concreta y accionable del gate endurecido, por fichero, sobre los workflows
> reales del repo. `cicd-pipeline.md` (Infrastructure Design) dio el diseño;
> este documento da el "cómo" ejecutable. Los snippets son la forma objetivo de
> cada paso; la materialización final va en los commits `chore(ci)`.

## Herramienta y estrategia (ya afirmadas)

- **CI tool**: GitHub Actions. Dos workflows-gate: `ci.yml` (job `quality`, PR →
  `main`, required status check) y `fly-deploy.yml` (job `verify`, push → `main`).
- **Branch strategy**: trunk-based, squash-merge a `main`.
- **Restricción dura**: coste 0 €; toda acción/herramienta OSS.

## Decisiones de configuración

| Decisión | Valor | Origen |
|----------|-------|--------|
| Pin de `ruff` | `pip install ruff==<versión exacta>` en el paso que lo instala | Q1=A, NFR-SEC.5 |
| Pin de `pip-audit` | `pip install pip-audit==<versión exacta>` | Q1=A |
| Pin de `vitest` | versión exacta emparejada con `@vitest/coverage-v8 == 4.1.11` | NFR-SEC.5 |
| gitleaks unificado | `gitleaks/gitleaks-action@v3` en AMBOS gates | Q2=B |
| Allowlist backend | fichero de texto versionado con columnas | Q3=A |
| Expiry check | script versionado único, `run:` step con nombre en ambos gates | Infra Q2 |
| Piso de cobertura backend | `--cov-fail-under=<valor medido>` en `pytest.ini`, line-only | FR11, Q6 |

> Los `<versión exacta>` se fijan al materializar el commit con la última
> estable disponible; nunca rangos abiertos en un check bloqueante.

## Cambios por fichero (diff a nivel de diseño)

### `.github/workflows/ci.yml` (job `quality`, PR-gate)

Orden fail-fast (barato-y-rápido primero, Infra Q1):

1. **gitleaks**: `@v3` (sin cambio de versión; ya es `@v3`). Sigue bloqueante.
2. **allowlist expiry check** (NUEVO): `run:` step con nombre que invoca
   `scripts/check-allowlist-expiry.sh`.
3. **pip-audit**: pinnar (`pip install pip-audit==<v>`), cambiar a auditar el
   **entorno instalado** (`pip-audit` sin `-r`, tras `pip install -r
   requirements.txt`), gobernar findings sin fix con `--ignore-vuln` desde la
   allowlist, y **quitar `continue-on-error: true`** (bloqueante).
4. **npm audit**: `npm audit --audit-level=high`, **quitar `continue-on-error`**
   (bloqueante). Sin tocar devDependencies.
5. **ruff check**: pinnar (`pip install ruff==<v>`) y **quitar
   `continue-on-error: true`** (bloqueante, último del escalón). Sin `--fix` ni
   `ruff format`.
6. **pytest**: añadir el piso — la invocación pasa a apoyarse en el
   `--cov-fail-under` de `pytest.ini` (ver abajo). Sigue con `JWT_SECRET`
   efímero.
7. **ng test**: sin cambio de invocación; el ratchet sube en `angular.json`.

Snippet objetivo del paso pip-audit (ilustrativo, ≤15 líneas):

```yaml
- name: Dependency audit (pip-audit, blocking)
  working-directory: ./backend
  run: |
    pip install pip-audit==<versión exacta>
    # Audita el entorno instalado (no -r); findings sin fix via allowlist.
    pip-audit $(grep -v '^#' .pip-audit-allowlist | awk '{print "--ignore-vuln "$1}')
```

### `.github/workflows/fly-deploy.yml` (job `verify`, push-gate)

Cerrar la paridad **AÑADIENDO** pasos (hoy `verify` solo tiene gitleaks +
`pytest -q` sin `--cov` + `ng test`). La cadena `needs:`
(`verify → deploy-backend → deploy-frontend → smoke-test`) **no se toca**.

1. **gitleaks**: subir `@v2` → **`@v3`** (unificación, Q2=B).
2. **allowlist expiry check** (NUEVO): mismo `run:` step / mismo script.
3. **pip-audit** (NUEVO en `verify`): mismo paso bloqueante que en `ci.yml`.
4. **npm audit** (NUEVO en `verify`): `--audit-level=high`, bloqueante.
5. **ruff check** (NUEVO en `verify`): pinnado, bloqueante.
6. **pytest**: cambiar `pytest -q` → `pytest -q --cov=app` con el mismo piso
   `--cov-fail-under` de `pytest.ini` (paridad de cobertura, FR17.3).
7. **ng test**: sin cambio (ya presente).

### `backend/pytest.ini`

Añadir el piso único dentro del mismo `addopts` de `pytest` (config, no un paso
extra), line-only:

```ini
# addopts existente + piso bloqueante line-coverage total (sin --cov-branch).
addopts = --cov=app --cov-fail-under=<valor medido exacto>
```

El `<valor medido exacto>` se mide al FINAL del escalón sobre la suite ya
estabilizada por el saneamiento de lint/audit, SIN margen. Sube solo por
trinquete; un flake se arregla en el test, nunca bajando el piso.

### `backend/requirements.txt`

Pinnar la deuda de rangos abiertos (`requests>=`, `fastapi>=`,
`psycopg2-binary>=`, `curl_cffi>=`, `pytest>=`) a versión exacta como parte
natural del endurecimiento, para que `pip-audit` sobre el entorno instalado sea
reproducible.

### `angular.json`

Subir el ratchet de los 4 umbrales de `coverageThresholds` (statements 15 /
branches 15 / functions 13 / lines 14) al valor medido. Fuente única de umbral;
sin pasos extra ni `continue-on-error`. Solo sube.

### `scripts/check-allowlist-expiry.sh` (NUEVO)

Script versionado único que ambos workflows invocan. Falla el job si alguna
entrada de la allowlist superó su fecha de caducidad (Infra Q2). Snippet
objetivo (≤15 líneas):

```bash
#!/usr/bin/env bash
set -euo pipefail
today=$(date -u +%F); fail=0
while read -r cve dep ver reason date expiry; do
  [ "${cve#\#}" != "$cve" ] && continue          # comentarios
  [ -z "${cve:-}" ] && continue
  if [ "$expiry" \< "$today" ]; then
    echo "::error::allowlist $cve ($dep $ver) expired $expiry ($reason)"; fail=1
  fi
done < backend/.pip-audit-allowlist
exit $fail
```

### `backend/.pip-audit-allowlist` (NUEVO)

Fichero de texto columnar (Q3=A), fuente única de findings sin fix:

```
# CVE           dependencia   versión   motivo                       fecha        caducidad
# (vacío al inicio; se añaden entradas solo para findings SIN fix upstream)
```

## Secuencia de commits `chore(ci)` (aislados, trinquete fijado)

1. `chore(ci): unificar gitleaks a @v3 en ambos gates`
2. `chore(ci): pinnar ruff, pip-audit y vitest a versión exacta`
3. `chore(ci): añadir allowlist versionada y expiry check en ambos gates`
4. `chore(ci): pip-audit sobre entorno instalado y bloqueante (PR + verify)`
5. `chore(ci): npm audit --audit-level=high bloqueante (PR + verify)`
6. `chore(ci): sanear deuda de lint y promover ruff check a bloqueante (PR + verify)`
7. `chore(ci): piso de cobertura backend en pytest.ini + paridad --cov en verify`
8. `chore(ci): subir ratchet de cobertura frontend en angular.json`

Cada commit es rollback-quirúrgico. Ninguna promoción sin sanear/silenciar antes
la deuda que reportaría. Si `npm audit high` mete demasiado ruido de golpe,
promover primero en `critical`, sanear, y endurecer a `high` en commit posterior.

## Qué NO cambia

- Cadena `needs:` de `fly-deploy.yml`; deploy on-merge; smoke test `/health`.
- Crons `daily-sync.yml` / `sofascore-sync.yml`.
- devDependencies del frontend (ESLint frontend = deuda diferida).
- Topología Fly.io / Neon.

## Sources

- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml` (estado real leído).
- `../infrastructure-design/cicd-pipeline.md`, `../infrastructure-design/infrastructure-specification.md`.
- `../nfr-design/security-design.md` (controles C1–C6).
- `aidlc/spaces/default/memory/team.md` §Code Style / §Deployment / §Testing Posture.

## Assumptions & Open Questions

- Los valores numéricos de pin y del piso de cobertura se fijan al materializar cada commit con la medición sobre la suite estabilizada; la política ya está afirmada.
