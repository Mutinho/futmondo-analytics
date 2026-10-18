# CI Config — F1: Login nativo end-to-end

> Fase: construcción (ci-pipeline). Perspectiva de release engineer. Idioma: castellano;
> identificadores/claves YAML verbatim en inglés. F1 **no introduce** workflows nuevos: reutiliza
> el gate de CI bloqueante ya operativo del repo y documenta qué cubre.

## CI existente del repo (reutilizado, sin cambios)

- **`.github/workflows/ci.yml`** (disparo `pull_request` → `main`, job `quality` como required
  status check): gitleaks + `ruff check` + `pytest` + `pip-audit` + `ng test` + `npm audit`.
- **`.github/workflows/fly-deploy.yml`** (push directo a `main`, job `verify`): replica el gate
  antes de desplegar (`verify → deploy-backend → deploy-frontend → smoke-test`).

## Cobertura para F1

- **Ajuste de backend (D-01)**: cubierto por el CI existente. El PR del backend pasó
  `ruff check` + `pytest` (incluidos los 8 tests nuevos de `test_auth_refresh_transport.py`) +
  gitleaks + pip-audit. Un rojo nunca llega a `main` (regla durable).
- **Cliente nativo Swift (`ios/`)**: **NO** cubierto por el CI del repo. No hay runner de Swift en
  GitHub Actions configurado; la verificación de la lógica (`swift test`, 29 tests) se ejecuta en
  WSL (Swift 6.4), y la validación de dispositivo con `xtool` en el iPhone. gitleaks sí escanea
  también `ios/` (no hay secretos).

## Deuda registrada (no se aborda en F1)

- **CI de Swift** (`swift test` en GitHub Actions): queda como **deuda** (P-1 + coste 0 €). Añadir
  un job de Swift es trabajo de un intent posterior; para F1 la verificación de `swift test` es
  local y reproducible por el propietario. No se introduce aquí para no inflar el alcance ni el
  coste.

## Sources

- [consumes] build-and-test-summary.md, test-results.md; code-summary de los bolts.
- [code] `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`; team.md (gate de CI).

## Assumptions & Open Questions

None.
