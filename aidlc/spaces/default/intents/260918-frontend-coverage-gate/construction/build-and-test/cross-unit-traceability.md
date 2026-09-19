# Cross-Unit Traceability — frontend-coverage-gate

Gate de cobertura cross-unit (nivel etapa, no frontera de fase). Fuentes:
- Requisitos: `<record>/inception/requirements-analysis/requirements.md`.
- User stories: **no aplica** (la etapa User Stories 2.4 fue SKIPPED — tooling/infra), así que no hay `AC` de tres segmentos que enumerar.
- Trazabilidad de unidad: `<record>/construction/frontend-coverage-gate/code-generation/traceability.json` (unidad única; no hay traceability.json a nivel etapa).

## Verdicto: **PASS** — todos los IDs enumerados están cubiertos con status `OK` y su fichero objetivo existe.

| ID | Cubierto | Status | Unidad | Fichero objetivo | Existe |
|---|---|---|---|---|---|
| FR10.1 | Sí | OK | frontend-coverage-gate | `angular-app/angular.json` | ✔ |
| FR10.2 | Sí | OK | frontend-coverage-gate | `angular-app/package.json` | ✔ |
| FR10.2.1 | Sí | OK | frontend-coverage-gate | `angular-app/angular.json` | ✔ |
| FR10.2.2 | Sí | OK | frontend-coverage-gate | `angular-app/angular.json` | ✔ |
| FR10.2.3 | Sí | OK | frontend-coverage-gate | `angular-app/angular.json` | ✔ |
| FR10.3 | Sí | OK | frontend-coverage-gate | `angular-app/src/app/core/guards/auth.guard.spec.ts` | ✔ |
| FR10.3.1 | Sí | OK | frontend-coverage-gate | `angular-app/src/app/core/services/auth.service.spec.ts` | ✔ |
| FR10.3.2 | Sí | OK | frontend-coverage-gate | `angular-app/src/app/features/market/bid-dialog.component.spec.ts` | ✔ |
| FR17.1 | Sí | OK | frontend-coverage-gate | `.github/workflows/ci.yml` | ✔ |
| FR17.1.1 | Sí | OK | frontend-coverage-gate | `angular-app/angular.json` | ✔ |
| FR17.1.2 | Sí | OK | frontend-coverage-gate | `.github/workflows/fly-deploy.yml` | ✔ |
| NFR1 (=NFR1.1 trazado) | Sí | OK | frontend-coverage-gate | `angular-app/package.json` | ✔ |
| NFR1.3 | Sí | OK | frontend-coverage-gate | `angular-app/src/app/core/services/auth.service.spec.ts` | ✔ |
| NFR2 | Sí | OK (aditivo, sin reescrituras; verificado por diff frontend-only) | frontend-coverage-gate | `angular-app/angular.json` + specs nuevos | ✔ |
| NFR3 | Sí | OK | frontend-coverage-gate | `angular-app/angular.json` (umbral bajo la base) + suite verde | ✔ |
| NFR4 | Sí | OK | frontend-coverage-gate | `angular-app/src/app/core/services/assistant.service.spec.ts` | ✔ |
| NFR5 | Sí | OK | frontend-coverage-gate | `angular-app/package-lock.json` | ✔ |

## Notas de mapeo

- El `traceability.json` de la unidad enumera FR10.1/.2/.2.1/.2.2/.2.3/.3/.3.1/.3.2, FR17.1/.1.1/.1.2 y NFR1.1/1.3/3/4/5, todos `OK`. Los IDs de requisitos de nivel superior (NFR1, NFR2) se cubren por sus derivados/artefactos; NFR2 (sin reescrituras) se evidencia por el diff frontend-only y el mandato de no reformatear en masa.
- No hay IDs sin cubrir. Sin hallazgos para el gate.
