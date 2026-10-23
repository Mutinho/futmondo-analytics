# CI Pipeline — Questions (F2)

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de CI Pipeline (re-confirmado tras el re-trabajo de U2):

- **NO-APLICA cambios de CI**: el gate bloqueante existente (gitleaks + `ruff check` + `pytest` + `pip-audit` + `ng test` + `npm audit`) aplica al PR de F2 (ahora con FR6 detalle incluido) tal cual y queda en verde (F2 no toca backend ni frontend Angular); gitleaks escanea también el Swift nuevo.
- **Verificación del código iOS** (`swift build && swift test` = 105 verde + validación en dispositivo) es **local/manual**; no se añade runner Swift al CI (coste 0 €, deuda aceptada, follow-up).
- **Ningún umbral modificado** (invariante del trinquete: sólo sube).

¿Does this all look correct?

[Answer]: Looks correct
