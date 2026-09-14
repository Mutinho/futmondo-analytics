# Trazabilidad Cross-Unit — Mejoras de CI/Tooling

> Etapa Build and Test (Construction) · Intent `260914-ci-tooling-mejoras` · Scope `refactor` (zero-Unit).
> Gate de cobertura final a nivel de etapa. Fuente de IDs: `requirements.md`. No hay `stories.md` (user-stories no ejecutó en este scope). Trazabilidad de code-generation: `construction/code-generation/traceability.json`.

## Veredicto

**PASS** — todos los FR y NFR de `requirements.md` están cubiertos con estado `OK` en `code-generation/traceability.json` y sus ficheros destino existen.

## Cobertura por elemento

| ID | Cubierto | Fichero destino (existe) | Etapa/Unit |
|----|----------|--------------------------|------------|
| FR1.1 | OK | .github/workflows/ci.yml | code-generation |
| FR1.2 | OK | .github/workflows/ci.yml | code-generation |
| FR1.3 | OK | .github/workflows/fly-deploy.yml | code-generation |
| FR2.1 | OK | angular-app/package-lock.json | code-generation |
| FR2.2 | OK | angular-app/package.json | code-generation |
| FR2.3 | OK | codekb/futmondo-analytics/dependencies.md | code-generation |
| FR3.1 | OK | angular-app/src/app/app.config.ts | code-generation |
| FR3.3 | OK | codekb/futmondo-analytics/architecture.md | code-generation |
| FR3.4 | OK | codekb/futmondo-analytics/architecture.md | code-generation |
| FR4.1 | OK | angular-app/angular.json | code-generation |
| FR4.2 | OK | angular-app/package.json | code-generation |
| FR4.3 | OK | angular-app/src/app/core/interceptors/auth.interceptor.spec.ts (6/6 verdes) | code-generation + build-and-test |
| FR4.4 | OK | angular-app/package-lock.json | code-generation |
| FR4.5 | OK | unit-test-instructions.md (línea base + verificación) | code-generation + build-and-test |
| FR5.1 | OK | .nvmrc | code-generation |
| FR5.2 | OK | README.md | code-generation |
| FR6.1 | OK | fly-deploy.yml (criterio transversal) | code-generation |
| FR6.2 | OK | code-generation-plan.md (secuencia por riesgo) | code-generation |
| NFR1 | OK | angular-app/package.json (coste 0€, tiers gratuitos) | code-generation |
| NFR2 | OK | auth.interceptor.spec.ts (no regresión funcional) | code-generation + build-and-test |
| NFR3 | OK | .nvmrc (reproducibilidad de entorno) | code-generation |
| NFR4 | OK | ci.yml (sin runtime inseguro de Node) | code-generation |
| NFR5 | OK | angular.json (tooling de test con soporte activo) | code-generation |

## Elementos sin cobertura

Ninguno. Todos los FR/NFR de `requirements.md` están cubiertos.

## Nota

El fallo del build de producción por presupuesto de bundle (`BUILD-prod-budget`, 1.03 MB > 1 MB) es un objetivo de calidad preexistente ajeno a los FR/NFR de este intent; se registra en `test-results.md` y se eleva al gate de aprobación como hallazgo, sin afectar a la cobertura de requisitos del intent.
