# Cost Analysis — F2 (Feedback & Optimization)

> Fase: operación (cierre). Idioma: castellano; tokens técnicos verbatim en inglés.

## Coste recurrente de F2

**0 €.** F2 se construye con el SDK de Apple (SwiftUI/XCTest) + xtool; `Package.swift` mantiene `dependencies: []` (sólo se añadió el deployment target iOS 26 y el recurso `background.jpg`, ambos coste 0 €). No añade infraestructura, servicios cloud ni dependencias de pago. Backend Fly.io/Neon/GitHub Actions siguen en tier free.

## Excepción conocida (NO activada)

Apple Developer Program (~99 €/año) — única excepción bounded, para publicación en App Store; **no activada** en F2 (distribución por instalación en dispositivo de desarrollo).

## Oportunidades de optimización

- Añadir un runner Swift al CI (deuda aceptada) para cerrar el hueco de verificación arm64 sólo-dispositivo; requeriría runner macOS (coste) → se mantiene local por ahora.

## Assumptions & Open Questions

None.
