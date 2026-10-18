# Feedback Loop — F1: Login nativo end-to-end

> Fase: operación (feedback-optimization). Idioma: castellano; tokens técnicos verbatim en inglés.
> Documento de cierre que alimenta el **siguiente ciclo de ideación**: insights operativos, deuda
> registrada y fast-follows identificados durante F1. Coste 0 € salvo la excepción acotada de
> publicación nativa.

## Qué entregó F1

Login nativo end-to-end de la app iOS (Swift/SwiftUI, construida con `xtool` desde WSL) contra el
backend FastAPI, con refresh token en iOS Keychain y el ajuste aditivo del backend (D-01) para el
transporte del refresh token. Validado en el iPhone 13 Pro: login → auto-login (Keychain) →
logout. Backend desplegado en Fly.io; app instalada por firma gratuita.

## Insights operativos

- El stack Fly.io + Neon a coste 0 € soporta F1 sin cambios de topología; el SLI informal está en
  verde y D-01 no añadió latencia material.
- La observabilidad pull (`fly logs`/`fly status`/`/health`) es suficiente para un entorno
  single-maintainer; no se justifica (ni se puede pagar) observabilidad gestionada.

## Deuda registrada (candidatos a próximos intents)

| ID | Deuda | Impacto | Prioridad sugerida |
|----|-------|---------|--------------------|
| D-P1 | Arnés de test nativo iOS (XCTest) + smoke E2E de dispositivo automatizado | Hoy la validación iOS es manual | Media |
| D-CI | Job de Swift (`swift test`) en GitHub Actions | La lógica iOS no entra en el gate del repo | Media |
| D-B09 | Publicación en App Store (Apple Developer Program ~99 €/año) | Firma gratuita caduca ~7 días | Baja (decisión de producto + coste) |
| D-DOC | Cabecera stale de `backend/ruff.toml` (describe advisory) | Documentación desalineada | Baja |

## Fast-follows (funcionalidad, fuera de alcance de F1)

- **Sistema de diseño / theming nativo** (decisión del propietario, 2026-10-18): intent propio que
  produce la capa de diseño reutilizable (tokens de color claro/oscuro, tipografía con Dynamic
  Type, espaciado, componentes SwiftUI base: botones, campos, tarjetas, estados de carga/error),
  **con solo SDK de Apple** (coste 0 €, coherente con FR-8/NFR-2). **Momento óptimo: precede a F2 y
  alimenta su construcción**; de camino **reviste el login de F1** con coste marginal. Rationale:
  hacerlo con F1 sola (una pantalla) es sobredimensionado; hacerlo tras F2/F3 ya construidas obliga
  a repasar todas las pantallas (retrabajo). Se materializa cuando ya hay >1 pantalla real que
  diseñar (entrada a las pantallas de datos) pero **antes de codificarlas**.
- **Face ID / Touch ID** (B-03): biometría para desbloquear el refresh token — fast-follow natural
  del login nativo.
- **F2 / F3**: pantallas de datos y navegación/tab bar nativa (el login ya desbloquea la sesión);
  se construyen **sobre el sistema de diseño** anterior, no antes.
- Refresco de firma ~7 días: automatizar el recordatorio de reinstalación mientras B-09 siga
  diferido.

## Entradas al siguiente ciclo de ideación

1. **Arrancar el intent de sistema de diseño / theming nativo que precede a F2** (decidido como
   punto óptimo por el propietario): define tokens + componentes base y reviste el login de F1.
2. ¿Priorizar Face ID (B-03) antes o después del diseño + F2?
3. ¿Invertir en el arnés de test nativo (D-P1 + D-CI) antes de ampliar funcionalidad?
4. ¿Decidir sobre la publicación en App Store (B-09) y su coste acotado?

Ninguna de estas entradas es un compromiso; son el material para la próxima ideación si el
propietario decide seguir iterando.

## Sources

- [consumes] slo-report.md, cost-analysis.md, drift-report.md; test-results.md
  (performance-validation); incident-plan.md; deployment-log.md.
- [consumes] requirements.md "Fuera de alcance" (Face ID, F2/F3, App Store); ci-config.md (deuda CI
  de Swift); build-and-test (deuda P-1 del arnés iOS).
- [memory] project.md (coste 0 € + excepción acotada); aidlc-shared/operation-fly-stack.md.

## Assumptions & Open Questions

None.
