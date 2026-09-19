# Decisiones de Stack Tecnológico (NFR) — frontend-coverage-gate

Unidad `frontend-coverage-gate` (kind `packaging`). El stack de la app está fijado (Angular 22 + Vitest + FastAPI + Neon + Fly.io) y NO cambia por este intent. Las únicas decisiones tecnológicas nuevas son las del tooling de cobertura y su cableado.

## Decisiones

| # | Decisión | Elección | Rationale |
|---|----------|----------|-----------|
| TS1 | Proveedor de cobertura | **`@vitest/coverage-v8`** (versión exacta, casada en major con `vitest` 4.x) | OSS, coste 0 € (NFR1); mismo scope `@vitest` que el runner ya usado (`^4.0.8`), evita mismatch de major que rompe la instrumentación; alternativa `istanbul` descartada por no aportar ventaja y añadir superficie. No se usa servicio de pago (no Codecov/Coveralls): el reporte se genera y consume dentro de `ng test`. |
| TS2 | Ubicación de la config de cobertura | **Target `test` de `angular.json`** (opciones del builder `@angular/build:unit-test`) | Fuente única de umbral; el builder lee cobertura/umbrales de las `options` del target. Un `vitest.config` suelto podría quedar fuera del flujo del builder (corrección developer O1, restricción C2). |
| TS3 | Forma del umbral | **Por métrica** (`lines`, `branches`, `functions`, `statements`), trinquete solo-arriba | `branches`/`functions` detectan tests-espejo sin aserciones (significatividad FR17.1); ratcheting manual por MR (Q3=A), nunca se baja para pasar el gate (regla dura Q7-A). Valor inicial medido tras la siembra P0 y fijado por debajo de la base. |
| TS4 | Denominador de cobertura | **`coverage.all: true` + `coverage.include: src/app/**` + `coverage.exclude`** (specs, `main.ts`, `*.config.ts`, entornos, `*.d.ts`, mocks, barrels) | Universo estable desde el día 1 para que el ratchet no caiga al sembrar (Q1=A). |
| TS5 | Runner y entorno de test | **Vitest `^4.0.8` + `jsdom` `^25.0.1`** vía `@angular/build:unit-test` (sin cambios), Node `22.22.3` (`.nvmrc`) | Ya establecido; se reutiliza. Verificación en contenedor `node:22.22.3` antes de pushear (NFR5). |
| TS6 | Cableado del gate | **Corregir el comando `ng test` con cobertura en `ci.yml` (PR) y en el job `verify` de `fly-deploy.yml` (push→`main`)** | La cobertura no se hereda sola (developer O2); una única fuente de umbral en `angular.json`, ejercida en ambos caminos (FR17.1). |

## Restricciones heredadas

- Coste 0 € (NFR1): todo en tiers gratuitos, proveedor OSS.
- Sin reescrituras (NFR2): intervención aditiva sobre config/tooling/workflows.
- Stack de la app inalterado (C1): backend `pytest`+`pytest-cov` sin cambios.

## Assumptions & Open Questions

- El soporte exacto de las opciones `coverage.*` del builder `@angular/build:unit-test` de Angular 22 se valida al cablear (supuesto A2 de requisitos).
