# Mapa Unidad ↔ Requisitos — Frontend Coverage Gate

No se produjeron user stories (User Stories se saltó: intent de developer-tooling/infrastructure-only). Por tanto el mapa relaciona los **requisitos funcionales** (`requirements.md`) con la unidad que los implementa.

## Mapa de requisitos por unidad

| Requisito | Descripción | Unit ID | Directory |
|-----------|-------------|---------|-----------|
| FR10.1 | Retirar `skipTests` de schematics de lógica; el código nuevo nace con spec | U1 | `u1-frontend-coverage-gate` |
| FR10.2 | Infraestructura de cobertura (`@vitest/coverage-v8`, `coverage.all`/`include`/`exclude`, umbrales por métrica) en `angular.json` | U1 | `u1-frontend-coverage-gate` |
| FR10.2.1 | Denominador estable (`coverage.all: true` + `include: src/app/**` + excludes) | U1 | `u1-frontend-coverage-gate` |
| FR10.2.2 | Umbral por métrica en `angular.json` | U1 | `u1-frontend-coverage-gate` |
| FR10.2.3 | Ratcheting manual por MR (solo sube; valor medido tras siembra) | U1 | `u1-frontend-coverage-gate` |
| FR10.3 | Siembra de specs de la capa crítica (P0 duro + P1/P2 guía) | U1 | `u1-frontend-coverage-gate` |
| FR10.3.1 | Mínimo duro P0: `auth.guard.ts` + `auth.service.ts` con aserciones reales | U1 | `u1-frontend-coverage-gate` |
| FR10.3.2 | Guía P1/P2: resto de `core/services/*`, `auth.interceptor`, bid-dialog | U1 | `u1-frontend-coverage-gate` |
| FR17.1 | Umbral de cobertura bloquea en `ci.yml` y en `verify` | U1 | `u1-frontend-coverage-gate` |
| FR17.1.1 | Significatividad: cobertura por métrica (branches/functions) + revisión humana en MR | U1 | `u1-frontend-coverage-gate` |
| FR17.1.2 | Sin `continue-on-error` que sustituya el enforcement dentro de `ng test` | U1 | `u1-frontend-coverage-gate` |

## Requisitos transversales (cross-cutting)

Los NFR aplican a la única unidad U1 en su conjunto: NFR1 (coste 0 €), NFR2 (sin reescrituras / cambio acotado), NFR3 (estabilidad del gate), NFR4 (determinismo de tests), NFR5 (reproducibilidad de tooling en `node:22.22.3`).

## Orden de implementación dentro de la unidad

Orden obligado (secuencia interna, no dependencia entre unidades): **FR10.1 → FR10.2 (denominador + provider) → FR10.3 (siembra P0) → activar umbral por métrica → FR17.1 (cablear el gate en `ci.yml` y `verify`)**. La suite existente permanece en verde en cada paso.

## Verificación de cobertura

- Todos los requisitos funcionales (FR10.1, FR10.2.*, FR10.3.*, FR17.1.*) están asignados a U1.
- La unidad U1 tiene requisitos asignados (no hay unidad huérfana).

## Assumptions & Open Questions

- None.
