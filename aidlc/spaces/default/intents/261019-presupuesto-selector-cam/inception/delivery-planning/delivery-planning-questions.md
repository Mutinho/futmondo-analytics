# Delivery Planning — Questions (F2)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Delivery Planning (cierre de Inception):

- **2 Bolts secuenciales**: Bolt 1 `u1-budget-data` (lógica/datos, checkpoint `swift build && swift test`) → Bolt 2 `u2-budget-ui` (UI, checkpoint `swift build` + validación en iPhone 13 Pro). Orden forzado por dependencia.
- **Walking skeleton OFF** (team practice); squash-merge trunk-based; gate de CI en el PR.
- **Single-maintainer**: sin reparto entre personas; propietario decide y valida en dispositivo.
- **Riesgos** R-01 (selector), R-02 (formato dinero), R-03 (validación en dispositivo) mapeados a los Bolts.
- **Dependencias externas**: sólo SDK de Apple + cimientos de F1 + backend existente + `xtool`/iPhone; **ninguna nueva de pago/OSS**, sin bloqueos. Apple Developer Program no activado.
- **Autonomía de construcción**: propuesta autónomo hasta checkpoint de cada unidad con un "ok" por summary (a confirmar al entrar en Construcción).

¿Does this all look correct?

[Answer]: Looks correct
