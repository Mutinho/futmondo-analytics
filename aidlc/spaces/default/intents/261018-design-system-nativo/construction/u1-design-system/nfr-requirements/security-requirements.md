# Security Requirements — U1 `u1-design-system`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.
> U1 es una librería de presentación (kind `library`): no maneja datos, red, credenciales ni autenticación.

## Modelo de amenazas (resumen)

La librería no procesa entradas de usuario sensibles, no persiste datos, no hace llamadas de red ni gestiona credenciales. Su superficie de ataque es prácticamente nula: expone tipos y vistas SwiftUI consumidos in-process.

## Requisitos

| ID | Requisito | Fuente |
|----|-----------|--------|
| NFR2.1 | La librería NO introduce dependencias de pago ni de terceros: sólo SDK de Apple (coste 0 €). | NFR2 |
| NFR2.2 | La librería NO almacena ni maneja credenciales, tokens ni datos personales; no tiene estado persistente. (Preserva la regla durable de no credenciales en claro — no la toca.) | memory:project.md |
| NFR2.3 | El `TextInputField` en modo secure no registra ni expone el texto introducido fuera de su `Binding`; el toggle de visibilidad es local a la vista. | FR4.2 |

## Autenticación / Autorización

No aplica: la librería no tiene lógica de auth. El login (U2) reutiliza la auth de F1 sin cambios.

## Compliance

No aplica (sin datos personales ni regulados).

## Assumptions & Open Questions

None.
