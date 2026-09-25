# Runbooks — Incident Response (FR3.2 + FR4)

Procedimientos operativos por modo de fallo, a coste 0 € (Fly.io + `fly logs`).
Cada runbook incluye ruta de escalado y contacto (ver `escalation-matrix.md`).
Aprovecha el logging estructurado y la taxonomía recuperable/fatal de este intent.

## RB-1 — Baneo de Sofascore (403, FATAL)

- **Síntoma**: `fly logs --app futmondo-api | grep 'failure_mode=ban'` (level=ERROR).
- **Efecto esperado (por diseño)**: el paso `sofascore` aborta limpio (sin datos a
  medias); el resto del sync continúa; los pasos dependientes degradan.
- **Acción**: no reintentar inmediatamente (evitar reforzar el baneo). Esperar a
  la siguiente ventana de cron; el throttle preventivo (~750 ms) reduce recurrencia.
  Si persiste varios días, revisar el rate-limiting del cliente.
- **Escalado**: P2 (degradación parcial, no caída). Single-maintainer.

## RB-2 — Timeout / respuesta no parseable / error de conexión (RECUPERABLE)

- **Síntoma**: `fly logs | grep -E 'failure_mode=(timeout|unparseable|request_exception)'` (level=WARNING).
- **Efecto esperado**: el paso se marca `DEGRADED` (`sync_step_status.py`) y el
  sync NO falla.
- **Acción**: normalmente ninguna (transitorio). Si es **inesperado o repetido**
  en el mismo paso, revisar el proveedor externo y el `endpoint` del log.
- **Escalado**: P3 (informativo) salvo repetición → P2.

## RB-3 — Fallo en punto de escritura `team_prizes` (FATAL, no-corrupción)

- **Síntoma**: error fatal durante el reemplazo de premios; `fly logs | grep failure_mode=`.
- **Efecto esperado**: la transacción atómica hace `rollback` completo — el
  conjunto previo de `team_prizes` queda íntegro (todo-o-nada). NO hay estado mixto.
- **Acción**: re-lanzar el sync en la siguiente ventana (idempotente por
  recomputación); verificar en `fly logs` que no hubo escritura parcial.
- **Escalado**: P2.

## RB-4 — Release fallida (smoke test /health ≠ 200)

- **Síntoma**: job `smoke-test` de `fly-deploy.yml` en rojo (notificación GitHub).
- **Acción**: ejecutar el **rollback** (`docs/ROLLBACK.md` / `rollback-runbook.md`):
  `fly releases rollback <vN> --app futmondo-api`; verificar `curl /health` = 200.
  Abrir PR con el fix real (gate CI antes de merge; nunca push directo a `main`).
- **Escalado**: P1 (release rota en producción).

## RB-5 — Cron fallido (`daily-sync` / `sofascore-sync`)

- **Síntoma**: job de GitHub Actions del cron en rojo.
- **Acción**: revisar `fly logs` del intervalo del cron; si fue transitorio, la
  siguiente ejecución programada lo reintenta. Si es sistémico, diagnosticar y PR.
- **Escalado**: P2/P3 según impacto.

## Herramientas comunes

```bash
fly status --app futmondo-api
fly logs --app futmondo-api | grep task_id=<ID>   # reconstruir un sync
curl -sS https://futmondo-api.fly.dev/health
```

## Assumptions & Open Questions

None.
