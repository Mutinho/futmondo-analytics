# Approval & Handoff — Preguntas de aprobación

> Proyecto personal, decisor único. Las preguntas de "acuerdo entre stakeholders",
> "presupuesto" y "mobs" se simplifican a confirmación del propietario.

## QA1. ¿Confirmas el intent y el alcance tal como quedan compilados en el initiative-brief?

Intent: app iOS nativa (Swift/SwiftUI) desde el conocimiento de la app Angular, build con `xtool` en Windows/WSL, coste 0 € con firma gratuita. Alcance v1: Login + Mercado + Presupuesto (MVP), luego Favoritos + Calculadora; widgets documentados (no v1); push fuera.

- A. Sí, intent y alcance confirmados.
- B. Quiero ajustar algo (lo indico).
- X. Other (please specify)

[Answer]: A. Sí, intent y alcance confirmados.

## QA2. ¿Reconoces los riesgos clave con sus mitigaciones?

Principal: R-01 (cadena `xtool` end-to-end no validada → spike F0 como mitigación). También R-02 (fricción de refirmado ~7 días), D-01 (posible ajuste de `/auth/refresh`).

- A. Sí, riesgos reconocidos; el spike F0 es la primera acción.
- B. Quiero añadir/matizar algún riesgo.
- X. Other (please specify)

[Answer]: A. Sí, riesgos reconocidos; el spike F0 es la primera acción.

## QA3. Recomendación go/no-go: ¿procedemos?

Recomendación del estudio: **GO condicionado** al resultado del spike F0 (validar `xtool`). Como es análisis, "proceder" significa que el estudio queda aprobado y la ruta lista para abrir un intent de construcción posterior (empezando por el spike).

- A. GO — apruebo el estudio y la ruta; el siguiente paso real sería un intent de construcción que empiece por el spike F0.
- B. GO condicionado — igual que A, pero quiero dejar explícito que si el spike falla se reconsidera la ruta/coste.
- C. No-go por ahora.
- X. Other (please specify)

[Answer]: B. GO condicionado — apruebo el estudio y la ruta; si el spike F0 falla se reconsidera la ruta/coste. El siguiente paso real sería un intent de construcción que empiece por el spike.

<!-- Nota: puedes responder en modo Guía (una a una), Edición, o Chat. -->
