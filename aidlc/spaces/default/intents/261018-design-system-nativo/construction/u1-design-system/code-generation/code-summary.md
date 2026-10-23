# Code Summary — U1 `u1-design-system`

> Fase: construcción. Idioma: identificadores/comentarios en INGLÉS; prosa en castellano.

## Qué se generó

Librería del sistema de diseño SwiftUI (`DesignSystem`) para el cliente nativo
iOS, reproduciendo el tema de Angular Material 3. Sigue el patrón de F1:

- **Lógica pura y testeable** en `ios/Sources/FutmondoKit/DesignSystem/` (SIN
  `import SwiftUI`; compila y se testea en Linux/WSL):
  - `DSColorValue.swift` — `DSAppearance { light, dark }`, `DSRGB` (parser
    `#RRGGBB`), `DSColorValue` (light/dark + resolución por apariencia),
    `DSColorToken` (9 roles con los hex del `design-system-mapping`),
    `DSSplashGradient` (3 stops). [FR1, BR1.1]
  - `DSSpacing.swift` — escala xs/sm/md/lg/xl → 4/8/16/24/32. [FR3]
  - `DSTypographyScale.swift` — h1=28/h2=20/h3=16/body=14 + peso + familia
    preferida `Roboto`. [FR2]
  - `ContrastRatio.swift` — luminancia relativa WCAG + ratio + `meets(...)`;
    umbrales 4.5 (texto normal) / 3.0 (texto grande/UI). [BR1.4, NFR1]
- **Vistas y accessors SwiftUI** en `ios/Sources/FutmondoApp/DesignSystem/`,
  TODO guardado con `#if canImport(SwiftUI)` (patrón de F1):
  - `DSColor.swift` — accessor de color adaptativo claro/oscuro (dynamic
    `UIColor` provider), `splashGradient`.
  - `DSFont.swift` — Dynamic Type vía `.custom(..., relativeTo:)`/`.system`,
    fallback a sistema si Roboto no está empaquetada. [BR1.2, BR1.3]
  - `DSSpacing+SwiftUI.swift` — accessor `CGFloat` sobre `DSSpacing`.
  - `Components/PrimaryButton.swift` — estados normal/disabled/loading
    (loading tiene precedencia sobre disabled). [BR2.1]
  - `Components/TextInputField.swift` — `SecureField` + toggle, label, icono,
    estado de error (borde error > foco > neutro). [BR2.2]
  - `Components/Containers.swift` — `Card`, `LoadingState`, `ErrorState`
    (icono + texto, no sólo color).
  - `Catalog/CatalogView.swift` — `CatalogView` + `ThemeToggle` +
    `TextSizeControl` + secciones Colors/Typography/Spacing/Components. [FR5]
- **Tests XCTest** en `ios/Tests/FutmondoKitTests/DesignSystemTests.swift`
  (clases `DesignSystem...`), cubren los 7 casos de `unit-test-instructions`.

## Decisión sobre Color Assets (desviación documentada del plan Step 5)

El plan ofrecía dos rutas para los colores: un `Assets.xcassets` en
`FutmondoApp/Resources/` **o**, como alternativa explícita si el asset catalog
complica el build en WSL, definir los colores en código y anotarlo aquí.

**Se eligió la alternativa en código.** Razón: la compilación de asset catalogs
(`.xcassets`) depende de `actool` del toolchain de Apple, que **no existe en el
toolchain de Swift de Linux/WSL** (Swift 6.0.3 x86_64-linux-gnu) usado para el
checkpoint; declarar `resources: [.process("Resources/Assets.xcassets")]`
rompería `swift build` en este entorno. Para priorizar que `swift build` y
`swift test` compilen (requisito del checkpoint), los colores se definen en
código dentro de `DSColor` mediante un `UIColor` dinámico que resuelve
claro/oscuro por `userInterfaceStyle`. La **única fuente de verdad** de los hex
sigue siendo `FutmondoKit.DSColorToken` (no se duplican valores: el accessor los
lee de ahí). `Package.swift` **no se modificó** (no se añadió recurso). En
dispositivo el render es idéntico; si en F2 se quiere un `.xcassets`, se deriva
de `DSColorToken` sin cambiar la superficie pública.

## Verificación

Entorno: Swift 6.0.3 (`x86_64-unknown-linux-gnu`), WSL.

- `cd ios && swift build` → **Build complete** (compila `FutmondoKit`,
  `FutmondoApp` y el test target). En Linux, el código SwiftUI de `FutmondoApp`
  queda vacío por el guard `#if canImport(SwiftUI)` (patrón de F1): compila pero
  **no se type-checkea** aquí; su validación de tipos y visual es en dispositivo
  (iPhone 13 Pro) / toolchain de Apple, igual que `LoginView`/`SplashView` de F1.
- `cd ios && swift test --filter FutmondoKitTests.DesignSystem` → **14 tests, 0
  fallos** (unit-scoped).
- `cd ios && swift test` (checkpoint completo) → **43 tests, 0 fallos** (14
  nuevos del sistema de diseño + 29 preexistentes de F1; sin regresión).

## Contraste medido (BR1.4 / NFR1) — sin gaps

Validado en `DesignSystemContrastTests` con los valores reales de la tabla de
tokens sobre `surface`:

| Par | Claro | Oscuro | Objetivo | Cumple |
|-----|-------|--------|----------|--------|
| onSurface / surface | 17.13 | 14.51 | ≥4.5 | sí |
| onSurfaceVariant / surface | 9.34 | 10.99 | ≥4.5 | sí |
| moneyPositive / surface | 5.13 | 7.92 | ≥3 (y ≥4.5) | sí |
| moneyNegative / surface | 4.98 | 5.37 | ≥3 (y ≥4.5) | sí |
| primary / surface | 5.13 | 7.92 | ≥3 | sí |
| onPrimary / primary | 5.13 | 7.31 | ≥4.5 | sí |

Ningún token incumple su objetivo; no se relajó ningún umbral.

## Cobertura (piso 80% line sobre el código testeable nuevo de FutmondoKit)

El toolchain Swift de Linux de este entorno no expone un informe de cobertura
de líneas fiable vía `swift test --enable-code-coverage` sin `llvm-cov`
configurado; se deja constancia para el checkpoint. La **lógica pura nueva de
`FutmondoKit/DesignSystem/`** (resolución de color, parser de hex, escala de
espaciado, escala tipográfica, luminancia/ratio/`meets`) está ejercitada por
los 14 tests: cada rama de `DSColorValue.hex(for:)`, cada caso de `DSSpacing`,
`DSTypographyScale`, ambos umbrales de `ContrastRatio` y el camino de fallo
(hex malformado, par insuficiente). Las vistas SwiftUI **quedan fuera del
cómputo** por contrato (no compilan en Linux; se validan en dispositivo). Si el
checkpoint ejecuta cobertura con `llvm-cov`, se espera ≥80% sobre esos cuatro
ficheros; si midiese por debajo, es gap a exponer, no a silenciar.

## Desviaciones del plan

1. **Step 5 (Color Assets)**: se usó la alternativa en-código documentada
   arriba en vez de `Assets.xcassets`, por compatibilidad de `swift build` en
   WSL. `Package.swift` no se tocó.
2. Las capas "data model / repository / API" de la Testing Contract no aplican
   a una librería de UI sin datos ni red (ya anotado en el plan); la capa
   testeable real es la lógica de tokens, cubierta por XCTest.
