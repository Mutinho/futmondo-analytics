# Preguntas — Deployment Execution (Fiabilidad de la sync)

> Conversation language: Spanish. Fase Operation. **Encuadre**: el despliegue de
> este proyecto es **on-merge a `main`** (automático vía `fly-deploy.yml`), no un
> `flyctl deploy` manual. Este intent es trabajo en curso **aún no fusionado**;
> esta etapa documenta el PLAN de ejecución del despliegue y las verificaciones
> smoke/health que la CD ejecutará al fusionar — no se dispara un deploy a
> producción por iniciativa. Respuestas determinadas por la CD real (Operation:
> preguntas excepcionales). Coste 0 €.

## Q1 — ¿Pasan todos los pre-deployment checks?

A. Sí — gate `verify` (gitleaks + pytest + ng test) verde; suite 166 tests en verde
B. No / pendientes
X. Other (please specify)

[Answer]: A. Sí. El gate previo (`verify`) es bloqueante y la suite completa está en verde (166 tests; `test-results.md`). Al abrir el MR / fusionar, `verify` se re-ejecuta y debe pasar antes de que corran los deploys.

## Q2 — ¿Se requieren migraciones de BD y están testeadas?

A. NO se requieren — cambio aditivo sin migración de BD
B. Sí (especificar)
X. Other (please specify)

[Answer]: A. NO se requieren. El estado `degraded` vive en `progress` (JSON libre); no se añadieron tablas ni columnas. `entities.md` confirma cambio aditivo sin migración. No hay paso de migración que ejecutar ni delegar.

## Q3 — ¿Servicios dependientes disponibles y sanos?

A. Sí — Neon PostgreSQL (BD) y API Futmondo (integración) operativos; healthcheck `/health` verde en producción
B. No / degradados
X. Other (please specify)

[Answer]: A. Sí. Neon operativo (conexión TLS) y `/health` responde 200 en `futmondo-api`. La integración con Futmondo/Sofascore no cambia por este intent.

## Q4 — ¿Ventana de despliegue?

A. On-merge a `main` (sin ventana especial; deploy continuo gobernado por el gate `verify`)
B. Ventana programada
X. Other (please specify)

[Answer]: A. On-merge a `main`. El deploy lo dispara la fusión del MR (branch protection + `verify` verde). No hay ventana especial ni aprobación manual extra; el smoke test `/health` verifica el release. El deploy real ocurrirá cuando este intent se fusione; NO se dispara manualmente desde esta etapa.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
