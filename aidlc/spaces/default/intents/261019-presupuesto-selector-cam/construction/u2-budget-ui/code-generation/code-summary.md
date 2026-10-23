# Code Summary — U2 `u2-budget-ui`

> Fase: construcción. Unidad: `u2-budget-ui` (app `FutmondoApp`, SwiftUI).
> Idioma: identificadores/comentarios en inglés; prosa en castellano. Todo bajo
> `#if canImport(SwiftUI)` (y `&& canImport(Observation)` donde se usa `@Observable`).

## Qué se construyó

La capa de presentación nativa iOS del presupuesto por equipo + selector de
campeonato, consumiendo la lógica pura ya testeada de U1 (`FutmondoKit/Budget`)
y los tokens/componentes de F1 (`DesignSystem`), e integrada en el seam
autenticado de F1 (`SplashView.case .resumed`) sin tocar la lógica de sesión.

## Ficheros creados

| Fichero | Rol |
|---------|-----|
| `ios/Sources/FutmondoApp/Budget/BudgetViewModel.swift` | `@MainActor @Observable`; máquina de estados `BudgetState { loading, loaded, emptyTeams, noChampionships, error }`; `load()` / `selectChampionship(_:)` / `setSort(_:)`. Inyecta `BudgetService`/`ChampionshipService`/`ActiveChampionshipStore`; usa `ActiveChampionshipResolver` + `TeamBudgetSort` (U1). |
| `ios/Sources/FutmondoApp/Budget/RootTabView.swift` | `TabView` con una pestaña "Presupuesto" → `NavigationStack(BudgetView)`; recibe el VM y un closure de logout; expone "Cerrar sesión" como toolbar item. |
| `ios/Sources/FutmondoApp/Budget/BudgetView.swift` | Pantalla dentro del `NavigationStack`; `.toolbar` con `ChampionshipMenu` (posición `.principal`) y `SortMenu` (`.primaryAction`); cuerpo por `BudgetState` (LoadingState / List de BudgetRow / mensajes vacío / ErrorState + Reintentar con foco VoiceOver). |
| `ios/Sources/FutmondoApp/Budget/BudgetRow.swift` | Fila: `team_name` (DSFont h3), `balance`/`performance` con `MoneyFormatter` (performance `signed: true`) y `DSColor.moneyPositive/Negative`, `max_bid`/`prizes` secundarios (`prizes` → `-` cuando 0). Label VoiceOver compuesto; el signo acompaña siempre al color (A7). |
| `ios/Sources/FutmondoApp/Budget/ChampionshipMenu.swift` | `Menu` en el título (activo con ✓; deshabilitado si la lista está vacía); llama a `viewModel.selectChampionship`. |
| `ios/Sources/FutmondoApp/Budget/SortMenu.swift` | `Menu` con las 6 claves `SortKey` (activa con ✓); llama a `viewModel.setSort`. Etiquetas castellanas definidas en la capa app. |
| `ios/Sources/FutmondoKit/Budget/ActiveChampionshipPersistence.swift` | **Lógica pura extraída** del VM: `shouldPersist(resolvedId:storedId:)` (FR3.3). Vive en `FutmondoKit` para ser testeable con XCTest en WSL. |
| `ios/Tests/FutmondoKitTests/ActiveChampionshipPersistenceTests.swift` | 5 XCTest (happy-path + bordes: nil resuelto, nil almacenado, iguales, ambos nil) del helper anterior. |

## Ficheros editados

| Fichero | Cambio |
|---------|--------|
| `ios/Sources/FutmondoApp/SplashView.swift` | **Seam edit**: (1) `init` ahora recibe `networkClient: NetworkClient` y compone el `BudgetViewModel` sobre el MISMO cliente HTTPS (`HTTPBudgetService`/`HTTPChampionshipService` + `UserDefaultsActiveChampionshipStore`); (2) el cuerpo de `case .resumed` presenta `RootTabView` con un closure de logout que ejecuta el mismo seam F1 (`await viewModel.logout(); phase = .noSession`); (3) se eliminó el `authenticatedPlaceholder` que sustituye. `runBootstrap`, `.onChange(of: viewModel.state)` y los casos `.checking/.offline/.expired/.noSession` quedan **intactos**. |
| `ios/Sources/FutmondoApp/FutmondoApp.swift` | Se guarda el `NetworkClient` HTTPS ya construido y se pasa a `SplashView(authService:networkClient:)`, para que los servicios de presupuesto reutilicen el único transporte https (AR8 / SEC-N1). No se crea un segundo cliente ni se debilita la regla https-only. |

## Decisiones

- **Reutilización del transporte HTTPS**: el `NetworkClient` se construye una
  sola vez en `FutmondoApp` y se inyecta tanto a `AuthService` como, vía
  `SplashView`, a los servicios de U1. No hay segundo cliente inseguro (SEC-N1).
- **Error verbatim sin interpolación**: `BudgetState.error(String)` recibe
  `error.localizedDescription` del error tipado de U1 (`NetworkError`), sin
  interpolar `championship_id` ni tokens (SR1). `NetworkError` sólo lleva
  `Int`/`String` no sensibles, así que no puede filtrar credenciales.
- **No corromper el activo persistido ante fallo**: si `fetchChampionships()`
  lanza, se va a `.error` **sin** tocar `activeStore` (FR4.2). La persistencia
  del id resuelto sólo ocurre cuando cambia, vía el helper puro
  `ActiveChampionshipPersistence.shouldPersist` (FR3.3).
- **`loading` síncrono**: `state = .loading` se fija antes de cada `await`
  (`load`, `selectChampionship`) para que el indicador aparezca <100 ms (NFR4).
- **`setSort` sin recarga**: reordena in-place sólo cuando `.loaded`; en otro
  caso sólo guarda la clave (se aplica en el siguiente `.loaded`).
- **Lógica pura extraída mínima**: sólo `shouldPersist` era limpiamente
  extraíble y no trivial; el resto del VM es orquestación `async` de llamadas de
  U1 (ya cubierta por los 39 tests de U1) y vistas SwiftUI → validación en
  dispositivo, sin tests artificiales (test-after, regla durable iOS/WSL).
- **Accesibilidad**: filas como único elemento VoiceOver con label compuesto;
  foco movido a "Reintentar" en error (`@AccessibilityFocusState`); color nunca
  portador único (signo presente); todos los textos vía `DSFont` (Dynamic Type).

## Resultado de `swift build && swift test`

- `cd ios && swift build` → **Build complete** (sin errores ni warnings en los
  ficheros nuevos). En este entorno `canImport(SwiftUI)` resolvió verdadero, así
  que los cuerpos SwiftUI de `FutmondoApp` **sí** se type-checkearon (no sólo la
  librería `FutmondoKit`).
- `cd ios && swift test` → **87 tests, 0 failures** (82 de F1/U1 preexistentes +
  5 nuevos de `ActiveChampionshipPersistenceTests`). **Sin regresión.**

## Validación en dispositivo (pendiente, iPhone 13 Pro)

Las vistas SwiftUI y el `BudgetViewModel` ligado a `@Observable` se validan en
dispositivo (cobertura de UI no fiable en WSL, regla durable): flujo
login → presupuesto del activo → cambio de campeonato (persiste) → ordenar →
estados vacío/error → logout re-alojado; VoiceOver (filas/selector/Reintentar),
Dynamic Type, fidelidad de tokens de dinero y verde Material 3, claro/oscuro,
Liquid Glass de la tab bar.

## Desviaciones

- Ninguna respecto al plan. El único matiz es que el entorno sí compiló la capa
  SwiftUI (mejor que el mínimo esperado de "sólo `FutmondoKit`"), lo que da una
  verificación de compilación más fuerte del código nuevo de U2.

## Ámbito tocado

Sólo ficheros bajo `ios/` (nuevos en `FutmondoApp/Budget/`, un helper+test en
`FutmondoKit/Budget` y `FutmondoKitTests`, y las ediciones de seam en
`SplashView.swift` + `FutmondoApp.swift`) y los dos artefactos de
code-generation. No se modificó `Package.swift`, `Networking/`, `Auth/`,
`DesignSystem/`, `AuthViewModel` ni `LoginView`. Sin dependencias SwiftPM nuevas.

---

## Iteración 2 — Re-trabajo de fidelidad visual (2026-10-20)

Tras validar la iteración 1 en un iPhone 13 Pro, el propietario la encontró
pobre frente al tema Angular y poco pulida para iOS 26. Esta iteración
**mantiene toda la funcionalidad, el consumo de U1, la seguridad, la máquina de
estados, la integración en `SplashView` y la sesión F1 intactas** y reescribe la
capa visual según las 5 decisiones del plan aprobado. La lógica (VM, servicios,
formateo, persistencia) **no cambia**; es un re-trabajo de presentación.

### Decisiones implementadas

- **D1 — `BudgetRow` como CARD elevada**: la fila pasa de una `List` plana a una
  `ElevatedCard` (superficie `surface`, esquinas 16, borde sutil y **sombra
  suave** `0 2px 8px rgba(0,0,0,0.08)`), reproduciendo `.team-card` de Angular.
  `team_name` como cabecera (`DSFont.h3`); fila primaria con **SALDO** (color
  money) y **RENDIMIENTO como BADGE** redondeado y tintado (`DSMoneyBadge`);
  `Divider`; fila secundaria **PUJA MÁXIMA** / **PREMIOS** con etiquetas pequeñas
  en MAYÚSCULAS (`DSStatLabel`), igual que la web. `BudgetView` presenta las
  cards en un `ScrollView` + `VStack` con fondo `surface` e insets (`DSSpacing`)
  para que se lean como tarjetas separadas (adiós a los separadores de `List`).
- **D2 — Tab bar FLOTANTE Liquid Glass**: `Package.swift` sube el deployment
  target de iOS a **26.0** (vía la forma string `.iOS("26.0")`, porque el enum
  `.v26` no existe en el `swift-tools-version:6.0` instalado). `RootTabView` usa
  el `TabView` **nativo** con la API `Tab(_:systemImage:)` (iOS 18+, con fallback
  `tabItem` defensivo), sin efecto propio: el look flotante de cristal lo aporta
  el runtime iOS 26. **Coste 0 €** (sólo SDK de Apple). El bump sólo acota builds
  Apple; en Linux/WSL el triple es `x86_64-unknown-linux-gnu`, así que
  `swift build`/`swift test` siguen compilando `FutmondoKit` + tests contra
  Foundation **sin verse afectados**.
- **D3 — Selector de campeonato como CHIP**: `ChampionshipMenu` usa el nuevo
  `DSChip` (icono SF `trophy` + nombre activo + `chevron.down`). El `Menu` lista
  los campeonatos con ✓ en el activo; con lista vacía el chip queda deshabilitado
  y atenuado (sin chevron).
- **D4 — Orden como CHIP "Ordenar por: X ▾" BAJO el título**: `SortMenu` ya no va
  en la toolbar; se renderiza como `DSChip` dentro del contenido, encima de las
  cards. Se **eliminó el botón de flechas** de la toolbar. El `Menu` ofrece las 6
  `SortKey` con ✓ en la activa.
- **D5 — Logout en MENÚ de AJUSTES (overflow ···)**: en la posición trailing de
  la navigation bar hay un `Menu` con icono `ellipsis.circle` cuyo único ítem
  (`role: .destructive`) "Cerrar sesión" invoca el **mismo** closure de logout
  (`AuthViewModel.logout()` + `phase = .noSession`, seam de F1). Se **eliminó**
  el botón suelto "Cerrar sesión" que antes vivía en la toolbar de `RootTabView`.

### Añadidos al DesignSystem de F1 (coste 0 €, sin romper el catálogo)

| Fichero | Rol |
|---------|-----|
| `ios/Sources/FutmondoApp/DesignSystem/DSElevation.swift` | **NUEVO** token de elevación/sombra (`DSElevation.card`/`.chip`), el modificador reutilizable `.dsShadow(_:)` y el contenedor `ElevatedCard` (la `Card` existente + sombra suave + padding generoso). La `Card` original queda **intacta**. |
| `ios/Sources/FutmondoApp/DesignSystem/Components/Chips.swift` | **NUEVO**: `DSStatLabel` (etiqueta pequeña en mayúsculas, `.card-stat-label`), `DSMoneyBadge` (badge money tintado, `.card-stat-val.badge`, signo como portador además del color) y `DSChip` (pill con icono/chevron/estado muted, usada por D3 y D4). |

### Ficheros reescritos (iteración 2)

- `ios/Sources/FutmondoApp/Budget/BudgetRow.swift` — card elevada (D1).
- `ios/Sources/FutmondoApp/Budget/BudgetView.swift` — `ScrollView`+`VStack` de
  cards, chip de orden bajo el título (D4), menú de ajustes con logout (D5);
  recibe ahora `onLogout`.
- `ios/Sources/FutmondoApp/Budget/RootTabView.swift` — `TabView` nativo con `Tab`
  API (D2); pasa `onLogout` a `BudgetView` en vez de alojar el botón suelto.
- `ios/Sources/FutmondoApp/Budget/ChampionshipMenu.swift` — chip con `trophy` (D3).
- `ios/Sources/FutmondoApp/Budget/SortMenu.swift` — chip "Ordenar por: X" (D4).
- `ios/Sources/FutmondoApp/DesignSystem/Catalog/CatalogView.swift` — se añaden
  `ElevatedCard`, `DSChip` y `DSMoneyBadge` a la sección Components (el catálogo
  previo se conserva íntegro).

### Ficheros editados (iteración 2)

- `ios/Package.swift` — `platforms` de iOS `.v15` → `"26.0"` (D2). Sin tocar el
  piso de macOS, productos, targets ni dependencias (siguen 0 dependencias SwiftPM).

### Invariantes preservadas

`BudgetViewModel`, `SplashView` (seam `.resumed`, `runBootstrap`, `.onChange`),
`FutmondoApp.swift`, `Networking/`, `Auth/`, `AuthViewModel`, `LoginView` y todo
`FutmondoKit` **sin cambios**. `BudgetState` sigue `Equatable` con payloads
`[TeamBudget]` (Equatable) y `String` — los nuevos tipos de vista
(`DSElevation.Level`, `DSChip`, `DSMoneyBadge`, `ElevatedCard`) no entran en
ningún payload de enum `Equatable`, así que la síntesis no se ve comprometida
(verificado por razonamiento ante el gap de WSL). Error verbatim de U1 sin
interpolar, https-only intacto, accesibilidad (label VoiceOver compuesto, Dynamic
Type vía `DSFont`, signo como portador además del color) preservada.

### Resultado de `swift build && swift test` (iteración 2)

- `cd ios && swift build` → **Build complete**. En este entorno
  `canImport(SwiftUI)` resuelve verdadero, así que **todo el target SwiftUI
  `FutmondoApp` se type-chequeó** (incluida la ruta `Tab` API y el código nuevo
  de card/badge/chip), no sólo `FutmondoKit`.
- `cd ios && swift test` → **87 tests, 0 failures**. **Sin regresión** (mismos 87
  de la iteración 1; no se extrajo lógica pura nueva, así que no se añadieron
  tests, conforme al contrato test-after).

### Nota sobre el gap de WSL

`swift test` no compila el target de app SwiftUI en el flujo de test (depende sólo
de `FutmondoKit`), pero aquí `swift build` **sí** lo compiló entero, lo que da una
verificación de compilación fuerte del código nuevo. La fidelidad visual real
(cristal flotante iOS 26, sombras, chips, badges, claro/oscuro, VoiceOver) se
valida en el iPhone 13 Pro.

### Desviaciones

- **D2 — forma de expresar iOS 26**: el `swift-tools-version:6.0` instalado no
  conoce el case `SupportedPlatform.IOSVersion.v26`; se usa la forma string
  SwiftPM `.iOS("26.0")`, equivalente y aceptada por el manifiesto. Sin otro
  impacto.
- Ninguna otra desviación respecto al plan de la iteración 2.

---

## Iteración 2b — Refinamiento visual adicional (2026-10-20)

Tras validar la iteración 2 en un iPhone 13 Pro, el propietario aprobó **3
cambios adicionales**. Esta iteración **mantiene toda la funcionalidad, el
consumo de U1, la seguridad, la máquina de estados, la integración en
`SplashView` y la sesión F1 intactas**; es de nuevo un re-trabajo de
presentación (la lógica VM/servicios/formateo/persistencia **no cambia**).

### Decisiones implementadas

- **1 — Selector de campeonato como BOTÓN ICONO GLASS arriba-izquierda**:
  `ChampionshipMenu` deja de ser un chip de título y pasa a un botón icono con
  estilo cristal (`DSGlassIcon`, nuevo) con SF Symbol **trophy** (`trophy.fill`
  con campeonatos, `trophy` atenuado cuando la lista está vacía/deshabilitada),
  colocado en la posición **leading** de la navigation bar. Se **eliminó el chip
  de título** en `.principal`. El `Menu` mantiene ✓ en el activo. La barra queda
  simétrica: trophy (leading) — título — ellipsis/ajustes (trailing), todos
  botones-icono glass con el **mismo** estilo.
- **2 — Orden como BOTÓN ICONO GLASS que abre un `.sheet` elegante**: `SortMenu`
  deja de ser un chip inline "Ordenar por"; ahora es un `DSGlassIcon`
  (`arrow.up.arrow.down`) en el grupo leading, junto al trophy, que abre un
  `.sheet` con `presentationDetents([.medium])`. La hoja (`SortSheet`) lista las
  6 `SortKey` como filas, **cada una con su propio SF Symbol** (saldo =
  `eurosign.circle`, rendimiento = `chart.line.uptrend.xyaxis`, puja máxima =
  `gauge.with.needle`, valor plantilla = `person.3`, gastado = `arrow.up.circle`,
  ingresado = `arrow.down.circle`) y ✓ en la activa; tocar una fila llama a
  `viewModel.setSort` y cierra la hoja. Estilada con el DesignSystem (`DSFont`,
  `DSColor`, `DSSpacing`), filas con `minHeight 44` y traits de accesibilidad
  (`.isHeader`, `.isSelected`).
- **3 — FONDO DEPORTIVO en la superficie autenticada**: nuevo modificador
  `.authenticatedBackground()` (`AuthenticatedBackground`) que carga el recurso
  empaquetado `background.jpg` vía **`Bundle.module`**
  (`UIImage(named:"background", in:.module, with:nil)` → `Image(decorative:)`),
  a sangre completa detrás del contenido (`scaledToFill`, `clipped`,
  `ignoresSafeArea`), con un **scrim de legibilidad** (gradiente negro sutil,
  más denso abajo) para mantener contraste del texto de las cards y las
  etiquetas de stats sobre la foto oscura (NFR1/NFR5). Las cards elevadas y la
  tab bar flotante Liquid Glass quedan **por encima**. Se aplica **sólo** a la
  superficie autenticada (`BudgetView`, dentro de `RootTabView`); **no** toca
  `SplashView`/login. Si `Bundle.module` no resuelve el recurso (p. ej. build
  Linux/WSL sin asset materializado), degrada con elegancia a un fondo sólido
  `DSColor.surface` — **nunca crash, nunca asset en blanco**.

### Añadidos al DesignSystem (coste 0 €)

| Fichero | Rol |
|---------|-----|
| `ios/Sources/FutmondoApp/DesignSystem/Components/GlassIconButton.swift` | **NUEVO** `DSGlassIcon`: botón-icono circular con relleno `.ultraThinMaterial` (look Liquid Glass), borde sutil y `dsShadow(.chip)`; `isEnabled` para el estado muted. Lo reutilizan trophy (D1 selector), sort y ajustes, para que los tres controles de la barra sean simétricos. |
| `ios/Sources/FutmondoApp/DesignSystem/Components/AuthenticatedBackground.swift` | **NUEVO** `AuthenticatedBackground` (`ViewModifier`) + `View.authenticatedBackground()`: fondo deportivo vía `Bundle.module` + scrim de legibilidad, con fallback sólido `DSColor.surface`. La imagen SwiftUI se resuelve una vez (`static let backgroundImage: Image?`). |

### Añadido a FutmondoKit (lógica pura, testeable en WSL)

| Fichero | Rol |
|---------|-----|
| `ios/Sources/FutmondoKit/Budget/SortKeyPresentation.swift` | **NUEVO** metadatos de presentación puros de `SortKey`: `SortKeyPresentation { key, label, symbolName }` (`Sendable, Equatable`), `SortKey.presentation`, `SortKey.displayOrder` y `SortKey.orderedPresentations`. Mueve el mapeo etiqueta/símbolo/orden fuera de la vista SwiftUI para poder testearlo con XCTest en Linux/WSL. |
| `ios/Tests/FutmondoKitTests/SortKeyPresentationTests.swift` | **NUEVO** 6 XCTest: el orden de display cubre los 6 casos en orden canónico, cada clave tiene label+símbolo no vacíos, labels = spec castellano, `orderedPresentations` alinea con `displayOrder`, y los 6 símbolos son distintos. |

### Ficheros reescritos (iteración 2b)

- `ios/Sources/FutmondoApp/Budget/ChampionshipMenu.swift` — botón-icono glass
  trophy en leading (1); fuera el chip de título.
- `ios/Sources/FutmondoApp/Budget/SortMenu.swift` — botón-icono glass +
  `.sheet` con filas por `SortKey` e iconos SF propios (2); contiene además la
  vista `SortSheet`.
- `ios/Sources/FutmondoApp/Budget/BudgetView.swift` — toolbar con trophy + sort
  en `.topBarLeading` y ajustes glass (`ellipsis`) en `.primaryAction`; fuera el
  chip de orden inline; hospeda `.authenticatedBackground()` y deja el contenido
  transparente sobre el fondo (3).

### Invariantes preservadas

`BudgetViewModel`, `SplashView`, `FutmondoApp.swift`, `RootTabView.swift`,
`Networking/`, `Auth/`, `AuthViewModel`, `LoginView`, `BudgetRow.swift` y el
resto de `FutmondoKit` **sin cambios**. `BudgetState` sigue `Equatable` con
payloads `[TeamBudget]`/`String`; los nuevos tipos (`DSGlassIcon`,
`AuthenticatedBackground`, `SortKeyPresentation`) **no** entran en ningún payload
de enum `Equatable`. Todo `static let` nuevo usa tipos `Sendable`
(`SortKeyPresentation`/`[SortKey]` sobre `SortKey: Sendable`; `Image?` que es
`Sendable` en SwiftUI) → seguro con Swift 6 strict-concurrency en el build de
dispositivo arm64. Error verbatim de U1 sin interpolar, https-only intacto,
VoiceOver (labels `trophy`/`sort`/`ajustes`, filas de la hoja) y Dynamic Type
(`DSFont`) preservados; el signo sigue siendo portador de significado además del
color.

### Resultado de `swift build && swift test` (iteración 2b)

- `cd ios && swift build` → **Build complete** (sin errores ni warnings nuevos).
  En este entorno `canImport(SwiftUI)` resuelve verdadero, así que el target
  SwiftUI `FutmondoApp` **sí** se type-chequeó entero (botones glass, hoja de
  orden y modificador de fondo incluidos). El recurso `background.jpg` se copia
  correctamente (`Copying background.jpg`).
- `cd ios && swift test` → **93 tests, 0 failures** (87 preexistentes + 6 nuevos
  de `SortKeyPresentationTests`). **Sin regresión.**

### Nota sobre el gap de WSL

`swift test` no compila el target de app SwiftUI en el flujo de test, pero aquí
`swift build` lo compiló entero (verificación de compilación fuerte del código
nuevo). La resolución real de `Bundle.module` para `background.jpg`, el look
Liquid Glass de los botones/tab bar, el contraste del scrim, la hoja con
detents, y VoiceOver/Dynamic Type/claro-oscuro se validan en el iPhone 13 Pro.

### Desviaciones

- **2 — símbolo de puja máxima**: el brief sugería `hammer`/`gauge`; se usó
  `gauge.with.needle` (un SF Symbol estable y legible para "puja máxima"). Sin
  otro impacto; es un detalle de icono.
- Ninguna otra desviación respecto a las 3 decisiones aprobadas. El background ya
  estaba movido a `Resources/` y declarado `.process` en `Package.swift` (hecho
  previamente); esta iteración sólo añadió el código Swift que lo consume, por lo
  que **`Package.swift` no se tocó** en 2b.

---

## Iteración 2c — Tema oscuro global + cards neon-glass (2026-10-20)

Tras validar la iteración 2b en un iPhone 13 Pro, el propietario dio una
dirección visual clara (más una captura de referencia, `presupuesto_sample.jpg`):
fondo de estadio casi negro con rejilla neón-verde, y cards de equipo **oscuras
translúcidas (dark glass)** con borde/halo neón-verde sutil, texto blanco,
etiquetas en gris claro, SALDO verde, RENDIMIENTO como badge, PREMIOS en azul.
Esta iteración **mantiene toda la funcionalidad, el consumo de U1, la seguridad,
la máquina de estados, la integración en `SplashView` y la sesión F1 intactas**;
es de nuevo un re-trabajo de presentación (la lógica VM/servicios/formateo/
persistencia **no cambia**).

### Decisiones implementadas

- **1 — DARK global**: `.preferredColorScheme(.dark)` se aplica en el contenido
  del `WindowGroup` de `FutmondoApp.swift` (el root de escena), de forma que
  toda la app —incluidas la presentación de login/splash de F1— renderiza en
  oscuro. **No** se tocó ninguna lógica de F1 (AuthViewModel/AuthService/
  LoginView/SplashView); sólo el color scheme, en el punto menos invasivo.
- **2 — Card DARK NEON-GLASS**: nuevo contenedor reutilizable `NeonGlassCard` en
  `DSElevation.swift`. El fondo es negro al ~0.45 de opacidad **sobre**
  `.ultraThinMaterial` (lee como cristal oscuro sobre la foto), con borde
  neón-verde sutil (`DSColor.primary` a alpha 0.35, `lineWidth` 1) y un
  **glow verde suave** (sombra verde de opacidad baja y radio generoso vía el
  nuevo nivel `DSElevation.neonGlow` = opacity 0.35 / radius 14 / y 0). Mantiene
  el **radio de esquina 16** y el padding del DS. **No** rompe `Card`/
  `ElevatedCard` (que el catálogo sigue usando); `BudgetRow` se **repunta** al
  nuevo estilo.
- **3 — Contenido de `BudgetRow`**: nombre de equipo en **BLANCO** (`DSFont.h3`,
  `DSColor.onSurface`) + **divider sutil** (`DSColor.onSurface` a 0.15); fila
  primaria SALDO (verde money) + RENDIMIENTO como **badge** redondeado tintado
  (`DSMoneyBadge`, verde ≥0 / rojo <0, con signo); fila secundaria PUJA MÁXIMA
  (blanco) + PREMIOS (**azul**, nuevo token `moneyPrize`); etiquetas en
  MAYÚSCULAS en gris claro (`DSStatLabel` → `DSColor.onSurfaceVariant`).
- **4 — Título "Presupuesto" legible**: con el dark scheme global el large title
  resuelve en blanco automáticamente; se dejó que lo maneje el esquema oscuro
  (sin `titleTextAttributes` ni principal custom), conservando el estilo large
  (Apple Music) ya fijado.
- **5 — Accesibilidad / contraste (NFR1 ≥4.5:1 / NFR5)**: se usó el helper puro
  `ContrastRatio` (FutmondoKit) para **validar** los colores elegidos contra la
  superficie de la card oscura. Se añadió el token opaco de referencia
  `cardSurfaceDark` (`#141814`, un carbón verdoso muy oscuro que aproxima el
  negro-0.45-sobre-material) y un test puro nuevo que asevera que cada color de
  texto de la card cumple ≥4.5:1 sobre esa superficie. El signo sigue siendo el
  portador NO-cromático del significado del dinero; labels VoiceOver compuestos
  y Dynamic Type intactos.

### Colores elegidos y contraste medido (sobre `cardSurfaceDark` `#141814`, apariencia dark)

| Rol | Color (dark) | Ratio medido | Umbral |
|-----|--------------|--------------|--------|
| Nombre de equipo + PUJA MÁXIMA (blanco) | `onSurface` `#E6E1E5` | **13.90:1** | ≥4.5 |
| Etiquetas MAYÚSCULAS (gris) | `onSurfaceVariant` `#CAC4D0` | **10.52:1** | ≥4.5 |
| SALDO + RENDIMIENTO positivo (verde) | `moneyPositive` `#66BB6A` | **7.59:1** | ≥4.5 |
| RENDIMIENTO negativo (rojo) | `moneyNegative` `#EF5350` | **5.15:1** | ≥4.5 |
| PREMIOS (azul) | `moneyPrize` `#64B5F6` | **8.10:1** | ≥4.5 |

Todos superan el umbral de texto normal ≥4.5:1 con holgura, así que no hizo falta
oscurecer la superficie ni aclarar el texto más allá de la paleta Material 3; los
acentos neón quedan vivos pero no estridentes. El azul `moneyPrize` dark `#64B5F6`
es el que se renderiza; su valor light `#1565C0` existe sólo por paridad (la app
va forzada a dark).

### Añadidos a FutmondoKit (lógica pura, testeable en WSL)

| Fichero | Rol |
|---------|-----|
| `ios/Sources/FutmondoKit/DesignSystem/DSColorValue.swift` | **EDITADO**: dos roles nuevos en `DSColorToken` — `moneyPrize` (azul PREMIOS, light `#1565C0` / dark `#64B5F6`) y `cardSurfaceDark` (`#141814` en ambas, baseline opaco de contraste de la card glass). El enum sigue `String`-raw, `CaseIterable`, `Sendable`; añadir cases no compromete `Sendable`/`Equatable`. |

### Añadidos / ediciones al DesignSystem de la app (coste 0 €)

| Fichero | Rol |
|---------|-----|
| `ios/Sources/FutmondoApp/DesignSystem/DSElevation.swift` | **EDITADO**: nuevo nivel `DSElevation.neonGlow` (glow verde, opacity 0.35 / radius 14 / y 0) y nuevo contenedor `NeonGlassCard` (negro 0.45 sobre `.ultraThinMaterial`, borde neón-verde, glow verde, radio 16). `Card`/`ElevatedCard`/`dsShadow` intactos. |
| `ios/Sources/FutmondoApp/DesignSystem/DSColor.swift` | **EDITADO**: accesores SwiftUI `DSColor.moneyPrize` y `DSColor.cardSurfaceDark` para los dos tokens nuevos. |

### Ficheros editados (iteración 2c)

- `ios/Sources/FutmondoApp/FutmondoApp.swift` — `.preferredColorScheme(.dark)` en
  el contenido del `WindowGroup` (1). Sin tocar el grafo de dependencias ni la
  lógica de arranque F1.
- `ios/Sources/FutmondoApp/Budget/BudgetRow.swift` — repuntada a `NeonGlassCard`;
  nombre blanco + divider; PREMIOS azul (`DSColor.moneyPrize`); PUJA MÁXIMA
  blanco; `secondaryMetric` ahora toma un `color` explícito (3).
- `ios/Tests/FutmondoKitTests/DesignSystemTests.swift` — recuento de roles 9 → 11;
  nuevo test `testDarkNeonGlassCardTextMeetsContrast` que asevera ≥4.5:1 de los 5
  colores de texto de la card sobre `cardSurfaceDark` (5).

### Invariantes preservadas

`BudgetViewModel`, `SplashView` (seam `.resumed`, `runBootstrap`, `.onChange`),
`RootTabView.swift`, `Networking/`, `Auth/`, `AuthViewModel`, `LoginView`,
`ChampionshipMenu`/`SortMenu`/`BudgetView` (lógica) y el resto de `FutmondoKit`
**sin cambios de comportamiento**. `BudgetState` sigue `Equatable` con payloads
`[TeamBudget]`/`String`; los tipos nuevos (`NeonGlassCard`, los tokens de color)
**no** entran en ningún payload de enum `Equatable`. Todo `static let` nuevo usa
tipos `Sendable` (`DSElevation.Level` es `Sendable`; los tokens son cases de un
enum `Sendable`) → seguro con Swift 6 strict-concurrency en arm64. APIs SwiftUI/
UIKit revisadas (`.preferredColorScheme`, `.ultraThinMaterial`,
`.background(_:in:)`, `.shadow`, `Divider().overlay`), todas iOS 15+. Error
verbatim de U1 sin interpolar, https-only intacto, sin dependencias SwiftPM
nuevas.

### Resultado de `swift build && swift test` (iteración 2c)

- `cd ios && swift build` → **Build complete** (sin errores ni warnings nuevos).
  En este entorno `canImport(SwiftUI)` resuelve verdadero, así que el target
  SwiftUI `FutmondoApp` **sí** se type-chequeó entero (`NeonGlassCard`, el dark
  scheme global y el `BudgetRow` repuntado incluidos).
- `cd ios && swift test` → **94 tests, 0 failures** (93 preexistentes + 1 nuevo
  `testDarkNeonGlassCardTextMeetsContrast`). **Sin regresión.**

### Nota sobre el gap de WSL

`swift test` no compila el target de app SwiftUI en el flujo de test (depende sólo
de `FutmondoKit`), pero aquí `swift build` lo compiló entero (verificación de
compilación fuerte del código nuevo de 2c). El look real del dark glass, el halo/
glow neón, la legibilidad del texto sobre la foto translúcida, el título blanco y
el dark scheme global se validan en el iPhone 13 Pro.

### Desviaciones

- Ninguna respecto a la dirección aprobada. El badge de RENDIMIENTO se mantiene
  con texto money-color sobre tinte translúcido (patrón A7 ya validado en 2/2b),
  en lugar de texto oscuro sobre relleno sólido claro de la captura: conserva el
  signo como portador y el contraste, y queda consistente con el resto del DS.

---

## Iteración 2d — Botones de barra blancos + pantalla de detalle de equipo (2026-10-20)

Dos trabajos sobre la base de 2c: (1) un ajuste pequeño de color en los tres
controles glass de la navigation bar, y (2) una **pantalla nueva aprobada en
scope** (detalle de equipo, **FR6**) consumiendo un endpoint ya verificado en el
codekb. Se mantiene todo lo anterior intacto: consumo de U1, seguridad
(https-only, error verbatim sin fugas), lógica F1 de auth/sesión, tema oscuro +
cards neon-glass, y sin dependencias SwiftPM nuevas.

### TAREA 1 — Botones de toolbar en BLANCO

- `DSGlassIcon` cambia su foreground **habilitado** de `DSColor.primary` (verde)
  a **`DSColor.onSurface`** (blanco en dark), para que los tres controles glass
  (trophy selector de campeonato, orden, ajustes ···) casen con el large title
  blanco. El estado muted/deshabilitado se conserva (`onSurfaceVariant` atenuado
  al 0.5). **No** se reintroduce material/círculo/sombra manual: la cápsula glass
  la sigue aportando la toolbar nativa de iOS 26.

### TAREA 2 — Pantalla DETALLE DE EQUIPO (FR6, expansión de scope)

Endpoint: `GET /api/v1/analytics/balances/{team_id}?championship_id=<id>` →
`TeamDetailResponse { success, team_id, team_name, balance, initial_budget,
total_spent, total_income, purchases:[Transaction], sales:[Transaction] }`,
`Transaction { player_id, player_name, price, date, from?, to? }` (claves
snake_case; `from` = procedencia en compras, `to` = destino en ventas).

#### U1 (`FutmondoKit/Budget/`) — datos/lógica, con XCTest (test-after)

| Fichero | Rol |
|---------|-----|
| `ios/Sources/FutmondoKit/Budget/Transaction.swift` | **NUEVO** DTO `Codable, Sendable, Equatable, Identifiable`; `CodingKeys` snake_case (`player_id`, `player_name`, `price`, `date`, `from`, `to`); `from`/`to` opcionales; `id` compuesto (`player_id#date`) estable dentro de una lista. |
| `ios/Sources/FutmondoKit/Budget/TeamDetailResponse.swift` | **NUEVO** DTO `Codable, Sendable, Equatable`; `CodingKeys` snake_case; listas `purchases`/`sales` de `Transaction` (vacías → listas vacías). `Equatable`/`Sendable` para poder ser payload del estado `Equatable` del view model y cruzar el `async`. |
| `ios/Sources/FutmondoKit/Budget/BudgetService.swift` | **EDITADO**: protocolo `BudgetService` extendido con `func fetchTeamDetail(teamId:championshipId:) async throws -> TeamDetailResponse`; implementado en `HTTPBudgetService` (GET `analytics/balances/{team_id}?championship_id=`, mismo `NetworkClient`, misma garantía typed-error/no-leak que `fetchBalances` — el `team_id` es segmento de ruta y el `championship_id` query; el `NetworkError` tipado no hace eco de URL/query, SR1). |
| `ios/Sources/FutmondoKit/Budget/TransactionDatePresenter.swift` | **NUEVO** presentador puro de fecha ISO `yyyy-MM-dd` (con/sin sufijo de hora) → `dd/MM/yyyy`; sin `DateFormatter`/locale (idéntico en WSL y dispositivo); fallback verbatim si no parsea. Extraído a `FutmondoKit` para testearlo con XCTest en WSL. |

XCTest añadidos (todos ejecutables en WSL):
- `BudgetDTOTests.swift` (**EDITADO**): +3 tests — `TeamDetailResponse` decodifica
  snake_case incl. `from`/`to` opcionales (compra con `from`/sin `to`, venta con
  `to`/sin `from`), listas vacías, y fallo de decode por campo requerido ausente
  (SR4).
- `BudgetServiceTests.swift` (**EDITADO**): +3 tests — `fetchTeamDetail` ok
  (decode incl. opcionales y ruta correcta), error de red propagado como
  `NetworkError` tipado, y **sin fuga** de `team_id`/`championship_id` en el error
  (SR1).
- `TransactionDatePresenterTests.swift` (**NUEVO**): 5 tests — ISO plano,
  ISO con hora (`T`/espacio), padding de un dígito, string no-ISO verbatim, y
  componentes no numéricos verbatim.

#### U2 (`FutmondoApp/Budget/`) — la pantalla, iOS 26+ moderno

| Fichero | Rol |
|---------|-----|
| `ios/Sources/FutmondoApp/Budget/TeamDetailViewModel.swift` | **NUEVO** `@MainActor @Observable`; estado `TeamDetailState { loading, loaded(TeamDetailResponse), error(String) }`; inyecta `BudgetService` + `ActiveChampionshipStore` (de donde resuelve el `championshipId` activo); `load(teamId:)` fija `.loading` síncrono antes del `await`; error verbatim de U1 sin interpolar ids (SR1). |
| `ios/Sources/FutmondoApp/Budget/TeamDetailView.swift` | **NUEVO** la pantalla: `TeamDetailRoute` (Hashable: `teamId`+`teamName`); hero large title colapsable con el nombre del equipo (blanco); SUMMARY de 3 mini-cards glass (Saldo actual / Gastado / Ingresado) con money tokens y `.contentTransition(.numericText())`; `Picker(.segmented)` **Compras | Ventas** con transición deslizante + háptica sutil (`UIImpactFeedbackGenerator`, `#if canImport(UIKit)`); cada operación como fila `NeonGlassCard` (nombre blanco, precio con money token — compras negativo/rojo, ventas positivo/verde —, procedencia/destino secundario, fecha `dd/MM/yyyy` vía `TransactionDatePresenter`), entrando con `.scrollTransition` fade/scale escalonado; estados vacíos por sección ('No hay compras registradas.' / 'No hay ventas registradas.') con contador en cabecera del picker; loading/error (`ErrorState` + Reintentar con foco VoiceOver); labels VoiceOver compuestos (filas y summary); el signo es el portador no-cromático. También `TeamDetailTransactionRow` público y el modificador `StaggeredAppear` (guardado iOS 17+). |

Integración de navegación:
- `ios/Sources/FutmondoApp/Budget/BudgetView.swift` (**EDITADO**): cada `BudgetRow`
  se envuelve en un `NavigationLink(value: TeamDetailRoute)` (`.buttonStyle(.plain)`)
  con `.matchedTransitionSource(id:in:)` (vía el modificador `ZoomSource`,
  `#available(iOS 18+)`); nuevo `.navigationDestination(for: TeamDetailRoute.self)`
  que construye `TeamDetailView` y aplica `.navigationTransition(.zoom(sourceID:in:))`
  bajo un `@Namespace` compartido (fallback a push normal si <iOS 18). `init` toma
  ahora un `makeTeamDetailViewModel: () -> TeamDetailViewModel`.
- `ios/Sources/FutmondoApp/Budget/RootTabView.swift` (**EDITADO**): reenvía el
  factory `makeTeamDetailViewModel` a `BudgetView`.
- `ios/Sources/FutmondoApp/SplashView.swift` (**EDITADO, seam**): retiene el
  `budgetService` (`HTTPBudgetService`) + `activeStore`
  (`UserDefaultsActiveChampionshipStore`) compartidos (mismo cliente HTTPS, AR8/
  SEC-N1) y pasa a `RootTabView` un factory que crea un `TeamDetailViewModel` por
  detalle sobre esos mismos colaboradores. `runBootstrap`, `.onChange`, casos
  `.checking/.offline/.expired/.noSession` y el closure de logout **intactos**.
- `ios/Sources/FutmondoApp/DesignSystem/Components/GlassIconButton.swift`
  (**EDITADO**): `DSGlassIcon` foreground habilitado verde → blanco (TAREA 1).

### Revisión mental arm64 (gap de WSL)

`swift test` no compila el target SwiftUI, así que se revisó para arm64: APIs
nuevas de transición (`matchedTransitionSource`, `navigationTransition(.zoom)`)
**guardadas con `#available(iOS 18)`**; `.scrollTransition`/`StaggeredAppear`
bajo el floor iOS 17 del VM/vista; `.contentTransition(.numericText())` iOS 16+;
háptica bajo `#if canImport(UIKit)`; `TeamDetailResponse` + `Transaction` son
`Equatable` (viajan en el payload `Equatable` del estado del VM); `Transaction`/
`TeamDetailResponse`/`TransactionDatePresenter` son `Sendable`; no se usa
`Image(decorative:)`; tipos valor y `@MainActor` en el VM. Aquí además
`swift build` compiló el target SwiftUI entero (verificación de compilación
fuerte).

### Resultado de `swift build && swift test` (iteración 2d)

- `cd ios && swift build` → **Build complete** (sin errores ni warnings nuevos);
  `canImport(SwiftUI)` resuelve verdadero → el target `FutmondoApp` se
  type-chequeó entero (detalle de equipo, links de navegación, zoom guardado y
  botones blancos incluidos).
- `cd ios && swift test` → **105 tests, 0 failures** (94 preexistentes + 11
  nuevos: 3 DTO `TeamDetailResponse`/`Transaction`, 3 de `fetchTeamDetail`, 5 de
  `TransactionDatePresenter`). **Sin regresión** de los 94.

### Invariantes preservadas

Lógica F1 de auth/sesión, https-only, error verbatim de U1 sin interpolar ids,
tema oscuro global + `NeonGlassCard`, `BudgetViewModel`/servicios de U1 sin
cambios de comportamiento, sin dependencias SwiftPM nuevas, `Package.swift` sin
tocar. Accesibilidad (labels compuestos de filas y summary, foco a Reintentar,
Dynamic Type vía `DSFont`, signo como portador además del color) preservada y
extendida a la pantalla nueva.

### Validación en dispositivo (pendiente, iPhone 13 Pro)

Tap en una fila de presupuesto → transición zoom al detalle; hero colapsable;
animación `numericText` de los 3 money del summary; conmutación Compras/Ventas
con deslizamiento + háptica; entrada escalonada de filas; estados vacíos por
sección; loading/error + Reintentar; botones de barra blancos sobre el glass
nativo; VoiceOver y Dynamic Type.

### Desviaciones

- `TransactionDatePresenter` se **extrajo a `FutmondoKit`** (en vez de dejar el
  formateo dentro de la vista SwiftUI) para poder cubrirlo con XCTest en WSL; es
  lógica pura no trivial (parsing/padding/fallback), coherente con la regla
  durable iOS/WSL de colocar la lógica testeable en el target library. Ninguna
  otra desviación respecto al brief.

---

## Iteración 2e — pulido de interacción del detalle de equipo

Dos refinamientos sobre `TeamDetailView` (y solo lo que necesitan), sin tocar
contratos F1/https/U1, sin dependencias SwiftPM nuevas y sin cambios de
comportamiento en el VM salvo el disparador de entrada.

### CAMBIO 1 — Selector Compras|Ventas a botón GLASS de la barra (Opción A)

- Se **retira el `Picker` segmentado inline** del cuerpo scrolleable.
- Se añade un `ToolbarItem(placement: .topBarTrailing)` cuya etiqueta es un
  `DSGlassIcon(systemImage: "arrow.left.arrow.right")` (icono glass blanco,
  mismo patrón que trophy/sort/ellipsis de `BudgetView`). El item vive en un
  `@ToolbarContentBuilder` (`sectionToolbar`) y **solo se muestra en `.loaded`**,
  porque sus etiquetas llevan los contadores por sección.
- El `Menu` contiene dos botones **"Compras (<n>)"** y **"Ventas (<n>)"**
  (contadores conservados) con `checkmark` vía `Label` en la sección activa.
  Seleccionar uno actualiza el `@State section` existente (enum
  `TransactionSection` conservado).
- La lista de la sección elegida sigue renderizándose en el cuerpo del scroll
  (ya sin el control inline), con la transición de deslizamiento/opacidad
  (`.animation(.easeInOut, value: section)` + `.transition(.opacity)`) y la
  **háptica guardada** movida a un `.onChange(of: section)` sobre el contenido
  cargado (antes colgaba del `Picker`).

### CAMBIO 2 — Entrada de datos escalonada tras el zoom (soft landing)

- Nuevo `@State hasAppeared`, puesto a `true` cuando el estado del VM pasa a
  `.loaded` (y a `false` al volver a `.loading`), desde el `.onChange(of:
  viewModel.state)` del `body`.
- Nuevo `ViewModifier` privado `EntranceAppear(visible:reduceMotion:delay:)`:
  aplica `opacity` + `offset(y:)` que se resuelven con
  `.animation(.easeOut(duration: 0.4).delay(delay), value: visible)` — fundido
  + leve desplazamiento hacia su sitio, sin mover el contenido una vez asentado
  (no interfiere con `.contentTransition(.numericText())` de los money del
  summary, **conservado**).
- El `summaryRow` entra con `EntranceAppear` sin delay; cada fila de
  transacción entra con **delay escalonado por índice** vía
  `staggerDelay(for:) = min(index * 0.05, 0.6)` (base 0.05 s/fila, capado a
  0.6 s) para una entrada secuencial, no un "pop".
- **Reduce Motion**: `@Environment(\.accessibilityReduceMotion)`. Si está
  activo, `EntranceAppear` devuelve el contenido tal cual (sin offset ni
  animación) y el flip de `hasAppeared` ocurre sin `withAnimation`.
- El `hero title` sigue siendo el large title colapsable del sistema
  (`.navigationTitle`), que ya anima con la transición de push/zoom; la entrada
  explícita se aplica al contenido que antes aparecía de golpe (summary + filas).

### Archivos editados (iteración 2e)

- `ios/Sources/FutmondoApp/Budget/TeamDetailView.swift` (**EDITADO**): toolbar
  glass menu de sección, entrada escalonada con `EntranceAppear`, Reduce Motion,
  háptica movida al contenido cargado, `StaggeredAppear` (basado en
  `scrollTransition`) **reemplazado** por `EntranceAppear`, y comentarios de doc
  actualizados (ya no es un segmented control inline). **No** se tocó
  `TeamDetailViewModel.swift` (no hizo falta estado adicional en el VM).

### Revisión mental arm64 (gap de WSL)

`swift test` no compila el target SwiftUI, así que se revisó para arm64: todo el
código nuevo vive bajo el floor `@available(iOS 17.0, macOS 14.0, *)` del
struct/modifier; `.topBarTrailing` y `@ToolbarContentBuilder` son iOS 16+
(cubierto por el floor 17, y ya usado análogamente con `.topBarLeading` en
`BudgetView`); `.contentTransition(.numericText())` conservado (iOS 16+);
háptica bajo `#if canImport(UIKit)` + `#available(iOS 17)`; `FutmondoKit.Transaction`
sigue **cualificado** en `TeamDetailTransactionRow` para no chocar con
`SwiftUI.Transaction`; `EntranceAppear` es un `ViewModifier` de tipo valor con
campos `Bool`/`Double` (sin estáticos `Sendable` ni payloads `Equatable`
nuevos); no se usa `Image(decorative:)`. Además `swift build` compiló el target
SwiftUI entero (verificación de compilación fuerte).

### Resultado de `swift build && swift test` (iteración 2e)

- `cd ios && swift build` → **Build complete** (sin errores ni warnings nuevos);
  `canImport(SwiftUI)` resuelve verdadero → `FutmondoApp` se type-chequeó entero
  (toolbar menu de sección y entrada escalonada incluidos).
- `cd ios && swift test` → **105 tests, 0 failures**. **Sin regresión**; no se
  añadió lógica pura nueva que justifique un test (`staggerDelay` es un clamp
  trivial).

### Desviaciones

Ninguna respecto al brief. El `hero title` se deja como large title del sistema
(anima con el zoom); la animación de entrada explícita se concentra en summary +
filas, que es exactamente lo que antes "aparecía de golpe".
