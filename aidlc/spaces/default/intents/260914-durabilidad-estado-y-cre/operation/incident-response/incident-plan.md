# Incident Plan — Durabilidad del estado (coste 0 €)

> Etapa Incident Response (Operation). Plan de respuesta adaptado a un proyecto personal de un solo
> operador sobre Fly.io + Neon (tier gratuito). Sin AWS Incident Manager, sin rotación on-call formal,
> sin comunicación externa a clientes (uso personal). Severidades simplificadas.

## Severidades (simplificadas)

| Nivel | Criterio | Respuesta |
|-------|----------|-----------|
| Alta | Backend caído / `/health` en rojo persistente; login imposible para todos | Atender en cuanto se detecte; RB-4/RB-5 |
| Media | Degradación de durabilidad: sesiones no rehidratan, tareas no consultables tras reinicio | Atender pronto; RB-1/RB-2/RB-3 |
| Baja | Ruido en logs, 401 esperados tras rotación de clave | Revisar cuando convenga; sin acción urgente |

## Detección (coste 0 €)

- **Automática**: healthcheck `/health` de Fly.io (auto-restart), smoke test del pipeline (bloquea deploy en rojo).
- **Manual**: revisión de `fly logs` ante un reporte de uso o tras un redeploy (ver `log-queries.md`).

## Flujo de respuesta (operador único)

1. **Detectar**: healthcheck/smoke test en rojo, o reporte de uso.
2. **Diagnosticar**: `fly logs --app futmondo-api`; identificar el modo de fallo (RB-1..RB-6).
3. **Mitigar**: aplicar el runbook correspondiente (re-fijar secret, restart, rollback).
4. **Verificar**: `/health` = 200, `fly status`, cese de errores en logs.
5. **Registrar**: anotar causa y acción (post-incidente ligero, abajo).

## Post-incidente (ligero)

Para un incidente de impacto real, anotar (en un issue o nota del repo):
- Qué pasó y cuándo, impacto, causa raíz, acción de mitigación, y prevención (¿falta un check, un
  secret documentado, un test?). Blameless: foco en el sistema, no en la persona.

## RTO / RPO (sin compromiso formal)

- **RTO**: recuperación por redeploy de release ~ minutos (Fly.io). Sin SLA formal.
- **RPO**: el estado durable ya escrito vive en Neon (persistente); RPO efectivamente 0 para lo ya
  confirmado. Neon (tier free) gestiona su propia retención/backup.

## No-aplica

- Rotación on-call, Incident Commander, comunicación externa a clientes, status page: **NO-APLICA** a
  un proyecto personal de un operador. Se documenta el flujo de operador único en su lugar.
