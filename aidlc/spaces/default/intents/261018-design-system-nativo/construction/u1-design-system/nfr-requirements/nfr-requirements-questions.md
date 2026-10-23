# NFR Requirements — U1 `u1-design-system` — Preguntas

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.
> U1 kind `library`: sin NFR de performance/scalability/reliability/observability (son de service/ui). Sin decisiones nuevas; tech stack ya decidido. No hubo preguntas abiertas.

## Consolidated Summary Confirmation

Resumen de NFR Requirements — U1:

- **Seguridad**: superficie nula; sin datos/red/credenciales. NFR2.1 (coste 0 €, sólo SDK de Apple), NFR2.2 (sin credenciales ni estado persistente), NFR2.3 (secure field no filtra el texto).
- **Tech stack**: Swift + SwiftUI, SwiftPM dentro de `ios/`, Color Assets (Any/Dark), Dynamic Type con Roboto + fallback a sistema; verificación `cd ios && swift build && swift test`.
- **No aplican** (kind library): performance, scalability, reliability, observability.
- **Trazabilidad**: NFR1 (accesibilidad, vía BR1.4 + checklist), NFR2 (OK → NFR2.1–2.3), NFR3 (OK → tech-stack), NFR4 (N/A, se trata en NFR Design/UI).

¿Does this all look correct?

[Answer]: Looks correct
