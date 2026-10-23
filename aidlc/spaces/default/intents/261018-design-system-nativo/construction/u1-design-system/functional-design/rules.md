# Business Rules — U1 `u1-design-system`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés. Lógica en lenguaje natural (sin código).

```yaml
rules:
  - id: BR1.1
    statement: Resolución de color según el modo de apariencia del sistema.
    category: calculation
    applies_to: ColorToken
    trigger: Al renderizar cualquier elemento que use un token de color.
    logic: SI el sistema está en modo oscuro ENTONCES usar darkValue; SI está en claro ENTONCES usar lightValue.
    violation_behaviour: N/A (resolución automática del asset catalog).
    source: FR1.4
  - id: BR1.2
    statement: La tipografía escala con Dynamic Type.
    category: calculation
    applies_to: TypographyToken
    trigger: Al renderizar texto con un estilo del sistema.
    logic: SI el usuario cambia el tamaño de texto del sistema ENTONCES el tamaño efectivo del estilo escala proporcionalmente respecto a baseSize.
    violation_behaviour: N/A.
    source: FR2.2
  - id: BR1.3
    statement: Fallback de fuente.
    category: policy
    applies_to: TypographyToken
    trigger: Al cargar la fuente.
    logic: SI Roboto no está empaquetada/disponible ENTONCES usar la fuente del sistema con la misma escala.
    violation_behaviour: Uso transparente del sistema; sin error.
    source: FR2.3
  - id: BR1.4
    statement: Objetivo de contraste de color.
    category: validation
    applies_to: ColorToken
    trigger: Al definir/validar un par de token sobre su superficie.
    logic: SI el ratio de contraste texto normal < 4.5:1 o (texto grande/UI) < 3:1 en claro u oscuro ENTONCES el token no cumple el objetivo y debe ajustarse.
    violation_behaviour: Se corrige el valor del token (verificable con Accessibility Inspector).
    source: NFR1
  - id: BR2.1
    statement: Estados del botón primario.
    category: constraint
    applies_to: PrimaryButton
    trigger: Al renderizar el botón.
    logic: SI isLoading ENTONCES muestra spinner y deshabilita la pulsación (precedencia sobre disabled); SI NOT isEnabled (y NOT isLoading) ENTONCES aspecto disabled y sin acción; EN OTRO CASO normal y pulsable.
    violation_behaviour: N/A (máquina de estados del componente).
    source: FR4.1
  - id: BR2.2
    statement: Estados del campo de texto.
    category: constraint
    applies_to: TextInputField
    trigger: Al renderizar/editar el campo.
    logic: SI errorMessage presente ENTONCES borde y texto de error; SI tiene foco ENTONCES borde primary; EN OTRO CASO borde neutro. SI isSecure ENTONCES ofrecer toggle de visibilidad.
    violation_behaviour: N/A.
    source: FR4.2
```

## Resumen de reglas

| ID | Regla | Categoría | Fuente |
|----|-------|-----------|--------|
| BR1.1 | Resolución color claro/oscuro | calculation | FR1.4 |
| BR1.2 | Escalado Dynamic Type | calculation | FR2.2 |
| BR1.3 | Fallback de fuente | policy | FR2.3 |
| BR1.4 | Objetivo de contraste | validation | NFR1 |
| BR2.1 | Estados del botón | constraint | FR4.1 |
| BR2.2 | Estados del campo | constraint | FR4.2 |

## Assumptions & Open Questions

None.
