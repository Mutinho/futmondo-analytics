# Contract Design — Preguntas de clarificación

> Fase: inception. Idioma: castellano; tokens técnicos (SwiftUI, SwiftPM, API pública Swift, SemVer) verbatim en inglés.
> Único boundary: U2 `u2-login-theming` consume la API pública de la librería U1 `u1-design-system`. No hay API externa ni REST/eventos. Rellena cada `[Answer]:`.

## Q1. Naturaleza del contrato U1→U2

- A. API pública de una librería Swift (SwiftPM): tipos y vistas públicas que U1 expone (Color Assets accesibles vía tokens, `DesignTokens` de tipografía/espaciado, y los componentes `PrimaryButton`, `TextInputField`, `Card`, `LoadingState`, `ErrorState`). El contrato es la superficie pública Swift, no un API de red.
- B. Not applicable (tratar U1 y U2 como un todo sin contrato formal).
- X. Other (please specify)

[Answer]: A. API pública de una librería Swift (SwiftPM): tokens y componentes que U1 expone; el contrato es la superficie pública Swift, no un API de red.

## Q2. Versionado y cambios rompientes del contrato interno

- A. Al ser mismo repo y único mantenedor, sin versionado formal: los cambios rompientes en la API pública de U1 se corrigen en U2 en el mismo cambio (compilador obliga). Cambios aditivos (nuevos tokens/componentes) no rompen a los consumidores.
- B. Versionado SemVer formal de la librería.
- X. Other (please specify)

[Answer]: A. Sin versionado formal (mismo repo, único mantenedor); los cambios rompientes en U1 se corrigen en U2 en el mismo cambio; los aditivos no rompen.

## Consolidated Summary Confirmation

Resumen de Contract Design:

- **Un único contrato**: U2 `u2-login-theming` consume la **API pública de la librería Swift** de U1 `u1-design-system` (in-process, SwiftPM). No hay API de red ni externa.
- **Contrato (Q1=A)**: superficie pública = tokens (colors/typography/spacing) + componentes (PrimaryButton, TextInputField, Card, LoadingState, ErrorState) con garantía de accesibilidad.
- **Versionado (Q2=A)**: sin SemVer formal; rompientes se corrigen en el mismo cambio (compilador), aditivos no rompen. Owner: U1.

¿Does this all look correct?

[Answer]: Looks correct
