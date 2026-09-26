# Health Check Report — Intent 4 (gate CI/CD hardening)

> Fase Operation. Validación de health checks tras el despliegue de la config del
> gate. El intent **no cambia el runtime**; los health checks son los ya
> operativos. Estado esperado, no ejecución fabricada (Q3=A).

## Health checks existentes (sin cambios)

| Componente | Health check | Criterio | Herramienta (gratuita) |
|------------|--------------|----------|------------------------|
| `futmondo-api` (backend) | `GET /health` | HTTP 200 + `{"status":"healthy"}` | smoke test, `fly status`, `fly logs` |
| `futmondo-app` (frontend) | `GET /` | responde (nginx sirve la SPA) | `fly status`, `fly logs` |
| Neon PostgreSQL | conexión TLS desde el backend | app arranca y sirve `/health` 200 | vía `/health` del backend |

## Pre-deployment checks documentados (Q5=A, coste 0 €)

Precondición de cada push de `chore(ci)`:

1. **Reproducir el gate en local** antes de pushear cambios de tooling/pins:
   venv efímero para `pytest` (excluyendo `libsql-experimental`, `JWT_SECRET`
   efímero); contenedor `node:22.22.3` para `ng test` **solo si** se tocara el
   frontend (no se toca en este intent).
2. **Medir el piso de cobertura** sobre la suite estabilizada ANTES de fijar
   `--cov-fail-under` (valor exacto, sin margen).
3. **Confirmar deuda saneada**: la deuda de lint/audit está saneada
   quirúrgicamente o silenciada (`per-file-ignores`/`# noqa`/allowlist) ANTES de
   promover el check a bloqueante.

## Estado esperado tras el despliegue

Como el intent no cambia el runtime, tras el deploy de cada commit `chore(ci)`
los health checks deben devolver **el mismo estado que la línea base** (backend
`/health` 200, frontend `/` OK). Cualquier desviación indicaría una causa ajena
al cambio de config.

## Métricas de salud / error (guardrail Operation)

| Componente | Métrica de salud | Métrica de error |
|------------|------------------|------------------|
| `futmondo-api` | `/health` 200 | no-200 / fallo del smoke test (`fly logs`) |
| `futmondo-app` | `/` disponible | error nginx (`fly logs`) |
| Gate de CI (componente lógico) | pass por paso con nombre (log de Actions) | tasa de rojos del job |

Sin métricas de pago (CloudWatch, SLO con burn-rate) — NO-APLICA; observables con
`fly status`/`fly logs` y el log de Actions.

## Verificación real

Los health checks se ejercitan en cada deploy (smoke test) y de forma continua
vía `fly status`/`fly logs`. Este informe fija el criterio y la expectativa; no
fabrica el resultado de una ejecución no realizada.

## Sources

- `.github/workflows/fly-deploy.yml`, `docs/ROLLBACK.md` (verificación `/health`).
- `./deployment-log.md`, `./smoke-test-results.md`.
- `../environment-provisioning/validation-report.md`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`.

## Assumptions & Open Questions

- El resultado real por push se observa en el log de Actions y en `fly logs`; esta etapa documenta el criterio y el estado esperado.
