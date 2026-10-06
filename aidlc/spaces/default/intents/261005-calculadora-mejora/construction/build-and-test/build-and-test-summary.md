# Build and Test Summary — calculadora-mejora

## Estado general

- **Build**: OK (`ng test` compila; sin errores de compilación).
- **Tests**: 75/75 en verde (15 ficheros) en contenedor `node:22.22.3`.
- **Cobertura frontend**: 24.05% stmt / 24.41% branch / 21.5% func / 23.21% lines
  — por encima de los umbrales de `angular.json` (15/15/13/14). Ratchet: solo
  sube; no se ha bajado ningún umbral.
- **Readiness**: build-ready, test-ready, deployment-ready (frontend-only).

## Inventario de tipos de test generados

| Tipo | Estado |
|------|--------|
| Unit (componente Angular) | Generado en Code Generation; 13 specs para `calculator-toggle` |
| Integración | NO-APLICA (Minimal/refactor) |
| Rendimiento | NO-APLICA (sin NFR de rendimiento) |
| Seguridad | NO-APLICA (frontend-only; gitleaks vigente sobre specs) |

## Expectativas de cobertura

- Umbrales por métrica en `angular.json` (fuente única); el intent sube el
  ratchet al valor medido, nunca lo baja. Cobertura medida ≥ umbrales.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| NFR3-ci-gate | requirements.md NFR3 | Gate CI bloqueante (ng test) en verde | 75/75 pass | `ng test` en `node:22.22.3` | build-and-test | Met |
| NFR4-testability | requirements.md NFR4 | Specs que aseveran el efecto (ON/OFF, invariante, persistencia) | 13 specs, pass | `calculator.component.spec.ts` | build-and-test | Met |
| COV-frontend | angular.json coverageThresholds | ≥ 15/15/13/14 | 24.05/24.41/21.5/23.21 | Coverage summary v8 | build-and-test | Met |
| NFR2-a11y | requirements.md NFR2 | mat-slide-toggle accesible (label, teclado, estado) | mat-slide-toggle con label | `calculator.component.html` | build-and-test | Met |

## Limitaciones / pendientes

- Warnings preexistentes de `SpanishDateAdapter` (DI deprecation): deuda
  brownfield, fuera de alcance de este intent.
- Verificación visual en el stack Docker local sujeta a recrear el proxy
  (incidencia de orquestación, no del código).

## Sources

- `code-generation/code-generation-plan.md`, `unit-test-instructions.md`, `code-summary.md`, `traceability.json`.
- Ejecución de `ng test` (contenedor `node:22.22.3`).

## Assumptions & Open Questions

None.
