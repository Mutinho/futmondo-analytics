# Build and Test Summary — frontend-coverage-gate

Intent `260918-frontend-coverage-gate` (scope `classic`, brownfield, frontend-only). Estrategia **standard**, metodología **test-after**. Una sola unidad: `frontend-coverage-gate` (kind `packaging`).

## Estado del build

- **Prerrequisitos**: Node `22.22.3`, `npm@11.12.1`. Verificado en contenedor `node:22.22.3` (coste 0 €).
- **Build**: `npx ng test --watch=false` arranca el builder `@angular/build:unit-test` → "Application bundle generation complete" (bundle OK) → suite con cobertura V8.
- **Resultado**: build-ready ✔.

## Inventario de tipos de test generados

- Unit (per-unit, de Code Generation): 12 specs sembrados + 2 preexistentes = 14 ficheros / 62 tests.
- Integration: cubierto a nivel unit con dobles HTTP deterministas (no hay integración cross-unit; unidad única). Ver `integration-test-instructions.md`.
- Performance: **N/A** (sin NFR de rendimiento). Ver `performance-test-instructions.md`.
- Security: higiene de specs + supply-chain del proveedor; SAST/DAST diferido. Ver `security-test-instructions.md`.

## Expectativas de cobertura (unidad `frontend-coverage-gate`)

Cobertura por métrica sobre `src/app/**/*.ts` (denominador estable `coverageInclude`), umbral en el target `test` de `angular.json`, trinquete solo-arriba. Umbrales: `statements 15`, `branches 15`, `functions 13`, `lines 14`.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| FR10.1 | requirements.md §FR10.1 | `skipTests` retirado de service/guard/interceptor/class/component; mantenido en pipe/resolver/directive | `angular.json`: retirado en los 5 schematics de lógica; mantenido en pipe/resolver/directive | `angular-app/angular.json` (schematics) | build-and-test | Met |
| FR10.2 | requirements.md §FR10.2 | `ng test` mide y exige cobertura por métrica; proveedor OSS pin exacto major-matched | `@vitest/coverage-v8@4.1.11` (lock, major-matched a vitest 4.1.11); cobertura reportada por V8 | `package-lock.json`; salida `ng test` "Coverage enabled with v8" | build-and-test | Met |
| FR10.2.1 | requirements.md §FR10.2.1 | Denominador estable `coverage.all`/`include src/app/**` + excludes | `coverage:true`, `coverageInclude:["src/app/**/*.ts"]`, `coverageExclude` explícito; denominador 2057 statements/1772 lines (app completa) | `angular-app/angular.json` target `test`; summary V8 | build-and-test | Met |
| FR10.2.2 | requirements.md §FR10.2.2 | Umbral por métrica (no global único) | `coverageThresholds{statements:15,branches:15,functions:13,lines:14}` | `angular-app/angular.json` | build-and-test | Met |
| FR10.2.3 | requirements.md §FR10.2.3 | Umbral ratcheting solo-arriba, fijado bajo la base medida | Umbrales ~4 pts bajo la base (19.2/19.53/17.26/18.05); regla dura "solo sube" afirmada | code-summary.md; salida `ng test` | build-and-test | Met |
| FR10.3.1 | requirements.md §FR10.3.1 | Specs P0 `auth.guard` + `auth.service` con aserciones reales | `auth.guard.spec.ts` (5 tests) y `auth.service.spec.ts` (6 tests) en verde; aserciones de payload/headers/estado | salida `ng test` (14 ficheros passed) | build-and-test | Met |
| FR10.3.2 | requirements.md §FR10.3.2 | Guía P1/P2 sembrada (resto core/services, interceptor, bid-dialog) | 9 servicios HTTP + interceptor + bid-dialog con spec en verde | salida `ng test` | build-and-test | Met |
| FR17.1 | requirements.md §FR17.1 | Umbral bloquea en `ci.yml` y en `verify`, fuente única en `angular.json` | Ambos workflows corren `ng test --watch=false` (ejerce umbral); fuente única en `angular.json`; fail-closed probado (95%→exit 1) | `.github/workflows/ci.yml`, `fly-deploy.yml`; code-summary.md | build-and-test | Met |
| FR17.1.1 | requirements.md §FR17.1.1 | `branches`/`functions` como proxy anti tests-espejo; sin tooling lint nuevo | Umbral por métrica incluye branches/functions; `expect(true).toBe(true)` ausente (grep 0) | `angular.json`; revisión de specs | build-and-test | Met |
| FR17.1.2 | requirements.md §FR17.1.2 | Enforcement dentro de `ng test`, sin `continue-on-error` sustitutivo | Sin `continue-on-error` en los pasos frontend; `needs:` intacto | `.github/workflows/ci.yml`, `fly-deploy.yml` | build-and-test | Met |
| COV-STATEMENTS | angular.json coverageThresholds | ≥ 15 | 19.2% (395/2057) | salida `ng test` V8 summary; NG_TEST_EXIT=0 | build-and-test | Met |
| COV-BRANCHES | angular.json coverageThresholds | ≥ 15 | 19.53% (176/901) | salida `ng test` V8 summary | build-and-test | Met |
| COV-FUNCTIONS | angular.json coverageThresholds | ≥ 13 | 17.26% (67/388) | salida `ng test` V8 summary | build-and-test | Met |
| COV-LINES | angular.json coverageThresholds | ≥ 14 | 18.05% (320/1772) | salida `ng test` V8 summary | build-and-test | Met |
| NFR1 | requirements.md §NFR1 | Coste 0 € (tiers gratuitos; proveedor OSS) | `@vitest/coverage-v8` OSS; verificación en contenedor gratuito; sin servicio de pago | package.json; build-instructions.md | build-and-test | Met |
| NFR3 | requirements.md §NFR3 | Suite existente en verde; umbral bajo la base | 62/62 verde (incluye los 2 specs preexistentes); umbrales bajo la base | salida `ng test` | build-and-test | Met |
| NFR4 | requirements.md §NFR4 | Determinismo (sin red/sleep; fakes; sin secretos reales) | HttpTestingController/fakes; SSE con ReadableStream mock; sin tokens reales | specs; security-test-instructions.md | build-and-test | Met |
| NFR5 | requirements.md §NFR5 | Verificado `npm ci`+`ng test` en `node:22.22.3` | Ejecutado en contenedor `node:22.22.3`, NG_TEST_EXIT=0 | test-results.md | build-and-test | Met |
| C3 | requirements.md §C3 | Proveedor pin exacto casado en major con vitest 4.x | `@vitest/coverage-v8@4.1.11` = `vitest@4.1.11` (lock) | package-lock.json | build-and-test | Met |
| NFR2-BACKEND | requirements.md §NFR2 (fuera de alcance backend) | Backend inalterado; suite backend enforced independientemente en CI | Sin cambios en `backend/`; `pytest` sigue como gate independiente en `ci.yml`/`verify` | git diff (frontend-only); ci.yml | build-and-test | Met |

## Readiness

- **Build-ready**: ✔
- **Test-ready**: ✔ (62/62 verde, umbral por métrica superado, fail-closed probado)
- **Deployment-ready**: ✔ (el umbral bloquea en `ci.yml` y `verify`; cadena `needs:` intacta; topología de despliegue sin cambios)

## Limitaciones / pendientes conocidos

- SAST/DAST del frontend y paridad `--cov` de backend en `verify`: **deuda de pipeline diferida** (Q8=A), fuera de alcance de este intent.
- El trinquete de cobertura sube manualmente por MR conforme crece la cobertura real; el umbral nunca se baja para pasar el gate (regla dura).
