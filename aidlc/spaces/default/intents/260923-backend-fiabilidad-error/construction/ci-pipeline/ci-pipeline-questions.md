# CI Pipeline — Preguntas · Construcción (FR3.2 + FR4)

El CI/CD **ya existe y es adecuado**: `ci.yml` (gate bloqueante gitleaks +
`pytest` + `ng test` en PR→`main`) y `fly-deploy.yml` (job `verify` + cadena de
despliegue). Este intent sólo añade el commit aislado de `E722` advisory. Una
sola pregunta de confirmación.

## Q1 — Alcance del CI Pipeline en este intent

- A. **Sin cambios estructurales del pipeline**: documentar la config CI
  existente y las quality gates tal cual (gate bloqueante gitleaks + `pytest` +
  `ng test`; `ruff check` advisory con `E722` re-habilitado; sin tocar la cadena
  `needs:` ni el orden de despliegue). El pipeline ya es adecuado.
- B. Modificar/ampliar el pipeline (p. ej. promover ruff a bloqueante o cerrar la
  asimetría `--cov`).
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
