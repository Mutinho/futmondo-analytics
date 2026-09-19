# Backlog — Cobertura de tests frontend (FR10) y fiabilidad del pipeline (FR17)

> Estado verificado el 2026-09-18 sobre el código en `main`. Origen: plan de
> mejoras del intent `260911-analisis-mejoras`
> (`inception/requirements-analysis/requirements.md`, FR10 y FR17). Se registra
> aquí, fuera de artefactos de intents cerrados, para abordarlo más adelante
> como un intent propio. No bloquea el despliegue actual (el pipeline pasa en
> verde), pero da falsa sensación de seguridad en el frontend.

## Cómo se verificó

- `angular-app/angular.json` — schematics y builder de test.
- `angular-app/package.json` — devDependencies del runner de test.
- `angular-app/src/**/*.spec.ts` — inventario de specs existentes (2).
- `.github/workflows/ci.yml` — gate de PR.
- `.github/workflows/fly-deploy.yml` — job `verify` + smoke test post-deploy.
- `docs/ROLLBACK.md` — runbook de rollback.
- `backend/pytest.ini` — configuración de cobertura backend (contexto FR11/FR17).

## FR10 — Cobertura de tests en el frontend — ABIERTO (parcial)

Ya resuelto:
- Runner migrado Karma → Vitest: `angular.json` → target `test` usa
  `@angular/build:unit-test` con `runner: vitest`; `package.json` trae
  `vitest ^4.0.8` y `jsdom ^25`. (Cierra el backlog nº4 de CI/tooling.)
- Existen 2 specs reales (antes ~1): `core/interceptors/auth.interceptor.spec.ts`
  y `core/preloading/idle-preloading-strategy.spec.ts`. `ng test` ya no pasa con
  literalmente 0 tests.

Pendiente (criterios de aceptación NO satisfechos):
- **FR10.1 — no cumplido**: `skipTests: true` sigue activo globalmente en
  `angular.json` para TODOS los schematics (component, class, directive, guard,
  interceptor, pipe, resolver, service). Los componentes/servicios nuevos
  siguen naciendo sin archivo de test.
- **FR10.2 — no cumplido**: no hay umbral de cobertura efectivo. No existe
  `vitest.config` con `coverage.thresholds` en el frontend. El gate `ng test`
  sigue pasando con cobertura efectiva ~0 % (solo mide 2 specs sobre toda la
  app).

Acciones propuestas (coste 0 €):
1. Quitar `skipTests: true` (o justificar excepciones puntuales) para que los
   nuevos artefactos nazcan con spec.
2. Añadir `vitest.config` con `coverage` (provider v8/istanbul) y un umbral
   inicial bajo pero creciente (ratcheting), sembrando primero specs de los
   servicios/guards/interceptores críticos.
3. Hacer que `ng test` reporte cobertura y aplique el umbral en el gate.

## FR17 — Endurecer el pipeline de despliegue — PARCIAL

Ya resuelto:
- **FR17.2 — cumplido**: el smoke test `/health` de `fly-deploy.yml` define
  comportamiento ante fallo (5 reintentos; `exit 1` si no hay HTTP 200) y
  `docs/ROLLBACK.md` documenta el procedimiento completo (identificar release
  previa, `fly releases rollback`, verificación de salud, limitaciones).
- Extra (no pedido en FR17): el job `verify` de `fly-deploy.yml` ahora replica
  gitleaks en push→`main`, cerrando el hueco de secretos del push directo.

Pendiente:
- **FR17.1 — no cumplido**: el job `verify` corre `pytest -q` (sin `--cov`) y
  `ng test`, pero arrastra la debilidad de FR10: sin cobertura efectiva ni
  umbral en el frontend, no hay "tests significativos" del lado frontend. Un
  cambio de frontend que rompa lógica no cubierta pasaría el gate igual. El
  criterio "un cambio que rompe tests significativos no llega a producción" solo
  se cumple para el backend.
- **FR17.3 — no abordado**: evaluar un gate de verificación más completo antes
  del deploy (respetando coste 0 €).

Nota (contexto FR11): `backend/pytest.ini` deja la cobertura como métrica
informativa, sin `fail_under`; el gate de MR corre `--cov` pero sin piso
bloqueante. Coherente con lo afirmado en `team.md`.

## Dependencia

FR17.1 depende de FR10: cerrar FR10 (quitar `skipTests`, sembrar specs, fijar
umbral) desbloquea la parte de "tests significativos" de FR17.1. Conviene
abordarlos juntos en un mismo intent (scope `refactor` o `feature`), con el
orden FR10 → FR17.1.

## Estado resumido

| Req    | Criterio                                              | Estado         |
|--------|-------------------------------------------------------|----------------|
| FR10.1 | Nuevos componentes nacen con test (`skipTests` fuera) | No cumplido    |
| FR10.2 | Umbral de cobertura efectivo                          | No cumplido    |
| FR17.1 | `verify` con tests significativos                     | No cumplido    |
| FR17.2 | Acción ante fallo del smoke + rollback documentado    | Cumplido       |
| FR17.3 | Gate de verificación más completo                     | No abordado    |
