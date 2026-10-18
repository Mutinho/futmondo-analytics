# Incident Response — Preguntas y confirmación — F1: Login nativo end-to-end

> Fase: operación (incident-response). Idioma: castellano; tokens técnicos verbatim en inglés.

## Preguntas de clarificación

- **¿Modos de fallo más probables?** Backend caído (`/health`), fallo de login (`/auth/login`),
  fallo de refresh/auto-login (`/auth/refresh`, transporte D-01), regresión por deploy, fallo de la
  app iOS (build/firma).
- **¿Rutas de escalado / on-call?** Single-maintainer: notificación de GitHub Actions al
  propietario; sin rotación on-call ni PagerDuty (NO-APLICA).
- **¿Remediación automatizada?** Gate `verify` + smoke como primera línea; rollback **manual**
  deliberado (sin auto-rollback por métrica de pago).
- **¿Comunicación en incidentes?** Registro en el PR del fix / nota de incidente; nunca
  credenciales/tokens.
- **¿RTO/RPO?** RTO minutos (rollback `flyctl` + verificación); RPO = datos en Neon (estado en
  memoria se pierde en redeploy); DR multi-región diferido/NO-APLICA.

## Consolidated Summary Confirmation

Resumen de lo producido en incident-response para F1 (single-maintainer, Fly.io + Neon, coste 0 €):

- **runbooks.md**: runbooks por modo de fallo (RB-1 backend caído, RB-2 login, RB-3 refresh/D-01,
  RB-4 rollback reutilizando `docs/ROLLBACK.md`, RB-5 app iOS), todos con comandos `flyctl`/`curl`
  gratuitos; guardarraíl de no volcar credenciales/tokens en logs ni notas.
- **incident-plan.md**: detección (smoke + pull), clasificación P1/P2/P3, ciclo de respuesta,
  RTO/RPO realistas (RTO minutos por rollback manual; RPO = Neon; estado en memoria se pierde),
  comunicación y post-incidente ligero; DR multi-región/backup gestionado diferido/NO-APLICA.
- **escalation-matrix.md**: escalado al mantenedor único vía GitHub Actions/paneles de proveedor
  (tier free); gate `verify`+smoke como primera línea; on-call/PagerDuty/AWS Incident Manager
  NO-APLICA.

Sin SSM Automation / AWS Incident Manager / AWS Backup (de pago): sustituidos por procedimientos
manuales con `flyctl`. No se inventa infraestructura: reliability/security-design e
infrastructure-specification no existen (etapas `skipped`); todo se deriva de la app desplegada,
`alarms.md`/`dashboards.md` y `docs/ROLLBACK.md`.

¿Es todo correcto?

[Answer]: Looks correct
