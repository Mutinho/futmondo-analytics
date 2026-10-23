# Infrastructure Design — CI/CD (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Aplicabilidad

**NO-APLICA infraestructura/CI-CD nuevo.** U2 es código SwiftUI de la app cliente (`FutmondoApp/Budget/`): no despliega, no toca Fly.io/Neon ni los workflows (`ci.yml`/`fly-deploy.yml`). El gate de CI bloqueante existente aplica al PR tal cual; un cambio de código SwiftUI no dispara pisos backend/frontend ni requiere pasos nuevos.

## Verificación

`cd ios && swift build` (compila, guardado por `#if canImport(SwiftUI)`) + validación de UI en iPhone 13 Pro con `xtool`. No hay runner Swift en el CI actual y no se añade (coste 0 €, fuera de alcance).

## Riesgo/deuda aceptada

La verificación de U2 (build + dispositivo) es **manual** (sin control automatizado en el PR para el paquete iOS), igual que U1. Deuda/riesgo aceptado ya registrado; runner Swift en CI como follow-up.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/infrastructure-design/cicd-pipeline.md`
- `aidlc/spaces/default/memory/team.md`

## Assumptions & Open Questions

None.
