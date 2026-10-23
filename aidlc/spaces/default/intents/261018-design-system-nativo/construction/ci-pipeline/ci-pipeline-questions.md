# CI Pipeline — Preguntas

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

## Q1. Tratamiento del CI para esta capa de diseño iOS

- A. NO modificar `ci.yml`/`fly-deploy.yml` (gate del repo heredado, gobierna backend/frontend Angular); dejar el job Swift en CI como deuda diferida (D-CI de F1); verificación iOS local (`swift build && swift test`) + dispositivo.
- B. Añadir ahora un job Swift a GitHub Actions.
- X. Other (please specify)

[Answer]: A. No modificar el CI del repo; job Swift diferido (D-CI); verificación local + dispositivo.

## Consolidated Summary Confirmation

Resumen de CI Pipeline:

- **CI del repo**: heredado, NO modificado por este intent; sigue gobernando backend (ruff/pytest/pip-audit/gitleaks) y frontend Angular (ng test/npm audit).
- **iOS en CI**: job Swift diferido (deuda D-CI de F1); verificación local `swift build && swift test` + validación en dispositivo.
- **Quality gates**: build nativo verde, 43 tests sin regresión; cobertura llvm-cov no medible en WSL (no es gate numérico aquí); invariantes durables (no bajar umbrales, sin deps de pago).

¿Does this all look correct?

[Answer]: Looks correct
