# Deployment Log — F2

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Ejecución

**NO-APLICA despliegue de servidor** (app cliente). La "ejecución" de F2 es la **instalación en dispositivo**, ya realizada varias veces durante la validación:

- `cd ios && ./scripts/install-app.sh` → build (arm64) + sign (firma gratuita) + install + launch en el iPhone 13 Pro = **OK**.
- Backend `futmondo-api`/Neon: no se despliega nada (F2 no los toca).

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/operation/deployment-pipeline/deployment-strategy.md`

## Assumptions & Open Questions

None.
