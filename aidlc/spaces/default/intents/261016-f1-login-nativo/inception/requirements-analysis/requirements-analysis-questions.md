# Requirements Analysis — Preguntas (F1: Login nativo end-to-end)

> Idioma: castellano; tokens técnicos verbatim en inglés.

## Q1 — ¿Los requisitos (FR-1…FR-9, NFR-1…NFR-4) son correctos y completos para F1?

- A. **Correctos y completos** — proceder a user stories (recomendado).
- B. Correctos con un ajuste (especifícalo: añadir/quitar/precisar algún requisito).
- C. Replantear requisitos (especifícalo).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar requirements-analysis, confirma los requisitos de F1:

- **FR**: login nativo (FR-1), access en memoria (FR-2), refresh token en Keychain (FR-3),
  transporte aditivo del refresh token (FR-4), refresh automático con un reintento (FR-5), logout
  (FR-6), cliente de red con Bearer + humo a `/api/v1/user/me` (FR-7), polish nativo SwiftUI
  (FR-8), sin regresión de la PWA (FR-9).
- **NFR**: seguridad de credenciales (NFR-1), coste 0 € / solo SDK de Apple (NFR-2), verificación
  `pytest` + manual en iPhone con arnés nativo como deuda (NFR-3), idioma inglés/castellano
  (NFR-4).
- Todos trazables a intent-statement, scope, codekb y prácticas afirmadas.

¿Está todo correcto?

[Answer]: Looks correct
