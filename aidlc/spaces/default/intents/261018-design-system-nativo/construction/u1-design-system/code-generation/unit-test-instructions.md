# Unit Test Instructions — U1 `u1-design-system`

> Fase: construcción. Idioma: identificadores/comentarios en INGLÉS; prosa en castellano.

## Framework y configuración

- XCTest (incluido en el toolchain de Swift; sin dependencias externas).
- Target de test: `FutmondoKitTests` (ya existe en `ios/Package.swift`), que depende sólo de `FutmondoKit`.
- Los tests cubren la **lógica pura de tokens** de `FutmondoKit/DesignSystem/` (compila en Linux/WSL). Las vistas SwiftUI de `FutmondoApp` NO se testean aquí (se validan en dispositivo).

## Comando (scoped a esta Unit)

```
cd ios && swift test --filter FutmondoKitTests.DesignSystem
```

Este comando corre sólo los tests del sistema de diseño (clases de test con prefijo `DesignSystem`), no toda la suite. El comando de checkpoint del intent (`cd ios && swift build && swift test`) corre el conjunto completo de `FutmondoKit`.

## Cobertura esperada

- Piso 80% line sobre el código testeable NUEVO de `FutmondoKit/DesignSystem/` (lógica de tokens). Las vistas SwiftUI quedan fuera del cómputo (no compilan en Linux; se validan en dispositivo).

## Mocking / stubbing

- No se necesita: la lógica de tokens es determinista y sin dependencias externas (sin red, sin disco, sin Keychain).

## Datos de test

- Valores de token esperados (hex claro/oscuro por rol) como constantes en el test; pares de contraste conocidos para validar el helper WCAG.

## Casos a cubrir (test-after, ≥5–8)

1. `DSColorValue` resuelve el valor claro en `.light` y el oscuro en `.dark` (BR1.1).
2. Cada rol de color tiene variante clara y oscura definida (FR1).
3. `DSSpacing` devuelve 4/8/16/24/32 para xs/sm/md/lg/xl (FR3).
4. `DSTypographyScale` devuelve los tamaños base h1=28/h2=20/h3=16/body=14 (FR2).
5. `ContrastRatio` ≥ 4.5:1 para texto normal sobre surface en claro y oscuro (BR1.4/NFR1).
6. `ContrastRatio` ≥ 3:1 para moneyPositive/moneyNegative sobre surface (BR1.4).
7. (edge) un par de contraste insuficiente se detecta como fallo de validación (BR1.4).
