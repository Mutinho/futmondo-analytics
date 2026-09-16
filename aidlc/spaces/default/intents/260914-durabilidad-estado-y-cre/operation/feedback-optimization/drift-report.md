# Drift Report — Durabilidad del estado (coste 0 €)

> Etapa Feedback & Optimization (Operation). Detección de drift de configuración/infraestructura. AWS
> Config NO-APLICA (Fly.io + Neon). Sin herramienta de drift automatizada de pago; se hace una
> revisión manual de la config declarada vs la real.

## Veredicto: sin drift de infraestructura activa; una desalineación de documentación menor

## Revisión

| Elemento | Declarado | Real / fuente de verdad | Drift |
|----------|-----------|--------------------------|-------|
| Región Fly.io | `docs/DEPLOY.md` menciona `mad` (Madrid) | `backend/fly.toml` fija `primary_region = "cdg"` (París) | **Desalineación de documentación** (no drift de infra): fly.toml es la fuente de verdad; la doc quedó desactualizada. Nota menor. |
| Máquinas | `min=max=1`, `shared-cpu-1x`/256 MB (fly.toml) | Igual | Sin drift |
| Healthcheck | `/health` 30s/5s (fly.toml) | Igual | Sin drift |
| Secretos | Documentados en `docs/DEPLOY.md` (incl. `FUTMONDO_CRED_KEY` nuevo) | Fijados via `fly secrets` (acción de operador previa al deploy) | Sin drift si se fijó el secret nuevo (ver validation-report de environment-provisioning) |
| Esquema BD | `sync_session`/`sync_task` idempotentes en arranque | Creado por la app | Sin drift (no gestionado por IaC; es código de arranque) |

## Acción recomendada (coste 0 €, opcional)

- Alinear `docs/DEPLOY.md` para que la región indique `cdg` (o confirmar la región deseada y ajustar
  fly.toml si se prefiere `mad`). Es una corrección de documentación, no urgente.

## No-aplica

- AWS Config drift detection, conformance packs, remediación automatizada: **NO-APLICAN** (no es AWS).
  Fly.io no expone un servicio de drift gestionado; la config vive en `fly.toml` versionado, que es la
  defensa contra drift (cambios por consola serían la fuente de drift, evitados usando IaC/fly.toml).
