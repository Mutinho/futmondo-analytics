# Feasibility & Constraints — Questions (F2)

> Fase: ideación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Feasibility & Constraints:

- **Veredicto: viable, sin bloqueantes.** Los cimientos de F1 (red/auth en `FutmondoKit`, tokens de diseño) + los endpoints existentes sin cambios de backend cubren casi todo; el único diseño genuinamente nuevo es el patrón del selector.
- **Riesgo dominante (R-01)**: patrón del selector sin sidebar (decidido Q1-A, menú en navigation bar); validable en dispositivo, revisable si incomoda.
- **Riesgo secundario (R-02)**: formateo de dinero M/K con signo; lógica pura testeable en `FutmondoKit`.
- **Restricciones duras (C-01..C-08)**: coste 0 €, sin cambios de backend, tema Angular como fuente de verdad, sesión F1 intacta, verificación `swift test` + dispositivo, idioma, gate de CI, Color Sets en código (WSL).
- **Coste 0 €**; Apple Developer Program no se activa en este intent.

¿Does this all look correct?

[Answer]: Looks correct
