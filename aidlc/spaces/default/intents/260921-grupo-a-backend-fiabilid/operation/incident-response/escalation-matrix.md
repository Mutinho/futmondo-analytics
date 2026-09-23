# Matriz de escalado — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: proyecto
> single-maintainer, Fly.io + Neon, coste 0 €. Sin PagerDuty ni rotación on-call
> gestionada. El escalado es a un único punto de responsabilidad.

## Punto de contacto (único)

| Rol | Contacto | Canal |
|---|---|---|
| Maintainer / on-call (único) | Responsable del repositorio (owner de GitHub del proyecto) | Notificaciones de GitHub Actions (workflow en rojo) + revisión manual |

> Nota: al ser single-maintainer no hay rotación ni segundo nivel humano. El
> "contacto" operativo es el propietario del repo, notificado por los correos/
> alertas de GitHub Actions cuando un workflow falla. Sustituir por el
> identificador real del maintainer si se externaliza el proyecto.

## Rutas de escalado por severidad

| Sev | Disparador automático | A quién / qué | Acción inmediata |
|---|---|---|---|
| P1 | `smoke-test`/`verify` en rojo, o `/health` en rojo | Maintainer (email de GitHub Actions) | RB-1 / RB-4 → rollback (`rollback-runbook.md`) |
| P2 | Recurrencia de `sync step degraded` en `fly logs` | Maintainer (revisión manual) | RB-2 → diagnóstico + PR de fix |
| P3 | `degraded` puntual / 422 esperado | Maintainer (bajo demanda) | RB-2 / RB-3 → relanzar sync o verificar techo |

## Proveedores externos (para escalado de infraestructura)

| Servicio | Uso | Escalado |
|---|---|---|
| Fly.io | hosting backend/frontend | estado de plataforma Fly.io; tier free |
| Neon | BD PostgreSQL | panel/estado de Neon; tier free |
| GitHub Actions | CI/CD | estado de GitHub; tier free |

- No hay contrato de soporte de pago con estos proveedores (tiers gratuitos); el
  escalado a ellos se limita a consultar su página de estado.

## NO-APLICA / diferido

- On-call rotation gestionada, PagerDuty/Opsgenie, SNS routing, escalado
  automático multi-nivel: servicios de pago; diferidos. La matriz de un solo
  punto de arriba es la real para un proyecto single-maintainer a coste 0 €.

## Sources

- `runbooks.md`, `incident-plan.md`, `README.md` (topología y proveedores),
  `phases/operation.md` (runbooks con rutas de escalado y contacto).

## Assumptions & Open Questions

None.
