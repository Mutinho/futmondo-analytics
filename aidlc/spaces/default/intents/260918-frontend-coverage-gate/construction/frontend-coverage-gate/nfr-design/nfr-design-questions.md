# NFR Design — frontend-coverage-gate

Unidad `frontend-coverage-gate` (kind `packaging`). No se generan preguntas nuevas: el diseño de seguridad deriva de los requisitos ya afirmados (`security-requirements.md` NFR1.1–1.5) y las prácticas. Las categorías NFR de runtime (resiliencia, escalabilidad, observabilidad de servicio) son N/A para una unidad packaging. Se procede a la confirmación consolidada antes de finalizar los artefactos.

## Consolidated Summary Confirmation

Resumen del diseño NFR de esta unidad (`security-design.md`):

- NFR1.1: diseño de cadena de suministro — `@vitest/coverage-v8` a versión exacta casada en major con Vitest 4.x; lockfile regenerado y commiteado.
- NFR1.2: procedimiento de verificación reproducible (`npm ci` + `ng test` en `node:22.22.3`) antes de pushear; `npm audit` advisory.
- NFR1.3: specs de auth con fakes/dobles (token de prueba inventado), gitleaks bloqueante escanea `*.spec.ts`.
- NFR1.4/1.5: integridad del gate — umbral en el target `test` de `angular.json` (fuente única), `ng test` sigue bloqueante en `ci.yml` y `verify`; reporte de cobertura solo observabilidad sin `continue-on-error` sustitutivo; ratchet solo-arriba.
- Categorías de runtime (resiliencia/escalabilidad/observabilidad de servicio): N/A (kind packaging).
- Deuda diferida: SAST/DAST frontend (Q8=A).

- Looks correct
- Request changes

[Answer]: Looks correct
