# NFR Validation Matrix — F2

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

| NFR | Objetivo | Método | Resultado |
|-----|----------|--------|-----------|
| NFR1.1 | Cero dependencias nuevas | inspección `Package.swift` (`dependencies: []`) | Met |
| NFR2.1 | Sin credenciales en la UI/errores; HTTPS; `UserDefaults` sólo id | tests U1 no-fuga + diseño U2 | Met (`swift test`) |
| NFR3.1 | Fidelidad al tema (oscuro neón) | validación visual en iPhone 13 Pro | Met (dispositivo) |
| NFR4.1 | 60 fps scroll / <100 ms loading | observación en iPhone 13 Pro | Met (dispositivo) |
| NFR5.1 | VoiceOver, Dynamic Type, contraste ≥4.5:1 | `ContrastRatio` test + observación | Met (contraste medido ≥4.5:1; resto dispositivo) |
| NFR6.1 | Verificación lógica en `FutmondoKit` | `swift build && swift test` 105/0 | Met |

Escalabilidad: NO-APLICA (UI cliente, sin carga de servidor).

## Veredicto

Todos los NFR **Met**; lo de render/accesibilidad validado en dispositivo (no numérico en WSL, regla durable). Ningún objetivo relajado.

## Assumptions & Open Questions

None.
