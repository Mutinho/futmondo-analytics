# Test Results — frontend-coverage-gate

Ejecución de Build and Test en contenedor `node:22.22.3` (coste 0 €), `2026-09-19`.

## Build status

- Comando: `npm ci && npx ng test --watch=false` (desde `angular-app/`).
- `npm ci`: OK (instala desde lock, incl. `@vitest/coverage-v8@4.1.11`).
- Build del bundle: **success** — "Application bundle generation complete. [1.388 seconds]".

## Test results (frontend, unit + integración simulada)

- **Ficheros de test**: 14 passed (14).
- **Tests**: **62 passed (62)**, 0 failed, 0 skipped.
- Duración: ~1.94 s.
- Ficheros: `idle-preloading-strategy.spec.ts` (5), `sync` (5), `championship` (3), `evolution` (2), `analytics` (5), `budget` (4), `favorites` (2), `stats` (3), `roster` (4), `auth.guard` (5), `auth.service` (6), `assistant` (5), `auth.interceptor` (6), `bid-dialog.component` (7).

## Coverage report (V8, sobre `src/app/**/*.ts`)

| Métrica | Cobertura | Cubierto/Total | Umbral | Verdicto |
|---|---|---|---|---|
| Statements | 19.2% | 395/2057 | 15 | Met |
| Branches | 19.53% | 176/901 | 15 | Met |
| Functions | 17.26% | 67/388 | 13 | Met |
| Lines | 18.05% | 320/1772 | 14 | Met |

`NG_TEST_EXIT=0` — el builder no falla porque toda métrica supera su umbral. Enforcement dentro de `ng test` (sin paso externo, sin `continue-on-error`). Fail-closed demostrado en Code Generation (forzar umbral 95% → exit 1).

## Failure details

Ninguno. Sin fallos de build ni de test.

## Backend (fuera de alcance de este intent)

Este intent es frontend-only; no toca `backend/`. La suite `pytest` del backend permanece como gate independiente en `ci.yml` (con `--cov=app`) y en `verify`, inalterada. No se re-ejecuta aquí (el Python del sistema es 3.14; CI usa 3.12 con `libsql-experimental`); ningún cambio de este intent puede afectarla. NFR3 (frontend) verificado directamente arriba (62/62 verde, incluidos los 2 specs preexistentes).

## Target Verification Matrix (final)

Ver `build-and-test-summary.md` → todas las filas aplicables con verdicto **Met**; no queda ningún `Pending`, `Not Met` ni `Unverified`.

## Verdicto de Build and Test

**Éxito.** Todos los comandos ejecutados pasaron y todos los objetivos aplicables están `Met`.
