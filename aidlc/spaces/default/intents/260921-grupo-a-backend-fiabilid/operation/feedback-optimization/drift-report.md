# Informe de drift — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: Fly.io + Neon, coste
> 0 €. AWS Config drift detection NO-APLICA.

## Veredicto: sin drift introducido por el intent

El intent no modifica infraestructura ni configuración de despliegue; no hay
divergencia entre lo diseñado/documentado y lo real atribuible a este trabajo.

## Comprobaciones

| Área | Estado | Nota |
|---|---|---|
| Config de Fly.io (`fly.toml`) | Sin cambios | el intent no toca sizing, puertos ni checks |
| Topología (apps, región, BD) | Sin cambios | `futmondo-api`/`futmondo-app` en `cdg`; Neon Frankfurt |
| CI/CD (`ci.yml`, `fly-deploy.yml`) | Sin cambios | los tests nuevos ya corren bajo `pytest tests` |
| Esquema de BD | Sin cambios | estado `degraded` en `progress` (JSON libre); sin migración |
| Secretos | Sin cambios | no se añaden ni rotan secretos |

## Fuente de verdad de la configuración

- La configuración vive en ficheros versionados (`fly.toml`, workflows YAML) y
  en los secrets de Fly/GitHub. El drift se detectaría por diff de git sobre
  esos ficheros — ninguno cambia por este intent salvo el código de aplicación
  y los tests.

## NO-APLICA / diferido

- AWS Config drift detection y reglas de conformidad gestionadas: servicios AWS
  de pago, inexistentes. El control de versiones de `fly.toml`/workflows cumple
  la función de "estado deseado vs real" a coste 0 €.

## Sources

- `operation/deployment-pipeline/cd-config.md`,
  `operation/environment-provisioning/environment-inventory.md`,
  `construction/sync-reliability/functional-design/entities.md` (sin cambio de esquema).

## Assumptions & Open Questions

None.
