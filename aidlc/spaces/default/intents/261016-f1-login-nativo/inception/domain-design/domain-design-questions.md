# Domain Design — Preguntas (F1: Login nativo end-to-end)

> Idioma: castellano; tokens técnicos verbatim en inglés.

## Q1 — ¿El diseño de componentes y los ADRs son correctos?

- A. **Correctos** — proceder a units generation (recomendado).
- B. Correctos con un ajuste (especifícalo).
- C. Replantear (especifícalo).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar domain-design, confirma:

- **Componentes iOS**: C1 `NetworkClient` (HTTP + Bearer + errores tipados), C2 `KeychainStore`
  (refresh token), C3 `AuthService` (login/refresh/bootstrap/logout, access en memoria), C4
  `AuthViewModel` (estado + reintento único), C5 `LoginView`/`SplashView` (UX nativa).
- **Backend**: C6 ajuste aditivo del transporte del refresh token (cookie O body/header), con
  tests `pytest` de ambos canales, sin ampliar god-files.
- **ADRs**: ADR-1 transporte aditivo; ADR-2 Keychain + access en memoria; ADR-3 separación por
  capas testables; ADR-4 reintento único sin bucle. Cada uno con alternativas rechazadas.
- **Trazabilidad**: FR/NFR → componentes sin orphans (`traceability.json`).

¿Está todo correcto?

[Answer]: Looks correct
