# Unidades de Trabajo — Frontend Coverage Gate

Intent: `260918-frontend-coverage-gate` (scope `classic`, brownfield). Este artefacto describe la **topología** de unidades. La secuencia económica (qué se implementa primero) la decide Delivery Planning (2.9); aquí no se recomienda orden de implementación ni ruta crítica.

## Fuentes

- `requirements.md` (FR10.1, FR10.2 y sub-reqs, FR10.3, FR17.1 y sub-reqs; NFR1–NFR5; restricciones).
- Prácticas afirmadas (`team-practices.md`): intervención acotada y aditiva, coste 0 €, gate de CI bloqueante, config en `angular.json`.
- Decisiones de la entrevista de esta etapa (`units-generation-questions.md`): Q1=A (una sola unidad), Q2=A (kind `packaging`).
- Nota: `components.md` (Domain Design) ausente por diseño — la etapa se saltó al no introducir componentes nuevos; la topología deriva de los requisitos directamente.

## Unidades

| Unit ID | Directory | Nombre | Kind | Complejidad | Modelo de despliegue |
|---------|-----------|--------|------|-------------|----------------------|
| U1 | `u1-frontend-coverage-gate` | frontend-coverage-gate | packaging | M | Vía pipeline existente (MR → gate CI → merge → Fly.io); sin cambio de topología |

### U1 — frontend-coverage-gate

**Descripción**: intervención acotada y aditiva que dota al frontend Angular de cobertura de tests medible y creciente, y hace que el pipeline exija esa cobertura antes de producción. Cubre FR10.1 + FR10.2 + FR17.1 como una unidad cohesiva, con orden interno obligado FR10 → FR17.1.

**Responsabilidades (qué posee y entrega la unidad)**:
- **FR10.1**: retirar `skipTests: true` de los schematics de lógica en `angular.json` (`service`, `guard`, `interceptor`, `class`, `component`); mantenerlo en `pipe`, `resolver`, `directive`.
- **FR10.2**: añadir el proveedor OSS `@vitest/coverage-v8` a versión fijada (cambio de `package.json`/`package-lock.json`); declarar la cobertura en el target `test` de `angular.json` (`coverage.all: true`, `coverage.include: src/app/**`, `coverage.exclude` explícito) y umbrales por métrica (`lines`, `branches`, `functions`, `statements`) como trinquete solo-arriba.
- **FR10.3**: sembrar specs de la capa crítica antes de activar el umbral bloqueante — mínimo duro P0 (`core/guards/auth.guard.ts`, `core/services/auth.service.ts`); resto de la fase 1 (demás servicios `core/*`, `auth.interceptor`, bid-dialog) como guía priorizada.
- **FR17.1**: cablear el comando `ng test` con cobertura para que el umbral bloquee en `ci.yml` (PR) y en el job `verify` de `fly-deploy.yml` (push→`main`), con una única fuente de umbral en `angular.json`.

**Kind — `packaging`**: la unidad ES configuración de build/test, tooling y workflows de CI, más specs de test; no es un servicio desplegable, ni una UI, ni una librería reutilizable. Esto acota los artefactos de diseño de Construcción aplicables (sin modelo de negocio ni doc de escalabilidad de servicio).

**Notas de implementación y restricciones**:
- Orden interno obligado: **FR10 → FR17.1** (el gate solo tiene sentido cuando existe el umbral).
- Umbral inicial medido tras la siembra P0 y fijado por debajo de la línea base (colchón 2–5 pts); no se afirma un número concreto (NFR3, evita romper el gate al activarlo).
- Verificar `npm ci` + `ng test` en `node:22.22.3` antes de pushear cambios de devDependencies (NFR5).
- Nunca reformatear en masa ficheros existentes al sembrar specs (NFR2); specs adyacentes a su fuente.
- Specs de auth con fakes/dobles, nunca secretos reales (gitleaks escanea `*.spec.ts`).
- Coste 0 € (NFR1): proveedor OSS, sin servicio de pago.
- La suite existente permanece en verde.

## Assumptions & Open Questions

- El valor numérico exacto del umbral por métrica se fija en implementación tras medir la base post-siembra (por diseño).
- La sintaxis exacta de las opciones de cobertura del builder `@angular/build:unit-test` de Angular 22 se confirma al cablear (principio de fuente única ya afirmado).
