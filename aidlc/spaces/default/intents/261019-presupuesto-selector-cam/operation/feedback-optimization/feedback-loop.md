# Feedback Loop — F2 (Feedback & Optimization)

> Fase: operación (cierre). Idioma: castellano; tokens técnicos verbatim en inglés.

## Fuente de feedback

Single-maintainer (propietario). El feedback llegó **en vivo durante la construcción** por uso en el iPhone 13 Pro: varias iteraciones de pulido visual (cards neón, tab bar flotante, botones blancos, fondo deportivo, título Apple Music) y dos mejoras de interacción del detalle (menú Compras/Ventas en toolbar, entrada escalonada). El feedback loop ya operó y refinó F2 hasta "perfecto" según el propietario.

## Entradas a intents futuros

- **Deuda backend**: arreglar la inconsistencia del "saldo" (lista con premios vs detalle sin premios) — intent de backend.
- **Runner Swift en CI**: cerrar el hueco de verificación arm64-only (requiere macOS) — follow-up.
- **F3+**: nuevas secciones consumirán el `TabView` (hoy 1 pestaña) y el DesignSystem oscuro/neón ya establecido; añadir pestañas sin re-estructurar la raíz.
- Posible migración de Color Sets a `Assets.xcassets` cuando se construya habitualmente en dispositivo.

## Ciclo

Instalar con `xtool` → usar en dispositivo → anotar mejoras → iterar. Validación de accesibilidad/render siempre en dispositivo (no numérica en WSL).

## Assumptions & Open Questions

None.
