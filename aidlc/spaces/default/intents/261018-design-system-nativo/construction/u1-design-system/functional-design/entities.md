# Entities — U1 `u1-design-system`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés. Tecnología-agnóstico (sin código).
> La librería no tiene entidades de dominio persistentes (ADR-002). Se describen los **grupos de tokens** como estructuras de configuración ligeras.

```yaml
entities:
  - name: ColorToken
    description: Token de color semántico con variante clara y oscura.
    persistent: false
    attributes:
      - { name: role, type: enum, required: true, allowed_values: [primary, onPrimary, tertiary, surface, onSurface, onSurfaceVariant, moneyPositive, moneyNegative, errorContainer] }
      - { name: lightValue, type: color-hex, required: true }
      - { name: darkValue, type: color-hex, required: true }
    constraints:
      - El par (lightValue, darkValue) debe cumplir el objetivo de contraste frente a su superficie (BR1.4).
    relationships: []
  - name: TypographyToken
    description: Estilo tipográfico de la escala con soporte Dynamic Type.
    persistent: false
    attributes:
      - { name: style, type: enum, required: true, allowed_values: [h1, h2, h3, body] }
      - { name: baseSize, type: number, required: true }     # pt en tamaño por defecto
      - { name: weight, type: enum, required: true, allowed_values: [regular, semibold, bold] }
      - { name: fontFamily, type: string, required: true, default: "Roboto (fallback: system)" }
    relationships: []
  - name: SpacingToken
    description: Paso de la escala de espaciado.
    persistent: false
    attributes:
      - { name: step, type: enum, required: true, allowed_values: [xs, sm, md, lg, xl] }
      - { name: points, type: number, required: true }       # 4/8/16/24/32
    relationships: []
  - name: SplashGradient
    description: Gradiente de fondo del splash/login (recurso de diseño).
    persistent: false
    attributes:
      - { name: stops, type: list<color-hex>, required: true, default: "[#1B5E20, #2E7D32, #43A047]" }
      - { name: angleDegrees, type: number, required: true, default: 135 }
    relationships: []
```

## Resumen

La librería define cuatro grupos de tokens de configuración (ColorToken, TypographyToken, SpacingToken, SplashGradient). Ninguno es una entidad de dominio persistente: son constantes de presentación que la app resuelve en memoria. No hay base de datos, identidad ni ciclo de vida.

## Assumptions & Open Questions

None.
