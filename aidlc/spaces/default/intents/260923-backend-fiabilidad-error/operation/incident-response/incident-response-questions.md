# Incident Response — Preguntas · Operación (FR3.2 + FR4)

Sin preguntas abiertas. Los modos de fallo, escalado y objetivos de recuperación
ya están decididos en las etapas previas (fiabilidad + observabilidad, aprobadas)
y en el mandato coste 0 € / single-maintainer.

## Decisiones ya tomadas (no se re-preguntan)

- **Modos de fallo más probables**: baneo de Sofascore (403, fatal), timeout /
  respuesta no parseable / error de conexión de integración (recuperables),
  fallo en punto de escritura `team_prizes` (fatal, no-corrupción garantizada).
- **Escalado / on-call**: single-maintainer; señal = notificación de GitHub
  Actions (deploy/cron rojo) + inspección de `fly logs`. Sin on-call rotativo ni
  PagerDuty (coste 0 €).
- **Remediación automatizada**: degradación automática (`DEGRADED`) para lo
  recuperable; rollback manual (`docs/ROLLBACK.md`) para release fallida.
- **Comunicación**: no aplica equipo (single-maintainer); se registra el
  incidente y la causa raíz.
- **RTO/RPO**: sin objetivos numéricos formales; recuperación por re-ejecución
  del sync (idempotente-por-recomputación) y redeploy de la release previa.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
