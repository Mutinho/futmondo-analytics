# Feedback Loop — Sistema de diseño nativo iOS

> Fase: operación (cierre). Idioma: castellano; tokens técnicos verbatim en inglés.

## Fuente de feedback

Single-maintainer (propietario). El feedback llega por uso propio de la app en el iPhone 13 Pro y por la comparación visual catálogo ↔ tema Angular, no por telemetría de usuarios ni encuestas.

## Ciclo

1. Instalar la build nativa con `xtool` en el iPhone 13 Pro.
2. Recorrer el catálogo (`CatalogView`) y el login revestido; comprobar render (60 fps), modo claro/oscuro, Dynamic Type, VoiceOver y fidelidad con el tema Angular.
3. Anotar desajustes como follow-up para un intent futuro (p. ej. migración a Color Sets, nuevos componentes para F2).
4. Re-sincronizar tokens Swift si el tema Angular cambia (ver drift-report).

## Entradas a intents futuros

- F2 (siguientes pantallas nativas) consumirá esta librería de diseño como base.
- Validación en dispositivo pendiente (render/accesibilidad/fidelidad) como primer checklist de F2.

## Assumptions & Open Questions

None.
