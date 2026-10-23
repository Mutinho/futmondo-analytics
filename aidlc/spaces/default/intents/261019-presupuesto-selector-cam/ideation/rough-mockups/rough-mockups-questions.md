# Rough Mockups — Questions (F2)

> Fase: ideación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Rough Mockups:

- **Presupuesto**: lista/cards por equipo (saldo, rendimiento, puja máxima, premios) con tokens `money-positive`/`money-negative` (color + signo, el color no es único portador de significado); estados de carga y error con reintento.
- **Selector de campeonato**: `Menu` nativo desplegado desde el título de la navigation bar (campeonato activo marcado con ✓); al elegir, persiste en `UserDefaults` y recarga.
- **Orden**: menú con las claves de la web (saldo, rendimiento, puja máxima, valor plantilla, gastado, ingresado).
- **Navegación**: `TabView` de abajo con una sola pestaña "Presupuesto" (Liquid Glass iOS 26).
- **User-flow**: campeonato activo desde `UserDefaults` (o primero de la lista); fallback de endpoints de campeonatos como la web; flujos de error no corrompen el estado.
- **Accesibilidad**: filas como elementos VoiceOver, Dynamic Type.

¿Does this all look correct?

[Answer]: Looks correct
