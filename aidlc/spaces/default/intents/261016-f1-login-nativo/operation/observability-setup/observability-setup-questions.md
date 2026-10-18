# Observability Setup — Preguntas y confirmación — F1: Login nativo end-to-end

> Fase: operación (observability-setup). Idioma: castellano; tokens técnicos verbatim en inglés.

## Preguntas de clarificación

- **¿Golden signals?** Latencia, tráfico, errores y saturación, observados en pull con
  `curl`/`fly status`/`fly logs` (sin histogramas gestionados de pago).
- **¿SLO/SLI?** SLI informal (disponibilidad `/health`, éxito de login/refresh, ausencia de picos
  de 4xx/5xx). SLO formal con error budget/burn-rate: NO-APLICA (de pago).
- **¿Layout de dashboards?** Recetas de comandos `fly`/`curl`, no dashboard gestionado.
- **¿Retención/agregación de logs?** Tier gratuito de `fly logs`; archivado gestionado NO-APLICA;
  logs estructurados sin credenciales.
- **¿Tracing distribuido?** NO-APLICA (de pago, topología plana); correlación por log.

## Consolidated Summary Confirmation

Resumen de lo producido en observability-setup para F1 (adaptado al stack Fly.io + Neon, coste 0 €):

- **dashboards.md**: "dashboard" pull con comandos `fly status`/`fly logs`/`curl` sobre la
  superficie de auth de F1; golden signals con el medio gratuito; CloudWatch gestionado NO-APLICA.
- **alarms.md**: alerting gratuito = gate `verify` bloqueante + smoke `/health` + notificación de
  GitHub Actions al mantenedor único; SNS/PagerDuty/burn-rate NO-APLICA.
- **slo-config.md**: SLI informal verificable gratis; SLO formal con error budget NO-APLICA, con
  rationale de coste 0 €.
- **log-queries.md**: recetas `fly logs`+`grep` para auth/errores; logs estructurados y NUNCA
  credenciales/tokens en logs (guardarraíl durable de D-01); archivado gestionado NO-APLICA.
- **tracing-config.md**: tracing distribuido NO-APLICA (de pago, topología plana); correlación por
  log como sustituto.
- **anomaly-config.md**: anomaly detection ML NO-APLICA; barreras deterministas (precedencia
  explícita del transporte) + estados explícitos + smoke/logs como detección práctica.

No se inventa infraestructura: nfr-design e infrastructure-design se reportaron `skipped` en los 3
bolts, así que sus artefactos no existen y la superficie observable se deriva de la app desplegada
y de deployment-execution.

¿Es todo correcto?

[Answer]: Looks correct
