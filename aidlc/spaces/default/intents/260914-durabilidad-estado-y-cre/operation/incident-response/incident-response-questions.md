# Incident Response Questions — Durabilidad del estado

> Etapa Incident Response (Operation). Adaptada al stack real (Fly.io, un solo operador, coste 0 €):
> sin AWS Incident Manager, SSM Automation ni rotación on-call formal. Se generan runbooks de los
> modos de fallo nuevos de la durabilidad con las herramientas gratuitas disponibles. No se abren
> preguntas nuevas: el enfoque está decidido por el contexto ya conocido.

## Contexto resuelto (no requiere pregunta)

- **Modos de fallo nuevos (durabilidad)**: (a) secret `FUTMONDO_CRED_KEY` ausente/rotado → sesiones
  no rehidratan (401 accionable); (b) error de descifrado de handle; (c) tareas huérfanas tras
  redeploy — ya se auto-marcan `interrupted_by_restart` (FR1.5), sin intervención; (d) errores de
  persistencia contra Neon.
- **Remediación disponible (coste 0 €)**: `fly secrets set`, `fly apps restart`, `fly logs`,
  redeploy de release anterior (`docs/ROLLBACK.md`). Sin runbooks SSM ni remediación automatizada de pago.
- **Escalación**: proyecto personal de un solo operador → sin rotación on-call formal (NO-APLICA);
  severidades simplificadas.
- **RTO/RPO**: sin compromiso formal numérico; Neon (tier free) gestiona su retención; la BD es la
  autoridad del estado durable. Recuperación = redeploy (RTO ~ minutos) + BD persistente (RPO
  efectivamente 0 para el estado durable ya escrito).

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
