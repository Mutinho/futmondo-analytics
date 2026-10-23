# Drift Report — Sistema de diseño nativo iOS

> Fase: operación (cierre). Idioma: castellano; tokens técnicos verbatim en inglés.

## Deriva de diseño (fuente de verdad: tema Angular)

El riesgo de deriva es que `angular-app/src/styles.scss` (Material 3 verde/violeta, Roboto, claro/oscuro, `money-positive`/`money-negative`, escala `h1`/`h2`/`h3`, gradiente de splash) evolucione y los tokens SwiftUI (`DSColor`, `DSFont`, `DSSpacing`) queden desalineados.

| Punto de deriva | Detección | Mitigación |
|-----------------|-----------|------------|
| Cambio de paleta/tipografía en Angular | revisión al tocar `styles.scss` | re-sincronizar tokens Swift (fuente única en código) |
| Material 3 sin equivalente 1:1 | ya cubierto con Apple HIG | documentado en los artefactos de diseño |
| Color Sets diferidos a `Assets.xcassets` | pendiente de build en dispositivo | migración coste 0 € con `xtool` |

## Deriva de infraestructura

NO-APLICA: este intent no provisiona ni modifica infraestructura; no hay IaC que derive.

## Assumptions & Open Questions

None.
