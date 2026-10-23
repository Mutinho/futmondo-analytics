# Deployment Strategy — F2

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Estrategia

**NO-APLICA despliegue de servidor.** La app nativa iOS de F2 se distribuye por **instalación en dispositivo** (`xtool dev run`), no por blue/green ni canary. No hay traffic-shifting ni entorno de producción nuevo: el backend que consume ya está en producción y no cambia.

- **"Release" de desarrollo**: `cd ios && ./scripts/install-app.sh` (build → sign → install → launch) en el iPhone 13 Pro. Firma gratuita ~7 días → reinstalar para refrescar.
- **Publicación App Store**: fuera de alcance de F2 (requeriría Apple Developer Program, excepción acotada no activada).

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/operation/deployment-pipeline/cd-config.md`
- `ios/scripts/install-app.sh`, `ios/xtool.yml`

## Assumptions & Open Questions

None.
