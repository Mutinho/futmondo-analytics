# Constraint Register — F1: Login nativo end-to-end

> Fase: ideación (feasibility). Idioma: castellano; tokens técnicos verbatim en inglés.

| ID | Restricción | Tipo | Origen | Impacto en F1 |
|----|-------------|------|--------|----------------|
| C-01 | Coste 0 € recurrente; dependencias OSS a versión exacta; firma gratuita de Apple ID. | Económica (durable) | [memory:M1] / team.md | El cliente usa SDK (URLSession, Keychain); sin librerías de pago. |
| C-02 | El refresh token nunca en claro; va a **iOS Keychain**. El access token sólo en memoria. | Seguridad (durable) | [memory:M2] | Define el almacenamiento de credenciales del cliente nativo (Q3=A). |
| C-03 | El ajuste de backend debe ser **aditivo**: no romper el canal cookie `HttpOnly` de la PWA. | Compatibilidad | intent-statement Q1=A | La PWA sigue en producción sin regresión. |
| C-04 | Identificadores/código/docstrings en **inglés**; texto de usuario y commits (Conventional Commits con scope) en **castellano**. | Estilo (durable) | team.md Code Style | Aplica al cliente Swift y al ajuste de backend. |
| C-05 | Cualquier cambio de backend pasa el **gate de CI bloqueante** (gitleaks + `ruff check` + `pytest` + `pip-audit` + `ng test` + `npm audit`) antes de `main`. | Proceso (durable) | team.md / org.md | El ajuste de backend trae tests `pytest` y pasa el gate. |
| C-06 | `JWT_SECRET` no-default en arranque; secretos vía `secrets` de GitHub Actions/Fly.io; en CI `JWT_SECRET` efímero. | Seguridad (durable) | project.md | El ajuste no introduce secretos; reutiliza la emisión existente. |
| C-07 | Entorno de build nativo: WSL + Swift 6.4 + usbmuxd + `xtool` (validado en el spike F0). | Entorno | 261016-xtool-spike | El cliente Swift se construye/instala con la cadena ya probada. |
| C-08 | Firma gratuita caduca ~7 días (reinstalación/refirmado). | Operativa | feasibility viabilidad | No bloquea F1; el flujo de refirmado es B-09 (fuera de F1). |

## Sources

- [consumes] intent-statement de F1.
- [memory:M1] [memory:M2] reglas durables.
- team.md / org.md / project.md (gate de CI, estilo, secretos).
- [spike] `261016-xtool-spike` (cadena de build nativa validada).

## Assumptions & Open Questions

None.
