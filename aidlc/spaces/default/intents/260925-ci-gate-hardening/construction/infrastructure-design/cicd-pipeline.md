# CI/CD Pipeline Design — Intent 4 (gate CI/CD hardening)

> Etapa de diseño. El pipeline endurecido se describe como **DELTA sobre el
> existente** (Q4=A): un pipeline Fly.io maduro con gate bloqueante ya operativo.
> La intervención es acotada y aditiva sobre configuración; no toca lógica de
> negocio. Los snippets son ilustrativos (≤15 líneas).

## Pipeline existente (línea base)

- **PR-gate**: `.github/workflows/ci.yml`, disparo `pull_request` → `main`, job
  `quality` como required status check. Hoy corre: gitleaks `@v3`, `pip-audit`
  (advisory), `npm audit` (advisory), `ruff check` (advisory), `pytest` con
  `--cov=app` observability-only (sin piso), `ng test`.
- **Push-gate**: `.github/workflows/fly-deploy.yml`, job `verify` en push →
  `main`. Hoy corre: gitleaks `@v2`, `pytest -q` **sin `--cov`**, `ng test`. **No
  tiene audits ni lint.**
- **Cadena de deploy**: `verify → deploy-backend → deploy-frontend → smoke-test`
  (`/health`, 5 reintentos, HTTP 200).
- **Crons**: `daily-sync.yml`, `sofascore-sync.yml` (máquinas Fly one-shot).

## Qué NO cambia (invariantes)

- La **cadena `needs:`** (`verify → deploy-backend → deploy-frontend →
  smoke-test`): el endurecimiento refuerza el CONTENIDO de `verify`, no reordena.
- El **deploy on-merge** y el **smoke test** `/health`.
- Los **crons** y la topología Fly.io/Neon.
- Las **devDependencies del frontend** (ESLint frontend queda como deuda diferida).

## Delta del gate endurecido

### Orden de pasos dentro del job (Q1=A, fail-fast)

Los pasos de segundos van antes de la suite cara, para no gastar minutos cuando
un check trivial ya rompe el build:

```
1. gitleaks (versión única fijada)
2. allowlist expiry check (script versionado)
3. pip-audit (backend, entorno instalado, findings con fix)
4. npm audit (frontend, --audit-level=high)
5. ruff check (backend, bloqueante — último del escalón)
6. pytest --cov (backend, piso --cov-fail-under)
7. ng test (frontend, ratchet)
```

### Mapeo etapa → gate (ambos workflows)

| Paso | `ci.yml` (PR-gate) | `verify` (push-gate) | Cambio |
|------|:---:|:---:|--------|
| gitleaks | Sí | Sí | Unificar a versión única fijada (hoy `@v3` vs `@v2`) |
| allowlist expiry check | **Añadir** | **Añadir** | Script versionado nuevo, `run:` step con nombre |
| `pip-audit` (bloqueante, entorno instalado) | Promover (quitar `continue-on-error`) | **Añadir** | Antes advisory en PR, ausente en push |
| `npm audit` (`high`, bloqueante) | Promover | **Añadir** | Antes advisory en PR, ausente en push |
| `ruff check` (bloqueante) | Promover (quitar `continue-on-error`) | **Añadir** | Último paso del escalón |
| `pytest --cov` + piso | Introducir piso `--cov-fail-under` | **Añadir** `--cov` + mismo piso | Hoy `verify` corre `pytest -q` sin `--cov` |
| `ng test` (ratchet) | Subir umbrales en `angular.json` | Ya presente | Solo ratchet; ya con paridad |

### Ubicación del expiry check (Q2=A)

Script versionado único en el repo (p. ej. `scripts/check-allowlist-expiry.*`),
invocado como `run:` step con nombre propio en ambos workflows. Una sola fuente
de verdad; testeable en local a coste 0 €. Pseudocódigo ilustrativo (≤15
líneas):

```bash
today=$(date -u +%F)
fail=0
while read -r cve dep expiry _; do
  [ "${cve#\#}" != "$cve" ] && continue         # salta comentarios
  [ "$expiry" \< "$today" ] && { echo "::error::$cve ($dep) expired $expiry"; fail=1; }
done < "$ALLOWLIST_FILE"
exit $fail
```

## Estrategia de promoción escalonada (secuencia de commits `chore(ci)`)

Cada endurecimiento en su propio commit `chore(ci)` aislado con el trinquete
fijado, para rollback quirúrgico. Orden afirmado (mayor señal de seguridad y
menor ruido primero):

1. `chore(ci)`: unificar y fijar gitleaks en ambos gates.
2. `chore(ci)`: pinnar tooling (`ruff`, `pip-audit`, `vitest`).
3. `chore(ci)`: añadir la allowlist versionada + el expiry check en ambos gates.
4. `chore(ci)`: promover `pip-audit` a bloqueante (PR) + añadirlo a `verify`.
5. `chore(ci)`: promover `npm audit --audit-level=high` (PR) + añadirlo a `verify`.
   (Si el ruido heredado es alto, promover primero en `critical`, sanear, luego `high`.)
6. `chore(ci)`: sanear/silenciar quirúrgicamente la deuda de lint (por fichero o
   `per-file-ignores`/`# noqa`), luego promover `ruff check` a bloqueante (PR) +
   añadirlo a `verify`.
7. `chore(ci)`: introducir el piso `--cov-fail-under` en `pytest.ini` (medido al
   final del escalón sobre la suite estabilizada, valor exacto sin margen) + la
   misma invocación con `--cov` y el mismo piso en `verify` (mismo commit o
   inmediatamente después).
8. `chore(ci)`: subir el ratchet de cobertura frontend en `angular.json`.

Cada promoción **NO** se hace de golpe sin sanear antes la deuda que reportaría.

## Deployment strategy y rollback (sin cambios)

- **Estrategia**: deploy on-merge a `main`; sin blue-green/canary (topología de
  dos apps Fly.io intacta). El smoke test `/health` es la verificación de release.
- **Rollback**: redeploy de la release anterior con Fly.io (`fly releases
  rollback`), runbook `docs/ROLLBACK.md`. Además, cada endurecimiento del gate en
  commit `chore(ci)` aislado permite rollback quirúrgico de un solo cambio.
- **Promoción de entornos**: no hay staging separado; línea base afirmada.

## Secrets management en CI/CD

- Secretos siempre vía `secrets` de GitHub Actions / Fly.io.
- En CI el `JWT_SECRET` es **efímero y no productivo**
  (`ci-ephemeral-secret-not-a-real-one`).
- gitleaks (unificado y fijado) escanea repo y tests; los tests usan fakes/dobles,
  nunca credenciales reales. NUNCA hardcodear secretos en workflows ni specs.
- El pin por SHA de acciones de terceros mutables (`setup-flyctl@master`, etc.)
  se decide en **ci-pipeline**, no aquí.

## Free tier (NFR1.1, Q3=A)

Medir cobertura backend en dos jobs es el coste marginal dominante; se **acepta
como coste necesario** de la paridad (un push no puede eludir el piso). Se
**documenta** el consumo de minutos y el umbral que forzaría salir del free tier
en FR16 (ci-pipeline); no se condiciona ni se salta la medición en `verify`
(eso abriría una ventana de evasión del piso).

## Trazabilidad

- NFR-SEC.1–6 → mapeo etapa→gate + secuencia de promoción; NFR-REL.1 → invariante
  cadena `needs:`; NFR2.1 → commits `chore(ci)` aislados; NFR-OBS.1/.2 → orden
  fail-fast + pasos con nombre; NFR1.1 → sección free tier.

## Sources

- `../nfr-design/security-design.md`, `../nfr-design/reliability-design.md`, `../nfr-design/logical-components.md` (delta de controles y dominios de fallo).
- `./infrastructure-specification.md`, `./monitoring-design.md` (este stage).
- `aidlc/spaces/default/memory/team.md` §Way of Working / §Deployment / §Code Style (secuenciación, cadena `needs:`, promoción escalonada).
- `../nfr-requirements/tech-stack-decisions.md` (pins, allowlist, superficies).

## Assumptions & Open Questions

- El valor numérico del piso de cobertura backend y el consumo exacto de minutos se cierran en ci-pipeline.
