# Escalation Matrix — Durabilidad del estado (coste 0 €)

> Etapa Incident Response (Operation). Matriz de escalación adaptada a un proyecto personal de **un
> solo operador**. La escalación multi-nivel con rotación on-call de AWS Incident Manager NO-APLICA;
> se documenta la ruta real disponible.

## Ruta de escalación (operador único)

| Nivel | Responsable | Contacto | Cuándo |
|-------|-------------|----------|--------|
| Primario | El operador/dueño del proyecto | (propio) | Todos los incidentes |
| Proveedor — Fly.io | Soporte / status de Fly.io | https://status.flyio.net , comunidad Fly.io | Fallo de plataforma (máquinas no arrancan, red) |
| Proveedor — Neon | Status / soporte de Neon | https://neonstatus.com | Fallo de base de datos (conexión, disponibilidad) |

## Cuándo escalar a proveedor

- **Fly.io**: el `fly logs`/`fly status` indican que la máquina no arranca por causa de plataforma (no
  por config de la app), o la región `cdg` tiene incidencia. Revisar el status page antes de invertir
  tiempo en diagnóstico propio.
- **Neon**: errores de conexión persistentes a `DATABASE_URL` no atribuibles a la app; revisar el
  status de Neon y los límites del tier free.

## Contactos y automatismos

- **Notificación automática**: ninguna de pago (no hay PagerDuty/SNS). El healthcheck de Fly.io
  reinicia la máquina automáticamente; el operador revisa manualmente ante reportes o tras redeploy.
- **Documentación de referencia**: `runbooks.md` (esta etapa), `docs/ROLLBACK.md`, `docs/DEPLOY.md`.

## No-aplica (documentado)

- Rotación on-call semanal, secundario de guardia, Incident Commander, tiempos de respuesta
  contractuales (SLA): **NO-APLICA** a un proyecto personal de un operador y coste 0 €. La "escalación"
  real es al status/soporte del proveedor cuando la causa es de plataforma.
