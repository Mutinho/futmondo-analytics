# NFR Validation Matrix — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

| NFR | Objetivo | Método de validación | Resultado | Owning |
|-----|----------|----------------------|-----------|--------|
| NFR4.1 | Render fluido (60 fps) en el catálogo/login | Observación en dispositivo | Pendiente (manual) | iPhone 13 Pro |
| NFR4.2 | Feedback de loading <100 ms | Observación en dispositivo | Pendiente (manual) | iPhone 13 Pro |
| NFR1 (contraste) | ≥4.5:1 / ≥3:1 | `ContrastRatio` + tests | Met | build-and-test |
| NFR1 (Dynamic Type/VoiceOver) | escalado + labels | Accessibility Inspector | Pendiente (manual) | iPhone 13 Pro |
| NFR3 (fidelidad) | reproducir tema Angular | comparación visual | Pendiente (manual) | iPhone 13 Pro / catálogo |
| NFR2 (coste/seguridad) | 0 €; sin credenciales; auth de F1 intacto | inspección + suite | Met | build-and-test |

Escalabilidad: NO-APLICA (UI cliente, sin carga de servidor).

## Veredicto

Lo ejecutable está **Met**; lo de render/accesibilidad/fidelidad queda **Pendiente de validación manual** en el iPhone 13 Pro (no medible en WSL por naturaleza de la UI nativa). Ningún objetivo relajado.

## Assumptions & Open Questions

None.
