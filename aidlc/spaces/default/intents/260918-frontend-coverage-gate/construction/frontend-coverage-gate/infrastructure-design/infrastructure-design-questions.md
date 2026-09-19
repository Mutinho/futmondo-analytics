# Infrastructure Design — frontend-coverage-gate

Unidad `frontend-coverage-gate` (kind `packaging`). No se generan preguntas nuevas: el diseño deriva de los requisitos y el diseño NFR ya afirmados. No hay infraestructura desplegable nueva; el foco es el cableado del gate de cobertura en los workflows existentes (FR17.1). Se procede a la confirmación consolidada antes de finalizar.

## Consolidated Summary Confirmation

Resumen del diseño de infraestructura de esta unidad:

- `cicd-pipeline.md`: fuente única de umbral en `angular.json`; se corrige `ng test --watch=false` en `ci.yml` (PR) y en el job `verify` de `fly-deploy.yml` (push→`main`) para ejercitar cobertura; sin cambiar la cadena `needs:`; `ng test`/gitleaks/pytest siguen bloqueantes; reporte de cobertura solo observabilidad sin `continue-on-error` sustitutivo; Node 22 / `.nvmrc` 22.22.3.
- `infrastructure-specification.md`: sin infraestructura desplegable nueva; misma topología Fly.io + Neon; IaC/AWS NO-APLICA (stack real Fly.io + GitHub Actions); coste 0 €.
- `monitoring-design.md`: la observabilidad es el reporte de cobertura de CI; SLO/tracing formales NO-APLICA (packaging, coste 0 €); healthcheck `/health` sin cambios.
- Deuda diferida: paridad `--cov` backend en `verify` y SAST/DAST frontend (Q8=A).

- Looks correct
- Request changes

[Answer]: Looks correct
