# Practices Discovery — Afirmación (F1: Login nativo end-to-end)

> Idioma: castellano; tokens técnicos verbatim en inglés. La etapa reconoció las prácticas
> durables ya afirmadas (en `team-practices.md`) y propone 4 reglas NUEVAS específicas de la
> superficie nativa iOS, todas aditivas. Tu afirmación decide cuáles se promueven y en qué layer.

## Q1 — ¿Afirmas las 4 prácticas nuevas propuestas (P-1…P-4)?

- **P-1** — Testing posture del cliente nativo Swift: verificación **manual** en el iPhone 13 Pro
  en F1; arnés XCTest como **deuda registrada**; su futuro umbral es un suelo nuevo por-runner
  que **no arrastra** el ratchet de `pytest`/`Vitest`; posture test-after con aserción de efecto
  adoptada como intención durable para el futuro código Swift. (Recomendado: `project.md`.)
- **P-2** — Ajuste de backend D-01 **estrictamente aditivo**, cubierto por `pytest` en **ambos
  canales** (cookie `HttpOnly` de la PWA + body/header nativo), sin regresión, sin cambios de
  CORS/cripto, characterization-first. (Recomendado: `team.md`.)
- **P-3** — Cliente nativo con **solo SDK de Apple** (URLSession, Keychain Services, SwiftUI,
  LocalAuthentication si se activa Face ID diferido); **cero librerías de terceros** en F1;
  especialización del coste 0 €. (Recomendado: `team.md`.)
- **P-4** — Convenciones de scope de Conventional Commits (`feat(ios-auth)`, `feat(ios-net)`) e
  idioma (código Swift en inglés, UI/commits en castellano) para la superficie nativa.
  (Recomendado: `project.md`.)

Opciones:
- A. **Afirmar las 4** con los layers recomendados (P-2, P-3 → `team.md`; P-1, P-4 → `project.md`).
- B. Afirmar las 4, pero todas en `project.md` (específicas de este proyecto).
- C. Afirmar solo algunas (especifica cuáles).
- D. No afirmar ninguna todavía (quedan como propuesta documentada, sin promover).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar practices-discovery, confirma:

- **Ya afirmado (reconocido, no re-propuesto)**: coste 0 €, gate de CI bloqueante, trunk-based +
  squash-merge + Conventional Commits, idioma inglés/castellano, seguridad de credenciales
  (refresh token en Keychain, `JWT_SECRET` no-default), testing posture test-after con ratchet,
  characterization-first, no ampliar god-files.
- **Nuevo propuesto (P-1…P-4)**: testing posture nativa (manual en F1, XCTest como deuda), ajuste
  backend D-01 aditivo cubierto por `pytest` en ambos canales, dependencias solo-SDK de Apple,
  convenciones de scope/idioma Swift.
- **Afirmación elegida**: P-2, P-3 → `team.md`; P-1, P-4 → `project.md` (opción A).

¿Está todo correcto?

[Answer]: Looks correct
