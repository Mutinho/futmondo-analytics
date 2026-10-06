# Test Results — calculadora-mejora

## Build

- **Estado**: OK. `ng test` compiló el proyecto sin errores (contenedor `node:22.22.3`).

## Resultados de tests

- **Total**: 75 · **Passed**: 75 · **Failed**: 0 · **Skipped**: 0.
- **Ficheros de test**: 15.
- Spec de la unidad `calculator-toggle`: `calculator.component.spec.ts` — 13 tests, pass (141 ms).
- Comando (unit-scoped del componente): `npx ng test --include "src/app/features/calculator/calculator.component.spec.ts"` → 13/13.
- Comando (suite completa): `npx ng test` → 75/75.

## Cobertura

```
Statements : 24.05% (515/2141)
Branches   : 24.41% (239/979)
Functions  : 21.5%  (86/400)
Lines      : 23.21% (419/1805)
```

Por encima de los umbrales de `angular.json` (statements 15 / branches 15 /
functions 13 / lines 14). Sin bajar ningún umbral.

## Detalle de fallos

- Ninguno.

## Matriz de verificación de targets (finalizada)

| Target ID | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|----------|--------|----------|--------------|---------|
| NFR3-ci-gate | ng test en verde | 75/75 pass | ejecución `ng test` | build-and-test | Met |
| NFR4-testability | specs que aseveran el efecto | 13 specs pass | `calculator.component.spec.ts` | build-and-test | Met |
| COV-frontend | ≥ 15/15/13/14 | 24.05/24.41/21.5/23.21 | coverage summary v8 | build-and-test | Met |
| NFR2-a11y | toggle Material accesible | mat-slide-toggle + label | `calculator.component.html` | build-and-test | Met |

Sin verdicts `Pending`, `Not Met` ni `Unverified`.

## Notas

- Warnings `SpanishDateAdapter` (DI deprecation): deuda brownfield preexistente,
  no introducida por este cambio, fuera de alcance.

## Sources

- Ejecución de `ng test` en `node:22.22.3`; `code-generation/*`.

## Assumptions & Open Questions

None.
