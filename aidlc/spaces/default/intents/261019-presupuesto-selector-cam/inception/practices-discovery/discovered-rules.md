# Discovered Rules — F2 `261019-presupuesto-selector-cam`

> Reglas candidatas `ALWAYS`/`NEVER` evidenciadas por el codebase actual y por el
> set afirmado. Cada una etiquetada `ya afirmada` o `nueva`, con una línea de
> rationale. Para F2 se espera que casi todo sea `ya afirmada`. El marcador
> `ALWAYS`/`NEVER` es token fijo; la prosa va en castellano.

## Reglas ya afirmadas (vigentes para F2)

- **[ya afirmada]** NEVER introducir dependencias de pago ni salir de los tiers
  gratuitos; cualquier librería nueva sería OSS y fijada a versión exacta.
  — *Rationale*: `ios/Package.swift` declara `dependencies: []`; SwiftUI es SDK de
  Apple. Mandato coste 0 € durable.

- **[ya afirmada]** NEVER almacenar la contraseña ni el refresh token Futmondo en
  claro; el refresh token va a Keychain nativo (`AfterFirstUnlockThisDeviceOnly`),
  NUNCA a `localStorage`/`ApplicationSettings`.
  — *Rationale*: `KeychainTokenStore.swift` ya lo implementa; Budget reutiliza la
  sesión existente sin tocar almacenamiento de credenciales.

- **[ya afirmada]** NEVER incluir material de credencial (password/token) en el
  `message`/`repr`/`exc_info` de una excepción.
  — *Rationale*: `NetworkError`/`AuthError`/`KeychainError` son `Equatable` con
  payloads no sensibles (SEC-N4).

- **[ya afirmada]** NEVER bajar/relajar un umbral o piso de cobertura para pasar el
  gate; el ratchet sólo sube y el flapping se arregla en el test no-determinista.
  — *Rationale*: pisos backend `--cov-fail-under=27` y frontend 19/19/17/18
  vigentes; F2 no los toca.

- **[ya afirmada]** NEVER ampliar los god-files existentes
  (`data_manager_v2.py`, `data_sync_service.py`, `assistant_service.py`,
  `photo_service.py`) ni el patrón SQL-en-router.
  — *Rationale*: F2 es cliente nativo iOS, no toca backend; se cumple por
  construcción.

- **[ya afirmada]** NEVER correr `ruff format` masivo ni `--fix` de repo entero (ni
  Prettier masivo) sobre ficheros brownfield ya modificados; formatear sólo lo
  nuevo o de forma quirúrgica.
  — *Rationale*: regla durable de estabilidad del diff y del pase de revisión.

- **[ya afirmada]** NEVER reintroducir Google Stitch como referencia de diseño; la
  única fuente de verdad es el tema Angular Material 3.
  — *Rationale*: decisión del propietario (2026-10-18) registrada en `project.md`.

- **[ya afirmada]** ALWAYS pasar el gate de CI bloqueante (gitleaks + `ruff check` +
  `pytest` + `pip-audit` + `ng test` + `npm audit`) antes de fusionar a `main`,
  incluso para cambios de cliente nativo/diseño; un rojo nunca llega a producción.
  — *Rationale*: gate replicado en `ci.yml` y `fly-deploy.yml`.

- **[ya afirmada]** ALWAYS mantener trunk-based + squash-merge a `main` (base `main`,
  destino `main`), con ramas cortas prefijadas por tipo y Conventional Commits con
  scope en castellano.
  — *Rationale*: Way of Working en `team.md`/`org.md`.

- **[ya afirmada]** ALWAYS reproducir en SwiftUI el tema Angular Material 3 como
  fuente de verdad (tokens de color/tipografía/superficies, modo claro/oscuro);
  cubrir con Apple HIG donde no haya equivalente 1:1.
  — *Rationale*: `DSColorToken`/`DSColorValue`/`DSTypographyScale` ya reproducen la
  paleta verde/violeta y la escala; Budget/selector consumen esos tokens.

- **[ya afirmada]** ALWAYS usar identificadores/docstrings/comentarios en INGLÉS y
  texto de usuario / mensajes de commit en CASTELLANO.
  — *Rationale*: política de idioma durable; el código iOS existente ya la sigue
  (docstrings en inglés en `DSColor.swift`, `DSColorValue.swift`).

- **[ya afirmada]** ALWAYS colocar la lógica pura testeable en `FutmondoKit`
  (cubierta por `swift test`/XCTest) y las vistas SwiftUI en `FutmondoApp` tras
  `#if canImport(SwiftUI)`, validándolas en dispositivo (iPhone 13 Pro, `xtool`);
  el testTarget depende sólo de `FutmondoKit`.
  — *Rationale*: Correction aprendida 2026-10-19 en `project.md`, evidenciada en
  `Package.swift` y en la separación de targets actual. (Candidato "nuevo" plausible
  que resulta YA afirmado.)

- **[ya afirmada]** ALWAYS definir los Color Sets en código (`DSColorToken`/
  `DSColorValue`), no en `Assets.xcassets`, y mantener `Package.swift` sin
  `resources` de asset catalog mientras se construya en WSL/Linux (`actool` ausente).
  — *Rationale*: Correction aprendida 2026-10-19; `Package.swift` no declara
  `resources`.

- **[ya afirmada]** ALWAYS aceptar que la cobertura de línea iOS (`llvm-cov`) no es
  medible de forma fiable en WSL/Linux: cubrir `FutmondoKit` con `swift test` y
  validar las vistas en dispositivo, sin introducir un piso numérico iOS en WSL.
  — *Rationale*: Correction aprendida 2026-10-19.

## Reglas nuevas (propuestas a afirmar)

**Ninguna.** No se evidencia en la capa iOS ni en las áreas Budget/championship
ninguna práctica que no esté ya capturada por las reglas afirmadas o las Corrections
aprendidas. El candidato esperado (estructura/testing iOS) resultó ya afirmado.

## Sources

- `aidlc/spaces/default/memory/{team.md,project.md,org.md}`
- `aidlc/spaces/default/codekb/futmondo-analytics/{technology-stack,code-quality-assessment,dependencies,code-structure}.md`
- `ios/Package.swift`, `ios/xtool.yml`
- `ios/Sources/FutmondoKit/DesignSystem/{DSColorValue,DSTypographyScale,ContrastRatio}.swift`
- `ios/Sources/FutmondoApp/DesignSystem/DSColor.swift`
- `ios/Tests/FutmondoKitTests/{DesignSystemTests,AuthServiceTests,NetworkClientTests}.swift`

## Assumptions & Open Questions

None.
