# Cost Analysis — Sistema de diseño nativo iOS

> Fase: operación (cierre). Idioma: castellano; tokens técnicos verbatim en inglés.

## Coste recurrente de este intent

**0 €.** El sistema de diseño nativo se sostiene exclusivamente con el **SDK de Apple** (SwiftUI, XCTest), sin tooling de diseño de pago, sin dependencias OSS nuevas (stdlib/SDK suficiente), sin servicios en la nube añadidos. No toca la infraestructura Fly.io/Neon/GitHub Actions (todas en tier free), que sigue a coste 0 €.

## Excepción conocida y acotada (NO activada en este intent)

- **Apple Developer Program (~99 €/año)**: coste de publicación de distribución nativa. Es la única excepción bounded al mandato de coste 0 €, y **no se activa en este intent** (sólo librería de diseño + login revestido, sin publicación en App Store).

## Oportunidades de optimización

Ninguna con coste. La migración a Color Sets en `Assets.xcassets` (diferida por falta de `actool` en WSL) es coste 0 € y se hará al construir en dispositivo con `xtool`.

## Assumptions & Open Questions

None.
