# Plan de Bolts — Frontend Coverage Gate

Un **Bolt** es una pasada de construcción sobre una pieza del trabajo que termina en algo que corre y se puede demostrar. Este intent tiene una sola unidad de trabajo, así que el plan es un **único Bolt**.

## Walking skeleton

**No se ejecuta ceremonia de walking skeleton** (afirmado en `team-practices.md`, línea base OFF): el sistema ya está en producción con pipeline Fly.io maduro y un gate de CI bloqueante operativo. No hay nada que arrancar de cero; la intervención es acotada y aditiva sobre infraestructura existente. El primer (y único) Bolt corre como un Bolt normal.

## Secuencia de Bolts

### Bolt 1 — `frontend-coverage-gate` (único)

- **Unidad(es) incluida(s)**: `U1` `frontend-coverage-gate` (dir `u1-frontend-coverage-gate`), kind `packaging`.
- **Walking-skeleton marker**: No.
- **Alcance**: FR10.1 + FR10.2 (+ sub-reqs) + FR10.3 (siembra P0 duro / P1-P2 guía) + FR17.1 (+ sub-reqs).
- **Orden interno (secuencia dentro del Bolt)**: primero un **spike de cableado/medición** que valida los supuestos técnicos A2 (el builder `@angular/build:unit-test` lee `coverage.*` desde el target `test` de `angular.json`) y A3 (el enforcement se propaga a `ci.yml` y `verify`) — Q1=A —; después FR10.1 (`skipTests`) → FR10.2 (provider `@vitest/coverage-v8` a versión fijada + `coverage.all`/`include`/`exclude` + umbrales por métrica) → FR10.3 (siembra P0 `auth.guard` + `auth.service`, luego P1/P2) → medir base y fijar umbral por debajo → FR17.1 (cablear el comando `ng test` con cobertura en `ci.yml` y `verify`).
- **Definition of Done**:
  - `angular.json` no genera código de lógica sin spec (FR10.1: `skipTests` retirado de service/guard/interceptor/class/component; mantenido en pipe/resolver/directive).
  - `ng test` mide y **exige** cobertura por métrica (`lines`, `branches`, `functions`, `statements`) contra un umbral con denominador estable (`coverage.all` + `include src/app/**` + excludes), declarado en el target `test` de `angular.json` (FR10.2).
  - Specs P0 (`auth.guard`, `auth.service`) verdes con aserciones reales; suite existente en verde (FR10.3.1, NFR3).
  - El umbral **bloquea** en `ci.yml` (PR) y en el job `verify` de `fly-deploy.yml` (push→`main`) con una única fuente de umbral (FR17.1).
  - Coste 0 € (NFR1); `npm ci` + `ng test` verificados en `node:22.22.3` antes de pushear (NFR5).
- **Hipótesis de confianza (qué prueba shipear este Bolt)**: que un cambio que rompa lógica cubierta del frontend (p. ej. `auth.interceptor` o un servicio `core/*`) **falla el gate** en ambos caminos de CI y no llega a producción; y que la cobertura es medible y puede crecer por trinquete sin romper el gate.
- **Demo esperada**: abrir una PR con una regresión deliberada en código cubierto y mostrar que `ng test` falla por métrica de cobertura; mostrar el mismo enforcement en el job `verify`; mostrar el reporte de cobertura por métrica sobre `src/app/**`.

## Assumptions & Open Questions

- El valor numérico exacto del umbral por métrica se fija en implementación tras medir la base post-siembra (por diseño).
- A2/A3 se validan en el spike inicial del Bolt (Q1=A).
