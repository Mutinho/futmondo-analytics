# Functional Design — U2 `u2-login-theming` — Preguntas

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés. Unit UI-only, sin decisiones nuevas.

## Consolidated Summary Confirmation

Resumen de Functional Design — U2 (revestir login):

- **Alcance**: sustituir la capa visual de `LoginView` (F1) por componentes/tokens de U1 (TextInputField, PrimaryButton, ErrorState, Card, DSColor.splashGradient), preservando `AuthViewModel` y todos los flujos.
- **functional-spec**: workflow W1 del login revestido + tabla de equivalencia antes→después; máquina de estados heredada de AuthViewModel sin cambios.
- **frontend-components**: jerarquía del LoginView revestido con los componentes de U1; misma API pública; sin estado nuevo de lógica.
- **Sin entities/rules propias** (UI-only); ACs de US4.1 N/A (lógica de F1, verificación en W1 + dispositivo).

¿Does this all look correct?

[Answer]: Looks correct
