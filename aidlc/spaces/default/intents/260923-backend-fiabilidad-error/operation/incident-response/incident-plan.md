# Incident Plan — Operación (FR3.2 + FR4)

Plan de respuesta a incidentes single-maintainer, a coste 0 €. Se apoya en el
logging estructurado (`fly logs`), la taxonomía recuperable/fatal y el runbook de
rollback de este intent.

## Ciclo de vida del incidente

1. **Detectar**: notificación de GitHub Actions (deploy/cron rojo) o smoke test
   `/health` fallido; o `level=ERROR failure_mode=` en `fly logs`.
2. **Diagnosticar**: `fly logs --app futmondo-api | grep task_id=<ID>` para
   reconstruir el sync; `fly status`; `curl /health`. Clasificar por modo de
   fallo (ver `runbooks.md`).
3. **Mitigar**: aplicar el runbook correspondiente (RB-1..RB-5). Release rota →
   rollback inmediato (`rollback-runbook.md`).
4. **Recuperar**: re-lanzar el sync (idempotente por recomputación) o esperar la
   siguiente ventana de cron; verificar salud (`/health` 200, sin `DEGRADED`
   inesperado).
5. **Post-mortem** (obligatorio P1/P2, ver guardarraíl de fase): registrar
   cronología, causa raíz y prevención. Sin herramienta de pago; nota en el repo
   / issue de GitHub.

## RTO / RPO

- **Sin objetivos numéricos formales** (proyecto personal, coste 0 €, proceso
  batch). Recuperación por **re-ejecución** del sync y **redeploy** de la release
  previa. El diseño garantiza que un fallo no deja datos corruptos (reemplazo
  atómico de `team_prizes`), por lo que la "pérdida de datos" (RPO) se limita a
  los datos de la ventana de sync no completada, que se recomputan.

## Remediación automatizada (a coste 0 €)

- **Recuperable** → degradación automática (`DEGRADED`) sin intervención; el sync
  continúa.
- **Fatal** → aborto limpio automático (sin datos a medias); intervención manual
  para diagnóstico/rollback.
- Sin auto-remediación gestionada de pago (Lambda/EventBridge) → NO-APLICA.

## Comunicación

- Single-maintainer: no hay canal de equipo. Se documenta el incidente (issue /
  nota) para trazabilidad y prevención.

## Assumptions & Open Questions

None.
