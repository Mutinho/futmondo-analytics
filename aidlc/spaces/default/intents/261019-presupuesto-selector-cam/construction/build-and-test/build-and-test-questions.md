# Build and Test — Questions (F2)

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Build and Test (estado final, tras el re-trabajo de U2):

- **Build + suite ejecutable verde**: `cd ios && swift build && swift test` → Build complete + **105 tests, 0 fallos** (F1 + U1 + U2, incluye FR6 detalle de equipo), sin regresión; compila para arm64 en dispositivo.
- **Validado en dispositivo** (iPhone 13 Pro) por el propietario: Presupuesto con cards neón-glass oscuras, tema oscuro global, fondo deportivo, tab bar flotante Liquid Glass, botones de toolbar blancos; detalle de equipo con zoom transition, summary animado, menú Compras/Ventas en toolbar y entrada escalonada.
- **Seguridad** (no-fuga de credenciales, HTTPS, `UserDefaults` sólo id) preservada; sin dependencias nuevas; sesión F1 intacta.
- **Accesibilidad/contraste** validados (≥4.5:1, VoiceOver, Dynamic Type, Reduce Motion).
- **Deuda registrada** (fuera de alcance): el "saldo" difiere entre lista y detalle por inconsistencia del backend (lista suma premios, detalle no) → intent de backend aparte.
- Cross-unit traceability cubre FR1–FR6 Must.

¿Does this all look correct?

[Answer]: Looks correct
