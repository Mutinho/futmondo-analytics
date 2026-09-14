# Resumen de Build y Test — Mejoras de CI/Tooling

> Etapa Build and Test (Construction) · Intent `260914-ci-tooling-mejoras` · Scope `refactor` · Estrategia Minimal.

## Estado general

- **Build (`npm ci`)**: OK, 0 vulnerabilidades.
- **Build (`ng build` producción)**: FALLA por presupuesto de bundle preexistente (1.03 MB > 1 MB), ajeno al alcance del intent.
- **Unit tests (Vitest)**: 6/6 verdes, sin regresión.

## Inventario de tipos de test generados

| Tipo | Generado | Motivo |
|------|----------|--------|
| Unit | (cubierto en Code Generation, migrado a Vitest) | Estrategia Minimal: unit por componente |
| Integration | No | Estrategia Minimal no genera integración |
| Performance | No | Sin NFR de rendimiento nuevos |
| Security | No | Sin NFR de seguridad nuevos (NFR4 verificado por inspección de workflows) |

## Expectativas de cobertura

- Scope `refactor`, estrategia Minimal: sin suelo de cobertura nuevo. Criterio = suite existente en verde + despliegue operativo (BR6.1).

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| FR1-actions-node24 | requirements.md FR1 | setup-node a Node 24, sin flag inseguro | setup-node@v5 en ambos workflows | ci.yml, fly-deploy.yml | Met |
| FR2-punycode | requirements.md FR2 | DEP0040 eliminado o vigilado | punycode fuera del lock; nota de vigilancia | package-lock.json, dependencies.md | Met |
| FR3-animaciones | requirements.md FR3 | Sin aviso deprecación; provider conservado | Sin API antigua; provider conservado; documentado | app.config.ts, architecture.md | Met |
| FR4-karma-vitest | requirements.md FR4 | runner vitest; sin Karma; suite verde | runner=vitest; Karma fuera; 6/6 verdes | angular.json, package.json, test run | Met |
| FR5-node-local | requirements.md FR5 | .nvmrc + README | .nvmrc=22.22.3; README | .nvmrc, README.md | Met |
| NFR4-ci-seguridad | requirements.md NFR4 | Sin runtime inseguro de Node | Sin flag inseguro; Node 24 | ci.yml, fly-deploy.yml | Met |
| BUILD-prod-budget | angular.json budgets | Bundle inicial <= 1 MB | 1.03 MB | ng build output | Not Met (preexistente, fuera de alcance) |

## Evaluación de readiness

- **Build-ready**: parcial — el frontend compila pero el build de producción no supera el presupuesto de bundle preexistente. Los cambios de este intent (runner de test, workflows, .nvmrc, dependencias) no afectan al tamaño del bundle.
- **Test-ready**: sí — suite verde con Vitest, sin regresión.
- **Deployment-ready**: la decisión sobre el fallo de presupuesto de bundle corresponde al humano (fuera del alcance de CI/tooling).

## Limitaciones / pendientes

- El presupuesto de bundle (1 MB) es deuda preexistente; su resolución (optimizar bundle o ajustar presupuesto) es un intent aparte, no de CI/tooling.
- La ejecución de los workflows de CI (mejoras 1 y 4) y del despliegue (`fly-deploy.yml`) se confirma en GitHub Actions al abrir PR / push.
