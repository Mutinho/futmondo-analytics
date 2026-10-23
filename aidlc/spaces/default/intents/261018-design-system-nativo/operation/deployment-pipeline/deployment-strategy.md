# Deployment Strategy — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés. Adaptado al stack real (no AWS).

## Alcance de despliegue de este intent

Este intent entrega una **capa de diseño** (librería `DesignSystem` de U1 + login revestido de U2) **embebida en la app iOS**; no es un servicio desplegable ni toca la topología de producción. No se despliega a Fly.io.

- El **backend** (`futmondo-api`) y el **frontend Angular** (`futmondo-app`) en Fly.io (región `cdg`) NO cambian por este intent.
- La app iOS se **distribuye** instalándola en el iPhone 13 Pro con **`xtool`** (firma gratuita, coste 0 €), como en F1. No hay pipeline de despliegue a App Store en este intent (Apple Developer Program es la excepción acotada, no activada aquí).

## Estrategia

- **On-merge a `main`**: el PR de este intent (código iOS + artefactos de diseño) pasa el gate de CI del repo (que no cambia) y aterriza por squash-merge, igual que cualquier otro cambio.
- **Entrega a dispositivo**: `cd ios && xtool dev build` (manual, local), tras `swift build && swift test` verde. Caducidad de firma ~7 días (deuda B-09 conocida).

## NO-APLICA

| Estándar (AWS/servicio) | Estado |
|-------------------------|--------|
| Pipeline CD a cloud | NO-APLICA; app cliente iOS, sin despliegue de servidor |
| Blue/green / canary | NO-APLICA; distribución a un único dispositivo personal |
| Traffic shifting | NO-APLICA |

## Assumptions & Open Questions

None.
