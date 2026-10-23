# Performance Requirements — U2 `u2-login-theming`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.
> U2 es revestimiento visual del login; no cambia la lógica ni las llamadas de red.

| ID | Requisito | Fuente |
|----|-----------|--------|
| NFR4.1 | El revestimiento no degrada la percepción de rendimiento del login: render fluido (sin jank perceptible, objetivo 60 fps) en el iPhone 13 Pro; no introduce trabajo en el hilo principal más allá del render de SwiftUI. Verificación: observación manual en dispositivo (iPhone 13 Pro). | NFR4 |
| NFR4.2 | El estado `loading` del `PrimaryButton` refleja de inmediato la pulsación (feedback < 100 ms), igual que en F1. | FR6.2 |

No hay objetivos de throughput/latencia de red (U2 no hace red; reutiliza `AuthService` de F1).

## Assumptions & Open Questions

None.
