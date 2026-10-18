# Refined Mockups — Preguntas (F1: Login nativo)

> Idioma: castellano; tokens técnicos verbatim en inglés.

## Q1 — ¿Los mockups de alta fidelidad, la interacción y el mapeo SwiftUI son correctos?

- A. **Correctos** — proceder a domain design (recomendado).
- B. Correctos con un ajuste (especifícalo).
- C. Replantear (especifícalo).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar refined-mockups, confirma:

- **Mockups**: Splash (recuperación de sesión con 5 estados) y Login (campos con autorrelleno,
  toggle de contraseña, botón con progreso, banner de error), tarjeta `.ultraThinMaterial`,
  transición de logo con `matchedGeometryEffect`.
- **Interacción**: estados idle/typing/loading/error/success; refresh ante 401 con un reintento
  sin bucle; haptics; Reduce Motion suprime animaciones/shake.
- **Mapeo SwiftUI**: cada elemento a una API del SDK de Apple (URLSession, Keychain Services,
  SecureField, matchedGeometryEffect, symbolEffect, sensoryFeedback); cero librerías de terceros.
- **Accesibilidad**: labels, foco, Dynamic Type, VoiceOver, Reduce Motion, contraste, error no
  solo por color, objetivos táctiles ≥ 44 pt.

¿Está todo correcto?

[Answer]: Looks correct
