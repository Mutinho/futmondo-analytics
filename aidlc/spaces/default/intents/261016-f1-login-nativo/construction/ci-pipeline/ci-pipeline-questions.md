# CI Pipeline — Preguntas (F1: Login nativo end-to-end)

> Idioma: castellano; tokens técnicos verbatim en inglés.

## Q1 — ¿La configuración de CI y los quality gates para F1 son correctos?

- A. **Correctos** — reutilizar el gate de CI existente; CI de Swift como deuda registrada
  (recomendado).
- B. Correctos con un ajuste (especifícalo: p. ej. añadir ya un job de `swift test` a CI).
- C. Replantear (especifícalo).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar ci-pipeline, confirma:

- **F1 no añade workflows nuevos**: reutiliza el gate de CI bloqueante ya operativo del repo
  (`ci.yml` job `quality` + `fly-deploy.yml` job `verify`): gitleaks + `ruff check` + `pytest` +
  `pip-audit` + `ng test` + `npm audit`.
- **Backend D-01**: cubierto por ese CI (el PR pasó ruff + pytest + gitleaks + pip-audit).
- **Swift (`ios/`)**: la lógica se verifica con `swift test` en WSL (29 passed) y el dispositivo
  con `xtool`; **no** hay job de Swift en GitHub Actions → **deuda registrada** (P-1, coste 0 €).
- El trinquete de cobertura backend no se baja; no hay piso iOS aún (deuda del arnés de dispositivo).

¿Está todo correcto?

[Answer]: Looks correct
