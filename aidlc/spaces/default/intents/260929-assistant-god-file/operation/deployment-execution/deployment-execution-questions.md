# Deployment Execution — Questions

Intent `260929-assistant-god-file`, scope `refactor` (Minimal), fase Operation. **Brownfield**,
sistema ya en producción (Fly.io + Neon, coste 0 €). Criterio de "hecho" del refactor = paridad de
comportamiento (suite verde, cobertura, superficie intacta), no un despliegue nuevo. El código
refactorizado está verificado en verde pero **aún no fusionado a `main`**; la ejecución real del
despliegue es **on-merge a `main`** a través de `.github/workflows/fly-deploy.yml`.

## Q1 — ¿Pasan todos los pre-deployment checks?

Sí (evidencia de Build and Test): suite 244 passed / 3 xfailed (preexistentes), cobertura 33.82% ≥
piso 27, `ruff check` del paquete nuevo limpio, import histórico del endpoint OK. El job `verify`
(gitleaks + pip-audit + ruff + pytest con cobertura + npm audit + ng test) los re-ejecuta on-merge;
un rojo nunca llega a producción.

- A. Sí, los checks pasan (verificado en Build and Test; el gate `verify` los replica on-merge).
- X. Other (please specify)

[Answer]: A

## Q2 — ¿Se requieren migraciones de BD y están testeadas?

No. El refactor **no toca esquema** de BD: el `CREATE TABLE IF NOT EXISTS` idempotente se preserva
en el adaptador (OOS5); no hay migración explícita que ejecutar ni probar.

- A. No se requieren migraciones (sin cambio de esquema; DDL idempotente preservado).
- X. Other (please specify)

[Answer]: A

## Q3 — ¿Están los servicios dependientes disponibles y sanos?

Sí. Neon PostgreSQL (Frankfurt, free) y las dos apps Fly.io (`futmondo-api`, `futmondo-app`) ya
están en producción. El refactor no cambia dependencias externas (Groq/Gemini vía el adaptador LLM,
comportamiento preservado).

- A. Sí, dependencias sanas y sin cambios (Neon + Fly.io en producción; sin dependencias nuevas).
- X. Other (please specify)

[Answer]: A

## Q4 — ¿Cuál es la ventana de despliegue?

Despliegue continuo on-merge a `main` (single-maintainer), sin ventana de freeze formal. La
ejecución real ocurre cuando el usuario fusiona a `main`; la verificación de release es el smoke
test `/health` post-deploy (5 reintentos, HTTP 200). Esta etapa documenta el plan y los checks; la
ejecución en producción queda **pendiente del merge** (no la ejecuta el agente).

- A. On-merge a `main`, sin ventana de freeze; ejecución real pendiente del merge del usuario.
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Resumen de los pre-deployment checks confirmados para la ejecución del despliegue del refactor:

- **Q1 Checks**: pasan (suite 244 passed/3 xfailed, cobertura 33.82% ≥ 27, ruff limpio, import
  histórico OK); el gate `verify` los replica on-merge.
- **Q2 Migraciones**: ninguna (sin cambio de esquema; DDL idempotente preservado).
- **Q3 Dependencias**: sanas y sin cambios (Neon + Fly.io en producción; sin dependencias nuevas).
- **Q4 Ventana**: on-merge a `main`, sin freeze; verificación por smoke `/health`; **la ejecución
  real en producción queda pendiente del merge del usuario** (no la ejecuta el agente).

Los artefactos (`deployment-log.md`, `smoke-test-results.md`, `health-check-report.md`) documentan
el plan de ejecución y el estado (verificado localmente; despliegue en producción pendiente del
merge), sin fabricar un despliegue que no ha ocurrido. NO-APLICA lo de pago (CloudWatch, canary
gestionado).

- Looks correct
- Request changes

[Answer]: Looks correct
