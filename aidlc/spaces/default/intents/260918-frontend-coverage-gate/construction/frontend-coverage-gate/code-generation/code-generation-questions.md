# Code Generation — frontend-coverage-gate

## Plan Approval

Aprobar este plan exacto de generación de código (cubre `code-generation-plan.md`, su Testing Contract embebido y `unit-test-instructions.md`).

Resumen del plan (11 pasos, metodología test-after, orden FR10 → FR17.1):
1. Spike de cableado/medición (valida A2/A3) en `node:22.22.3`.
2. Runner readiness (Vitest existente; comando unit-scoped registrado).
3. FR10.1: retirar `skipTests` en service/guard/interceptor/class/component; mantener en pipe/resolver/directive.
4. FR10.2: añadir `@vitest/coverage-v8` a versión exacta; regenerar lock.
5. FR10.2.1: denominador estable (`coverage.all` + `include src/app/**` + excludes) en el target `test` de `angular.json`.
6. FR10.3.1 (P0 duro): specs de `auth.guard` + `auth.service` con aserciones reales, fakes.
7. FR10.3.2 (P1/P2 guía): resto de `core/services/*`, interceptor, bid-dialog.
8. Medir base y fijar umbral por métrica ligeramente por debajo (trinquete solo-arriba).
9. FR17.1: cablear `ng test` con cobertura en `ci.yml` y `verify`, bloqueante, sin `continue-on-error` sustitutivo, `needs:` intacto.
10. Verificación local `npm ci` + `ng test` en `node:22.22.3`; suite existente en verde.
11. Documentación + `source-manifest.json` + `traceability.json`.

Instrucciones de test (`unit-test-instructions.md`): comando exacto `npm ci` + `npx ng test --watch=false` desde `angular-app/` (Vitest + cobertura desde `angular.json`); estrategia standard; mocking con `HttpTestingController`/`provideHttpClientTesting`/`runInInjectionContext`; datos deterministas con fakes, nunca secretos reales; aserciones significativas.

[Approval Fingerprint]: sha256:v3:0845baa70369454893ca57c916214f2df343eb5a9f478f13b7aeb19739c9e57e
[Planned Source]: f87b21a1bec7828690f526442b382e10ac9206a98a327ee45c6dfbfa445410c3

- Approve Plan
- Request Changes

[Answer]: Approve Plan
