# Constraint Register — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (feasibility). Idioma: castellano; tokens técnicos verbatim en inglés.

| ID | Restricción | Origen | Tipo |
|----|-------------|--------|------|
| C-01 | **Coste 0 €**: sólo SDK de Apple; sin dependencias de pago ni tooling de pago. | `project.md`/`team.md` (durable) | Dura |
| C-02 | **Sin cambios de backend/datos**: se consumen `/api/v1/analytics/balances` y `/api/v1/user/championships` tal cual. | intent-statement | Dura |
| C-03 | **Tema Angular como fuente de verdad** del diseño; Apple HIG donde no haya equivalente 1:1. | `project.md` (durable) | Dura |
| C-04 | **Sesión de F1 intacta**: refresh token en Keychain, access token en memoria; no se toca el modelo de auth. | `project.md` (durable, seguridad) | Dura |
| C-05 | **Verificación**: lógica pura en `FutmondoKit` con `swift test`; vistas SwiftUI validadas en iPhone 13 Pro (cobertura no numérica en WSL). | `project.md` (learned F1) | Dura |
| C-06 | **Idioma**: identificadores/comentarios en inglés; UI/commits en castellano; prosa de artefactos en castellano con tokens verbatim. | `project.md`/`team.md` (durable) | Dura |
| C-07 | **Gate de CI bloqueante** aplica igual al PR (gitleaks + `ruff check` + `pytest` + `pip-audit` + `ng test` + `npm audit`), aunque el cambio sea de app nativa. | `team.md` (durable) | Dura |
| C-08 | **`actool` no disponible en WSL**: Color Sets en código, no en `Assets.xcassets`; migración diferida a build en dispositivo. | `project.md` (learned F1) | Blanda (arrastrada) |

## Sources

- [memory:M1] `project.md`/`team.md`: reglas durables de coste, diseño, seguridad, idioma, CI y verificación.
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/intent-capture/intent-statement.md`.

## Assumptions & Open Questions

None.
