# NFR Requirements — frontend-coverage-gate

Unidad `frontend-coverage-gate` (kind `packaging`). No se generan preguntas nuevas: los NFR aplicables (seguridad de cadena de suministro del proveedor de cobertura, no filtración de secretos en specs, integridad del gate, reproducibilidad de tooling) y las decisiones de stack ya están resueltos por `requirements.md` y las prácticas afirmadas (`team-practices.md`, Q1–Q8). Los NFR de runtime (performance/scalability/reliability/observability) NO aplican a una unidad `packaging`. Se procede directamente a la confirmación consolidada antes de generar artefactos.

## Consolidated Summary Confirmation

Resumen de los NFR/decisiones de esta unidad:

- Seguridad: pin exacto de `@vitest/coverage-v8` (OSS, coste 0 €); verificar `npm ci` + `ng test` en `node:22.22.3` antes de pushear; specs de auth con fakes/dobles (gitleaks escanea `*.spec.ts`); el umbral en `ng test` no debilita el gate bloqueante (gitleaks+pytest+ng test siguen bloqueantes); sin `continue-on-error` sustitutivo.
- Stack: proveedor `@vitest/coverage-v8` casado en major con Vitest 4.x; config de cobertura en el target `test` de `angular.json` (fuente única); umbral por métrica y trinquete; denominador `coverage.all` + `include src/app/**` + excludes; cableado del gate en `ci.yml` y `verify`.
- Runtime NFRs (performance/scalability/reliability/observability): N/A para kind packaging.
- Deuda diferida: SAST/DAST frontend fuera de alcance (Q8=A).

- Looks correct
- Request changes

[Answer]: Looks correct
