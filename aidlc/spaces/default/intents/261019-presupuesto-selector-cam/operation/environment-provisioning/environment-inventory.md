# Environment Inventory — F2

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Aplicabilidad

**NO-APLICA provisión de infraestructura.** F2 es app nativa cliente; no crea ni modifica entornos cloud. El "entorno" relevante es:

| Entorno | Estado | Notas |
|---------|--------|-------|
| Dispositivo (iPhone 13 Pro) | Existente (del propietario) | Target de ejecución/validación; `xtool` + firma gratuita. |
| Backend `futmondo-api` (Fly.io `cdg`) | Existente, sin cambios | F2 lo consume tal cual; no se provisiona nada. |
| Neon PostgreSQL (Frankfurt) | Existente, sin cambios | No tocado por F2. |

Sin recursos nuevos, sin IaC, coste 0 €.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/infrastructure-design/infrastructure-specification.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/operation/deployment-pipeline/cd-config.md`

## Assumptions & Open Questions

None.
