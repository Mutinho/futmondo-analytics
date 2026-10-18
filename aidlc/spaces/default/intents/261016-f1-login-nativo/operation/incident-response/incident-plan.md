# Incident Plan — F1: Login nativo end-to-end

> Fase: operación (incident-response). Idioma: castellano; tokens técnicos verbatim en inglés. Sin
> AWS Incident Manager (de pago): plan ligero para un entorno single-maintainer en Fly.io + Neon.
> Coste 0 €.

## Detección

- **Automática**: `smoke-test` `/health` del CD en rojo → notificación de GitHub Actions; gate
  `verify` en rojo bloquea el deploy.
- **Manual/pull**: `curl /health`, `fly status`, `fly logs | grep` (ver `dashboards.md`,
  `log-queries.md`).

## Clasificación de severidad

| Severidad | Criterio (F1) | Ejemplo |
|-----------|---------------|---------|
| P1 (crítico) | Backend caído o auth inservible para todos | `/health` != 200; 5xx sistemático en `/auth/login` |
| P2 (alto) | Degradación funcional del login/refresh | auto-login (refresh) roto por regresión de D-01 |
| P3 (menor) | Fallo acotado o cosmético | fallo solo en la app iOS de un build; firma caducada |

## Respuesta (ciclo)

1. **Detectar** (ver arriba) → **confirmar** con `curl`/`fly logs`.
2. **Clasificar** (P1/P2/P3).
3. **Mitigar** con el runbook aplicable (`runbooks.md`): normalmente rollback (RB-4) para P1/P2 de
   backend; reinstalar build para P3 de iOS.
4. **Verificar** recuperación (`/health` 200 + flujo de auth).
5. **Registrar** causa raíz y fix; abrir PR con el arreglo real (gate de CI verde antes de merge).

## RTO / RPO

| Objetivo | Valor (realista para el stack) | Rationale |
|----------|-------------------------------|-----------|
| RTO (backend) | minutos — tiempo de un `fly releases rollback` + verificación `/health` | Rollback manual rápido; entorno único |
| RPO | datos persistidos en Neon; estado en memoria (`TaskManager`, syncs en curso) se **pierde** en redeploy/rollback | Limitación aceptada del entorno único (sin réplica caliente) |
| RTO (app iOS) | minutos — reinstalar build previo con `install-app.sh` | Un dispositivo; impacto contenido |

DR multi-región / backup gestionado: **diferido/NO-APLICA** (de pago). El RPO se apoya en la
durabilidad de Neon.

## Comunicación

- Single-maintainer: no hay stakeholders externos que notificar en tiempo real. El registro del
  incidente (causa raíz + fix) va en el PR del arreglo y/o en una nota de incidente.
- NUNCA incluir credenciales/tokens en la comunicación del incidente.

## Post-incidente

- Revisión ligera para P1/P2: timeline, causa raíz, prevención (coherente con el guardarraíl de la
  fase operación). Para P3, nota breve.

## Sources

- [consumes] alarms.md, dashboards.md; runbooks.md.
- [consumes] reliability-design.md, infrastructure-specification.md — NO existen (`skipped`).
- [memory] phases/operation.md (post-incident review P1/P2; runbooks con escalado);
  aidlc-shared/operation-fly-stack.md (rollback manual; RPO = Neon; DR de pago diferido); project.md
  (coste 0 €, no credenciales).

## Assumptions & Open Questions

None.
