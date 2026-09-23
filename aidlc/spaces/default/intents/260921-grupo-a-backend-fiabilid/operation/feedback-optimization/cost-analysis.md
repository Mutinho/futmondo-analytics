# Análisis de coste — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: Fly.io + Neon +
> GitHub Actions, todos en tier gratuito. Mandato: **coste 0 €**. AWS Cost
> Explorer / Trusted Advisor NO-APLICA.

## Coste del intent: 0 €

| Componente | Coste | Nota |
|---|---|---|
| Backend `futmondo-api` (Fly.io) | 0 € | free allowance; el intent no cambia el sizing |
| Frontend `futmondo-app` (Fly.io) | 0 € | sin cambios por este intent (backend-only) |
| BD Neon | 0 € | tier free Frankfurt; sin tablas/columnas nuevas |
| CI/CD (GitHub Actions) | 0 € | free tier; los 4 tests nuevos son segundos extra despreciables |
| Herramientas de test | 0 € | `pytest` ya presente; sin dependencias de pago |

- El intent es **aditivo** y no introduce recursos, dependencias ni servicios
  con gasto recurrente. Se respeta el mandato de coste 0 €.

## Oportunidades de optimización

- **Ninguna acción de coste necesaria**: el proyecto ya opera en el mínimo
  (tiers gratuitos). No hay recursos infrautilizados de pago que recortar.

## NO-APLICA / diferido

- AWS Cost Explorer, Trusted Advisor, análisis de rightsizing gestionado:
  servicios AWS de pago, inexistentes en este stack. La "gestión de coste" es el
  propio mandato de mantenerse en tiers gratuitos, verificado por diseño.

## Sources

- `project.md` (ALWAYS coste 0 €), `operation/environment-provisioning/environment-inventory.md`,
  `construction/sync-reliability/code-generation/code-summary.md` (cambio aditivo).

## Assumptions & Open Questions

None.
