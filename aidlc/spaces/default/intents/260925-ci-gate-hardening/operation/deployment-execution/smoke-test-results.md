# Smoke Test Results — Intent 4 (gate CI/CD hardening)

> Fase Operation. Este intent **no cambia el runtime**; el smoke test es el ya
> operativo. Este documento describe el **criterio y el estado esperado** del
> smoke test tras el despliegue de los commits `chore(ci)`, no una ejecución
> fabricada (Q3=A).

## Smoke test existente (sin cambios)

- **Definición**: job `smoke-test` en `fly-deploy.yml`, `needs:
  [deploy-backend, deploy-frontend]`.
- **Prueba**: `curl` a `/health` del backend, **5 reintentos**, éxito si
  **HTTP 200** (con backoff de 10 s entre intentos).
- **URL**: `${SMOKE_HEALTH_URL:-https://futmondo-api.fly.dev/health}`.
- **Efecto**: si tras 5 intentos no hay 200 → el job falla → release marcado
  fallido → rollback (`docs/ROLLBACK.md`).

## Estado esperado por commit desplegado

Como el intent **no toca el runtime** (solo la config del gate pre-deploy y del
tooling), el resultado esperado del smoke test tras el deploy de cada commit
`chore(ci)` es **idéntico a la línea base**:

| Commit `chore(ci)` | Resultado esperado del smoke test | Motivo |
|--------------------|-----------------------------------|--------|
| 1–8 (todos) | HTTP 200 en `/health` (igual que antes del intent) | Ningún commit cambia el código de la app ni su arranque; solo config de CI/CD |

## Criterio de éxito / fallo

- **Éxito**: `/health` responde 200 dentro de los 5 reintentos → release OK.
- **Fallo**: no-200 tras 5 intentos → release fallido → rollback. Dado que el
  intent no cambia el runtime, un fallo del smoke test tras un commit `chore(ci)`
  indicaría un problema **ajeno** al cambio de config (p. ej. incidencia de
  plataforma), no una regresión introducida por el endurecimiento del gate.

## Verificación real

La ejecución real del smoke test ocurre **automáticamente** en la cadena de
deploy cada vez que un commit aterriza en `main`. Este documento fija el criterio
y la expectativa; el resultado concreto se observa en el log de GitHub Actions
del job `smoke-test` en cada push. **No se fabrica** un resultado de una
ejecución no realizada.

## Sources

- `.github/workflows/fly-deploy.yml` (job `smoke-test`).
- `./deployment-log.md`, `../deployment-pipeline/deployment-strategy.md`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`.

## Assumptions & Open Questions

- El resultado real por push se observa en el log de Actions; esta etapa documenta el criterio y el estado esperado (verde, sin cambio de runtime).
